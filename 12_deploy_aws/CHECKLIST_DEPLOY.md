# ✅ Checklist de Deploy AWS

Use este checklist para não esquecer nenhum passo durante o deploy.

## Pré-Deploy

- [ ] Conta AWS ativa
- [ ] AWS CLI instalado (`aws --version`)
- [ ] AWS CLI configurado (`aws configure`)
- [ ] Docker instalado e rodando (`docker --version`)
- [ ] Permissões AWS: ECR, Lambda, API Gateway, S3, CloudFront

## Configuração Inicial

- [ ] Copiei `deploy_config.example.sh` para `deploy_config.sh`
- [ ] Editei `deploy_config.sh` com:
  - [ ] AWS_REGION
  - [ ] AWS_ACCOUNT_ID (12 dígitos)
  - [ ] ECR_REPO_NAME
  - [ ] S3_BUCKET_NAME (nome único!)
- [ ] Script tem permissão de execução (`chmod +x deploy_aws.sh`)

## Deploy da API

- [ ] Executei `./deploy_aws.sh` e escolhi opção 1
- [ ] Build da imagem Docker concluído
- [ ] Push para ECR concluído
- [ ] Função Lambda criada/atualizada
- [ ] API Gateway criado com rotas:
  - [ ] GET /health
  - [ ] POST /predict
  - [ ] GET /app
- [ ] CORS configurado no API Gateway:
  - [ ] Access-Control-Allow-Origin: * (temporário)
  - [ ] Access-Control-Allow-Methods: GET, POST, OPTIONS
  - [ ] Access-Control-Allow-Headers: Content-Type
- [ ] Copiei a Invoke URL do API Gateway
- [ ] Testei o endpoint `/health`: `curl https://INVOKE_URL/health`

## Deploy da UI

- [ ] Atualizei `07_web/app.js` com a Invoke URL da API
- [ ] Se houver `07_web/app.min.js`, atualizei também
- [ ] Executei `./deploy_aws.sh` e escolhi opção 4
- [ ] Bucket S3 criado
- [ ] Arquivos da UI enviados para S3
- [ ] CloudFront criado:
  - [ ] Origin: Bucket S3
  - [ ] OAC configurado
  - [ ] Default root object: index.html
  - [ ] Política de bucket aplicada
- [ ] Copiei o Domain name do CloudFront
- [ ] Atualizei CORS no API Gateway com domínio CloudFront
- [ ] Acessei a URL do CloudFront e testei a aplicação

## Testes Finais

- [ ] Endpoint `/health` retorna `"status": "ok"`
- [ ] Formulário da UI carrega corretamente
- [ ] Botão "Preencher exemplo" funciona
- [ ] Botão "Calcular risco" retorna predição
- [ ] Resultado mostra: probabilidade, threshold, modelo
- [ ] Não há erros de CORS no console do browser (F12)

## Documentação

- [ ] Documentei a Invoke URL para referência futura
- [ ] Documentei o Domain name do CloudFront
- [ ] Salvei o ID da distribuição CloudFront
- [ ] Anotei os custos estimados (se aplicável)

## Extras (Opcional)

- [ ] Configurei domínio personalizado no CloudFront
- [ ] Configurei certificado SSL/TLS (ACM)
- [ ] Configurei alarmes no CloudWatch
- [ ] Configurei logs da Lambda
- [ ] Criei dashboard no CloudWatch

## Comandos Úteis

```bash
# Testar API localmente antes do deploy
uvicorn main:app --app-dir 06_api --reload

# Build da imagem Docker localmente
docker build -t hypertension-api:latest .

# Testar container localmente
docker run -p 8000:8000 hypertension-api:latest

# Ver logs da Lambda
aws logs tail /aws/lambda/hypertension-api --follow

# Invalidar cache do CloudFront
aws cloudfront create-invalidation --distribution-id SEU_ID --paths "/*"

# Listar distribuições CloudFront
aws cloudfront list-distributions --query "DistributionList.Items[*].[Id,DomainName]" --output table

# Ver status da Lambda
aws lambda get-function --function-name hypertension-api
```

## Troubleshooting

### Se algo deu errado:

1. **API não responde**:
   - Verifique logs no CloudWatch: `aws logs tail /aws/lambda/hypertension-api`
   - Teste Lambda diretamente no console AWS
   - Verifique memória e timeout da Lambda

2. **CORS error**:
   - Confirme configuração CORS no API Gateway
   - Confirme URL correta no `app.js`
   - Limpe cache do CloudFront

3. **UI não carrega**:
   - Verifique política do bucket S3
   - Verifique OAC no CloudFront
   - Verifique Default root object = `index.html`

4. **Modelo não carrega**:
   - Verifique pasta `05_artifacts/` no container
   - Aumente memória da Lambda para 1536 MB
   - Verifique logs de erro no CloudWatch

---

**Última atualização**: 2026-01-16
**Versão**: 1.0
