#!/usr/bin/env bash
set -euo pipefail

echo "Iniciando API (FastAPI)..."
python -m uvicorn main:app --app-dir 06_api --reload
