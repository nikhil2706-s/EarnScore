
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .scoring import calculate_score


app = FastAPI(
    title="EarnScore API",
    description="Explainable Alternative Credit Scoring for Gig Workers",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "project": "EarnScore",
        "message": "Alternative Credit Scoring API",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "EarnScore Scoring API"
    }


class FinancialFeatures(BaseModel):
    active_months_ratio: float = Field(ge=0, le=1)
    income_cv: float = Field(ge=0)
    source_diversity: float = Field(ge=0, le=1)
    positive_cashflow_months_ratio: float = Field(ge=0, le=1)
    expense_to_income_ratio: float = Field(ge=0)
    income_trend: float
    emergency_buffer_days: Optional[float] = Field(
        default=None,
        ge=0
    )


class DataQualitySummary(BaseModel):
    coverage_months: int = Field(ge=0)
    missing_months: int = Field(ge=0)
    total_transactions: int = Field(ge=0)
    unclassified_ratio: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)


class ScoreRequest(BaseModel):
    applicant_id: str = Field(min_length=1)
    analysis_period_months: int = Field(gt=0)
    features: FinancialFeatures
    data_quality: Optional[DataQualitySummary] = None


@app.post("/score")
def score_applicant(request: ScoreRequest):
    result = calculate_score(
        request.features.model_dump()
    )

    return {
        "applicant_id": request.applicant_id,
        "analysis_period_months": request.analysis_period_months,
        "features": request.features.model_dump(),
        "data_quality": (
            request.data_quality.model_dump()
            if request.data_quality is not None
            else None
        ),
        **result,
    }
