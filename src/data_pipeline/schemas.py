"""Data contracts and schemas for EarnScore Data Pipeline.

Shared contracts comply with docs/HACKATHON_PLAN.md:
- Amount convention: Amounts are strictly positive decimal magnitudes with an explicit
  credit/debit type.
- Emergency buffer: `emergency_buffer_days` is Optional[float] (null) if reliable
  running/ending balance records are unavailable, preventing fabrication of financial buffer data.
- Feature set: exactly 7 keys under `features` matching Member 2's scoring input.
- Data quality: defined as a separate optional object at root level to avoid breaking the 7-feature contract.
"""

import datetime as _dt
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TransactionType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"


class TransactionCategory(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    REFUND = "refund"


class NormalizedTransaction(BaseModel):
    """Normalized schema for single financial transactions.
    
    Convention:
    - `amount` must be a positive decimal magnitude (> 0).
    - Cash-flow direction is explicitly indicated by `type` ('credit' or 'debit').
    - `balance` is optional; when present, it reflects observed account balance.
    """
    transaction_id: str = Field(..., min_length=1, description="Unique transaction identifier")
    applicant_id: str = Field(..., min_length=1, description="Applicant identifier")
    date: _dt.date = Field(..., description="Date of transaction in YYYY-MM-DD")
    amount: float = Field(..., gt=0, description="Positive decimal magnitude of transaction")
    type: TransactionType = Field(..., description="Direction: credit or debit")
    category: TransactionCategory = Field(..., description="Category: income, expense, transfer, or refund")
    source: str = Field(..., min_length=1, description="Source or platform (e.g., Uber, DoorDash, Bank)")
    description: str = Field(..., description="Raw narration/memo or description")
    balance: Optional[float] = Field(default=None, description="Optional observed account running balance")

    @field_validator("amount")
    @classmethod
    def validate_positive_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be a strictly positive magnitude (> 0). Direction is indicated by type.")
        return round(float(v), 2)


class FinancialFeatures(BaseModel):
    """The 7 exact features agreed upon in docs/HACKATHON_PLAN.md for Member 2 scoring."""
    active_months_ratio: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Ratio of months with observed earning activity (0.0 to 1.0)"
    )
    income_cv: float = Field(
        ...,
        ge=0.0,
        description="Coefficient of variation of monthly income (std_dev / mean)"
    )
    source_diversity: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Source diversification index (0.0 to 1.0)"
    )
    positive_cashflow_months_ratio: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Fraction of months where income exceeded expenses (0.0 to 1.0)"
    )
    expense_to_income_ratio: float = Field(
        ...,
        ge=0.0,
        description="Total expenses divided by total income over the analysis period"
    )
    income_trend: float = Field(
        ...,
        description="Income trend slope or rate of change over the period"
    )
    emergency_buffer_days: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Days of average daily expenses covered by observable buffer. None/null if reliable balance data is absent."
    )


class DataQualitySummary(BaseModel):
    """Optional data-quality assessment produced by Member 1."""
    coverage_months: int = Field(..., ge=0, description="Total months covered by transaction records")
    missing_months: int = Field(..., ge=0, description="Months with zero recorded transactions")
    total_transactions: int = Field(..., ge=0, description="Total number of processed transactions")
    unclassified_ratio: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Proportion of transactions with unknown or unclassified source"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall data quality confidence score based on record completeness and verification"
    )


class Member1FeaturePayload(BaseModel):
    """Output payload from Member 1 data pipeline for Member 2 scoring service.
    
    Top-level fields preserve the agreed contract:
    - applicant_id
    - analysis_period_months
    - features (exactly 7 financial feature keys)
    - data_quality (optional separate block for data integrity metadata)
    """
    applicant_id: str = Field(..., min_length=1, description="Applicant ID")
    analysis_period_months: int = Field(..., gt=0, description="Observation period in months (e.g. 12)")
    features: FinancialFeatures = Field(..., description="Agreed 7 financial features")
    data_quality: Optional[DataQualitySummary] = Field(
        default=None,
        description="Optional data quality audit metrics"
    )
