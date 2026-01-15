import json
from pathlib import Path
from typing import Optional, Dict, Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = ROOT / '05_artifacts' / 'gb_v1'

PIPELINE_PATH = ARTIFACTS_DIR / 'pipeline.pkl'
FEATURES_PATH = ARTIFACTS_DIR / 'features.json'
THRESHOLDS_PATH = ARTIFACTS_DIR / 'thresholds.json'
METADATA_PATH = ARTIFACTS_DIR / 'metadata.json'

app = FastAPI(title='Hypertension Risk Inference', version='1.0.0')

pipeline = None
features = None
thresholds = None
metadata = None
html_index = None


class PredictionInput(BaseModel):
    sexo: Optional[int] = Field(None, ge=0, le=1)
    idade: Optional[float] = Field(None, ge=0)
    fumante_atualmente: Optional[int] = Field(None, ge=0, le=1)
    cigarros_por_dia: Optional[float] = Field(None, ge=0)
    medicamento_pressao: Optional[int] = Field(None, ge=0, le=1)
    diabetes: Optional[int] = Field(None, ge=0, le=1)
    colesterol_total: Optional[float] = Field(None, ge=0)
    pressao_sistolica: Optional[float] = Field(None, ge=0)
    pressao_diastolica: Optional[float] = Field(None, ge=0)
    imc: Optional[float] = Field(None, ge=0)
    frequencia_cardiaca: Optional[float] = Field(None, ge=0)
    glicose: Optional[float] = Field(None, ge=0)


class CacheControlStaticFiles(StaticFiles):
    def __init__(self, *args, cache_control: str = "public, max-age=31536000", **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_control = cache_control

    async def get_response(self, path: str, scope) -> Response:
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = self.cache_control
        return response


@app.on_event('startup')
def load_artifacts() -> None:
    global pipeline, features, thresholds, metadata, html_index

    if not PIPELINE_PATH.exists():
        raise RuntimeError(f'Pipeline not found: {PIPELINE_PATH}')
    if not FEATURES_PATH.exists():
        raise RuntimeError(f'Features not found: {FEATURES_PATH}')

    pipeline = joblib.load(PIPELINE_PATH)

    with open(FEATURES_PATH, 'r', encoding='utf-8') as f:
        features_data = json.load(f)
    features = features_data.get('features')

    if THRESHOLDS_PATH.exists():
        with open(THRESHOLDS_PATH, 'r', encoding='utf-8') as f:
            thresholds = json.load(f)

    if METADATA_PATH.exists():
        with open(METADATA_PATH, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

    web_index_path = ROOT / '07_web' / 'index.html'
    if web_index_path.exists():
        html_index = web_index_path.read_text(encoding='utf-8')

    static_dir = ROOT / '07_web'
    if static_dir.exists():
        app.mount('/static', CacheControlStaticFiles(directory=str(static_dir)), name='static')


@app.get('/health')
def health() -> Dict[str, Any]:
    return {
        'status': 'ok',
        'pipeline_loaded': pipeline is not None,
        'features_count': len(features) if features else 0,
        'artifacts_dir': str(ARTIFACTS_DIR),
    }


@app.get('/')
def root() -> RedirectResponse:
    return RedirectResponse(url='/app')


@app.get('/app')
def app_ui() -> HTMLResponse:
    if html_index is None:
        raise HTTPException(status_code=404, detail='UI not available')
    return HTMLResponse(content=html_index)


@app.post('/predict')
def predict(payload: PredictionInput, threshold_key: str = Query('balanced')) -> Dict[str, Any]:
    if pipeline is None or features is None:
        raise HTTPException(status_code=500, detail='Artifacts not loaded')

    data = payload.dict()
    row = {k: data.get(k) for k in features}

    missing = [k for k, v in row.items() if v is None]
    if len(missing) == len(features):
        raise HTTPException(status_code=400, detail='No features provided')

    df = pd.DataFrame([row], columns=features)

    if hasattr(pipeline, 'predict_proba'):
        prob = float(pipeline.predict_proba(df)[:, 1][0])
    else:
        prob = float(pipeline.predict(df)[0])

    threshold = 0.5
    threshold_profile = threshold_key
    if thresholds and threshold_key in thresholds:
        threshold = float(thresholds[threshold_key]['threshold'])
    else:
        threshold_profile = 'default'

    prediction = int(prob >= threshold)

    risk_category = "medium"
    if thresholds and "screening" in thresholds and "confirmation" in thresholds:
        low_cut = float(thresholds["screening"]["threshold"])
        high_cut = float(thresholds["confirmation"]["threshold"])
        if prob < low_cut:
            risk_category = "low"
        elif prob >= high_cut:
            risk_category = "high"

    return {
        'probability': prob,
        'threshold': threshold,
        'prediction': prediction,
        'threshold_profile': threshold_profile,
        'risk_category': risk_category,
        'missing_features': missing,
        'model': metadata.get('model') if metadata else None,
        'model_version': metadata.get('model_version') if metadata else None,
    }
