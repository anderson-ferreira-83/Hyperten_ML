# Guia Rápido de Deploy na AWS

Este guia vai te ajudar a fazer o deploy da aplicação de predição de hipertensão na AWS de forma simples e rápida.

## Pré-requisitos

Antes de começar, você precisa ter:

1. **Conta AWS** ativa
2. **AWS CLI** instalado e configurado
   ```bash
   aws configure
   ```
3. **Docker** instalado e rodando
4. **Git Bash** (no Windows) ou terminal Linux/Mac

## Arquitetura do Deploy

```
┌─────────────────┐
│   CloudFront    │  ← Interface do usuário (HTML/CSS/JS)
│   + S3 Bucket   │
└────────┬────────┘
         │
         │ HTTPS
         ▼
┌─────────────────┐
│  API Gateway    │  ← Endpoint público da API
└────────┬────────┘
         │
         │ Invoke
         ▼
┌─────────────────┐
│  Lambda (ECR)   │  ← FastAPI rodando em container
│   + Modelo ML   │
└─────────────────┘
```

## Passo 1: Obter suas credenciais AWS

Você vai precisar de:

- **AWS Account ID**: Acesse o [Console AWS](https://console.aws.amazon.com) e clique no seu nome no canto superior direito
- **AWS Region**: Escolha uma região próxima (ex: `us-east-1` ou `sa-east-1` para Brasil)

## Passo 2: Configurar o arquivo de deploy

1. Copie o arquivo de configuração de exemplo:
   ```bash
   cp deploy_config.example.sh deploy_config.sh
   ```

2. Edite o arquivo `deploy_config.sh`:
   ```bash
   nano deploy_config.sh
   # ou use seu editor preferido (VSCode, vim, etc)
   ```

3. Preencha com suas informações:
   ```bash
   export AWS_REGION="us-east-1"              # Sua região AWS
   export AWS_ACCOUNT_ID="123456789012"       # Seu Account ID (12 dígitos)
   export ECR_REPO_NAME="hypertension-api"    # Nome do repositório (pode deixar assim)
   export LAMBDA_FUNCTION_NAME="hypertension-api"
   export LAMBDA_MEMORY_SIZE="1024"           # Memória em MB
   export LAMBDA_TIMEOUT="30"                 # Timeout em segundos
   export S3_BUCKET_NAME="hypertension-ui"    # Nome único para o bucket S3
   ```

   **IMPORTANTE**: O `S3_BUCKET_NAME` precisa ser único globalmente! Se `hypertension-ui` já existir, use algo como `hypertension-ui-seunome-2026`.

## Passo 3: Executar o deploy da API

1. Dê permissão de execução ao script:
   ```bash
   chmod +x deploy_aws.sh
   ```

2. Execute o script:
   ```bash
   ./deploy_aws.sh
   ```

3. Escolha a opção **1** (Deploy completo)

4. Aguarde o processo (pode levar 5-10 minutos):
   - Criará o repositório ECR
   - Fará build da imagem Docker
   - Enviará a imagem para o ECR
   - Atualizará a função Lambda

## Passo 4: Criar a função Lambda (se necessário)

Se a Lambda ainda não existir, você precisará criá-la manualmente:

1. Acesse o [Console Lambda](https://console.aws.amazon.com/lambda)
2. Clique em **"Create function"**
3. Escolha **"Container image"**
4. Preencha:
   - **Function name**: `hypertension-api`
   - **Container image URI**: Copie a URI que apareceu no script (formato: `123456789012.dkr.ecr.us-east-1.amazonaws.com/hypertension-api:latest`)
5. Clique em **"Create function"**
6. Vá em **"Configuration" → "General configuration"** e configure:
   - **Memory**: 1024 MB
   - **Timeout**: 30 segundos
   - **Ephemeral storage**: 512 MB (padrão)

## Passo 5: Configurar o API Gateway

1. Acesse o [Console API Gateway](https://console.aws.amazon.com/apigateway)
2. Clique em **"Create API"**
3. Escolha **"HTTP API"** e clique em **"Build"**
4. Em **"Integrations"**:
   - Selecione **"Lambda"**
   - Escolha a função `hypertension-api`
   - Em **"API name"**: `hypertension-api`
5. Clique em **"Next"**
6. Configure as rotas:
   - `GET /health`
   - `POST /predict`
   - `GET /app`
7. Em **"Stages"**:
   - Stage name: `prod`
8. Clique em **"Create"**

## Passo 6: Habilitar CORS

1. No API Gateway criado, vá em **"CORS"**
2. Configure:
   - **Access-Control-Allow-Origin**: `*` (temporário) ou seu domínio CloudFront depois
   - **Access-Control-Allow-Methods**: `GET, POST, OPTIONS`
   - **Access-Control-Allow-Headers**: `Content-Type`
3. Salve

## Passo 7: Obter a URL da API

1. No API Gateway, vá em **"Stages" → "prod"**
2. Copie o **"Invoke URL"** (formato: `https://abc123.execute-api.us-east-1.amazonaws.com`)
3. **IMPORTANTE**: Salve essa URL, você vai precisar dela!

## Passo 8: Testar a API

Teste o endpoint de health:
```bash
curl https://SEU_INVOKE_URL/health
```

Deve retornar algo como:
```json
{
  "status": "ok",
  "pipeline_loaded": true,
  "features_count": 12,
  "selected_model": "Random Forest"
}
```

## Passo 9: Atualizar a UI com a URL da API

1. Edite o arquivo `07_web/app.js`:
   ```bash
   nano 07_web/app.js
   ```

2. Altere a linha 1:
   ```javascript
   // De:
   const API_URL = '/predict?threshold_key=balanced';

   // Para:
   const API_URL = 'https://SEU_INVOKE_URL/predict?threshold_key=balanced';
   ```

3. Se houver `07_web/app.min.js`, atualize também.

## Passo 10: Deploy da UI no S3

1. Execute o script novamente:
   ```bash
   ./deploy_aws.sh
   ```

2. Escolha a opção **4** (Deploy da UI no S3)

3. Aguarde o upload dos arquivos

## Passo 11: Configurar CloudFront

1. Acesse o [Console CloudFront](https://console.aws.amazon.com/cloudfront)
2. Clique em **"Create distribution"**
3. Configure:
   - **Origin domain**: Escolha seu bucket S3 (`hypertension-ui`)
   - **Origin access**: **"Origin access control settings (recommended)"**
   - **Create control setting**: Crie um novo OAC
   - **Default root object**: `index.html`
4. Clique em **"Create distribution"**
5. **IMPORTANTE**: Copie a política de bucket S3 que aparecerá e aplique no bucket (CloudFront vai mostrar instruções)

## Passo 12: Atualizar CORS com domínio CloudFront

1. Copie o **Domain name** da distribuição CloudFront (ex: `d111111abcdef8.cloudfront.net`)
2. Volte ao API Gateway → **CORS**
3. Altere **Access-Control-Allow-Origin** de `*` para `https://d111111abcdef8.cloudfront.net`

## Passo 13: Acessar sua aplicação!

Acesse: `https://SEU_DOMINIO_CLOUDFRONT.cloudfront.net`

Você verá a interface de predição de hipertensão funcionando! 🎉

## Solução de Problemas

### Erro: "No artifacts found"
- Verifique se a pasta `05_artifacts/` está sendo copiada corretamente no Dockerfile
- Confirme que há artefatos em `05_artifacts/rf_v1/` ou `05_artifacts/gb_v1/`

### Erro: "CORS error"
- Verifique se configurou o CORS no API Gateway
- Confirme que a URL no `app.js` está correta
- Limpe o cache do CloudFront: `aws cloudfront create-invalidation --distribution-id SEU_ID --paths "/*"`

### Erro: "Task timed out after 3.00 seconds"
- Aumente o timeout da Lambda para 30 segundos
- Aumente a memória da Lambda para 1024 MB ou mais

### Erro: "Docker daemon not running"
- Inicie o Docker Desktop
- No Linux: `sudo systemctl start docker`

### Erro: "Unable to locate credentials"
- Execute `aws configure` e insira suas credenciais
- Verifique se tem permissões de ECR, Lambda, API Gateway, S3 e CloudFront

## Custos Estimados

Com o AWS Free Tier:
- **Lambda**: 1M de requisições/mês grátis
- **API Gateway**: 1M de requisições/mês grátis (primeiros 12 meses)
- **S3**: 5GB grátis
- **CloudFront**: 50GB de transferência grátis (primeiros 12 meses)

Para um projeto de TCC com baixo tráfego, **deve ficar dentro do free tier** (custo zero ou poucos dólares/mês).

## Atualizações Futuras

Para atualizar apenas o código sem refazer tudo:

1. **Atualizar API**:
   ```bash
   ./deploy_aws.sh
   # Escolha opção 2 (Build e push) ou 1 (Deploy completo)
   ```

2. **Atualizar UI**:
   ```bash
   ./deploy_aws.sh
   # Escolha opção 4 (Deploy da UI)
   ```

3. **Limpar cache do CloudFront**:
   ```bash
   aws cloudfront create-invalidation --distribution-id SEU_ID --paths "/*"
   ```

## Documentação Adicional

- [Documentação completa de deploy](04_reports/docs/DEPLOY_AWS.md)
- [Passo a passo API Gateway](04_reports/docs/PASSO_API_GATEWAY.md)
- [Tutorial de inferência local](04_reports/docs/TUTORIAL_INFERENCIA_LOCAL.md)

## Suporte

Se tiver problemas:
1. Consulte a documentação em `04_reports/docs/`
2. Verifique os logs no CloudWatch
3. Teste a API localmente primeiro: `uvicorn main:app --app-dir 06_api --reload`

---

**Desenvolvido por**: Marcelo V Duarte Colpani, Nicolas Souza, Rubens Jose Collin, Tiago Dias Borges
**Orientador**: Prof. Dr. Anderson Henrique Rodrigues Ferreira
**Instituição**: CEUNSP - Centro Universitário Nossa Senhora do Patrocínio
