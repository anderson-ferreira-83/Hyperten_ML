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

**Linux/Mac (curl):**
```bash
curl https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/health
```

**Windows (PowerShell):**
```powershell
Invoke-RestMethod -Uri "https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/health"
```

**Resposta esperada:**
```json
{
  "status": "ok",
  "pipeline_loaded": true,
  "features_count": 12,
  "artifacts_dir": "/var/task/05_artifacts/rf_v1",
  "selected_model": "rf_v1",
  "requested_model": null,
  "model_summary_path": null
}
```

### Predicao

**Linux/Mac (curl):**
```bash
curl -X POST https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/predict \
  -H "Content-Type: application/json" \
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

**Windows (PowerShell):**
```powershell
$json = '{
    "sexo": 0,
    "idade": 35,
    "fumante_atualmente": 1,
    "cigarros_por_dia": 35,
    "medicamento_pressao": 0,
    "diabetes": 1,
    "colesterol_total": 200,
    "pressao_sistolica": 130,
    "pressao_diastolica": 90,
    "imc": 28,
    "frequencia_cardiaca": 90,
    "glicose": 100
}'

Invoke-RestMethod -Uri "https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/predict" `
    -Method Post `
    -ContentType "application/json" `
    -Body $json
```

**Resposta esperada:**
```json
{
  "probability": 0.72,
  "threshold": 0.3,
  "prediction": 1,
  "threshold_profile": "balanced",
  "risk_category": "high",
  "missing_features": [],
  "model": "RandomForestClassifier",
  "model_version": "rf_v1",
  "model_selected": "rf_v1",
  "model_requested": null
}
```

> **Interpretacao da resposta:**
> - `probability`: Probabilidade de risco (0.0 a 1.0) - neste exemplo, 72%
> - `prediction`: 0 = baixo risco, 1 = alto risco
> - `risk_category`: "low" (< 30%), "medium" (30-70%), "high" (> 70%)
> - `threshold_profile`: Perfil de limiar usado (balanced, screening, confirmation)

### Interface Web
```
http://hypertension-tcc-ceunsp-2026.s3-website-sa-east-1.amazonaws.com/ui/index.html
```

---

## Arquitetura do Deploy

### Diagrama Geral

```
                            ┌─────────────────────────────────────────────────────────────┐
                            │                      USUARIO FINAL                           │
                            │         (Navegador Web / Aplicacao / Terminal)               │
                            └─────────────────────────┬───────────────────────────────────┘
                                                      │
                    ┌─────────────────────────────────┴─────────────────────────────────┐
                    │                                                                   │
                    ▼                                                                   ▼
    ┌───────────────────────────────────────┐               ┌───────────────────────────────────────┐
    │         AMAZON API GATEWAY            │               │            AMAZON S3                  │
    │            (HTTP API)                 │               │         (Website Hosting)             │
    │  ┌─────────────────────────────────┐  │               │  ┌─────────────────────────────────┐  │
    │  │ Endpoint:                       │  │               │  │ Bucket:                         │  │
    │  │ yrac79mzj9.execute-api.sa-east-1│  │               │  │ hypertension-tcc-ceunsp-2026    │  │
    │  │                                 │  │               │  │                                 │  │
    │  │ Rotas:                          │  │               │  │ Conteudo:                       │  │
    │  │  GET  /health                   │  │               │  │  - index.html (interface)       │  │
    │  │  POST /predict                  │  │               │  │  - styles.css (estilos)         │  │
    │  └─────────────────────────────────┘  │               │  │  - app.js (logica frontend)     │  │
    └──────────────────┬────────────────────┘               │  └─────────────────────────────────┘  │
                       │                                    └───────────────────────────────────────┘
                       │ Lambda Proxy Integration
                       │ (encaminha requisicao completa)
                       ▼
    ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
    │                                    AWS LAMBDA                                                    │
    │                              (Funcao Serverless)                                                 │
    │  ┌─────────────────────────────────────────────────────────────────────────────────────────┐   │
    │  │                           LAMBDA CODE (5.6 MB)                                          │   │
    │  │  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────────────┐  │   │
    │  │  │   lambda_handler.py  │  │    06_api/main.py    │  │   05_artifacts/rf_v1/        │  │   │
    │  │  │   (Entry Point)      │  │    (FastAPI App)     │  │   (Modelo ML)                │  │   │
    │  │  │                      │  │                      │  │                              │  │   │
    │  │  │  - Recebe evento     │  │  - /health endpoint  │  │  - pipeline.pkl (modelo)     │  │   │
    │  │  │  - Usa Mangum        │  │  - /predict endpoint │  │  - features.json (ordem)     │  │   │
    │  │  │  - Retorna resposta  │  │  - Validacao Pydantic│  │  - thresholds.json (limiares)│  │   │
    │  │  └──────────────────────┘  └──────────────────────┘  └──────────────────────────────┘  │   │
    │  └─────────────────────────────────────────────────────────────────────────────────────────┘   │
    │                                            +                                                    │
    │  ┌─────────────────────────────────────────────────────────────────────────────────────────┐   │
    │  │                           LAMBDA LAYER (69 MB)                                          │   │
    │  │                        (Dependencias Python compartilhadas)                             │   │
    │  │                                                                                         │   │
    │  │   numpy 2.2.6 | pandas 2.3.3 | scikit-learn 1.7.2 | scipy 1.16.3 | joblib | imblearn   │   │
    │  └─────────────────────────────────────────────────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────────────────────────────────────────────────┘
                       │
                       ▼
    ┌───────────────────────────────────────┐
    │         AMAZON CLOUDWATCH             │
    │           (Logs e Metricas)           │
    │  ┌─────────────────────────────────┐  │
    │  │ Log Group:                      │  │
    │  │ /aws/lambda/hypertension-api    │  │
    │  │                                 │  │
    │  │ - Logs de execucao              │  │
    │  │ - Erros e excecoes              │  │
    │  │ - Metricas de performance       │  │
    │  └─────────────────────────────────┘  │
    └───────────────────────────────────────┘
```

---

### Descricao Detalhada de Cada Componente

#### 1. Usuario Final (Cliente)

O ponto de entrada do sistema. Pode ser:
- **Navegador Web**: Acessa a interface HTML hospedada no S3
- **Aplicacao**: Qualquer sistema que faca requisicoes HTTP
- **Terminal**: Usando curl (Linux/Mac) ou PowerShell (Windows)

O usuario interage de duas formas:
- **UI Web** → Acessa S3 diretamente para carregar a interface
- **API** → Envia requisicoes para o API Gateway

---

#### 2. Amazon API Gateway (HTTP API)

**O que e:** Servico gerenciado que atua como "porta de entrada" para a API.

**O que faz:**
- Recebe requisicoes HTTP/HTTPS da internet
- Roteia para o servico correto (Lambda)
- Gerencia CORS (permite requisicoes de outros dominios)
- Controla throttling e rate limiting
- Fornece URL publica acessivel

**Configuracao atual:**

| Atributo | Valor |
|----------|-------|
| Tipo | HTTP API (mais barato e rapido que REST API) |
| ID | `yrac79mzj9` |
| Regiao | `sa-east-1` (Sao Paulo) |
| Integracao | Lambda Proxy (passa evento completo) |
| CORS | Habilitado para todos origins |

**Rotas configuradas:**
- `GET /health` → Verifica status da API
- `POST /predict` → Realiza predicao de risco

---

#### 3. Amazon S3 (Simple Storage Service)

**O que e:** Servico de armazenamento de objetos (arquivos) na nuvem.

**O que faz:**
- Hospeda arquivos estaticos da interface web
- Serve como "CDN simples" para o frontend
- Permite acesso publico controlado

**Configuracao atual:**

| Atributo | Valor |
|----------|-------|
| Bucket | `hypertension-tcc-ceunsp-2026` |
| Website Hosting | Habilitado |
| Acesso | Publico (somente leitura) |

**Arquivos hospedados:**
```
/ui/
  ├── index.html      # Interface principal
  ├── styles.css      # Estilos visuais
  ├── styles.min.css  # Estilos minificados
  ├── app.js          # Logica JavaScript
  └── app.min.js      # JavaScript minificado
```

---

#### 4. AWS Lambda (Funcao Serverless)

**O que e:** Servico de computacao serverless que executa codigo sob demanda.

**O que faz:**
- Executa o codigo Python quando recebe uma requisicao
- Carrega o modelo de ML na memoria
- Processa os dados de entrada
- Retorna a predicao de risco

**Por que Lambda?**
- **Sem servidor para gerenciar**: AWS cuida da infraestrutura
- **Escala automatica**: De 0 a milhares de requisicoes
- **Paga pelo uso**: Cobra apenas quando executa
- **Ideal para baixo trafego**: Projeto academico/TCC

**Configuracao atual:**

| Atributo | Valor |
|----------|-------|
| Nome | `hypertension-api` |
| Runtime | Python 3.11 |
| Memoria | 1024 MB |
| Timeout | 30 segundos |
| Handler | `lambda_handler.handler` |

**Estrutura interna da Lambda:**
```
/var/task/                          # Diretorio raiz da Lambda
  ├── lambda_handler.py             # Entry point (Mangum adapter)
  ├── 06_api/
  │     └── main.py                 # Aplicacao FastAPI
  ├── 05_artifacts/
  │     └── rf_v1/                  # Artefatos do modelo
  │           ├── pipeline.pkl      # Modelo treinado (Random Forest)
  │           ├── features.json     # Ordem das 12 features
  │           ├── thresholds.json   # Limiares clinicos
  │           └── metadata.json     # Metadados do modelo
  └── 08_src/                       # Codigo fonte auxiliar
```

---

#### 5. Lambda Layer (Camada de Dependencias)

**O que e:** Pacote ZIP com bibliotecas Python compartilhadas.

**O que faz:**
- Fornece dependencias pesadas (NumPy, Pandas, Scikit-learn)
- Reduz tamanho do pacote principal da Lambda
- Permite reutilizacao entre multiplas funcoes

**Por que usar Layer?**
- Limite de 50 MB para upload direto → Layer permite ate 250 MB
- Bibliotecas ML sao grandes (~200 MB descompactadas)
- Atualizar codigo sem re-upload das dependencias

**Bibliotecas incluidas:**

| Biblioteca | Versao | Tamanho | Funcao |
|------------|--------|---------|--------|
| numpy | 2.2.6 | ~50 MB | Arrays numericos |
| pandas | 2.3.3 | ~60 MB | Manipulacao de dados |
| scikit-learn | 1.7.2 | ~70 MB | Modelos ML |
| scipy | 1.16.3 | ~40 MB | Computacao cientifica |
| joblib | 1.5.3 | ~2 MB | Serializacao de modelos |
| imbalanced-learn | 0.14.1 | ~5 MB | SMOTE (balanceamento) |

---

#### 6. Amazon CloudWatch (Monitoramento)

**O que e:** Servico de monitoramento e observabilidade.

**O que faz:**
- Armazena logs de execucao da Lambda
- Registra erros e excecoes
- Coleta metricas de performance
- Permite criar alertas

**Metricas disponiveis:**
- Invocacoes (quantas vezes executou)
- Duracao (tempo de execucao)
- Erros (falhas de execucao)
- Cold starts (inicializacoes a frio)

---

### Fluxo de uma Requisicao de Predicao

```
1. Usuario envia POST /predict com dados do paciente
                    │
                    ▼
2. API Gateway recebe a requisicao HTTPS
   - Valida headers
   - Verifica CORS
   - Cria evento Lambda
                    │
                    ▼
3. Lambda e invocada
   - Se "fria": carrega codigo e modelo (~2-3s)
   - Se "quente": executa imediatamente (~50-200ms)
                    │
                    ▼
4. lambda_handler.py recebe o evento
   - Mangum converte para formato ASGI
   - FastAPI processa a requisicao
                    │
                    ▼
5. main.py executa /predict
   - Valida dados com Pydantic
   - Carrega pipeline do modelo
   - Executa predicao
   - Aplica threshold clinico
                    │
                    ▼
6. Resposta retorna pelo mesmo caminho
   Lambda → API Gateway → Usuario
   {
     "probability": 0.72,
     "prediction": 1,
     "risk_category": "high"
   }
```

---

### Vantagens desta Arquitetura

| Aspecto | Beneficio |
|---------|-----------|
| **Custo** | ~$0/mes no Free Tier (ideal para TCC) |
| **Escalabilidade** | Escala automaticamente de 0 a milhares |
| **Manutencao** | Zero servidores para gerenciar |
| **Disponibilidade** | AWS garante 99.95% de uptime |
| **Seguranca** | HTTPS automatico, IAM integrado |
| **Simplicidade** | Deploy em minutos com CLI |

### Limitacoes e Trade-offs

| Limitacao | Impacto | Mitigacao |
|-----------|---------|-----------|
| Cold Start | 2-3s na primeira requisicao | Provisioned Concurrency (custo extra) |
| Timeout 30s | Predicoes devem ser rapidas | Modelo ja e leve (~50ms) |
| Memoria 1GB | Limita modelos muito grandes | Suficiente para Random Forest |
| Stateless | Nao mantem estado entre chamadas | Adequado para API de predicao |

---

## Modelo de Machine Learning Deployado

- **Algoritmo**: Random Forest Classifier
- **Versao**: rf_v1
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

> **Nota**: Os testes abaixo foram realizados durante o deploy inicial. O modelo oficial atual e o **Random Forest (rf_v1)**, selecionado por apresentar melhor Recall (92%) e F2-Score (0.89).

### ✅ Health Check
- Status: OK
- Pipeline: Carregado
- Features: 12
- Modelo: rf_v1 (Random Forest)

### ✅ Predicao
- Input: 12 features de paciente
- Output: Probabilidade, predicao, categoria de risco
- Latencia: ~2-3s (cold start), ~50-200ms (warm)
- Modelo: RandomForestClassifier funcionando

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
