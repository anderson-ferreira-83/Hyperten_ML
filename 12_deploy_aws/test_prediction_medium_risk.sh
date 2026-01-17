#!/bin/bash
# Script para testar predição de RISCO MÉDIO

API_URL="https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com"

echo "================================================"
echo "  Testando Predição - PACIENTE DE RISCO MÉDIO"
echo "================================================"
echo ""
echo "Paciente: Mulher, 55 anos, alguns fatores"
echo "- Não fumante"
echo "- Sem medicamentos"
echo "- Pressão levemente elevada: 135/85"
echo "- IMC levemente elevado: 28 (sobrepeso)"
echo "- Colesterol alto: 240"
echo ""
echo "Enviando request..."
echo ""

curl -s -X POST "$API_URL/predict" \
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
  }' | jq '.'

echo ""
echo "================================================"
echo "✅ Resultado esperado: 0.3 < probability < 0.7"
echo "✅ risk_category = 'medium'"
echo "================================================"
