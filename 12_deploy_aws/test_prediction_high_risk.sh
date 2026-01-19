#!/bin/bash
# Script para testar predição de ALTO RISCO

API_URL="https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com"

echo "==============================================="
echo "  Testando Predição - PACIENTE DE ALTO RISCO"
echo "==============================================="
echo ""
echo "Paciente: Homem, 65 anos, múltiplos fatores"
echo "- Fumante ativo (20 cigarros/dia)"
echo "- Usa medicamento para pressão"
echo "- Diabético"
echo "- Pressão alta: 160/100"
echo "- IMC elevado: 32 (obesidade)"
echo "- Glicose alta: 140"
echo ""
echo "Enviando request..."
echo ""

curl -s -X POST "$API_URL/predict" \
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
  }' | jq '.'

echo ""
echo "================================================"
echo "✅ Resultado esperado: probability > 0.7"
echo "✅ risk_category = 'high'"
echo "✅ prediction = 1 (hipertenso)"
echo "================================================"
