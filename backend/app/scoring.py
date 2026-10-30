
from typing import Optional


def calculate_score(features: dict) -> dict:
    """Calculate an explainable alternative credit score."""

    weights = {
        "active_months_ratio": 0.25,
        "income_cv": 0.20,
        "positive_cashflow_months_ratio": 0.20,
        "expense_to_income_ratio": 0.15,
        "income_trend": 0.10,
        "emergency_buffer_days": 0.05,
        "source_diversity": 0.05,
    }

    def clamp(value, low=0.0, high=1.0):
        return max(low, min(high, value))

    normalized = {
        "active_months_ratio": clamp(features["active_months_ratio"]),
        "income_cv": clamp(1 - features["income_cv"]),
        "positive_cashflow_months_ratio": clamp(
            features["positive_cashflow_months_ratio"]
        ),
        "expense_to_income_ratio": clamp(
            1 - features["expense_to_income_ratio"]
        ),
        "income_trend": clamp(
            (features["income_trend"] + 0.5) / 1.0
        ),
        "emergency_buffer_days": (
            clamp(features["emergency_buffer_days"] / 90)
            if features.get("emergency_buffer_days") is not None
            else None
        ),
        "source_diversity": clamp(features["source_diversity"]),
    }

    available = {
        key: value
        for key, value in normalized.items()
        if value is not None
    }

    total_weight = sum(weights[key] for key in available)

    weighted_score = sum(
        weights[key] * value
        for key, value in available.items()
    ) / total_weight

    score = round(300 + 600 * weighted_score)

    if score >= 750:
        band = "Strong"
    elif score >= 600:
        band = "Moderate"
    else:
        band = "Needs Review"

    factors = []

    for key, value in available.items():
        max_points = round(600 * weights[key])
        points = round(600 * weights[key] * value / total_weight)

        factors.append({
            "key": key,
            "label": key.replace("_", " ").title(),
            "points": points,
            "max_points": max_points,
            "explanation": (
                f"Normalized contribution: {value:.2f}"
            ),
            "evidence": {key: features[key]},
        })

    risk_flags = []

    if features["income_cv"] > 0.5:
        risk_flags.append("High income volatility")

    if features["expense_to_income_ratio"] > 0.85:
        risk_flags.append("High expense-to-income ratio")

    if features["active_months_ratio"] < 0.5:
        risk_flags.append("Irregular income activity")

    if features.get("emergency_buffer_days") is None:
        risk_flags.append("Emergency buffer data unavailable")

    confidence = round(
        sum(weights[key] for key in available), 2
    )

    return {
        "score": score,
        "band": band,
        "confidence": confidence,
        "factors": factors,
        "risk_flags": risk_flags,
        "disclaimer": "Decision-support output requiring human review.",
    }
