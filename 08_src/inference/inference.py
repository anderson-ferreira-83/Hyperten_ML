import json
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_BASE = ROOT / '05_artifacts'
DEFAULT_ARTIFACT_KEY = 'gb_v1'
MODEL_SUMMARY_CANDIDATES = [
    ROOT / '02_notebooks' / '06_model_metrics' / '6_analysis_metrics' / 'model_training_summary.json',
    ROOT / '04_reports' / 'modeling' / 'model_training_summary.json',
]


def _normalize_model_name(value):
    if not value:
        return None
    return ''.join(ch for ch in value.lower().strip() if ch.isalnum())


def _load_best_model_name():
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


def _build_artifact_map():
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


def _resolve_artifacts_dir():
    artifact_map = _build_artifact_map()
    best_model_name, summary_path = _load_best_model_name()
    if best_model_name:
        key = _normalize_model_name(best_model_name)
        if key in artifact_map:
            return artifact_map[key], best_model_name, summary_path

    env_key = os.getenv('MODEL_KEY')
    if env_key:
        env_dir = ARTIFACTS_BASE / env_key
        if env_dir.exists():
            return env_dir, env_key, summary_path

    default_dir = ARTIFACTS_BASE / DEFAULT_ARTIFACT_KEY
    if default_dir.exists():
        return default_dir, DEFAULT_ARTIFACT_KEY, summary_path

    if artifact_map:
        first_dir = next(iter(artifact_map.values()))
        return first_dir, first_dir.name, summary_path

    raise FileNotFoundError(f'No artifacts found under {ARTIFACTS_BASE}')


def load_artifacts():
    artifacts_dir, selected_model, summary_path = _resolve_artifacts_dir()
    pipeline_path = artifacts_dir / 'pipeline.pkl'
    features_path = artifacts_dir / 'features.json'
    thresholds_path = artifacts_dir / 'thresholds.json'

    if not pipeline_path.exists():
        raise FileNotFoundError(f'Pipeline not found: {pipeline_path}')
    if not features_path.exists():
        raise FileNotFoundError(f'Features not found: {features_path}')

    pipeline = joblib.load(pipeline_path)
    with open(features_path, 'r', encoding='utf-8') as f:
        features_data = json.load(f)

    thresholds = None
    if thresholds_path.exists():
        with open(thresholds_path, 'r', encoding='utf-8') as f:
            thresholds = json.load(f)

    return pipeline, features_data['features'], thresholds


def predict_single(payload, threshold_key='balanced'):
    pipeline, features, thresholds = load_artifacts()

    # Ensure correct order and types
    row = {k: payload.get(k) for k in features}
    df = pd.DataFrame([row], columns=features)

    # Predict probability
    if hasattr(pipeline, 'predict_proba'):
        prob = float(pipeline.predict_proba(df)[:, 1][0])
    else:
        prob = float(pipeline.predict(df)[0])

    # Apply threshold
    threshold = 0.5
    if thresholds and threshold_key in thresholds:
        threshold = float(thresholds[threshold_key]['threshold'])

    label = int(prob >= threshold)

    return {
        'probability': prob,
        'threshold': threshold,
        'prediction': label,
        'threshold_profile': threshold_key,
    }


def main():
    # Example payload (edit for real inputs)
    payload = {
        'sexo': 1,
        'idade': 55,
        'fumante_atualmente': 0,
        'cigarros_por_dia': 0,
        'medicamento_pressao': 0,
        'diabetes': 0,
        'colesterol_total': 220,
        'pressao_sistolica': 140,
        'pressao_diastolica': 90,
        'imc': 27.5,
        'frequencia_cardiaca': 78,
        'glicose': 90,
    }

    result = predict_single(payload, threshold_key='balanced')
    print('Result:', result)


if __name__ == '__main__':
    main()
