import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = ROOT / '05_artifacts' / 'gb_v1'

PIPELINE_PATH = ARTIFACTS_DIR / 'pipeline.pkl'
FEATURES_PATH = ARTIFACTS_DIR / 'features.json'
THRESHOLDS_PATH = ARTIFACTS_DIR / 'thresholds.json'


def load_artifacts():
    if not PIPELINE_PATH.exists():
        raise FileNotFoundError(f'Pipeline not found: {PIPELINE_PATH}')
    if not FEATURES_PATH.exists():
        raise FileNotFoundError(f'Features not found: {FEATURES_PATH}')

    pipeline = joblib.load(PIPELINE_PATH)
    with open(FEATURES_PATH, 'r', encoding='utf-8') as f:
        features_data = json.load(f)

    thresholds = None
    if THRESHOLDS_PATH.exists():
        with open(THRESHOLDS_PATH, 'r', encoding='utf-8') as f:
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
