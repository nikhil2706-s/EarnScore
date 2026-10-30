
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

ROOT = Path(__file__).resolve().parents[2]

PERSONAS = [
    ("demo-stable-001", 836),
    ("demo-volatile-002", 485),
    ("demo-seasonal-003", 509),
]


@pytest.mark.parametrize("applicant_id,expected_score", PERSONAS)
def test_csv_upload_persona(applicant_id, expected_score):
    csv_path = ROOT / "data" / "raw" / f"{applicant_id}.csv"

    with csv_path.open("rb") as csv_file:
        response = client.post(
            "/score/upload-csv",
            files={"file": (csv_path.name, csv_file, "text/csv")},
        )

    assert response.status_code == 200, response.text

    result = response.json()

    assert result["applicant_id"] == applicant_id
    assert result["score"] == expected_score
    assert 300 <= result["score"] <= 900

    assert result["score"] == 300 + sum(
        factor["points"] for factor in result["factors"]
    )

    assert result["data_quality"] is not None
    assert 0 <= result["data_quality"]["confidence"] <= 1
    assert result["confidence"] == 0.95

    assert "Emergency buffer data unavailable" in result["risk_flags"]


def test_non_csv_upload_rejected():
    response = client.post(
        "/score/upload-csv",
        files={"file": ("invalid.txt", b"not a csv", "text/plain")},
    )

    assert response.status_code == 400


def test_empty_csv_rejected():
    response = client.post(
        "/score/upload-csv",
        files={"file": ("empty.csv", b"", "text/csv")},
    )

    assert response.status_code == 400
def test_oversized_csv_rejected():
    oversized_content = b"x" * (5 * 1024 * 1024 + 1)

    response = client.post(
        "/score/upload-csv",
        files={
            "file": (
                "oversized.csv",
                oversized_content,
                "text/csv"
            )
        },
    )

    assert response.status_code == 413
    
def test_malformed_csv_rejected():
    response = client.post(
        "/score/upload-csv",
        files={
            "file": (
                "malformed.csv",
                b"this,is,not,a,valid,transaction,schema\n1,2,3",
                "text/csv",
            )
        },
    )

    assert response.status_code == 422
