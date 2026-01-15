import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "06_api"))

from main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["pipeline_loaded"] is True


def test_predict_basic(client):
    payload = {
        "sexo": 1,
        "idade": 55,
        "fumante_atualmente": 0,
        "cigarros_por_dia": 0,
        "medicamento_pressao": 0,
        "diabetes": 0,
        "colesterol_total": 220,
        "pressao_sistolica": 140,
        "pressao_diastolica": 90,
        "imc": 27.5,
        "frequencia_cardiaca": 78,
        "glicose": 90,
    }
    resp = client.post("/predict?threshold_key=balanced", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "probability" in data
    assert "prediction" in data
    assert data["threshold_profile"] in ("balanced", "default")
    assert "risk_category" in data
    assert data["risk_category"] in ("low", "medium", "high")
    assert "model_version" in data
