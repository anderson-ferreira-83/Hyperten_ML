#!/bin/bash
# Script para executar todos os testes da API AWS

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   SUITE DE TESTES - API PREDIÇÃO DE HIPERTENSÃO AWS      ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Verificar se jq está instalado
if ! command -v jq &> /dev/null; then
    echo "⚠️  AVISO: 'jq' não está instalado."
    echo "   Os resultados serão mostrados em JSON sem formatação."
    echo "   Para melhor visualização, instale jq:"
    echo "   - Ubuntu/Debian: sudo apt-get install jq"
    echo "   - macOS: brew install jq"
    echo "   - Windows: baixar de https://stedolan.github.io/jq/"
    echo ""
    read -p "Pressione ENTER para continuar sem jq..."
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "TESTE 1: Health Check"
echo "═══════════════════════════════════════════════════════════"
echo ""
bash test_health.sh
echo ""
echo "Pressione ENTER para continuar..."
read

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "TESTE 2: Predição - Baixo Risco"
echo "═══════════════════════════════════════════════════════════"
echo ""
bash test_prediction_low_risk.sh
echo ""
echo "Pressione ENTER para continuar..."
read

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "TESTE 3: Predição - Risco Médio"
echo "═══════════════════════════════════════════════════════════"
echo ""
bash test_prediction_medium_risk.sh
echo ""
echo "Pressione ENTER para continuar..."
read

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "TESTE 4: Predição - Alto Risco"
echo "═══════════════════════════════════════════════════════════"
echo ""
bash test_prediction_high_risk.sh
echo ""

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║                  TESTES CONCLUÍDOS! ✅                    ║"
echo "║                                                           ║"
echo "║  Todos os 4 testes foram executados.                     ║"
echo "║                                                           ║"
echo "║  Verifique os resultados acima:                          ║"
echo "║  • Health check deve mostrar pipeline_loaded = true      ║"
echo "║  • Baixo risco: probability < 0.1                        ║"
echo "║  • Médio risco: 0.3 < probability < 0.7                  ║"
echo "║  • Alto risco: probability > 0.7                         ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
