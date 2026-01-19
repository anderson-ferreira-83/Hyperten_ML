# Início Rápido - Teste em 30 Segundos! ⚡

## Testar Agora (Linha de Comando)

```bash
# 1. Entre no diretório
cd 12_deploy_aws

# 2. Execute todos os testes
./run_all_tests.sh
```

**Pronto!** O script vai mostrar 4 testes:
- ✅ Health check
- ✅ Predição de baixo risco
- ✅ Predição de risco médio
- ✅ Predição de alto risco

---

## Testar pela Interface Web

Copie e cole no navegador:
```
http://hypertension-tcc-ceunsp-2026.s3-website-sa-east-1.amazonaws.com/ui/index.html
```

Preencha o formulário e clique em "Predizer Risco".

---

## Testar com curl (Direto)

```bash
# Health check
curl https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/health

# Fazer uma predição
curl -X POST https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/predict \
  -H "Content-Type: application/json" \
  -d '{"sexo":1,"idade":50,"fumante_atualmente":0,"cigarros_por_dia":0,"medicamento_pressao":0,"diabetes":0,"colesterol_total":200,"pressao_sistolica":120,"pressao_diastolica":80,"imc":25,"frequencia_cardiaca":70,"glicose":90}'
```

---

## O que você deve ver

### Health Check ✅
```json
{
  "status": "ok",
  "pipeline_loaded": true,
  "features_count": 12
}
```

### Predição de Baixo Risco ✅
```json
{
  "probability": 0.048,
  "prediction": 0,
  "risk_category": "low"
}
```

### Predição de Alto Risco ✅
```json
{
  "probability": 0.85,
  "prediction": 1,
  "risk_category": "high"
}
```

---

## Problemas?

1. **Scripts não executam?**
   ```bash
   chmod +x *.sh
   ```

2. **Quer mais detalhes?**
   - Leia: `TUTORIAL_TESTE.md`
   - Documentação completa: `DEPLOY_COMPLETO.md`

3. **Quer testar outros cenários?**
   - Execute scripts individuais:
     - `./test_health.sh`
     - `./test_prediction_low_risk.sh`
     - `./test_prediction_medium_risk.sh`
     - `./test_prediction_high_risk.sh`

---

**Está tudo funcionando?** Você tem uma API de ML 100% funcional na AWS! 🎉
