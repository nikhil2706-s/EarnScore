from fastapi import UploadFile, File, HTTPException
from pathlib import Path
from tempfile import TemporaryDirectory

from src.data_pipeline.pipeline import run_pipeline
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel, Field

from .scoring import calculate_score


app = FastAPI(
    title="EarnScore API",
    description="Explainable Alternative Credit Scoring for Gig Workers",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
    allow_credentials=False,
)


@app.get("/")
async def home():
    return {
        "project": "EarnScore",
        "message": "Alternative Credit Scoring API",
        "status": "running"
    }


@app.get("/health")
async def health():
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
async def score_applicant(request: ScoreRequest):
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

@app.post("/score/upload-csv")
async def score_uploaded_csv(file: UploadFile = File(...)):
    """Process a gig-worker CSV through the pipeline and scoring engine."""

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file."
        )

    # Limit uploaded CSV files to 5 MB.
    max_bytes = 5 * 1024 * 1024
    content = await file.read(max_bytes + 1)
    await file.close()

    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail="CSV file exceeds the 5 MB limit."
        )

    if not content.strip():
        raise HTTPException(
            status_code=400,
            detail="CSV file is empty."
        )

    with TemporaryDirectory() as temp_dir:
        csv_path = Path(temp_dir) / "transactions.csv"
        csv_path.write_bytes(content)

        try:
            payload = run_pipeline(csv_path)

            result = calculate_score(
                payload.features.model_dump()
            )

            return {
                "applicant_id": payload.applicant_id,
                "analysis_period_months": payload.analysis_period_months,
                "features": payload.features.model_dump(),
                "data_quality": payload.data_quality.model_dump()
                if payload.data_quality is not None else None,
                **result,
            }

        except (ValueError, UnicodeError) as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid transaction data: {exc}"
            ) from exc
