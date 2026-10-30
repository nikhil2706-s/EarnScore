# EarnScore 24-hour execution plan

## The winning pitch

Traditional underwriting asks, “Do you receive a salary?” EarnScore asks, “How reliably do you earn, how resilient is your cash flow, and what evidence supports that conclusion?” The product rewards consistency and resilience instead of simply rewarding a high monthly income.

The demo should tell the story of one gig worker whose income arrives from several platforms. Raw transactions initially look irregular. EarnScore combines them, identifies recurring work patterns, measures volatility and expense pressure, and produces a score with explanations a lender can verify.

## Team split

### Member 1 — Data pipeline (`feature/data-pipeline`)

Own the path from raw records to trustworthy features.

Deliverables:

- Simulated datasets for at least three personas: stable gig worker, volatile new worker, and seasonal worker.
- CSV upload format for bank and platform transactions.
- Normalized transaction schema and duplicate detection.
- Income-source classification, refunds/reversals handling, and monthly aggregation.
- Feature output consumed by the scoring API.
- A data-quality summary: coverage period, missing months, unknown transactions, and confidence.

Done when one command can turn fixtures or an uploaded CSV into the agreed feature JSON.

### Member 2 — Scoring and API (`feature/scoring-api`)

Own the transparent model and backend contract.

Deliverables:

- FastAPI service with applicant, transaction, analysis, score, and report endpoints.
- Deterministic 300–900 scoring model based on the agreed features.
- Factor-level points, plain-language explanations, evidence, confidence, and risk flags.
- Unit tests for boundary cases, missing data, and each demo persona.
- A human-review decision endpoint that does not change the calculated score.

Done when the same input always returns the expected score and every point contribution is explainable.

### Member 3 — Lender dashboard and integration (`feature/lender-dashboard`)

Own the visible product and the final presentation.

Deliverables:

- Applicant selector and CSV upload/simulated-data flow.
- Score gauge, confidence badge, factor cards, income timeline, source mix, and risk flags.
- Evidence drawer explaining how every factor was calculated.
- Human-review form with approve, request-more-data, and decline options plus notes.
- Responsive polish, empty/error/loading states, and final integration.
- Five-minute demo script and pitch deck/screenshots.

Done when a judge can complete the whole journey without terminal interaction.

## Shared contract

Freeze this shape during the first hour. Add fields when needed, but coordinate renames.

```json
{
  "applicant_id": "demo-stable-001",
  "analysis_period_months": 12,
  "features": {
    "active_months_ratio": 0.92,
    "income_cv": 0.21,
    "source_diversity": 0.68,
    "positive_cashflow_months_ratio": 0.83,
    "expense_to_income_ratio": 0.62,
    "income_trend": 0.08,
    "emergency_buffer_days": 18
  },
  "score": 742,
  "band": "Strong",
  "confidence": 0.91,
  "factors": [
    {
      "key": "income_consistency",
      "label": "Income consistency",
      "points": 145,
      "max_points": 180,
      "explanation": "Income was recorded in 11 of the last 12 months.",
      "evidence": {"active_months": 11, "observed_months": 12}
    }
  ],
  "risk_flags": [],
  "disclaimer": "Decision-support output requiring human review."
}
```

## Explainable scoring model

Start at 300 and award up to 600 points. Clamp the result to 300–900.

| Factor | Maximum points | What earns points |
| --- | ---: | --- |
| Income consistency | 180 | Income appears across most observed weeks/months |
| Income stability | 130 | Lower month-to-month variation, with safeguards for sparse data |
| Cash-flow health | 110 | More positive-cash-flow months and sustainable expense ratio |
| Source resilience | 70 | Multiple genuine income sources without excessive dependence |
| Income trend | 50 | Stable or improving recent income, with outlier caps |
| Financial buffer | 60 | Observable balance buffer relative to typical daily expenses |

Suggested bands:

- 750–900: Strong
- 650–749: Stable
- 550–649: Developing
- 300–549: Limited evidence / higher volatility

Confidence must be separate from the score. Base it on observation length, transaction coverage, source verification, and the proportion of classified transactions. A high score with low confidence should visibly request more data.

## Minimal API

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Readiness check |
| `GET` | `/demo-personas` | List simulated applicants |
| `POST` | `/transactions/upload` | Validate and normalize a CSV |
| `POST` | `/analysis` | Calculate features from normalized transactions |
| `POST` | `/score` | Return score, explanations, confidence, and flags |
| `GET` | `/reports/{applicant_id}` | Return the lender-facing report |
| `POST` | `/reviews` | Record a human review decision and notes |

## 24-hour schedule

### Hours 0–2: Freeze the story and contract

- Agree on the three personas and the JSON contract.
- Sketch the final dashboard before coding.
- Create one end-to-end happy-path fixture.
- Decide the exact five-minute judging narrative.

### Hours 2–8: Build in parallel

- Data member creates fixtures, normalization, and feature extraction.
- Scoring member implements formula, explanations, endpoints, and tests.
- Dashboard member builds against the committed mock JSON.

### Hours 8–13: First integration

- Connect normalized features to the score endpoint.
- Connect the dashboard to the real API.
- Resolve contract differences immediately.
- Produce a complete, plain-looking end-to-end demo before polishing.

### Hours 13–18: Differentiate

- Add evidence-backed explanations and data-confidence warnings.
- Add comparison between raw fragmented income and normalized earning capacity.
- Add a PDF/print-friendly lender report only if the core flow is stable.
- Test all three personas and failure states.

### Hours 18–21: Product polish

- Improve visual hierarchy and responsive behavior.
- Add loading, invalid-file, insufficient-data, and API-error states.
- Remove anything that cannot be explained during judging.

### Hours 21–24: Freeze and rehearse

- Stop adding features.
- Rehearse the demo repeatedly with a backup recorded flow/screenshots.
- Prepare a 30-second pitch, five-minute demo, architecture slide, fairness slide, and next-steps slide.
- Keep a local fixture mode so the demo survives network failure.

## Demo sequence

1. Introduce a delivery worker earning through two gig platforms plus direct jobs.
2. Show the fragmented raw records and explain why a salary-based check misses the pattern.
3. Run the analysis and reveal the score with confidence.
4. Open two factor explanations and show the underlying evidence.
5. Highlight a risk flag or missing-data warning to demonstrate responsible behavior.
6. Compare a second persona to prove the model rewards stability rather than raw income.
7. Record a human review decision and close with the lender and borrower value.

## What to avoid in 24 hours

- Real bank integrations, production authentication, blockchain, or a trained black-box ML model.
- Claiming the score predicts default without labeled repayment data.
- Too many screens or borrower features that do not strengthen the judging story.
- A score with no factor math, evidence, confidence, or human-review step.

## Judging evidence

Be ready to show:

- The same score is reproducible for the same data.
- A lower-income but consistent worker can outperform a higher-income volatile worker.
- Missing or short histories reduce confidence instead of silently producing certainty.
- Each factor maps to visible transaction evidence.
- Protected attributes are excluded and a human makes the final decision.

