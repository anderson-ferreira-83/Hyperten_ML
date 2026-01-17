#!/bin/bash
# ============================================
# TEMPLATE - Arquivo de configuracao para deploy AWS
# ============================================
#
# INSTRUCOES:
# 1. Copie este arquivo: cp deploy_config.example.sh deploy_config.sh
# 2. Edite deploy_config.sh com suas credenciais
# 3. NUNCA commite deploy_config.sh (ja esta no .gitignore)
#
# ============================================

# Configuracoes AWS (SUBSTITUA COM SEUS VALORES)
export AWS_REGION="sa-east-1"                    # Regiao AWS (ex: sa-east-1, us-east-1)
export AWS_ACCOUNT_ID="SEU_ACCOUNT_ID_AQUI"      # AWS Account ID (12 digitos)

# Configuracoes do ECR (Elastic Container Registry)
export ECR_REPO_NAME="hypertension-api"          # Nome do repositorio ECR

# Configuracoes da Lambda
export LAMBDA_FUNCTION_NAME="hypertension-api"   # Nome da funcao Lambda
export LAMBDA_MEMORY_SIZE="1024"                 # Memoria em MB (512, 1024, 2048, etc)
export LAMBDA_TIMEOUT="30"                       # Timeout em segundos

# Configuracoes do S3 (para UI)
# IMPORTANTE: O nome do bucket deve ser unico globalmente!
export S3_BUCKET_NAME="SEU-BUCKET-UNICO-AQUI"    # Nome do bucket S3 para a UI

# Configuracoes do API Gateway
export API_GATEWAY_NAME="hypertension-api"       # Nome da API Gateway

# Configuracoes opcionais
export IMAGE_TAG="latest"                        # Tag da imagem Docker

# ============================================
# COMO OBTER SEU AWS_ACCOUNT_ID:
# aws sts get-caller-identity --query Account --output text
# ============================================
