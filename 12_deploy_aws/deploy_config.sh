#!/bin/bash
# Arquivo de configuração para deploy AWS
# Configuração automática baseada nas credenciais existentes

# Configurações AWS (obtidas automaticamente)
export AWS_REGION="sa-east-1"                    # Região AWS (São Paulo)
export AWS_ACCOUNT_ID="710586046477"             # AWS Account ID

# Configurações do ECR (Elastic Container Registry)
export ECR_REPO_NAME="hypertension-api"          # Nome do repositório ECR

# Configurações da Lambda
export LAMBDA_FUNCTION_NAME="hypertension-api"   # Nome da função Lambda
export LAMBDA_MEMORY_SIZE="1024"                 # Memória em MB (512, 1024, 2048, etc)
export LAMBDA_TIMEOUT="30"                       # Timeout em segundos

# Configurações do S3 (para UI)
# IMPORTANTE: Altere este nome para algo único!
export S3_BUCKET_NAME="hypertension-tcc-ceunsp-2026"  # Nome do bucket S3 para a UI

# Configurações do API Gateway
export API_GATEWAY_NAME="hypertension-api"       # Nome da API Gateway

# Configurações opcionais
export IMAGE_TAG="latest"                        # Tag da imagem Docker
