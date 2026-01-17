#!/bin/bash
# Script para testar o health check da API

API_URL="https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com"

echo "========================================="
echo "  Testando Health Check da API AWS"
echo "========================================="
echo ""
echo "URL: $API_URL/health"
echo ""

curl -s "$API_URL/health" | jq '.'

echo ""
echo "========================================="
echo "✅ Se 'pipeline_loaded' = true, está OK!"
echo "========================================="
