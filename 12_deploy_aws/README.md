# Deploy AWS - API de Predição de Hipertensão

Esta pasta contém a documentação e scripts para o deploy da aplicação na AWS.

## Arquivos

### Documentação
- **DEPLOY_COMPLETO.md** - Documentação completa do deploy realizado
- **TUTORIAL_TESTE.md** - Tutorial passo a passo para testar a aplicação

### Scripts de Teste (Prontos para Usar!) ⭐
- **run_all_tests.sh** - Executa TODOS os testes automaticamente
- **test_health.sh** - Testa se a API está funcionando
- **test_prediction_low_risk.sh** - Testa predição de baixo risco
- **test_prediction_medium_risk.sh** - Testa predição de risco médio
- **test_prediction_high_risk.sh** - Testa predição de alto risco

### Configuração
- **deploy_config.sh** - Configurações AWS (Account ID, região, etc.)
- **.dockerignore** - Arquivos ignorados no build Docker

## Status do Deploy

✅ **Deploy concluído com sucesso!**

### Endpoints Ativos

**API de Predição:**
```
https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/predict
```

**Health Check:**
```
https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/health
```

**Interface Web:**
```
http://hypertension-tcc-ceunsp-2026.s3-website-sa-east-1.amazonaws.com/ui/index.html
```

## Começar Agora - Teste Rápido! 🚀

### Opção 1: Executar Todos os Testes (Recomendado)

```bash
cd 12_deploy_aws
./run_all_tests.sh
```

Este script executa automaticamente:
1. Health check da API
2. Predição de baixo risco
3. Predição de risco médio
4. Predição de alto risco

### Opção 2: Testes Individuais

```bash
# Apenas health check
./test_health.sh

# Apenas teste de baixo risco
./test_prediction_low_risk.sh

# Apenas teste de alto risco
./test_prediction_high_risk.sh
```

### Opção 3: Interface Web

Abra no navegador:
```
http://hypertension-tcc-ceunsp-2026.s3-website-sa-east-1.amazonaws.com/ui/index.html
```

### Documentação Completa

- **TUTORIAL_TESTE.md** - Tutorial detalhado com mais exemplos
- **DEPLOY_COMPLETO.md** - Informações técnicas do deploy

## Recursos AWS

- **Região**: sa-east-1 (São Paulo)
- **Account ID**: 710586046477
- **Lambda Function**: hypertension-api
- **API Gateway**: yrac79mzj9
- **S3 Bucket**: hypertension-tcc-ceunsp-2026
- **Custo Estimado**: ~$0.00 - $0.50/mês (Free Tier)
