
from backend.app.scoring import calculate_score


def sample_features():
    return {
        "active_months_ratio": 0.92,
        "income_cv": 0.21,
        "source_diversity": 0.68,
        "positive_cashflow_months_ratio": 0.83,
        "expense_to_income_ratio": 0.62,
        "income_trend": 0.08,
        "emergency_buffer_days": 18,
    }


def test_score_range():
    result = calculate_score(sample_features())
    assert 300 <= result["score"] <= 900


def test_missing_emergency_buffer():
    features = sample_features()
    features["emergency_buffer_days"] = None

    result = calculate_score(features)

    assert 300 <= result["score"] <= 900
    assert result["confidence"] < 1
    assert "Emergency buffer data unavailable" in result["risk_flags"]


def test_high_income_volatility():
    features = sample_features()
    features["income_cv"] = 0.8

    result = calculate_score(features)

    assert "High income volatility" in result["risk_flags"]


def test_factor_points_match_score():
    result = calculate_score(sample_features())

    total_points = sum(
        factor["points"] for factor in result["factors"]
    )

    assert result["score"] == 300 + total_points

def test_missing_buffer_points_match_score():
    features = sample_features()
    features["emergency_buffer_days"] = None

    result = calculate_score(features)

    total_points = sum(
        factor["points"] for factor in result["factors"]
    )

    assert result["score"] == 300 + total_points
    assert result["confidence"] == 0.95
    assert all(
        factor["key"] != "emergency_buffer_days"
        for factor in result["factors"]
    )