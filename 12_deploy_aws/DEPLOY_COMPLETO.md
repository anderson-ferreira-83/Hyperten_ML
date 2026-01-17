# Deploy Completo - API de Predição de Hipertensão na AWS

## Status: DEPLOY CONCLUÍDO COM SUCESSO! ✅

Data: 2026-01-16/17
Região: sa-east-1 (São Paulo)

---

## Recursos Criados na AWS

### 1. Lambda Function
- **Nome**: `hypertension-api`
- **ARN**: `arn:aws:lambda:sa-east-1:710586046477:function:hypertension-api`
- **Runtime**: Python 3.11
- **Memória**: 1024 MB
- **Timeout**: 30 segundos
- **Tamanho do código**: 5.6 MB
- **Handler**: `lambda_handler.handler`

### 2. Lambda Layer (Dependências ML)
- **Nome**: `hypertension-ml-deps`
- **Versão**: 4
- **ARN**: `arn:aws:lambda:sa-east-1:710586046477:layer:hypertension-ml-deps:4`
- **Tamanho**: 69 MB (compactado), 242 MB (descompactado)
- **Bibliotecas incluídas**:
  - numpy 2.2.6
  - pandas 2.3.3
  - scikit-learn 1.7.2
  - scipy 1.16.3
  - joblib 1.5.3
  - imbalanced-learn 0.14.1

### 3. API Gateway HTTP API
- **Nome**: HTTP API para Lambda
- **ID**: `yrac79mzj9`
- **Endpoint**: `https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com`
- **Stage**: `$default` (sem prefixo no caminho)
- **Tipo de integração**: AWS_PROXY (Lambda Proxy Integration)
- **CORS**: Configurado para todos os origins

### 4. S3 Bucket
- **Nome**: `hypertension-tcc-ceunsp-2026`
- **Região**: sa-east-1
- **Website Endpoint**: `http://hypertension-tcc-ceunsp-2026.s3-website-sa-east-1.amazonaws.com/ui/index.html`
- **Conteúdo**: Arquivos da UI (HTML, CSS, JS)
- **Acesso**: Público (somente leitura para /ui/*)

### 5. IAM Role
- **Nome**: `hypertension-lambda-execution-role`
- **ARN**: `arn:aws:iam::710586046477:role:hypertension-lambda-execution-role`
- **Permissões**: CloudWatch Logs (básico)

---

## Endpoints da API

### Health Check
```bash
curl https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/health
```

**Resposta:**
```json
{
  "status": "ok",
  "pipeline_loaded": true,
  "features_count": 12,
  "artifacts_dir": "/var/task/05_artifacts/gb_v1",
  "selected_model": "gb_v1",
  "requested_model": null,
  "model_summary_path": null
}
```

### Predição
```bash
curl -X POST https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/predict \\
  -H "Content-Type: application/json" \\
  -d '{
    "sexo": 1,
    "idade": 50,
    "fumante_atualmente": 0,
    "cigarros_por_dia": 0,
    "medicamento_pressao": 0,
    "diabetes": 0,
    "colesterol_total": 200,
    "pressao_sistolica": 120,
    "pressao_diastolica": 80,
    "imc": 25,
    "frequencia_cardiaca": 70,
    "glicose": 90
  }'
```

**Resposta:**
```json
{
  "probability": 0.048,
  "threshold": 0.3,
  "prediction": 0,
  "threshold_profile": "balanced",
  "risk_category": "low",
  "missing_features": [],
  "model": "GradientBoostingClassifier",
  "model_version": "gb_v1",
  "model_selected": "gb_v1",
  "model_requested": null
}
```

### Interface Web
```
http://hypertension-tcc-ceunsp-2026.s3-website-sa-east-1.amazonaws.com/ui/index.html
```

---

## Arquitetura do Deploy

```
┌─────────────────┐
│   Usuário/UI    │
└────────┬────────┘
         │
         ├─────────────────────────────────────┐
         │                                     │
         ▼                                     ▼
┌─────────────────┐                   ┌──────────────┐
│  API Gateway    │                   │  S3 Bucket   │
│  HTTP API       │                   │  (Static UI) │
│  yrac79mzj9     │                   └──────────────┘
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│           AWS Lambda Function                    │
│  ┌────────────────────────────────────────────┐ │
│  │  Lambda Code (5.6 MB)                      │ │
│  │  - FastAPI + Mangum                        │ │
│  │  - Código da aplicação (06_api, 08_src)    │ │
│  │  - Artefatos do modelo (05_artifacts)      │ │
│  └────────────────────────────────────────────┘ │
│                      +                           │
│  ┌────────────────────────────────────────────┐ │
│  │  Lambda Layer (69 MB)                      │ │
│  │  - NumPy, Pandas, Scikit-learn             │ │
│  │  - SciPy, Joblib, Imbalanced-learn         │ │
│  └────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

---

## Modelo de Machine Learning Deployado

- **Algoritmo**: Gradient Boosting Classifier
- **Versão**: gb_v1
- **Features**: 12 características clínicas
- **Threshold balanceado**: 0.3
- **Categorias de risco**: low, medium, high
- **Formato**: Pipeline scikit-learn com SMOTE

---

## Custos Estimados (Free Tier)

### Lambda
- **Requests**: 1 milhão grátis/mês
- **Compute**: 400.000 GB-s grátis/mês
- **Custo estimado**: $0/mês (dentro do free tier)

### API Gateway
- **Requests**: 1 milhão grátis/mês (primeiros 12 meses)
- **Custo estimado**: $0/mês (free tier)

### S3
- **Storage**: 5 GB grátis/mês (primeiros 12 meses)
- **Requests**: 20.000 GET grátis/mês
- **Transfer**: 15 GB out grátis/mês
- **Uso atual**: ~20 KB
- **Custo estimado**: $0/mês (free tier)

### Total Mensal Estimado
**~$0.00 - $0.50/mês** (considerando uso baixo/médio)

---

## Testes Realizados

### ✅ Health Check
- Status: OK
- Pipeline: Carregado
- Features: 12
- Modelo: gb_v1

### ✅ Predição
- Input: 12 features de paciente
- Output: Probabilidade, predição, categoria de risco
- Latência: ~2-3s (cold start), ~50-200ms (warm)
- Modelo: GradientBoostingClassifier funcionando

### ✅ CORS
- Configurado para aceitar requests de qualquer origin
- Headers: Content-Type, Authorization

### ✅ UI Deployment
- Arquivos hospedados no S3
- Acesso público configurado
- JavaScript atualizado com URL da API

---

## Próximos Passos (Opcionais)

### Melhorias de Produção
1. **Custom Domain**: Configurar domínio personalizado via Route 53
2. **CloudFront**: CDN para melhorar latência global
3. **WAF**: Web Application Firewall para segurança
4. **CloudWatch Alarms**: Monitoramento e alertas
5. **X-Ray**: Tracing distribuído para debugging

### Otimizações
1. **Lambda Provisioned Concurrency**: Eliminar cold starts
2. **API Gateway Caching**: Cache de respostas
3. **Compression**: Compressão de responses

### Segurança
1. **API Key**: Autenticação por chave
2. **Rate Limiting**: Throttling de requests
3. **VPC**: Lambda dentro de VPC privada
4. **Secrets Manager**: Gerenciar credenciais

---

## Comandos Úteis

### Atualizar código da Lambda
```bash
cd /mnt/c/Users/Anderson/Downloads/tcc_hipertensao_arquivos/trabalho_tcc_mod_classifc_hipertensao-master/trabalho_tcc_mod_classifc_hipertensao-master
zip -r deployment.zip 06_api 05_artifacts 08_src lambda_handler.py
aws lambda update-function-code --function-name hypertension-api --zip-file fileb://deployment.zip --region sa-east-1
```

### Ver logs da Lambda
```bash
aws logs tail /aws/lambda/hypertension-api --follow --region sa-east-1
```

### Atualizar arquivos da UI
```bash
aws s3 sync 07_web/ s3://hypertension-tcc-ceunsp-2026/ui/ --region sa-east-1
```

### Deletar todos os recursos (cleanup)
```bash
# Lambda
aws lambda delete-function --function-name hypertension-api --region sa-east-1

# Lambda Layer
aws lambda delete-layer-version --layer-name hypertension-ml-deps --version-number 4 --region sa-east-1

# API Gateway
aws apigatewayv2 delete-api --api-id yrac79mzj9 --region sa-east-1

# S3 (esvaziar e deletar)
aws s3 rm s3://hypertension-tcc-ceunsp-2026 --recursive --region sa-east-1
aws s3api delete-bucket --bucket hypertension-tcc-ceunsp-2026 --region sa-east-1

# IAM Role
aws iam delete-role-policy --role-name hypertension-lambda-execution-role --policy-name lambda-basic-execution
aws iam delete-role --role-name hypertension-lambda-execution-role
```

---

## Troubleshooting

### Lambda retorna Internal Server Error
- Verifique os logs: `aws logs tail /aws/lambda/hypertension-api --follow`
- Verifique se o Layer está anexado
- Verifique se os artefatos estão no ZIP

### CORS Error no navegador
- Verifique CORS no API Gateway
- Verifique headers na resposta

### UI não carrega
- Verifique bucket policy
- Verifique se os arquivos foram uploaded
- Verifique a URL da API no app.js

---

## Links Importantes

- **API Gateway Console**: https://sa-east-1.console.aws.amazon.com/apigateway/main/apis/yrac79mzj9
- **Lambda Console**: https://sa-east-1.console.aws.amazon.com/lambda/home?region=sa-east-1#/functions/hypertension-api
- **S3 Console**: https://s3.console.aws.amazon.com/s3/buckets/hypertension-tcc-ceunsp-2026
- **CloudWatch Logs**: https://sa-east-1.console.aws.amazon.com/cloudwatch/home?region=sa-east-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252Fhypertension-api

---

**Deploy concluído com sucesso em 2026-01-16/17** 🎉
