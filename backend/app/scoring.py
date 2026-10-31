
from decimal import Decimal, ROUND_HALF_UP

WEIGHTS = {
    "active_months_ratio": 0.25,
    "income_cv": 0.20,
    "positive_cashflow_months_ratio": 0.20,
    "expense_to_income_ratio": 0.15,
    "income_trend": 0.10,
    "emergency_buffer_days": 0.05,
    "source_diversity": 0.05,
}

LABELS = {
    "active_months_ratio": "Income consistency",
    "income_cv": "Income stability",
    "positive_cashflow_months_ratio": "Positive cash-flow months",
    "expense_to_income_ratio": "Expense management",
    "income_trend": "Income growth trend",
    "emergency_buffer_days": "Emergency savings buffer",
    "source_diversity": "Income source diversity",
}


def clamp(value):
    return max(0.0, min(1.0, float(value)))


def round_points(value):
    return int(
        Decimal(str(value)).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
    )


def calculate_score(features: dict) -> dict:
    normalized = {
        "active_months_ratio": clamp(features["active_months_ratio"]),
        "income_cv": clamp(1 - features["income_cv"]),
        "positive_cashflow_months_ratio": clamp(
            features["positive_cashflow_months_ratio"]
        ),
        "expense_to_income_ratio": clamp(
            1 - features["expense_to_income_ratio"]
        ),
        "income_trend": clamp(features["income_trend"] + 0.5),
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

    total_weight = sum(WEIGHTS[key] for key in available)

    if total_weight <= 0:
        raise ValueError("No financial features available")

    # Allocate the 600 variable points across available factors.
    raw_points = {
        key: 600 * WEIGHTS[key] * value / total_weight
        for key, value in available.items()
    }

    variable_points = round_points(sum(raw_points.values()))

    # Largest-remainder allocation keeps factor points consistent.
    points = {
        key: int(value)
        for key, value in raw_points.items()
    }
    remaining = variable_points - sum(points.values())

    ranked = sorted(
        raw_points,
        key=lambda key: (
            -(raw_points[key] - points[key]),
            key,
        ),
    )

    for key in ranked[:remaining]:
        points[key] += 1

    score = 300 + sum(points.values())

    if score >= 750:
        band = "Strong"
    elif score >= 600:
        band = "Moderate"
    else:
        band = "Needs Review"

    factors = []
    for key, value in available.items():
        maximum = 600 * WEIGHTS[key] / total_weight

        factors.append({
            "key": key,
            "label": LABELS[key],
            "points": points[key],
            "max_points": round_points(maximum),
            "explanation": (
                f"{LABELS[key]} contributed {points[key]} "
                f"points based on the available financial data."
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

    # Confidence currently measures feature completeness only.
    confidence = round(total_weight, 2)

    return {
        "score": score,
        "band": band,
        "confidence": confidence,
        "factors": factors,
        "risk_flags": risk_flags,
        "disclaimer": "Decision-support output requiring human review.",
    }
