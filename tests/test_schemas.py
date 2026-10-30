"""Tests for Member 1 data pipeline schemas."""

import pytest
from datetime import date
from pydantic import ValidationError

from src.data_pipeline.schemas import (
    NormalizedTransaction,
    TransactionType,
    TransactionCategory,
    FinancialFeatures,
    DataQualitySummary,
    Member1FeaturePayload,
)


def test_normalized_transaction_valid():
    tx = NormalizedTransaction(
        transaction_id="tx_001",
        applicant_id="demo-stable-001",
        date=date(2026, 3, 15),
        amount=250.50,
        type=TransactionType.CREDIT,
        category=TransactionCategory.INCOME,
        source="Uber",
        description="Weekly trip earnings payout",
        balance=1420.00,
    )
    assert tx.transaction_id == "tx_001"
    assert tx.amount == 250.50
    assert tx.type == TransactionType.CREDIT
    assert tx.category == TransactionCategory.INCOME
    assert tx.balance == 1420.00


def test_normalized_transaction_enforces_positive_amount():
    # Negative amounts must be rejected; type must indicate debit/credit
    with pytest.raises(ValidationError):
        NormalizedTransaction(
            transaction_id="tx_002",
            applicant_id="demo-stable-001",
            date="2026-03-16",
            amount=-50.00,
            type=TransactionType.DEBIT,
            category=TransactionCategory.EXPENSE,
            source="Fuel",
            description="Gas station debit",
        )

    # Zero magnitude must also be rejected
    with pytest.raises(ValidationError):
        NormalizedTransaction(
            transaction_id="tx_003",
            applicant_id="demo-stable-001",
            date="2026-03-16",
            amount=0.0,
            type=TransactionType.DEBIT,
            category=TransactionCategory.EXPENSE,
            source="Fuel",
            description="Zero fee entry",
        )


def test_financial_features_schema_exact_seven_keys():
    features_data = {
        "active_months_ratio": 0.92,
        "income_cv": 0.21,
        "source_diversity": 0.68,
        "positive_cashflow_months_ratio": 0.83,
        "expense_to_income_ratio": 0.62,
        "income_trend": 0.08,
        "emergency_buffer_days": 18.0,
    }
    features = FinancialFeatures(**features_data)
    dumped = features.model_dump()
    assert set(dumped.keys()) == {
        "active_months_ratio",
        "income_cv",
        "source_diversity",
        "positive_cashflow_months_ratio",
        "expense_to_income_ratio",
        "income_trend",
        "emergency_buffer_days",
    }


def test_financial_features_emergency_buffer_can_be_null_when_unavailable():
    # If reliable balance data is absent, emergency_buffer_days must accept None/null
    features_data = {
        "active_months_ratio": 0.85,
        "income_cv": 0.35,
        "source_diversity": 0.50,
        "positive_cashflow_months_ratio": 0.75,
        "expense_to_income_ratio": 0.70,
        "income_trend": -0.02,
        "emergency_buffer_days": None,
    }
    features = FinancialFeatures(**features_data)
    assert features.emergency_buffer_days is None


def test_financial_features_range_validations():
    # active_months_ratio cannot exceed 1.0
    with pytest.raises(ValidationError):
        FinancialFeatures(
            active_months_ratio=1.5,
            income_cv=0.2,
            source_diversity=0.5,
            positive_cashflow_months_ratio=0.8,
            expense_to_income_ratio=0.6,
            income_trend=0.1,
            emergency_buffer_days=10.0,
        )


def test_member1_feature_payload_matches_shared_contract():
    payload_data = {
        "applicant_id": "demo-stable-001",
        "analysis_period_months": 12,
        "features": {
            "active_months_ratio": 0.92,
            "income_cv": 0.21,
            "source_diversity": 0.68,
            "positive_cashflow_months_ratio": 0.83,
            "expense_to_income_ratio": 0.62,
            "income_trend": 0.08,
            "emergency_buffer_days": 18,
        },
        "data_quality": {
            "coverage_months": 12,
            "missing_months": 1,
            "total_transactions": 250,
            "unclassified_ratio": 0.02,
            "confidence": 0.91,
        },
    }
    payload = Member1FeaturePayload(**payload_data)
    assert payload.applicant_id == "demo-stable-001"
    assert payload.analysis_period_months == 12
    assert payload.features.emergency_buffer_days == 18.0
    assert payload.data_quality is not None
    assert payload.data_quality.confidence == 0.91

    # Verify optional data_quality can be omitted without breaking contract
    payload_without_dq = Member1FeaturePayload(
        applicant_id="demo-volatile-002",
        analysis_period_months=6,
        features=payload_data["features"],
    )
    assert payload_without_dq.data_quality is None

