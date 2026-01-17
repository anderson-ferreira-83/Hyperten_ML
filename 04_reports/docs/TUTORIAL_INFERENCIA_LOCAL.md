# Tutorial de inferencia local

Este guia mostra como rodar e testar a inferencia localmente (script e API).

## 1) Requisitos

- Python 3.10+
- Dependencias instaladas

Se necessario, instale:
```bash
pip install -r requirements.txt
```

## 2) Teste rapido com script

Executa uma predicao usando o pipeline em `05_artifacts/rf_v1`:
```bash
python 08_src/inference/inference.py
```

Saida esperada (exemplo):
```
Result: {'probability': 0.82, 'threshold': 0.3, 'prediction': 1, 'threshold_profile': 'balanced'}
```

## 3) Subir a API local (FastAPI)

Inicie o servidor:
```bash
python -m uvicorn main:app --app-dir 06_api --reload
```

Endpoints:
- `GET /health`
- `GET /docs`
- `POST /predict?threshold_key=balanced`

## 4) Teste via API (curl)

```bash
curl -X POST "http://127.0.0.1:8000/predict?threshold_key=balanced" \
  -H "Content-Type: application/json" \
  -d "{\"sexo\":1,\"idade\":55,\"fumante_atualmente\":0,\"cigarros_por_dia\":0,\"medicamento_pressao\":0,\"diabetes\":0,\"colesterol_total\":220,\"pressao_sistolica\":140,\"pressao_diastolica\":90,\"imc\":27.5,\"frequencia_cardiaca\":78,\"glicose\":90}"
```

## 5) Teste via API (PowerShell)

```powershell
$body = @{
  sexo = 1
  idade = 55
  fumante_atualmente = 0
  cigarros_por_dia = 0
  medicamento_pressao = 0
  diabetes = 0
  colesterol_total = 220
  pressao_sistolica = 140
  pressao_diastolica = 90
  imc = 27.5
  frequencia_cardiaca = 78
  glicose = 90
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict?threshold_key=balanced" `
  -Method Post -ContentType "application/json" -Body $body
```

## 6) Observacoes

- O pipeline oficial esta em `05_artifacts/rf_v1/pipeline.pkl`.
- A ordem oficial das features esta em `05_artifacts/rf_v1/features.json`.
- Thresholds clinicos estao em `05_artifacts/rf_v1/thresholds.json`.
