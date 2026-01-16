#!/bin/bash
# Arquivo de configuração para deploy AWS
# Copie este arquivo para deploy_config.sh e preencha com suas informações

# Configurações AWS
export AWS_REGION="us-east-1"                    # Região AWS (ex: us-east-1, sa-east-1)
export AWS_ACCOUNT_ID="123456789012"             # Seu AWS Account ID

# Configurações do ECR (Elastic Container Registry)
export ECR_REPO_NAME="hypertension-api"          # Nome do repositório ECR

# Configurações da Lambda
export LAMBDA_FUNCTION_NAME="hypertension-api"   # Nome da função Lambda
export LAMBDA_MEMORY_SIZE="1024"                 # Memória em MB (512, 1024, 2048, etc)
export LAMBDA_TIMEOUT="30"                       # Timeout em segundos

# Configurações do S3 (para UI)
export S3_BUCKET_NAME="hypertension-ui"          # Nome do bucket S3 para a UI

# Configurações do API Gateway
export API_GATEWAY_NAME="hypertension-api"       # Nome da API Gateway

# Configurações opcionais
export IMAGE_TAG="latest"                        # Tag da imagem Docker
