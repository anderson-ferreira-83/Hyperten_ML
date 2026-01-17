import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_BASE = ROOT / '05_artifacts'
DEFAULT_ARTIFACT_KEY = 'rf_v1'  # Random Forest - melhor modelo (Recall=92%, F2=0.89)
MODEL_SUMMARY_CANDIDATES = [
    ROOT / '02_notebooks' / '06_model_metrics' / '6_analysis_metrics' / 'model_training_summary.json',
    ROOT / '04_reports' / 'modeling' / 'model_training_summary.json',
]

app = FastAPI(title='Hypertension Risk Inference', version='1.0.0')

# CORS middleware para permitir requisições do navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = None
features = None
thresholds = None
metadata = None
html_index = None
artifacts_dir = None
selected_model = None
selected_summary_path = None
requested_model = None


def _normalize_model_name(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return ''.join(ch for ch in value.lower().strip() if ch.isalnum())


def _load_best_model_name() -> tuple[Optional[str], Optional[Path]]:
    candidates = [p for p in MODEL_SUMMARY_CANDIDATES if p.exists()]
    if not candidates:
        return None, None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    summary_path = candidates[0]
    with open(summary_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data.get('best_model'), dict):
        return data['best_model'].get('name'), summary_path
    if isinstance(data.get('experiment_info'), dict):
        return data['experiment_info'].get('best_model'), summary_path
    return None, summary_path


def _build_artifact_map() -> Dict[str, Path]:
    mapping = {}
    if not ARTIFACTS_BASE.exists():
        return mapping
    for item in ARTIFACTS_BASE.iterdir():
        if not item.is_dir():
            continue
        metadata_path = item / 'metadata.json'
        model_name = None
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            model_name = meta.get('model')
            if isinstance(model_name, str):
                if 'RandomForest' in model_name:
                    model_name = 'Random Forest'
                elif 'GradientBoosting' in model_name:
                    model_name = 'Gradient Boosting'
        for key in filter(None, [_normalize_model_name(model_name), _normalize_model_name(item.name)]):
            mapping[key] = item
    return mapping


def _resolve_artifacts_dir() -> tuple[Path, Optional[str], Optional[Path], Optional[str]]:
    artifact_map = _build_artifact_map()
    best_model_name, summary_path = _load_best_model_name()
    if best_model_name:
        key = _normalize_model_name(best_model_name)
        if key in artifact_map:
            return artifact_map[key], best_model_name, summary_path, best_model_name

    env_key = os.getenv('MODEL_KEY')
    if env_key:
        env_dir = ARTIFACTS_BASE / env_key
        if env_dir.exists():
            return env_dir, env_key, summary_path, best_model_name

    default_dir = ARTIFACTS_BASE / DEFAULT_ARTIFACT_KEY
    if default_dir.exists():
        return default_dir, DEFAULT_ARTIFACT_KEY, summary_path, best_model_name

    if artifact_map:
        first_dir = next(iter(artifact_map.values()))
        return first_dir, first_dir.name, summary_path, best_model_name

    raise RuntimeError(f'No artifacts found under {ARTIFACTS_BASE}')


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


class ComponentPipeline:
    """Pipeline que usa componentes separados (imputer, scaler, model)."""
    def __init__(self, imputer, scaler, model):
        self.imputer = imputer
        self.scaler = scaler
        self.model = model

    def predict(self, X):
        X_imputed = self.imputer.transform(X)
        X_scaled = self.scaler.transform(X_imputed)
        return self.model.predict(X_scaled)

    def predict_proba(self, X):
        X_imputed = self.imputer.transform(X)
        X_scaled = self.scaler.transform(X_imputed)
        return self.model.predict_proba(X_scaled)


@app.on_event('startup')
def load_artifacts() -> None:
    global pipeline, features, thresholds, metadata, html_index, artifacts_dir, selected_model, selected_summary_path, requested_model

    artifacts_dir, selected_model, selected_summary_path, requested_model = _resolve_artifacts_dir()
    pipeline_path = artifacts_dir / 'pipeline.pkl'
    imputer_path = artifacts_dir / 'imputer.pkl'
    scaler_path = artifacts_dir / 'scaler.pkl'
    model_path = artifacts_dir / 'model.pkl'
    features_path = artifacts_dir / 'features.json'
    thresholds_path = artifacts_dir / 'thresholds.json'
    metadata_path = artifacts_dir / 'metadata.json'

    if not features_path.exists():
        raise RuntimeError(f'Features not found: {features_path}')

    # Tenta carregar componentes separados primeiro (evita dependencia do imblearn)
    if imputer_path.exists() and scaler_path.exists() and model_path.exists():
        imputer = joblib.load(imputer_path)
        scaler = joblib.load(scaler_path)
        model = joblib.load(model_path)
        pipeline = ComponentPipeline(imputer, scaler, model)
    elif pipeline_path.exists():
        pipeline = joblib.load(pipeline_path)
    else:
        raise RuntimeError(f'No pipeline or components found in {artifacts_dir}')

    with open(features_path, 'r', encoding='utf-8') as f:
        features_data = json.load(f)
    features = features_data.get('features')

    if thresholds_path.exists():
        with open(thresholds_path, 'r', encoding='utf-8') as f:
            thresholds = json.load(f)

    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
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
        'artifacts_dir': str(artifacts_dir) if artifacts_dir else None,
        'selected_model': selected_model,
        'requested_model': requested_model,
        'model_summary_path': str(selected_summary_path) if selected_summary_path else None,
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
        'model_selected': selected_model,
        'model_requested': requested_model,
    }
