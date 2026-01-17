# Deploy AWS (fluxo Lambda para baixo trafego)

Este guia foca no deploy com **Lambda + API Gateway** (ideal para baixo trafego).

## 1) UI (S3 + CloudFront) - passo a passo

### 1.1) Ajuste da URL da API
No arquivo `07_web/app.js`, atualize a linha:
```js
const API_URL = '/predict?threshold_key=balanced';
```
para o endpoint publico do API Gateway, por exemplo:
```js
const API_URL = 'https://<API_ID>.execute-api.<REGION>.amazonaws.com/predict?threshold_key=balanced';
```
Se for publicar com os arquivos minificados, atualize tambem `07_web/app.min.js`.

### 1.2) Bucket S3
1. Crie um bucket S3 (pode ser privado).
2. Suba os arquivos de `07_web/`:
```bash
aws s3 sync 07_web/ s3://<NOME_BUCKET> --delete
```

### 1.3) CloudFront
1. Crie uma distribuicao CloudFront com origem no bucket.
2. Habilite OAC/OAI para acesso privado ao bucket.
3. Defina `index.html` como Default root object.
4. (Opcional) Apos atualizar arquivos, invalide o cache:
```bash
aws cloudfront create-invalidation --distribution-id <DIST_ID> --paths "/*"
```

## 2) API (Lambda com container)

### Dockerfile (recomendado)
Crie um `Dockerfile` na raiz:

```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY 06_api ./06_api
COPY 05_artifacts ./05_artifacts
CMD ["python", "-m", "uvicorn", "main:app", "--app-dir", "06_api", "--host", "0.0.0.0", "--port", "8000"]
```

### Passos resumidos
1. Criar repositorio no ECR.
2. Build da imagem e push para o ECR.
3. Criar Lambda a partir da imagem do ECR.
4. Expor via API Gateway (HTTP API).
5. Testar `/health` e `/predict`.

### Comandos (ECR + push)
Substitua `<REGION>`, `<ACCOUNT_ID>` e `<REPO_NAME>`:

```bash
aws ecr create-repository --repository-name <REPO_NAME> --region <REGION>

aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com

docker build -t <REPO_NAME>:latest .
docker tag <REPO_NAME>:latest <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/<REPO_NAME>:latest
docker push <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/<REPO_NAME>:latest
```

### Lambda (via console)
1. Criar Lambda com opcao "Container image".
2. Selecionar a imagem do ECR.
3. Configurar memoria (ex.: 1024 MB) e timeout (ex.: 30s).
4. Criar API Gateway HTTP API integrado a Lambda.

### Teste rapido
```bash
curl https://<API_ID>.execute-api.<REGION>.amazonaws.com/health
```

## 3) CORS

No API Gateway (HTTP API), habilite CORS com:
- Allow Origins: `https://<cloudfront_domain>`
- Allow Methods: `POST, GET, OPTIONS`
- Allow Headers: `Content-Type`

## 4) Observacoes

- O modelo e carregado no startup (cold start).
- Use `/health` como health check.
- Habilite logs no CloudWatch.

## Variaveis/artefatos usados

- API: `06_api/main.py`
- Artefatos do modelo: `05_artifacts/rf_v1/*`
- UI: `07_web/*`
