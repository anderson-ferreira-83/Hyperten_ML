#!/bin/bash
set -e

# Script de deploy automatizado para AWS
# Este script faz o deploy completo da aplicação (API + UI) na AWS

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para printar mensagens coloridas
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se o arquivo de configuração existe
if [ ! -f "deploy_config.sh" ]; then
    print_error "Arquivo deploy_config.sh não encontrado!"
    print_info "Copie o arquivo deploy_config.example.sh para deploy_config.sh e configure suas credenciais:"
    print_info "  cp deploy_config.example.sh deploy_config.sh"
    print_info "  nano deploy_config.sh"
    exit 1
fi

# Carregar configurações
source deploy_config.sh

# Verificar variáveis obrigatórias
if [ -z "$AWS_REGION" ] || [ -z "$AWS_ACCOUNT_ID" ] || [ -z "$ECR_REPO_NAME" ]; then
    print_error "Variáveis obrigatórias não configuradas!"
    print_info "Edite o arquivo deploy_config.sh e configure:"
    print_info "  - AWS_REGION"
    print_info "  - AWS_ACCOUNT_ID"
    print_info "  - ECR_REPO_NAME"
    exit 1
fi

# Variáveis derivadas
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
ECR_FULL_URI="${ECR_URI}/${ECR_REPO_NAME}:${IMAGE_TAG}"

print_info "=== Deploy AWS - Hypertension Prediction API ==="
print_info "Região: $AWS_REGION"
print_info "Account ID: $AWS_ACCOUNT_ID"
print_info "Repositório ECR: $ECR_REPO_NAME"
print_info ""

# Menu de opções
echo "Escolha uma opção:"
echo "1) Deploy completo (ECR + Lambda + API Gateway)"
echo "2) Apenas build e push da imagem Docker para ECR"
echo "3) Apenas criar/atualizar Lambda"
echo "4) Deploy da UI no S3"
echo "5) Sair"
read -p "Opção: " option

case $option in
    1)
        print_info "Iniciando deploy completo..."
        DO_ECR=true
        DO_LAMBDA=true
        ;;
    2)
        print_info "Build e push da imagem Docker..."
        DO_ECR=true
        DO_LAMBDA=false
        ;;
    3)
        print_info "Criar/atualizar Lambda..."
        DO_ECR=false
        DO_LAMBDA=true
        ;;
    4)
        print_info "Deploy da UI no S3..."
        DO_UI=true
        DO_ECR=false
        DO_LAMBDA=false
        ;;
    5)
        print_info "Saindo..."
        exit 0
        ;;
    *)
        print_error "Opção inválida!"
        exit 1
        ;;
esac

# ========================================
# 1) ECR - Criar repositório, build e push
# ========================================
if [ "$DO_ECR" = true ]; then
    print_info "Passo 1: Configurando ECR..."

    # Verificar se repositório existe, se não, criar
    if ! aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$AWS_REGION" &> /dev/null; then
        print_warn "Repositório ECR não encontrado. Criando..."
        aws ecr create-repository \
            --repository-name "$ECR_REPO_NAME" \
            --region "$AWS_REGION" \
            --image-scanning-configuration scanOnPush=true
        print_info "Repositório ECR criado com sucesso!"
    else
        print_info "Repositório ECR já existe."
    fi

    # Login no ECR
    print_info "Fazendo login no ECR..."
    aws ecr get-login-password --region "$AWS_REGION" | \
        docker login --username AWS --password-stdin "$ECR_URI"

    # Build da imagem
    print_info "Construindo imagem Docker..."
    docker build -t "$ECR_REPO_NAME:$IMAGE_TAG" .

    # Tag da imagem
    print_info "Tagueando imagem..."
    docker tag "$ECR_REPO_NAME:$IMAGE_TAG" "$ECR_FULL_URI"

    # Push da imagem
    print_info "Enviando imagem para ECR..."
    docker push "$ECR_FULL_URI"

    print_info "Imagem enviada com sucesso: $ECR_FULL_URI"
fi

# ========================================
# 2) Lambda - Criar ou atualizar função
# ========================================
if [ "$DO_LAMBDA" = true ]; then
    print_info "Passo 2: Configurando Lambda..."

    # Verificar se função Lambda existe
    if aws lambda get-function --function-name "$LAMBDA_FUNCTION_NAME" --region "$AWS_REGION" &> /dev/null; then
        print_warn "Função Lambda já existe. Atualizando código..."
        aws lambda update-function-code \
            --function-name "$LAMBDA_FUNCTION_NAME" \
            --image-uri "$ECR_FULL_URI" \
            --region "$AWS_REGION"

        print_info "Aguardando atualização da Lambda..."
        aws lambda wait function-updated \
            --function-name "$LAMBDA_FUNCTION_NAME" \
            --region "$AWS_REGION"

        print_info "Atualizando configuração da Lambda..."
        aws lambda update-function-configuration \
            --function-name "$LAMBDA_FUNCTION_NAME" \
            --memory-size "$LAMBDA_MEMORY_SIZE" \
            --timeout "$LAMBDA_TIMEOUT" \
            --region "$AWS_REGION" > /dev/null

        print_info "Lambda atualizada com sucesso!"
    else
        print_warn "Função Lambda não encontrada. Criação manual necessária via console AWS."
        print_info "Acesse: https://${AWS_REGION}.console.aws.amazon.com/lambda"
        print_info "Crie uma função Lambda com:"
        print_info "  - Nome: $LAMBDA_FUNCTION_NAME"
        print_info "  - Tipo: Container Image"
        print_info "  - Image URI: $ECR_FULL_URI"
        print_info "  - Memória: ${LAMBDA_MEMORY_SIZE}MB"
        print_info "  - Timeout: ${LAMBDA_TIMEOUT}s"
    fi
fi

# ========================================
# 3) UI - Deploy no S3
# ========================================
if [ "$DO_UI" = true ]; then
    print_info "Passo 3: Deploy da UI no S3..."

    if [ -z "$S3_BUCKET_NAME" ]; then
        print_error "S3_BUCKET_NAME não configurado!"
        exit 1
    fi

    # Verificar se bucket existe
    if ! aws s3 ls "s3://$S3_BUCKET_NAME" --region "$AWS_REGION" &> /dev/null; then
        print_warn "Bucket S3 não encontrado. Criando..."
        aws s3 mb "s3://$S3_BUCKET_NAME" --region "$AWS_REGION"
        print_info "Bucket S3 criado!"
    fi

    # Sincronizar arquivos
    print_info "Enviando arquivos da UI para S3..."
    aws s3 sync 07_web/ "s3://$S3_BUCKET_NAME" --delete

    print_info "UI enviada com sucesso para: s3://$S3_BUCKET_NAME"
    print_warn "ATENÇÃO: Configure CloudFront e CORS manualmente!"
fi

# ========================================
# Finalização
# ========================================
print_info ""
print_info "=== Deploy concluído com sucesso! ==="
print_info ""

if [ "$DO_LAMBDA" = true ]; then
    print_info "Próximos passos:"
    print_info "1. Configure o API Gateway para expor a Lambda"
    print_info "2. Obtenha a Invoke URL do API Gateway"
    print_info "3. Atualize o arquivo 07_web/app.js com a URL da API"
    print_info "4. Faça o deploy da UI no S3/CloudFront"
    print_info ""
    print_info "Documentação completa em: 04_reports/docs/DEPLOY_AWS.md"
fi
