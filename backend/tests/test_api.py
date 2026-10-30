
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_invalid_income_ratio():
    payload = {
        "applicant_id": "invalid-demo",
        "analysis_period_months": 12,
        "features": {
            "active_months_ratio": 1.5,
            "income_cv": 0.21,
            "source_diversity": 0.68,
            "positive_cashflow_months_ratio": 0.83,
            "expense_to_income_ratio": 0.62,
            "income_trend": 0.08,
            "emergency_buffer_days": None
        }
    }

    response = client.post("/score", json=payload)
    assert response.status_code == 422


def test_missing_required_features():
    payload = {
        "applicant_id": "missing-features",
        "analysis_period_months": 12,
        "features": {
            "active_months_ratio": 0.8
        }
    }

    response = client.post("/score", json=payload)
    assert response.status_code == 422


def test_negative_emergency_buffer():
    payload = {
        "applicant_id": "negative-buffer",
        "analysis_period_months": 12,
        "features": {
            "active_months_ratio": 0.8,
            "income_cv": 0.3,
            "source_diversity": 0.5,
            "positive_cashflow_months_ratio": 0.7,
            "expense_to_income_ratio": 0.6,
            "income_trend": 0.05,
            "emergency_buffer_days": -10
        }
    }

    response = client.post("/score", json=payload)
    assert response.status_code == 422
