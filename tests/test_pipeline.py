"""Tests for end-to-end command-line and pipeline execution."""

import json
from pathlib import Path
import subprocess
import sys
import pytest

from src.data_pipeline.pipeline import run_pipeline
from src.data_pipeline.schemas import Member1FeaturePayload


@pytest.fixture
def raw_dir() -> Path:
    return Path("data/raw")


def test_pipeline_run_direct(raw_dir: Path, tmp_path: Path):
    """Test direct Python function call with output writing."""
    csv_file = raw_dir / "demo-stable-001.csv"
    out_file = tmp_path / "output.json"

    payload = run_pipeline(csv_path=csv_file, output_path=out_file)

    assert isinstance(payload, Member1FeaturePayload)
    assert payload.applicant_id == "demo-stable-001"
    assert out_file.exists()

    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["applicant_id"] == "demo-stable-001"
    assert "features" in data
    assert len(data["features"]) == 7
    assert data["features"]["emergency_buffer_days"] is None


def test_cli_execution_all_three_personas(raw_dir: Path):
    """Verify CLI execution via subprocess for all 3 demo personas."""
    personas = ["demo-stable-001", "demo-volatile-002", "demo-seasonal-003"]

    for pid in personas:
        csv_file = raw_dir / f"{pid}.csv"
        result = subprocess.run(
            [sys.executable, "-m", "src.data_pipeline.pipeline", str(csv_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"CLI failed for {pid}: {result.stderr}"
        # Stderr contains diagnostic logging
        assert "[INFO]" in result.stderr
        # Stdout contains strictly valid JSON
        output_json = json.loads(result.stdout)
        assert output_json["applicant_id"] == pid
        assert output_json["analysis_period_months"] == 12
        assert output_json["features"]["emergency_buffer_days"] is None

        # Verify the 7 feature keys
        feature_keys = set(output_json["features"].keys())
        expected_keys = {
            "active_months_ratio",
            "income_cv",
            "source_diversity",
            "positive_cashflow_months_ratio",
            "expense_to_income_ratio",
            "income_trend",
            "emergency_buffer_days",
        }
        assert feature_keys == expected_keys


def test_cli_optional_output_flag(raw_dir: Path, tmp_path: Path):
    """Test --output flag generates target JSON file while still printing to stdout."""
    csv_file = raw_dir / "demo-stable-001.csv"
    out_file = tmp_path / "saved_report.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.data_pipeline.pipeline",
            str(csv_file),
            "--output",
            str(out_file),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert out_file.exists()

    # Both file and stdout must match
    with open(out_file, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
    stdout_data = json.loads(result.stdout)
    assert saved_data == stdout_data


def test_cli_handles_invalid_file():
    """Verify non-existent file exits cleanly with code 1 and error on stderr."""
    result = subprocess.run(
        [sys.executable, "-m", "src.data_pipeline.pipeline", "non_existent_file.csv"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "[ERROR]" in result.stderr


def test_cli_handles_conflicting_applicants(tmp_path: Path):
    """Verify that multiple conflicting applicant IDs in a single unguided file are rejected."""
    bad_csv = tmp_path / "mixed.csv"
    bad_csv.write_text(
        "transaction_id,applicant_id,date,amount,type,category,source,description,balance\n"
        "tx_1,applicant_A,2026-05-01,1000.0,credit,income,Swiggy,delivery,\n"
        "tx_2,applicant_B,2026-05-02,2000.0,credit,income,Uber,ride,\n"
    )

    result = subprocess.run(
        [sys.executable, "-m", "src.data_pipeline.pipeline", str(bad_csv)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "multiple distinct applicant IDs" in result.stderr

