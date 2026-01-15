# Passo a passo: criar API Gateway (HTTP API) e obter Invoke URL

Este guia cria uma **HTTP API** integrada a uma Lambda (container) e mostra onde copiar a URL publica.

## Pre-requisitos
- Lambda criada com imagem do ECR (container).
- Permissao para criar API Gateway.

## 1) Criar a API
1. Acesse **AWS Console > API Gateway**.
2. Clique em **Create API**.
3. Escolha **HTTP API** e clique em **Build**.
4. Em **Integrations**, selecione **Lambda** e escolha sua funcao.
5. Em **Routes**, crie:
   - `GET /health`
   - `POST /predict`
6. Clique em **Next**.

## 2) Criar o stage
1. Em **Stages**, crie um stage (ex.: `prod`).
2. Clique em **Next** e **Create**.

## 3) Habilitar CORS
1. Na sua HTTP API, abra **CORS**.
2. Configure:
   - **Allow Origins**: `https://<cloudfront_domain>` (ou `*` temporariamente).
   - **Allow Methods**: `GET, POST, OPTIONS`
   - **Allow Headers**: `Content-Type`
3. Salve.

## 4) Copiar a Invoke URL
1. Em **Stages**, selecione o stage (ex.: `prod`).
2. Copie o campo **Invoke URL**.
3. O formato sera algo como:
```
https://<API_ID>.execute-api.<REGION>.amazonaws.com
```

## 5) Teste rapido
```bash
curl https://<API_ID>.execute-api.<REGION>.amazonaws.com/health
```

## O que fazer com a URL
Use essa URL para atualizar o arquivo `07_web/app.js` (e `07_web/app.min.js`) conforme:
```js
const API_URL = 'https://<API_ID>.execute-api.<REGION>.amazonaws.com/predict?threshold_key=balanced';
```
