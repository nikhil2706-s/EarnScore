"""Data cleaning and transaction normalization pipeline for EarnScore.

Guardrails:
- Does NOT silently drop conflicting records: flags conflicting transaction IDs in audit.
- Does NOT invent or impute missing transaction values.
- Removes exact duplicates safely while tracking them in the audit summary.
- Enforces strictly positive amounts with direction stored in `type`.
- Tracks invalid rows and anomalies transparently.
"""

from dataclasses import dataclass, field
import datetime as _dt
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import pandas as pd

from src.data_pipeline.classifier import classify_category, identify_source, is_earned_income
from src.data_pipeline.schemas import (
    NormalizedTransaction,
    TransactionCategory,
    TransactionType,
)


@dataclass
class CleaningAudit:
    """Audit report produced during the cleaning process."""
    total_raw_rows: int = 0
    valid_normalized_rows: int = 0
    exact_duplicates_removed: int = 0
    conflicting_duplicate_ids: List[str] = field(default_factory=list)
    invalid_rows_flagged: List[Dict[str, Any]] = field(default_factory=list)
    refund_reversal_count: int = 0
    internal_transfer_count: int = 0
    unknown_source_count: int = 0

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicting_duplicate_ids) > 0


def clean_and_normalize_transactions(
    df_raw: pd.DataFrame,
    default_applicant_id: Optional[str] = None,
) -> Tuple[pd.DataFrame, CleaningAudit]:
    """Cleans and normalizes raw transaction dataframe into validated schema.
    
    Returns:
    - cleaned_df: pandas DataFrame containing valid normalized records.
    - audit: CleaningAudit object with detailed issue counts and flags.
    """
    audit = CleaningAudit()
    audit.total_raw_rows = len(df_raw)

    if df_raw.empty:
        return pd.DataFrame(), audit

    # Ensure required columns are present (case-insensitive strip)
    df = df_raw.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Check for exact duplicate rows (across all columns)
    exact_dup_mask = df.duplicated(keep="first")
    audit.exact_duplicates_removed = int(exact_dup_mask.sum())
    df = df[~exact_dup_mask].copy()

    # Check for conflicting duplicate transaction_ids
    # (same transaction_id with different values)
    if "transaction_id" in df.columns:
        # Check non-null transaction IDs
        id_series = df["transaction_id"].dropna().astype(str).str.strip()
        df["_tx_id_cleaned"] = id_series
        duplicate_ids = df[df["_tx_id_cleaned"].duplicated(keep=False)]["_tx_id_cleaned"].unique().tolist()
        if duplicate_ids:
            audit.conflicting_duplicate_ids = duplicate_ids
            # Flag conflicting rows and exclude them from normalized output so we don't pick one silently
            conflict_mask = df["_tx_id_cleaned"].isin(duplicate_ids)
            for idx, row in df[conflict_mask].iterrows():
                audit.invalid_rows_flagged.append({
                    "row_index": idx,
                    "reason": f"Conflicting duplicate transaction_id: {row['_tx_id_cleaned']}",
                    "raw_data": row.to_dict(),
                })
            df = df[~conflict_mask].copy()
        df.drop(columns=["_tx_id_cleaned"], inplace=True, errors="ignore")

    normalized_records: List[Dict[str, Any]] = []

    for idx, row in df.iterrows():
        # 1. Transaction ID
        tx_id = str(row.get("transaction_id", "")).strip()
        if not tx_id or tx_id.lower() in ["nan", "none", ""]:
            audit.invalid_rows_flagged.append({
                "row_index": idx,
                "reason": "Missing transaction_id",
                "raw_data": row.to_dict(),
            })
            continue

        # 2. Applicant ID
        app_id = str(row.get("applicant_id", default_applicant_id or "")).strip()
        if not app_id or app_id.lower() in ["nan", "none", ""]:
            audit.invalid_rows_flagged.append({
                "row_index": idx,
                "reason": "Missing applicant_id",
                "raw_data": row.to_dict(),
            })
            continue

        # 3. Date parsing
        date_raw = row.get("date", None)
        parsed_date: Optional[_dt.date] = None
        if pd.notna(date_raw):
            try:
                parsed_date = pd.to_datetime(date_raw).date()
            except Exception:
                parsed_date = None

        if not parsed_date:
            audit.invalid_rows_flagged.append({
                "row_index": idx,
                "reason": f"Invalid or missing date: {date_raw}",
                "raw_data": row.to_dict(),
            })
            continue

        # 4. Amount parsing and positive validation
        amount_raw = row.get("amount", None)
        try:
            amount_val = float(amount_raw)
            if amount_val <= 0 or pd.isna(amount_val):
                raise ValueError("Amount must be positive non-zero magnitude")
            amount_val = round(amount_val, 2)
        except Exception:
            audit.invalid_rows_flagged.append({
                "row_index": idx,
                "reason": f"Invalid or non-positive amount: {amount_raw}",
                "raw_data": row.to_dict(),
            })
            continue

        # 5. Type validation (credit / debit)
        type_raw = str(row.get("type", "")).strip().lower()
        if type_raw not in [TransactionType.CREDIT.value, TransactionType.DEBIT.value]:
            audit.invalid_rows_flagged.append({
                "row_index": idx,
                "reason": f"Invalid transaction type: {type_raw} (expected 'credit' or 'debit')",
                "raw_data": row.to_dict(),
            })
            continue
        tx_type = TransactionType(type_raw)

        # 6. Description & Source normalization
        desc = str(row.get("description", "")).strip()
        if desc.lower() in ["nan", "none"]:
            desc = ""
        source_raw = str(row.get("source", "")).strip()
        identified_source = identify_source(source_raw, desc)
        if identified_source == "Unknown":
            audit.unknown_source_count += 1

        # 7. Category classification
        cat_raw = str(row.get("category", "")).strip().lower()
        classified_cat = classify_category(
            tx_type=tx_type,
            category_raw=cat_raw,
            source=identified_source,
            description=desc,
        )

        if classified_cat == TransactionCategory.REFUND:
            audit.refund_reversal_count += 1
        elif classified_cat == TransactionCategory.TRANSFER:
            audit.internal_transfer_count += 1

        # 8. Balance
        balance_raw = row.get("balance", None)
        balance_val: Optional[float] = None
        if pd.notna(balance_raw) and str(balance_raw).strip() != "":
            try:
                balance_val = round(float(balance_raw), 2)
            except Exception:
                balance_val = None

        normalized_records.append({
            "transaction_id": tx_id,
            "applicant_id": app_id,
            "date": parsed_date.isoformat(),
            "amount": amount_val,
            "type": tx_type.value,
            "category": classified_cat.value,
            "source": identified_source,
            "description": desc,
            "balance": balance_val,
        })

    audit.valid_normalized_rows = len(normalized_records)

    cleaned_df = pd.DataFrame(normalized_records)
    if not cleaned_df.empty:
        # Sort by date ascending
        cleaned_df.sort_values(by=["date", "transaction_id"], inplace=True)
        cleaned_df.reset_index(drop=True, inplace=True)

    return cleaned_df, audit


def load_and_clean_csv(
    file_path: Union[str, Path],
    default_applicant_id: Optional[str] = None,
) -> Tuple[pd.DataFrame, CleaningAudit]:
    """Loads a transaction CSV file from disk and normalizes it."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Transaction file not found: {path}")

    df_raw = pd.read_csv(path)
    return clean_and_normalize_transactions(df_raw, default_applicant_id=default_applicant_id)

