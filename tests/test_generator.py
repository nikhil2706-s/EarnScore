"""Deterministic validation tests for synthetic dataset generator."""

import csv
from datetime import date
from pathlib import Path
import pytest

from src.data_pipeline.generator import (
    GLOBAL_SEED,
    export_transactions_to_csv,
    generate_all_datasets,
    generate_seasonal_worker_transactions,
    generate_stable_worker_transactions,
    generate_volatile_worker_transactions,
)
from src.data_pipeline.schemas import NormalizedTransaction, TransactionType, TransactionCategory


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    return tmp_path / "data" / "raw"


def test_generator_reproducibility():
    """Ensure that identical seeds generate identical transaction lists byte-for-byte."""
    txs_run1 = generate_stable_worker_transactions(seed=42)
    txs_run2 = generate_stable_worker_transactions(seed=42)

    assert len(txs_run1) == len(txs_run2)
    for t1, t2 in zip(txs_run1, txs_run2):
        assert t1.model_dump() == t2.model_dump()


def test_all_three_personas_generated():
    """Verify all 3 distinct personas can be generated with appropriate properties."""
    stable = generate_stable_worker_transactions()
    volatile = generate_volatile_worker_transactions()
    seasonal = generate_seasonal_worker_transactions()

    assert len(stable) > 0
    assert len(volatile) > 0
    assert len(seasonal) > 0

    # Ensure applicant_ids match the personas
    assert all(tx.applicant_id == "demo-stable-001" for tx in stable)
    assert all(tx.applicant_id == "demo-volatile-002" for tx in volatile)
    assert all(tx.applicant_id == "demo-seasonal-003" for tx in seasonal)


def test_schema_compatibility_and_positive_amounts():
    """Ensure all generated records conform to NormalizedTransaction and amounts are positive."""
    personas = [
        generate_stable_worker_transactions(),
        generate_volatile_worker_transactions(),
        generate_seasonal_worker_transactions(),
    ]

    for tx_list in personas:
        for tx in tx_list:
            assert isinstance(tx, NormalizedTransaction)
            assert tx.amount > 0
            assert isinstance(tx.date, date)
            assert tx.type in (TransactionType.CREDIT, TransactionType.DEBIT)
            assert tx.category in (
                TransactionCategory.INCOME,
                TransactionCategory.EXPENSE,
                TransactionCategory.TRANSFER,
                TransactionCategory.REFUND,
            )
            assert len(tx.source.strip()) > 0
            assert len(tx.description.strip()) > 0
            # Balance is None unless explicitly modeled
            assert tx.balance is None


def test_transaction_id_uniqueness():
    """Ensure each generated transaction within a persona has a unique transaction_id."""
    personas = [
        generate_stable_worker_transactions(),
        generate_volatile_worker_transactions(),
        generate_seasonal_worker_transactions(),
    ]

    for tx_list in personas:
        ids = [tx.transaction_id for tx in tx_list]
        assert len(ids) == len(set(ids)), "Transaction IDs must be unique"


def test_csv_export_and_file_content(temp_output_dir: Path):
    """Test CSV generation into files and verify rows can be read back and validated."""
    counts = generate_all_datasets(temp_output_dir)

    for persona_id in ["demo-stable-001", "demo-volatile-002", "demo-seasonal-003"]:
        csv_file = temp_output_dir / f"{persona_id}.csv"
        assert csv_file.exists(), f"CSV file for {persona_id} should exist"

        with open(csv_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == counts[persona_id]
            for row in rows:
                assert row["applicant_id"] == persona_id
                assert float(row["amount"]) > 0
                assert row["type"] in ["credit", "debit"]
                assert row["category"] in ["income", "expense", "transfer", "refund"]
                assert row["balance"] == ""  # Empty string for unmodeled balance


def test_persona_financial_characteristics():
    """Verify characteristics of each persona match domain expectations."""
    stable = generate_stable_worker_transactions()
    volatile = generate_volatile_worker_transactions()
    seasonal = generate_seasonal_worker_transactions()

    # Stable worker has multi-source weekly income across 12 months
    stable_income = [t for t in stable if t.type == TransactionType.CREDIT]
    stable_sources = set(t.source for t in stable_income)
    assert len(stable_sources) >= 2  # At least UrbanCompany and Swiggy

    # Volatile worker has shorter observation history (5 months) and large erratic gigs
    volatile_dates = [t.date for t in volatile]
    volatile_months = set((d.year, d.month) for d in volatile_dates)
    assert len(volatile_months) <= 5

    # Seasonal worker has high earnings during peak months (Oct-Feb)
    seasonal_peak_income = sum(
        t.amount for t in seasonal
        if t.type == TransactionType.CREDIT and t.date.month in [10, 11, 12, 1, 2]
    )
    seasonal_offpeak_income = sum(
        t.amount for t in seasonal
        if t.type == TransactionType.CREDIT and t.date.month in [3, 4, 5, 6, 7, 8, 9]
    )
    assert seasonal_peak_income > seasonal_offpeak_income

