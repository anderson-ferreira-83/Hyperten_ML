#!/bin/bash
# Script para testar predição de BAIXO RISCO

API_URL="https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com"

echo "================================================"
echo "  Testando Predição - PACIENTE DE BAIXO RISCO"
echo "================================================"
echo ""
echo "Paciente: Homem, 50 anos, saudável"
echo "- Não fumante"
echo "- Sem medicamentos"
echo "- Pressão normal: 120/80"
echo "- IMC normal: 25"
echo ""
echo "Enviando request..."
echo ""

curl -s -X POST "$API_URL/predict" \
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
  }' | jq '.'

echo ""
echo "================================================"
echo "✅ Resultado esperado: probability < 0.1"
echo "✅ risk_category = 'low'"
echo "================================================"
