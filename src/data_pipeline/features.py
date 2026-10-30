"""Financial feature extraction and monthly aggregation for EarnScore.

Features calculated (strictly complying with the 7-key contract):
1. active_months_ratio = active_months_with_earned_income / 12
2. income_cv = std_dev(monthly_earned_income) / mean(monthly_earned_income)
   Convention: Evaluated across the observed history span (from applicant's first observed month
   to analysis window end). Any months within this active tenure that had zero income count as 0.0.
   Prior unobserved calendar months before account tenure are not imputed as zero.
3. source_diversity = (1 - sum(s_i^2)) / (1 - 1/K) where K is the count of distinct earned income
   sources (K >= 2). Returns 0.0 if K <= 1.
4. positive_cashflow_months_ratio = positive_cashflow_months / observed_months
5. expense_to_income_ratio = total_eligible_expenses / total_earned_income
6. income_trend = (later_half_avg_income - earlier_half_avg_income) / earlier_half_avg_income
   (clamped to reasonable range or 0.0 if earlier_half_avg_income == 0).
7. emergency_buffer_days = null (None) unless reliable running balance is present.

Data Quality:
- coverage_months: Count of months within analysis window with observed transactions
- missing_months: 12 - coverage_months
- total_transactions: Total valid transaction count
- unclassified_ratio: Transactions with source == 'Unknown' / total_transactions
- confidence: Deterministic evidence completeness metric (0.0 to 1.0)
"""

import datetime as _dt
import math
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.data_pipeline.classifier import is_earned_income
from src.data_pipeline.schemas import (
    DataQualitySummary,
    FinancialFeatures,
    Member1FeaturePayload,
    TransactionCategory,
    TransactionType,
)


# Fixed 12-month analysis window ending September 2026
DEFAULT_ANALYSIS_END = _dt.date(2026, 9, 30)
ANALYSIS_PERIOD_MONTHS = 12


def _get_12_month_periods(end_date: _dt.date) -> List[Tuple[int, int]]:
    """Returns list of (year, month) tuples for the 12-month window ending at end_date."""
    periods = []
    curr_year = end_date.year
    curr_month = end_date.month

    for _ in range(ANALYSIS_PERIOD_MONTHS):
        periods.append((curr_year, curr_month))
        curr_month -= 1
        if curr_month == 0:
            curr_month = 12
            curr_year -= 1

    periods.reverse()
    return periods


def extract_features(
    df_clean: pd.DataFrame,
    applicant_id: str,
    end_date: _dt.date = DEFAULT_ANALYSIS_END,
    analysis_period_months: int = ANALYSIS_PERIOD_MONTHS,
) -> Member1FeaturePayload:
    """Aggregates normalized transactions into monthly series and computes financial features."""
    periods_12 = _get_12_month_periods(end_date)
    period_keys = [f"{y:04d}-{m:02d}" for y, m in periods_12]
    min_date = _dt.date(periods_12[0][0], periods_12[0][1], 1)

    # Filter dataframe to the applicant and 12-month analysis window
    if df_clean.empty:
        df_app = pd.DataFrame()
    else:
        df = df_clean.copy()
        df["date_parsed"] = pd.to_datetime(df["date"]).dt.date
        df["month_key"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m")
        df_app = df[
            (df["applicant_id"] == applicant_id)
            & (df["date_parsed"] >= min_date)
            & (df["date_parsed"] <= end_date)
        ].copy()

    total_tx_count = len(df_app)

    # If completely empty dataset
    if df_app.empty:
        features = FinancialFeatures(
            active_months_ratio=0.0,
            income_cv=0.0,
            source_diversity=0.0,
            positive_cashflow_months_ratio=0.0,
            expense_to_income_ratio=0.0,
            income_trend=0.0,
            emergency_buffer_days=None,
        )
        data_quality = DataQualitySummary(
            coverage_months=0,
            missing_months=analysis_period_months,
            total_transactions=0,
            unclassified_ratio=0.0,
            confidence=0.0,
        )
        return Member1FeaturePayload(
            applicant_id=applicant_id,
            analysis_period_months=analysis_period_months,
            features=features,
            data_quality=data_quality,
        )

    # Aggregate by month
    # Monthly earned income: strictly credit AND category == 'income'
    # Monthly eligible expenses: category == 'expense' (or debit not refund/transfer)
    monthly_stats = {pk: {"income": 0.0, "expense": 0.0, "sources": set(), "tx_count": 0} for pk in period_keys}
    source_totals: Dict[str, float] = {}

    for _, row in df_app.iterrows():
        m_key = row["month_key"]
        if m_key not in monthly_stats:
            continue

        tx_type = TransactionType(row["type"])
        tx_cat = TransactionCategory(row["category"])
        amt = float(row["amount"])
        src = str(row["source"])

        monthly_stats[m_key]["tx_count"] += 1

        # Earned income check
        if is_earned_income(tx_type, tx_cat):
            monthly_stats[m_key]["income"] += amt
            monthly_stats[m_key]["sources"].add(src)
            source_totals[src] = source_totals.get(src, 0.0) + amt

        # Eligible expense check
        if tx_cat == TransactionCategory.EXPENSE or (tx_type == TransactionType.DEBIT and tx_cat not in [TransactionCategory.REFUND, TransactionCategory.TRANSFER]):
            monthly_stats[m_key]["expense"] += amt

    # 1. Observed history tenure determination
    # Months with at least 1 recorded transaction
    observed_months = [pk for pk in period_keys if monthly_stats[pk]["tx_count"] > 0]
    coverage_months_count = len(observed_months)
    missing_months_count = analysis_period_months - coverage_months_count

    # Tenure range: from the first observed month to the last observed month (or end of window)
    if observed_months:
        first_observed_idx = period_keys.index(observed_months[0])
        # Tenure months includes all months from first observed onwards
        tenure_period_keys = period_keys[first_observed_idx:]
    else:
        tenure_period_keys = []

    # 2. active_months_ratio = months with verified earned income / 12
    active_earned_months = [pk for pk in period_keys if monthly_stats[pk]["income"] > 0]
    active_months_ratio = round(len(active_earned_months) / float(analysis_period_months), 4)

    # 3. income_cv = std_dev / mean of monthly earned income
    # Within observed history (tenure): months with zero income inside tenure count as 0.0
    tenure_incomes = [monthly_stats[pk]["income"] for pk in tenure_period_keys]
    if len(tenure_incomes) > 1:
        mean_income = float(np.mean(tenure_incomes))
        std_income = float(np.std(tenure_incomes, ddof=1))  # sample standard deviation
        income_cv = round(std_income / mean_income, 4) if mean_income > 0 else 0.0
    else:
        income_cv = 0.0

    # 4. source_diversity = normalized (1 - sum(s_i^2))
    # Normalized against number of distinct income sources K: (1 - sum(s_i^2)) / (1 - 1/K)
    # If K <= 1, returns 0.0
    total_earned_income = sum(source_totals.values())
    k_sources = len(source_totals)
    if k_sources >= 2 and total_earned_income > 0:
        shares = [inc / total_earned_income for inc in source_totals.values()]
        hhi = sum(s ** 2 for s in shares)
        # Max possible HHI is 1.0 (single source), min is 1/K (equal distribution)
        # Normalized diversity from 0 (concentrated) to 1 (perfectly diversified)
        raw_diversity = 1.0 - hhi
        max_possible_diversity = 1.0 - (1.0 / k_sources)
        source_diversity = round(raw_diversity / max_possible_diversity, 4)
    else:
        source_diversity = 0.0

    # 5. positive_cashflow_months_ratio = positive cashflow months / observed months
    positive_cf_months = sum(
        1 for pk in observed_months
        if monthly_stats[pk]["income"] > monthly_stats[pk]["expense"]
    )
    positive_cashflow_months_ratio = (
        round(positive_cf_months / float(coverage_months_count), 4)
        if coverage_months_count > 0
        else 0.0
    )

    # 6. expense_to_income_ratio = total expenses / total earned income
    total_eligible_expenses = sum(monthly_stats[pk]["expense"] for pk in period_keys)
    if total_earned_income > 0:
        expense_to_income_ratio = round(total_eligible_expenses / total_earned_income, 4)
    else:
        expense_to_income_ratio = 1.0 if total_eligible_expenses > 0 else 0.0

    # 7. income_trend = (later_half_avg - earlier_half_avg) / earlier_half_avg
    # Computed over sufficiently observed history (tenure)
    if len(tenure_incomes) >= 4:
        mid = len(tenure_incomes) // 2
        earlier_half = tenure_incomes[:mid]
        later_half = tenure_incomes[mid:]
        mean_earlier = float(np.mean(earlier_half))
        mean_later = float(np.mean(later_half))

        if mean_earlier > 0:
            trend = (mean_later - mean_earlier) / mean_earlier
            # Cap extreme trend values to [-1.0, 2.0] for model stability
            income_trend = round(max(-1.0, min(2.0, trend)), 4)
        else:
            income_trend = 1.0 if mean_later > 0 else 0.0
    else:
        # History too short to establish meaningful trend
        income_trend = 0.0

    # 8. emergency_buffer_days: null unless reliable balance exists across records
    # Check if df_app has non-null, valid balances
    has_balance = False
    if "balance" in df_app.columns:
        valid_balances = df_app["balance"].dropna()
        if len(valid_balances) > 0 and len(valid_balances) >= total_tx_count * 0.8:
            has_balance = True

    if has_balance:
        ending_balance = float(df_app["balance"].dropna().iloc[-1])
        daily_expense = (total_eligible_expenses / (coverage_months_count * 30.4)) if coverage_months_count > 0 else 0
        emergency_buffer_days = round(ending_balance / daily_expense, 1) if daily_expense > 0 else None
    else:
        emergency_buffer_days = None

    # Data Quality & Deterministic Evidence Confidence
    # Unclassified ratio:
    unknown_tx_count = sum(1 for _, r in df_app.iterrows() if str(r.get("source", "")).strip().lower() in ["unknown", ""])
    unclassified_ratio = round(unknown_tx_count / float(total_tx_count), 4) if total_tx_count > 0 else 0.0

    # Deterministic confidence formula reflecting evidence completeness:
    # 1. Observation tenure factor: coverage_months / 12 (weight 0.40)
    # 2. Transaction density factor: min(1.0, total_tx_count / 100) (weight 0.30)
    # 3. Source classification cleanliness factor: (1 - unclassified_ratio) (weight 0.20)
    # 4. Income verification factor: active_months_ratio (weight 0.10)
    # Confidence strictly measures evidence completeness, not borrower credit quality.
    tenure_factor = coverage_months_count / float(analysis_period_months)
    density_factor = min(1.0, total_tx_count / 100.0)
    classification_factor = 1.0 - unclassified_ratio
    active_factor = active_months_ratio

    confidence_score = round(
        (0.40 * tenure_factor) +
        (0.30 * density_factor) +
        (0.20 * classification_factor) +
        (0.10 * active_factor),
        2
    )

    features = FinancialFeatures(
        active_months_ratio=active_months_ratio,
        income_cv=income_cv,
        source_diversity=source_diversity,
        positive_cashflow_months_ratio=positive_cashflow_months_ratio,
        expense_to_income_ratio=expense_to_income_ratio,
        income_trend=income_trend,
        emergency_buffer_days=emergency_buffer_days,
    )

    data_quality = DataQualitySummary(
        coverage_months=coverage_months_count,
        missing_months=missing_months_count,
        total_transactions=total_tx_count,
        unclassified_ratio=unclassified_ratio,
        confidence=confidence_score,
    )

    return Member1FeaturePayload(
        applicant_id=applicant_id,
        analysis_period_months=analysis_period_months,
        features=features,
        data_quality=data_quality,
    )

