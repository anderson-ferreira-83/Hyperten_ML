#!/bin/bash
# Script de teste local antes do deploy
# Valida se a aplicação está funcionando localmente antes de subir para AWS

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

echo "========================================="
echo "   Teste Local - Hypertension API"
echo "========================================="
echo ""

# 1. Verificar dependências
print_info "Verificando dependências..."

if ! command -v python3 &> /dev/null; then
    print_error "Python3 não encontrado!"
    exit 1
fi
print_success "Python3 instalado"

if ! command -v docker &> /dev/null; then
    print_error "Docker não encontrado!"
    exit 1
fi
print_success "Docker instalado"

# 2. Verificar arquivos essenciais
print_info "Verificando arquivos essenciais..."

files=(
    "06_api/main.py"
    "07_web/index.html"
    "07_web/app.js"
    "requirements.txt"
    "Dockerfile"
)

for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Arquivo não encontrado: $file"
        exit 1
    fi
done
print_success "Todos os arquivos essenciais presentes"

# 3. Verificar artefatos do modelo
print_info "Verificando artefatos do modelo..."

if [ ! -d "05_artifacts" ]; then
    print_error "Pasta 05_artifacts não encontrada!"
    exit 1
fi

# Procurar por pelo menos um artefato
artifact_found=false
for dir in 05_artifacts/*/; do
    if [ -f "${dir}pipeline.pkl" ] && [ -f "${dir}features.json" ]; then
        artifact_found=true
        print_success "Artefatos encontrados em: ${dir}"
        break
    fi
done

if [ "$artifact_found" = false ]; then
    print_error "Nenhum artefato válido encontrado em 05_artifacts/"
    print_info "Certifique-se de ter executado os notebooks de treinamento"
    exit 1
fi

# 4. Testar build do Docker (opcional)
read -p "Deseja testar o build da imagem Docker? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    print_info "Construindo imagem Docker (pode demorar)..."
    if docker build -t hypertension-api-test:local . > /dev/null 2>&1; then
        print_success "Build Docker bem-sucedido!"

        # Limpar imagem de teste
        docker rmi hypertension-api-test:local > /dev/null 2>&1
    else
        print_error "Falha no build Docker!"
        print_info "Execute manualmente: docker build -t test ."
        exit 1
    fi
fi

# 5. Testar API localmente
read -p "Deseja iniciar a API localmente para teste? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    print_info "Instalando dependências Python..."
    pip install -q fastapi uvicorn pandas numpy scikit-learn joblib pydantic

    print_info "Iniciando servidor local na porta 8000..."
    print_info "Acesse: http://127.0.0.1:8000/app"
    print_info "Health check: http://127.0.0.1:8000/health"
    print_info ""
    print_info "Pressione Ctrl+C para parar o servidor"

    python -m uvicorn main:app --app-dir 06_api --host 0.0.0.0 --port 8000
fi

echo ""
print_success "Todos os testes passaram!"
print_info "Você está pronto para fazer o deploy na AWS!"
print_info "Execute: ./deploy_aws.sh"
