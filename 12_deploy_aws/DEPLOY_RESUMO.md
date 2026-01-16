# 🚀 Deploy na AWS - Resumo Executivo

## O que você vai fazer

Colocar sua aplicação de predição de hipertensão online na AWS, acessível via navegador de qualquer lugar.

## Em 5 passos simples

### 1️⃣ Pré-requisitos (5 minutos)
```bash
# Instalar AWS CLI
# Windows: https://awscli.amazonaws.com/AWSCLIV2.msi
# Linux/Mac: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html

# Configurar AWS CLI
aws configure
# Você vai precisar: Access Key, Secret Key, Region (ex: us-east-1)

# Verificar Docker rodando
docker --version
```

### 2️⃣ Configurar credenciais (2 minutos)
```bash
# Copiar template
cp deploy_config.example.sh deploy_config.sh

# Editar (use seu editor favorito)
nano deploy_config.sh
```

**Preencha apenas 3 campos essenciais:**
- `AWS_REGION="us-east-1"` → Sua região
- `AWS_ACCOUNT_ID="123456789012"` → Seu ID AWS (12 dígitos)
- `S3_BUCKET_NAME="hypertension-ui-SEUNOME"` → Nome único

### 3️⃣ Deploy da API (10 minutos)
```bash
# Executar script
chmod +x deploy_aws.sh
./deploy_aws.sh

# Escolha opção: 1 (Deploy completo)
# Aguarde... ☕
```

**Depois do script terminar:**
1. Acesse: https://console.aws.amazon.com/lambda
2. Se a função `hypertension-api` não existir, crie manualmente (5 min):
   - Container image → Use a URI que apareceu no terminal
   - Memory: 1024 MB, Timeout: 30s

3. Crie API Gateway: https://console.aws.amazon.com/apigateway
   - HTTP API → Integração: Lambda `hypertension-api`
   - Rotas: `GET /health`, `POST /predict`, `GET /app`
   - CORS: Allow Origin `*`, Methods `GET,POST,OPTIONS`, Headers `Content-Type`

4. **COPIE A INVOKE URL** (ex: `https://abc123.execute-api.us-east-1.amazonaws.com`)

### 4️⃣ Atualizar UI com URL da API (2 minutos)
```bash
# Editar arquivo JavaScript
nano 07_web/app.js

# Linha 1: mudar de
const API_URL = '/predict?threshold_key=balanced';

# Para (use SUA invoke URL):
const API_URL = 'https://abc123.execute-api.us-east-1.amazonaws.com/predict?threshold_key=balanced';
```

### 5️⃣ Deploy da UI (10 minutos)
```bash
# Upload para S3
./deploy_aws.sh
# Escolha opção: 4 (Deploy da UI)

# Criar CloudFront
# Acesse: https://console.aws.amazon.com/cloudfront
# Create distribution → Origin: seu bucket S3
# Default root object: index.html
# Aguarde distribuição ficar "Deployed" (5-10 min)

# COPIE O DOMAIN NAME (ex: d111111abcdef8.cloudfront.net)
```

**Atualize CORS com domínio CloudFront:**
- Volte ao API Gateway → CORS
- Mude Allow Origin de `*` para `https://d111111abcdef8.cloudfront.net`

## ✅ Pronto! Acesse sua aplicação

`https://d111111abcdef8.cloudfront.net`

## 🧪 Teste rápido

```bash
# Testar API
curl https://SUA_INVOKE_URL/health

# Deve retornar:
# {"status": "ok", "pipeline_loaded": true, ...}
```

## 💰 Custos

Com AWS Free Tier (primeiros 12 meses):
- **Lambda**: 1M requisições/mês GRÁTIS
- **API Gateway**: 1M requisições/mês GRÁTIS
- **S3**: 5GB GRÁTIS
- **CloudFront**: 50GB transferência GRÁTIS

**Para TCC com baixo tráfego**: CUSTO ZERO ou < $5/mês

## 📚 Documentação completa

Se você quiser mais detalhes ou encontrar problemas:

1. **Guia passo a passo completo**: [GUIA_DEPLOY_RAPIDO.md](GUIA_DEPLOY_RAPIDO.md)
2. **Checklist de validação**: [CHECKLIST_DEPLOY.md](CHECKLIST_DEPLOY.md)
3. **Documentação técnica**: [04_reports/docs/DEPLOY_AWS.md](04_reports/docs/DEPLOY_AWS.md)

## 🆘 Problemas comuns

| Problema | Solução |
|----------|---------|
| "No artifacts found" | Verifique se `05_artifacts/rf_v1/` existe |
| "CORS error" | Configure CORS no API Gateway |
| "Task timed out" | Aumente timeout da Lambda para 30s |
| "Docker not running" | Inicie Docker Desktop |
| UI não carrega | Verifique Default root object = `index.html` |

## 🔄 Para atualizar depois

```bash
# Atualizar API
./deploy_aws.sh → Opção 1

# Atualizar UI
./deploy_aws.sh → Opção 4

# Limpar cache CloudFront
aws cloudfront create-invalidation --distribution-id SEU_ID --paths "/*"
```

---

**Tempo total estimado**: 30-40 minutos
**Dificuldade**: Intermediária
**Pré-requisitos**: Conta AWS, Docker, AWS CLI

**Feito com ❤️ para facilitar seu TCC!**
