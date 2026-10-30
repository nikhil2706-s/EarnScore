"""Tests for feature extraction and monthly aggregation logic."""

import datetime as _dt
from pathlib import Path
import pandas as pd
import pytest

from src.data_pipeline.cleaner import load_and_clean_csv
from src.data_pipeline.features import extract_features
from src.data_pipeline.schemas import Member1FeaturePayload


def test_features_math_controlled_example():
    """Verify exact mathematical behavior on a hand-crafted dataset."""
    # 2 sources: SourceA = 6000/mo, SourceB = 4000/mo (total 10,000/mo)
    # Months 2025-10 to 2026-09 (12 full months)
    # Expenses: 6000/mo
    records = []
    end_date = _dt.date(2026, 9, 30)

    for m in range(1, 13):
        # 2025-10 to 2026-09
        yr = 2025 if m <= 3 else 2026
        mo = (9 + m) if m <= 3 else (m - 3)
        dt_str = f"{yr:04d}-{mo:02d}-10"
        records.append({
            "transaction_id": f"tx_{m}_1",
            "applicant_id": "test_app",
            "date": dt_str,
            "amount": 6000.0,
            "type": "credit",
            "category": "income",
            "source": "SourceA",
            "description": "Payout A",
            "balance": None,
        })
        records.append({
            "transaction_id": f"tx_{m}_2",
            "applicant_id": "test_app",
            "date": dt_str,
            "amount": 4000.0,
            "type": "credit",
            "category": "income",
            "source": "SourceB",
            "description": "Payout B",
            "balance": None,
        })
        records.append({
            "transaction_id": f"tx_{m}_3",
            "applicant_id": "test_app",
            "date": dt_str,
            "amount": 6000.0,
            "type": "debit",
            "category": "expense",
            "source": "Store",
            "description": "Monthly expenses",
            "balance": None,
        })

    df = pd.DataFrame(records)
    payload = extract_features(df, "test_app", end_date=end_date)

    f = payload.features
    # active_months: 12/12 = 1.0
    assert f.active_months_ratio == 1.0
    # monthly income is constant (10,000 every month), cv must be 0.0
    assert f.income_cv == 0.0

    # Source diversity: 2 sources. ShareA = 0.6, ShareB = 0.4
    # HHI = 0.6^2 + 0.4^2 = 0.36 + 0.16 = 0.52
    # raw_diversity = 1 - 0.52 = 0.48
    # max_possible_diversity = 1 - 1/2 = 0.50
    # normalized = 0.48 / 0.50 = 0.96
    assert pytest.approx(f.source_diversity, 0.001) == 0.96

    # positive cashflow months: 12/12 = 1.0
    assert f.positive_cashflow_months_ratio == 1.0
    # expense to income: (12 * 6000) / (12 * 10000) = 0.60
    assert pytest.approx(f.expense_to_income_ratio, 0.001) == 0.60
    # trend: flat income -> 0.0
    assert f.income_trend == 0.0
    # emergency buffer days: no balance info -> None
    assert f.emergency_buffer_days is None


def test_single_source_returns_zero_diversity():
    records = [
        {
            "transaction_id": "tx_1",
            "applicant_id": "app_single",
            "date": "2026-05-01",
            "amount": 15000.0,
            "type": "credit",
            "category": "income",
            "source": "Uber",
            "description": "Earnings",
            "balance": None,
        }
    ]
    df = pd.DataFrame(records)
    payload = extract_features(df, "app_single")
    assert payload.features.source_diversity == 0.0


def test_transfers_and_refunds_excluded_from_earnings():
    records = [
        # Transfer
        {
            "transaction_id": "tx_1",
            "applicant_id": "app_transfer",
            "date": "2026-05-01",
            "amount": 50000.0,
            "type": "credit",
            "category": "transfer",
            "source": "Self",
            "description": "Self bank transfer",
            "balance": None,
        },
        # Refund
        {
            "transaction_id": "tx_2",
            "applicant_id": "app_transfer",
            "date": "2026-05-02",
            "amount": 5000.0,
            "type": "credit",
            "category": "refund",
            "source": "Store",
            "description": "Product return refund",
            "balance": None,
        },
        # Actual income
        {
            "transaction_id": "tx_3",
            "applicant_id": "app_transfer",
            "date": "2026-05-03",
            "amount": 10000.0,
            "type": "credit",
            "category": "income",
            "source": "Swiggy",
            "description": "Delivery payout",
            "balance": None,
        },
    ]
    df = pd.DataFrame(records)
    payload = extract_features(df, "app_transfer")
    # Only 1 month has earned income (the 10,000 from Swiggy)
    assert payload.features.active_months_ratio == round(1.0 / 12, 4)
    # Single earned income source (Swiggy) -> diversity is 0.0
    assert payload.features.source_diversity == 0.0


def test_sparse_records_and_missing_months():
    # Only 1 transaction total
    records = [
        {
            "transaction_id": "tx_1",
            "applicant_id": "app_sparse",
            "date": "2026-08-01",
            "amount": 2000.0,
            "type": "credit",
            "category": "income",
            "source": "Local-Gigs",
            "description": "One-off job",
            "balance": None,
        }
    ]
    df = pd.DataFrame(records)
    payload = extract_features(df, "app_sparse")
    assert payload.data_quality.coverage_months == 1
    assert payload.data_quality.missing_months == 11
    # Low confidence due to sparse data
    assert payload.data_quality.confidence < 0.40


def test_three_personas_features_extraction():
    raw_dir = Path("data/raw")
    results = {}

    for persona in ["demo-stable-001", "demo-volatile-002", "demo-seasonal-003"]:
        csv_path = raw_dir / f"{persona}.csv"
        df_clean, audit = load_and_clean_csv(csv_path)
        payload = extract_features(df_clean, persona)

        assert isinstance(payload, Member1FeaturePayload)
        assert payload.applicant_id == persona
        assert payload.analysis_period_months == 12

        # Dump and check contract adherence
        f = payload.features
        assert 0.0 <= f.active_months_ratio <= 1.0
        assert f.income_cv >= 0.0
        assert 0.0 <= f.source_diversity <= 1.0
        assert 0.0 <= f.positive_cashflow_months_ratio <= 1.0
        assert f.expense_to_income_ratio >= 0.0
        assert f.emergency_buffer_days is None

        # Data quality checks
        dq = payload.data_quality
        assert dq.coverage_months + dq.missing_months == 12
        assert 0.0 <= dq.confidence <= 1.0

        results[persona] = payload

    # Persona differentiation checks:
    # 1. Stable persona has higher active_months_ratio and lower income_cv than volatile persona
    assert results["demo-stable-001"].features.active_months_ratio > results["demo-volatile-002"].features.active_months_ratio
    assert results["demo-stable-001"].features.income_cv < results["demo-volatile-002"].features.income_cv

    # 2. Stable persona has high confidence due to 12 months full tenure
    assert results["demo-stable-001"].data_quality.confidence > results["demo-volatile-002"].data_quality.confidence

