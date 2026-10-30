
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)
ROOT = Path(__file__).resolve().parents[2]

PERSONAS = [
    ("demo-stable-001", "demo-features.json"),
    ("demo-volatile-002", "demo-volatile.json"),
    ("demo-seasonal-003", "demo-seasonal.json"),
]


@pytest.mark.parametrize("applicant_id,filename", PERSONAS)
def test_persona_integration(applicant_id, filename):
    path = ROOT / filename
    assert path.exists(), f"Missing fixture: {filename}"

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["applicant_id"] == applicant_id
    assert len(payload["features"]) == 7

    response = client.post("/score", json=payload)
    assert response.status_code == 200, response.text

    result = response.json()

    assert result["applicant_id"] == applicant_id
    assert 300 <= result["score"] <= 900
    assert result["band"] in {
        "Strong", "Moderate", "Needs Review"
    }

    assert result["score"] == 300 + sum(
        factor["points"] for factor in result["factors"]
    )

    # Data-quality and feature-completeness confidence
    assert result["data_quality"] == payload["data_quality"]
    assert 0 <= result["confidence"] <= 1
    assert 0 <= result["data_quality"]["confidence"] <= 1

    # Missing emergency-buffer handling
    if payload["features"]["emergency_buffer_days"] is None:
        assert result["confidence"] == 0.95
        assert (
            "Emergency buffer data unavailable"
            in result["risk_flags"]
        )
        assert all(
            factor["key"] != "emergency_buffer_days"
            for factor in result["factors"]
        )

    # Risk flags must have readable explanations
    assert isinstance(result["risk_flags"], list)
    assert all(
        isinstance(flag, str) and flag.strip()
        for flag in result["risk_flags"]
    )

    assert len(result["factors"]) >= 6
    assert all(
        factor["explanation"].strip()
        for factor in result["factors"]
    )

    print(
        f"\n{applicant_id}: "
        f"score={result['score']}, "
        f"band={result['band']}, "
        f"feature_confidence={result['confidence']}, "
        f"data_quality_confidence="
        f"{result['data_quality']['confidence']}, "
        f"risk_flags={result['risk_flags']}"
    )
