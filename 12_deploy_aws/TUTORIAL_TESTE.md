# Tutorial de Teste - API de Predição de Hipertensão na AWS

Este tutorial mostra como testar a aplicação deployada na AWS de 3 formas diferentes:
1. Via linha de comando (curl)
2. Via interface web (navegador)
3. Via Postman/Insomnia (opcional)

---

## 1. Teste via Linha de Comando (curl)

### 1.1. Testar Health Check

Verifica se a API está funcionando e o modelo está carregado:

```bash
curl https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/health
```

**Resposta esperada:**
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

✅ Se `"pipeline_loaded": true`, o modelo está pronto para uso!

---

### 1.2. Fazer Predição de Risco Baixo

Paciente saudável (50 anos, sem fatores de risco):

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

**Resposta esperada:**
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

---

### 1.3. Fazer Predição de Risco Alto

Paciente com múltiplos fatores de risco (65 anos, hipertenso, diabético, fumante):

```bash
curl -X POST https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "sexo": 1,
    "idade": 65,
    "fumante_atualmente": 1,
    "cigarros_por_dia": 20,
    "medicamento_pressao": 1,
    "diabetes": 1,
    "colesterol_total": 280,
    "pressao_sistolica": 160,
    "pressao_diastolica": 100,
    "imc": 32,
    "frequencia_cardiaca": 90,
    "glicose": 140
  }'
```

**Resposta esperada:**
```json
{
  "probability": 0.85,
  "threshold": 0.3,
  "prediction": 1,
  "threshold_profile": "balanced",
  "risk_category": "high",
  "missing_features": [],
  "model": "GradientBoostingClassifier",
  "model_version": "gb_v1",
  "model_selected": "gb_v1",
  "model_requested": null
}
```

---

### 1.4. Fazer Predição de Risco Médio

Paciente com alguns fatores de risco (55 anos, levemente acima do peso):

```bash
curl -X POST https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "sexo": 0,
    "idade": 55,
    "fumante_atualmente": 0,
    "cigarros_por_dia": 0,
    "medicamento_pressao": 0,
    "diabetes": 0,
    "colesterol_total": 240,
    "pressao_sistolica": 135,
    "pressao_diastolica": 85,
    "imc": 28,
    "frequencia_cardiaca": 75,
    "glicose": 105
  }'
```

---

## 2. Teste via Interface Web

### 2.1. Acessar a Interface

Abra no navegador:
```
http://hypertension-tcc-ceunsp-2026.s3-website-sa-east-1.amazonaws.com/ui/index.html
```

### 2.2. Preencher o Formulário

**Exemplo 1: Paciente de Baixo Risco**
- Sexo: Masculino (1)
- Idade: 50
- Fumante atualmente: Não (0)
- Cigarros por dia: 0
- Medicamento para pressão: Não (0)
- Diabetes: Não (0)
- Colesterol total: 200
- Pressão sistólica: 120
- Pressão diastólica: 80
- IMC: 25
- Frequência cardíaca: 70
- Glicose: 90

### 2.3. Clicar em "Predizer Risco"

A interface mostrará:
- **Probabilidade de hipertensão**: ~5%
- **Categoria de risco**: Baixo
- **Predição**: Não hipertenso (0)

### 2.4. Testar Outros Perfis

**Exemplo 2: Paciente de Alto Risco**
- Idade: 65
- Fumante atualmente: Sim (1)
- Cigarros por dia: 20
- Medicamento para pressão: Sim (1)
- Diabetes: Sim (1)
- Colesterol total: 280
- Pressão sistólica: 160
- Pressão diastólica: 100
- IMC: 32
- Frequência cardíaca: 90
- Glicose: 140

Resultado esperado: **Probabilidade alta (~85%)**, **Categoria: Alto risco**

---

## 3. Teste via Postman/Insomnia (Opcional)

### 3.1. Importar Request

**Method**: POST
**URL**: `https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/predict`
**Headers**:
```
Content-Type: application/json
```

**Body (JSON)**:
```json
{
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
}
```

### 3.2. Enviar Request

Clique em "Send" e verifique a resposta JSON.

---

## 4. Verificar Logs da Lambda (Opcional)

Se você tem acesso à AWS CLI configurada:

```bash
# Ver logs em tempo real
aws logs tail /aws/lambda/hypertension-api --follow --region sa-east-1

# Ver últimas 50 linhas
aws logs tail /aws/lambda/hypertension-api --region sa-east-1
```

---

## 5. Testes de Performance

### 5.1. Testar Cold Start vs Warm Start

**Primeiro request (cold start - ~2-3 segundos):**
```bash
time curl -X POST https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/predict \
  -H "Content-Type: application/json" \
  -d '{"sexo":1,"idade":50,"fumante_atualmente":0,"cigarros_por_dia":0,"medicamento_pressao":0,"diabetes":0,"colesterol_total":200,"pressao_sistolica":120,"pressao_diastolica":80,"imc":25,"frequencia_cardiaca":70,"glicose":90}'
```

**Segundo request imediato (warm - ~50-200 ms):**
```bash
time curl -X POST https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/predict \
  -H "Content-Type: application/json" \
  -d '{"sexo":1,"idade":50,"fumante_atualmente":0,"cigarros_por_dia":0,"medicamento_pressao":0,"diabetes":0,"colesterol_total":200,"pressao_sistolica":120,"pressao_diastolica":80,"imc":25,"frequencia_cardiaca":70,"glicose":90}'
```

### 5.2. Teste de Carga (Múltiplos Requests)

```bash
# Fazer 10 requests seguidos
for i in {1..10}; do
  echo "Request $i:"
  curl -s -X POST https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/predict \
    -H "Content-Type: application/json" \
    -d '{"sexo":1,"idade":50,"fumante_atualmente":0,"cigarros_por_dia":0,"medicamento_pressao":0,"diabetes":0,"colesterol_total":200,"pressao_sistolica":120,"pressao_diastolica":80,"imc":25,"frequencia_cardiaca":70,"glicose":90}' \
    | jq '.probability'
  echo ""
done
```

---

## 6. Casos de Teste Completos

### Caso 1: Mulher Jovem Saudável
```json
{
  "sexo": 0,
  "idade": 30,
  "fumante_atualmente": 0,
  "cigarros_por_dia": 0,
  "medicamento_pressao": 0,
  "diabetes": 0,
  "colesterol_total": 180,
  "pressao_sistolica": 110,
  "pressao_diastolica": 70,
  "imc": 22,
  "frequencia_cardiaca": 65,
  "glicose": 85
}
```
**Resultado esperado**: Risco muito baixo (~1-3%)

### Caso 2: Homem Idoso com Pré-hipertensão
```json
{
  "sexo": 1,
  "idade": 70,
  "fumante_atualmente": 0,
  "cigarros_por_dia": 0,
  "medicamento_pressao": 0,
  "diabetes": 0,
  "colesterol_total": 220,
  "pressao_sistolica": 138,
  "pressao_diastolica": 88,
  "imc": 27,
  "frequencia_cardiaca": 72,
  "glicose": 100
}
```
**Resultado esperado**: Risco médio (~30-50%)

### Caso 3: Paciente Crítico
```json
{
  "sexo": 1,
  "idade": 75,
  "fumante_atualmente": 1,
  "cigarros_por_dia": 30,
  "medicamento_pressao": 1,
  "diabetes": 1,
  "colesterol_total": 300,
  "pressao_sistolica": 180,
  "pressao_diastolica": 110,
  "imc": 35,
  "frequencia_cardiaca": 95,
  "glicose": 160
}
```
**Resultado esperado**: Risco muito alto (~90-95%)

### Caso 4: Dados Incompletos (para testar validação)
```json
{
  "sexo": 1,
  "idade": 50
}
```
**Resultado esperado**: A API aceita e retorna predição baseada apenas nos valores fornecidos, indicando features faltantes.

---

## 7. Interpretação dos Resultados

### Campos da Resposta

- **probability**: Probabilidade de ter hipertensão (0.0 a 1.0)
- **threshold**: Limite usado para classificação (0.3 = balanced)
- **prediction**: Classificação binária (0 = sem hipertensão, 1 = com hipertensão)
- **threshold_profile**: Perfil de threshold utilizado ("balanced")
- **risk_category**: Categoria de risco ("low", "medium", "high")
- **missing_features**: Lista de features não fornecidas
- **model**: Algoritmo usado (GradientBoostingClassifier)
- **model_version**: Versão do modelo (gb_v1)

### Categorias de Risco

- **low** (baixo): probability < 0.3
- **medium** (médio): 0.3 ≤ probability < 0.7
- **high** (alto): probability ≥ 0.7

---

## 8. Solução de Problemas

### Erro: "Internal Server Error"
**Solução**: Aguarde alguns segundos e tente novamente (cold start da Lambda)

### Erro: "CORS error" no navegador
**Solução**: Verifique se está acessando via HTTP (não HTTPS) para a UI no S3

### Erro: "Connection timeout"
**Solução**: Verifique sua conexão com a internet e tente novamente

### API retorna erro 404
**Solução**: Verifique se a URL está correta (não inclua /prod no caminho)

---

## 9. Métricas de Sucesso

Após os testes, você deve observar:

✅ Health check retorna `"pipeline_loaded": true`
✅ Predições retornam em menos de 3 segundos (cold start)
✅ Predições retornam em menos de 500ms (warm start)
✅ Probabilidades fazem sentido clínico (alto risco para fatores de risco elevados)
✅ Interface web funciona e exibe resultados corretamente
✅ CORS funciona (sem erros no console do navegador)

---

## 10. Próximos Passos

Após validar que tudo funciona:

1. **Documentar casos de uso específicos** do seu TCC
2. **Coletar métricas de performance** para o relatório
3. **Testar com dados reais** (se disponível e autorizado)
4. **Preparar demonstração** para apresentação do TCC

---

**Dúvidas ou problemas?**

Consulte o arquivo `DEPLOY_COMPLETO.md` para detalhes técnicos completos do deploy.
