# EarnScore

EarnScore is an explainable alternative creditworthiness platform for gig workers. It converts fragmented income and cash-flow records into a transparent profile of earning consistency, resilience, and repayment capacity. It is a decision-support tool for a human lender, not an automated loan approval system.

## Hackathon MVP

The 24-hour demo follows one complete story:

1. Upload or select simulated transactions from bank accounts and gig platforms.
2. Normalize the records into a single income timeline.
3. Calculate an EarnScore from 300 to 900 using clearly defined factors.
4. Show the score, factor breakdown, income trends, risk flags, and evidence.
5. Let a lender review the report and record a human decision.

The implementation plan, team split, API contract, scoring formula, and demo script are in [docs/HACKATHON_PLAN.md](docs/HACKATHON_PLAN.md).

## Recommended stack

- Frontend: React, Vite, TypeScript, Tailwind CSS, Recharts
- API and scoring: Python, FastAPI, Pydantic, pandas
- Demo storage: SQLite or in-memory fixtures
- Testing: pytest for scoring and API tests; Vitest for critical UI logic

## Branches

- `feature/data-pipeline` — ingestion, simulation, cleaning, normalization, and data quality
- `feature/scoring-api` — score model, explanations, FastAPI endpoints, and tests
- `feature/lender-dashboard` — applicant flow, charts, report UI, and final demo integration

Each branch starts from the same baseline. Use small commits and open pull requests into `main`. Agree on the JSON contract before changing field names.

## Product guardrails

- Do not use protected traits such as religion, caste, gender, or ethnicity.
- Do not treat platform identity, location, or device type as a proxy for those traits.
- Display confidence and missing-data warnings alongside the score.
- Show the calculation factors and supporting evidence.
- Keep the final lending decision with a human reviewer.

