# EarnScore

**Explainable credit intelligence for gig workers**

EarnScore converts fragmented gig-worker transaction records into a transparent 300–900 financial assessment. It combines a CSV data pipeline, deterministic scoring API, and lender dashboard so reviewers can see the score, evidence, confidence, factor contributions, and risk flags before making a human decision.

EarnScore is a hackathon decision-support prototype. It is not a validated credit bureau score, a probability-of-default model, or an automated loan approval system.

## Team Winterfell Club

- Nikhil Upadhyay
- Sharath B S
- Shaikh Asgar

## What is implemented

- Three reproducible gig-worker datasets: stable, volatile, and seasonal
- CSV ingestion, schema validation, normalization, duplicate handling, and transaction classification
- Seven financial features covering consistency, volatility, cash flow, expenses, trend, buffer, and source diversity
- Separate data-quality and feature-completeness confidence indicators
- Deterministic 300–900 scoring with factor points, evidence, explanations, and risk flags
- FastAPI endpoints for direct feature scoring and CSV upload scoring
- Responsive React dashboard with demo profiles, CSV upload, charts, applicant registry, filters, and human review
- Browser-local signup, login, session, and logout for the demo experience
- Vercel configuration for the Vite frontend and FastAPI backend
- 48 Python tests across the data pipeline and backend API

## Architecture

```text
CSV or simulated transactions
            |
            v
Cleaning, classification, and monthly aggregation
            |
            v
Seven financial features + data-quality evidence
            |
            v
FastAPI explainable scoring engine
            |
            v
React lender dashboard + human review
```

## Score design

The model starts with 300 base points and awards up to 600 additional points.

| Factor | Weight |
| --- | ---: |
| Income consistency | 25% |
| Income stability | 20% |
| Positive cash-flow months | 20% |
| Expense management | 15% |
| Income trend | 10% |
| Emergency buffer | 5% |
| Source diversity | 5% |

If a feature is genuinely unavailable, its weight is excluded and the remaining weights are normalized. Missing emergency-buffer data is represented as `null`, not zero.

| Score | Assessment |
| --- | --- |
| 750–900 | Strong |
| 600–749 | Moderate |
| 300–599 | Needs Review |

## Repository layout

```text
api/                    Vercel FastAPI entrypoint
backend/app/            FastAPI routes and scoring engine
backend/tests/          API, scoring, upload, and integration tests
data/raw/               Simulated transaction CSV files
data/fixtures/          Reproducible feature payloads
frontend/               React and Vite lender dashboard
src/data_pipeline/      Cleaning, classification, schemas, and feature extraction
tests/                  Data-pipeline tests
docs/                   Submission, implementation notes, and hackathon plan
vercel.json             Integrated deployment configuration
```

## Local setup

Requirements:

- Python 3.11 or newer
- Node.js 20 or newer

### 1. Install the backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Start FastAPI from the repository root:

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Check readiness at `http://localhost:8000/health`. Interactive API documentation is available at `http://localhost:8000/docs`.

### 2. Install the frontend

In a second terminal:

```bash
cd frontend
npm ci
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`, create a local demo account, and either select a demo applicant, upload a CSV, or enter features manually.

## API

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/` | Service information |
| `GET` | `/health` | Readiness check |
| `POST` | `/score` | Score a validated financial-feature payload |
| `POST` | `/score/upload-csv` | Clean, analyze, and score a transaction CSV |

CSV uploads are limited to 5 MB and must contain one applicant. The expected transaction fields are documented in [Member 1 Data Pipeline](docs/MEMBER1_DATA_PIPELINE.md).

Process a CSV directly through the data pipeline:

```bash
python -m src.data_pipeline.pipeline data/raw/demo-stable-001.csv
```

## Validation

Run all Python tests from the repository root:

```bash
python -m pytest -q
```

Run frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

The merged project contains 29 data-pipeline tests and 19 backend tests. The production frontend build currently emits a non-blocking bundle-size warning because the dashboard and charting dependencies are included in one client bundle.

## Deployment

The repository includes [vercel.json](vercel.json):

- `/api/*` is routed to the FastAPI service through `api/index.py`.
- Other routes are served by the Vite frontend.
- In production, the frontend defaults to `/api`; locally it defaults to `http://localhost:8000`.

## Responsible-use limits

- Demo data is simulated; live bank and Account Aggregator connections are not implemented.
- Browser authentication is local demo functionality, not production identity management.
- Human-review records are session-local and are not stored in a production database.
- The model excludes protected attributes and uses explainable financial features.
- Score thresholds require lender-specific repayment calibration, fairness testing, security review, and regulatory review before real lending use.

## Documentation

- [Three-page hackathon submission](docs/EARNSCORE_SUBMISSION_FINAL.pdf)
- [Hackathon execution plan](docs/HACKATHON_PLAN.md)
- [Data-pipeline implementation and handoff](docs/MEMBER1_DATA_PIPELINE.md)
