"""Tests for cleaner and classifier modules."""

import io
from pathlib import Path
import pandas as pd
import pytest

from src.data_pipeline.classifier import classify_category, identify_source, is_earned_income
from src.data_pipeline.cleaner import CleaningAudit, clean_and_normalize_transactions, load_and_clean_csv
from src.data_pipeline.schemas import TransactionCategory, TransactionType


def test_identify_known_and_unknown_sources():
    # Known sources
    assert identify_source("Urban Company", "weekly settlement") == "UrbanCompany"
    assert identify_source("swiggy", "delivery payout") == "Swiggy"
    assert identify_source("Upwork Global", "milestone") == "Upwork"
    assert identify_source("fiverr", "order payment") == "Fiverr"
    assert identify_source("direct client", "invoice payment") == "Direct-Client"

    # Unknown sources: must return 'Unknown' or cleaned name, never invent
    assert identify_source("Unknown", "Random deposit") == "Unknown"
    assert identify_source("", "") == "Unknown"
    assert identify_source(None, None) == "Unknown"


def test_classify_category_rules():
    # Internal transfers must be categorized as TRANSFER and not income
    cat_transfer = classify_category(
        tx_type=TransactionType.CREDIT,
        category_raw=None,
        source="HDFC",
        description="Self transfer from savings",
    )
    assert cat_transfer == TransactionCategory.TRANSFER
    assert not is_earned_income(TransactionType.CREDIT, cat_transfer)

    # Refunds/reversals must be categorized as REFUND and not income
    cat_refund = classify_category(
        tx_type=TransactionType.CREDIT,
        category_raw=None,
        source="Merchant",
        description="Amazon order refund reversal",
    )
    assert cat_refund == TransactionCategory.REFUND
    assert not is_earned_income(TransactionType.CREDIT, cat_refund)

    # Legitimate gig earning is INCOME
    cat_income = classify_category(
        tx_type=TransactionType.CREDIT,
        category_raw="income",
        source="Swiggy",
        description="Weekly delivery earnings",
    )
    assert cat_income == TransactionCategory.INCOME
    assert is_earned_income(TransactionType.CREDIT, cat_income)


def test_cleaner_handles_valid_records():
    raw_data = """transaction_id,applicant_id,date,amount,type,category,source,description,balance
tx_1,app_1,2026-03-01,5000.0,credit,income,UrbanCompany,Partner payout,12000.0
tx_2,app_1,2026-03-02,450.0,debit,expense,Groceries,Kirana store,
"""
    df_raw = pd.read_csv(io.StringIO(raw_data))
    df_clean, audit = clean_and_normalize_transactions(df_raw)

    assert audit.valid_normalized_rows == 2
    assert audit.exact_duplicates_removed == 0
    assert len(audit.conflicting_duplicate_ids) == 0
    assert len(df_clean) == 2
    assert df_clean.iloc[0]["source"] == "UrbanCompany"
    assert df_clean.iloc[0]["balance"] == 12000.0
    assert pd.isna(df_clean.iloc[1]["balance"]) or df_clean.iloc[1]["balance"] is None


def test_cleaner_removes_exact_duplicates():
    raw_data = """transaction_id,applicant_id,date,amount,type,category,source,description,balance
tx_1,app_1,2026-03-01,5000.0,credit,income,UrbanCompany,Payout,
tx_1,app_1,2026-03-01,5000.0,credit,income,UrbanCompany,Payout,
"""
    df_raw = pd.read_csv(io.StringIO(raw_data))
    df_clean, audit = clean_and_normalize_transactions(df_raw)

    assert audit.exact_duplicates_removed == 1
    assert audit.valid_normalized_rows == 1
    assert len(df_clean) == 1


def test_cleaner_flags_conflicting_duplicate_ids():
    # Same ID, different amounts -> conflict! Must not silently pick one
    raw_data = """transaction_id,applicant_id,date,amount,type,category,source,description,balance
tx_1,app_1,2026-03-01,5000.0,credit,income,UrbanCompany,Payout,
tx_1,app_1,2026-03-01,6500.0,credit,income,UrbanCompany,Modified payout,
tx_2,app_1,2026-03-02,300.0,debit,expense,Fuel,Petrol,
"""
    df_raw = pd.read_csv(io.StringIO(raw_data))
    df_clean, audit = clean_and_normalize_transactions(df_raw)

    assert audit.has_conflicts
    assert "tx_1" in audit.conflicting_duplicate_ids
    # The conflicting rows are quarantined, leaving only tx_2 valid
    assert audit.valid_normalized_rows == 1
    assert df_clean.iloc[0]["transaction_id"] == "tx_2"


def test_cleaner_flags_invalid_rows():
    raw_data = """transaction_id,applicant_id,date,amount,type,category,source,description,balance
tx_valid,app_1,2026-03-01,1000.0,credit,income,Swiggy,Valid payout,
tx_neg,app_1,2026-03-01,-500.0,debit,expense,Store,Negative amount,
tx_zero,app_1,2026-03-01,0.0,credit,income,Swiggy,Zero amount,
tx_bad_date,app_1,invalid-date,200.0,debit,expense,Store,Bad date,
tx_bad_type,app_1,2026-03-02,200.0,invalid_type,expense,Store,Bad type,
,app_1,2026-03-02,200.0,debit,expense,Store,Missing ID,
"""
    df_raw = pd.read_csv(io.StringIO(raw_data))
    df_clean, audit = clean_and_normalize_transactions(df_raw)

    assert audit.valid_normalized_rows == 1
    assert len(audit.invalid_rows_flagged) == 5
    assert df_clean.iloc[0]["transaction_id"] == "tx_valid"


def test_cleaner_on_simulated_persona_csvs():
    raw_dir = Path("data/raw")
    for persona in ["demo-stable-001", "demo-volatile-002", "demo-seasonal-003"]:
        csv_path = raw_dir / f"{persona}.csv"
        df_clean, audit = load_and_clean_csv(csv_path)

        assert not audit.has_conflicts
        assert len(audit.invalid_rows_flagged) == 0
        assert audit.valid_normalized_rows > 0
        assert len(df_clean) == audit.valid_normalized_rows

