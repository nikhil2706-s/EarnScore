# EarnScore

## Alternative Creditworthiness Score for Gig Workers

**Winterfell Club — Nikhil Upadhyay · Sharath B S · Shaikh Asgar**

*FinTech · Alternative Credit Scoring and Financial Inclusion*

**Repository:** <https://github.com/nikhil2706-s/EarnScore>

---

## 1. Problem Statement

Gig workers, freelancers, delivery partners, drivers, independent service providers, and small vendors often earn regularly without receiving a fixed monthly salary. Their income may arrive through multiple platforms, bank accounts, UPI payments, and direct customer transfers. Although their total earnings may be sufficient and dependable, the records appear fragmented and irregular when assessed using traditional underwriting methods.

Conventional credit assessment relies heavily on salary slips, employer verification, formal employment, and previous borrowing history. A worker without these records may appear financially invisible even when transaction history demonstrates reliable earning capacity. The challenge is to transform dispersed financial signals into an interpretable profile of income consistency, cash-flow resilience, and repayment capacity without creating an opaque automated lending decision.

## 2. Problem Statement Understanding

Irregular evidence does not necessarily mean irregular work. A moderate-income worker with regular earnings, positive cash flow, and multiple sources may have a more sustainable financial pattern than a higher-income worker with long income gaps and extreme volatility. Total income alone is therefore incomplete; assessment must consider stability, frequency, diversity, expenses, trends, and available buffer.

Credit history is also backward-looking. It offers limited evidence for first-time borrowers, creating a cycle in which a person needs credit history to access suitable credit. Cash-flow information can help fill this gap, but short histories, missing months, and unclassified transactions must reduce confidence rather than create false certainty. EarnScore excludes protected characteristics, separates score from evidence quality, links every factor to a financial value, and keeps the lender responsible for the final decision.

## 3. Proposed Solution

EarnScore is an explainable decision-support prototype that converts simulated gig-worker transactions into a lender-ready profile. Its workflow is:

1. Ingest and normalize CSV transactions from multiple earning sources.
2. Remove duplicates and handle conflicts, refunds, reversals, and transfers.
3. Classify income and expenses and aggregate activity by month.
4. Calculate seven features: active earning months, income volatility, source diversity, positive-cash-flow months, expense-to-income ratio, income trend, and emergency-buffer days.
5. Produce separate data-quality indicators for coverage, missing months, transaction density, classification quality, and evidence confidence.
6. Calculate a deterministic score from 300 to 900 and display factor points, evidence, explanations, confidence, and risk flags.
7. Support local human review without presenting the score as automatic loan approval.

The model starts with 300 base points and awards up to 600 additional points:

| Financial factor | Weight | Financial meaning |
| --- | ---: | --- |
| Income consistency | 25% | Regular earning activity across observed months |
| Income stability | 20% | Lower month-to-month income volatility |
| Positive cash-flow months | 20% | Frequency with which income exceeds expenses |
| Expense management | 15% | Sustainability of the expense-to-income ratio |
| Income trend | 10% | Stability or improvement in recent earnings |
| Emergency buffer | 5% | Cushion against short interruptions |
| Source diversity | 5% | Resilience against dependence on one source |

If a feature is unavailable, its weight is excluded and the remaining weights are normalized. Missing emergency-buffer data is `null`, not zero. Scores of 750–900 are **Strong**, 600–749 are **Moderate**, and 300–599 **Need Review**. These are prototype thresholds, not calibrated repayment probabilities.

The MVP uses Python, pandas, NumPy, Pydantic, and FastAPI with a React/Vite dashboard. Three simulated personas contain 593 transactions. Integration results were: stable worker **836 — Strong** with data-quality confidence 1.00; volatile worker **485 — Needs Review** with confidence 0.61; and seasonal worker **509 — Needs Review** with confidence 0.96. Feature-completeness confidence was 0.95 for all three because buffer data was unavailable. The seasonal result proves that reliable evidence can still describe an unstable earning pattern. Eight backend integration tests passed; the data-pipeline member reported 29 tests passed; and the dashboard member reported successful linting, production build, and a live local assessment. Live bank connections, persistent review history, production security, and repayment-risk calibration remain future work.

## 4. Novelty

EarnScore creates a unified earning profile instead of forcing gig income into a salary-based model. It evaluates how several sources behave together and deliberately allows a consistent moderate-income worker to outperform a volatile high-income worker. Unlike a single authoritative score, it shows both the assessment and the strength of its supporting evidence. Every factor includes points, an explanation, and the underlying value, making the result easier to understand, challenge, and audit. The human decision remains separate from model output.

## 5. Innovation

The pipeline standardizes multi-source records, detects duplicates and conflicts, distinguishes income from refunds and transfers, and measures source diversity with a normalized concentration formula. The deterministic scoring API redistributes weight when a genuine feature is missing and ensures that factor points reconcile with the final score. This avoids presenting an opaque machine-learning model as a validated credit-risk predictor.

The dashboard combines a score gauge, factor breakdown, risk flags, confidence and data-quality indicators, evidence views, API status handling, and human review. Explicit thresholds flag high volatility, high expense-to-income ratio, irregular activity, and missing buffer information. Reproducible simulated data keeps the complete prototype demonstrable while providing a path toward future consent-based integrations.

## 6. Market Research

India's underwriting systems remain largely designed around formal employment even as platform work expands. NITI Aayog's 2022 report *India's Booming Gig and Platform Economy* estimated **7.7 million gig workers in 2020–21** and projected **23.5 million by 2029–30**. The Reserve Bank of India's Account Aggregator framework provides a direction for consent-based financial-data sharing, while the World Bank's *Global Findex 2021* and International Labour Organization research document the growth of digital finance and platform work.

Potential customers include NBFCs, digital lenders, banks serving self-employed or new-to-credit applicants, gig platforms, and FinTech infrastructure providers. Credit bureaus are strong in repayment history but limited for people without formal borrowing records. Bank-statement tools categorize transactions, while some alternative-data systems use signals that are difficult to explain. EarnScore is positioned as an **underwriting intelligence layer** combining gig-income normalization, evidence confidence, transparent scoring, and human review. A future B2B model could charge per assessment, dashboard subscription, or enterprise deployment; these are proposals, not validated forecasts.

Primary sources: NITI Aayog, *India's Booming Gig and Platform Economy* (2022); Reserve Bank of India, *NBFC–Account Aggregator Directions* (2016); World Bank, *Global Findex Database 2021* (2022); and International Labour Organization, *World Employment and Social Outlook 2021*.

## 7. Impact

For workers, EarnScore can make real earning capacity visible without requiring a conventional salary profile or previous formal loan. It may improve access to emergency credit, productive assets, education, and income-smoothing products while helping applicants understand which parts of their financial profile are strong or incomplete.

For lenders, it can reduce manual review of fragmented statements, expand the assessable applicant pool, and provide consistent features, explanations, risk flags, and data-quality warnings. Human review remains visible, and the score acts as structured support rather than an automatic approval mechanism.

The wider impact is more responsible financial inclusion for workers in new forms of employment. A pilot should measure access, review time, repayment outcomes, fairness, explanation quality, disputes, and consent compliance. Production use requires secure consent, audit controls, lender calibration, regulatory review, fairness monitoring, and human oversight.
