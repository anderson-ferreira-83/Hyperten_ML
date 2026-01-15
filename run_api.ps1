$ErrorActionPreference = 'Stop'

Write-Host "Iniciando API (FastAPI)..."
python -m uvicorn main:app --app-dir 06_api --reload
