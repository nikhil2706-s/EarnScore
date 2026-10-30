# EarnScore — Member 1 Data Pipeline Handoff

## Role
Data Engineering and Financial Feature Extraction

## Implementation
- Python and pandas transaction processing
- CSV ingestion, cleaning, and normalization
- Duplicate detection and conflicting-record quarantine
- Income-source classification
- Transfer and refund exclusion
- Monthly financial feature extraction
- Data-quality and confidence assessment
- JSON output for the FastAPI scoring backend

## Simulated Datasets
All records are synthetic and used for demonstration only.

| Persona | Transactions | History |
|---|---:|---|
| demo-stable-001 | 360 | 12 months |
| demo-volatile-002 | 71 | 5 months |
| demo-seasonal-003 | 162 | 12 months |

Total: 593 simulated transactions.

## Financial Features
1. active_months_ratio
2. income_cv
3. source_diversity
4. positive_cashflow_months_ratio
5. expense_to_income_ratio
6. income_trend
7. emergency_buffer_days

Emergency buffer is null when reliable balance evidence is unavailable.

## Data Quality
Reports coverage months, missing months, transaction count,
unclassified ratio, and evidence confidence.

Evidence confidence is not creditworthiness.

## Run Pipeline
python -m src.data_pipeline.pipeline data/raw/demo-stable-001.csv

## Run Tests
python -m pytest tests/

Last verified: 29 tests passed.

## Integration
JSON fixtures are stored in data/fixtures/.

Member 2's FastAPI /score endpoint accepts the generated feature
payloads, including nullable emergency_buffer_days and data_quality.

The three simulated personas were reported to pass scoring API
integration tests. Final combined-branch and dashboard verification
remain separate team tasks.

## Limitations
- Synthetic data only
- No real banking integration
- No verified loan repayment outcomes
- No calibrated probability of default
- Scores are prototype decision-support indicators
- Human lender review is required

## GitHub
Branch: feature/data-pipeline
Verified fixture commit: bd5f4f3
