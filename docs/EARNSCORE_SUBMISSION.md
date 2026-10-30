# EarnScore

## Alternative Creditworthiness Score for Gig Workers

**Category:** FinTech

**Secondary domain:** Alternative Credit Scoring and Financial Inclusion

**Team name:** Winterfell Club

**Team members:**

- Nikhil Upadhyay
- Sharath B S
- Shaikh Asgar

**GitHub repository:** <https://github.com/nikhil2706-s/EarnScore>

**Prototype scope:** EarnScore is an explainable decision-support prototype. It is not an officially validated credit score, a trained machine-learning credit-risk model, or an automated loan-approval system.

> **One-line pitch:** EarnScore converts fragmented gig-worker income and cash-flow records into an explainable financial profile that helps lenders recognize consistent earning capacity beyond salary slips and conventional credit history.

---

## 1. Problem Statement

Gig workers, freelancers, delivery partners, drivers, independent service providers, and small vendors often earn regularly without receiving a fixed monthly salary. Their income may arrive through several gig platforms, bank accounts, UPI payments, and direct customer transfers. Although the total income may be sufficient and dependable, it appears fragmented and irregular when viewed through traditional underwriting methods.

Conventional credit assessment commonly depends on formal employment records, salary slips, employer verification, and previous borrowing history. A worker without these records may be treated as financially invisible or high-risk even when their transaction history demonstrates reliable earning capacity. This creates an information gap: the borrower possesses real economic activity, but the lender lacks a simple, trustworthy way to interpret it.

The challenge is to build a practical software layer that consolidates dispersed financial signals and presents them as a transparent, interpretable assessment of income consistency, cash-flow resilience, and repayment capacity. The output should support a lender's judgment without becoming an opaque or fully automated lending decision.

## 2. Problem Statement Understanding

### The problem is irregular evidence, not necessarily irregular work

A salaried employee usually presents one employer, one salary amount, and a predictable payment date. A gig worker may complete work every week but receive different amounts from multiple sources on different days. A simple salary check therefore mistakes a different earning pattern for an absence of stability.

### Existing credit history is backward-looking

A credit bureau is useful when a person has already used formal credit. It provides less information for a new-to-credit worker. Rejecting such an applicant solely because no past loan exists creates a circular problem: a person needs credit history to access the first suitable credit product.

### Total income alone is an incomplete signal

Two applicants may earn the same annual amount while having very different financial conditions. One may earn consistently from several sources and maintain positive cash flow. The other may receive a few large, unpredictable payments and experience long income gaps. A useful assessment must evaluate the pattern, stability, diversity, and sustainability of income rather than only its total.

### Data quality must affect certainty

Three months of incomplete transactions should not produce the same certainty as twelve months of well-classified records. EarnScore therefore separates the calculated score from **confidence**. Missing months, short observation periods, unclassified transactions, and unverifiable sources lower confidence and trigger a request for more evidence.

### Fairness and explainability are product requirements

Alternative data can expand access, but poorly chosen signals can reproduce bias. EarnScore excludes protected traits such as religion, caste, gender, and ethnicity. It also avoids using platform identity, device type, or location as unexplained proxies. Every score contribution must link to a visible financial feature and supporting evidence. The lender remains responsible for the final decision.

### Primary users and their needs

| User | Need | EarnScore response |
| --- | --- | --- |
| Gig worker or freelancer | Have real earning capacity recognized fairly | Consolidated, consent-based income profile |
| Lender or NBFC analyst | Assess non-salaried applicants quickly and consistently | Score, confidence, factor breakdown, risk flags, and evidence |
| Financial institution | Expand responsible lending without hiding risk | Auditable rules, data-quality controls, and human review |
| Ecosystem or policy partner | Improve access while protecting applicants | Explainability, consent, minimal data use, and measurable outcomes |

## 3. Proposed Solution

EarnScore is an explainable decision-support platform that transforms raw gig-platform and bank transaction records into a lender-ready financial profile.

### User journey

1. **Collect with consent:** The current command-line pipeline ingests simulated CSV transaction records. A production version could accept applicant-authorized statements and consent-based bank or Account Aggregator connections.
2. **Normalize:** EarnScore standardizes dates, amounts, transaction directions, and source names across platforms and accounts.
3. **Clean and classify:** The system detects duplicate records, reversals, refunds, transfers between the applicant's own accounts, income, and expenses.
4. **Build financial features:** It measures active earning months, month-to-month income variation, positive-cash-flow months, expense-to-income ratio, source concentration, recent income trend, and available financial buffer.
5. **Calculate an EarnScore:** A deterministic model starts at 300 and awards up to 600 points across seven explainable financial features.
6. **Measure confidence:** Data coverage, transaction density, classification quality, active earning history, and feature availability produce separate evidence-quality indicators.
7. **Explain the result:** The dashboard displays factor-level points, plain-language explanations, evidence values, confidence indicators, data-quality information, and risk flags.
8. **Support human review:** A lender may approve, decline, or request more information and record notes. The review decision does not silently alter the calculated score.

### Explainable score design

| Factor | Weight | Maximum points when all features are available | Financial question answered |
| --- | ---: | ---: | --- |
| Income consistency | 25% | 150 | Does the applicant earn during most observed periods? |
| Income stability | 20% | 120 | How much does income fluctuate between months? |
| Positive cash-flow months | 20% | 120 | How often does observed income exceed expenses? |
| Expense management | 15% | 90 | Is the expense-to-income ratio sustainable? |
| Income trend | 10% | 60 | Is recent earning capacity stable or improving? |
| Emergency savings buffer | 5% | 30 | Is there a visible cushion against short interruptions? |
| Income-source diversity | 5% | 30 | Is income overly dependent on one source? |

If a feature such as running-balance-based buffer days is genuinely unavailable, its weight is excluded and the 600 variable points are proportionally allocated across the available factors. Feature completeness remains visible to the reviewer instead of silently treating missing data as good or bad behavior.

The result is clamped between 300 and 900. Suggested interpretation bands are:

- **750–900 — Strong:** consistent and resilient observed earning pattern
- **600–749 — Moderate:** useful earning evidence with some volatility or concerns
- **300–599 — Needs Review:** limited evidence or material instability requiring closer review

These bands describe observed financial behavior. They do not claim a validated probability of default. Production use would require lender-specific outcome data, calibration, bias testing, regulatory review, and continuous monitoring.

### MVP architecture

```text
CSV / simulated gig records
            |
            v
Ingestion and normalization pipeline
            |
            v
Feature extraction and data-quality checks
            |
            v
Explainable scoring API + confidence engine
            |
            v
Lender dashboard, evidence view, and human review
```

The hackathon implementation uses React, Vite, JavaScript, and responsive CSS for the dashboard, with Python, FastAPI, Pydantic, pandas, and NumPy for the data and scoring services. Reproducible CSV fixtures provide demonstration data without requiring access to real financial information.

### Implemented MVP

The three development branches already contain the following working components:

- **Data pipeline:** Three reproducible personas—stable, volatile, and seasonal—plus schema validation, transaction classification, exact-duplicate removal, conflicting-record quarantine, refund and transfer handling, monthly aggregation, seven financial features, and a command-line CSV-to-JSON workflow.
- **Data-quality engine:** Measures observed and missing months, transaction count, unclassified ratio, and evidence confidence. Its deterministic confidence formula considers coverage, transaction density, classification quality, and active earning history.
- **Scoring API:** A FastAPI service with health and scoring endpoints, strict request validation, deterministic 300–900 scoring, factor-level points, readable explanations, evidence values, score bands, and risk flags for volatility, high expenses, irregular activity, and unavailable buffer data.
- **Lender dashboard:** A responsive React interface connected to the scoring API, including an assessment form, score gauge, factor bars, data-quality indicators, risk flags, filtering controls, API status handling, and a human-review panel.
- **Automated validation:** Unit and integration tests cover generation, schemas, cleaning, feature extraction, command-line execution, scoring boundaries, missing features, API validation, and all three personas.

The human-review panel records the review locally in the current MVP. Persistent review storage and production identity controls are planned after the hackathon demonstration.

#### Member 1 — Data pipeline

The `feature/data-pipeline` branch at verified development commit `9482669` contains three simulated gig-worker datasets with **593 transactions** in total: 360 for the stable persona, 71 for the volatile persona, and 162 for the seasonal persona. The pipeline performs CSV ingestion, schema validation, normalization, exact-duplicate removal, conflicting-duplicate quarantine, refund and transfer handling, transaction classification, monthly aggregation, and CSV-to-JSON output.

It calculates seven financial features:

1. `active_months_ratio`
2. `income_cv`
3. `source_diversity`
4. `positive_cashflow_months_ratio`
5. `expense_to_income_ratio`
6. `income_trend`
7. `emergency_buffer_days`

Source diversity uses a normalized income-concentration measure. Emergency-buffer information is returned as `null` when reliable running-balance data is unavailable; it is never silently treated as zero. A separate root-level `data_quality` object reports coverage months, missing months, transaction count, unclassified ratio, and evidence confidence. Member 1 reported **29 automated tests passed** for generation, schemas, cleaning, feature extraction, and command-line execution.

#### Member 2 — backend and explainable scoring API

The `feature/scoring-api` branch contains the implementation commits `62bef8f`, `abd5fae`, and `bc47a81`, the three-persona integration-test commit `bce6451`, and CORS integration commit `0122245`. The Python, FastAPI, Pydantic, and Pytest backend provides `GET /`, `GET /health`, and `POST /score`.

The API validates request bounds; calculates a deterministic score from 300 to 900; returns assessment bands, factor-level point contributions, explanations, and evidence values; preserves the pipeline's data-quality object; reports feature-completeness confidence separately; and generates risk flags. When a feature is genuinely unavailable, its scoring weight is excluded and the remaining factor weights are normalized. Factor points always reconcile with the final score.

#### Member 3 — React lender dashboard

The `feature/lender-dashboard` branch at reported commit `2448073` contains a responsive React, Vite, JavaScript, and CSS dashboard. It integrates with the real `POST /score` endpoint and presents an applicant assessment form, creditworthiness gauge, dynamic factor breakdown, risk flags, confidence and data-quality indicators, evidence views, API loading and error states, and a human-review interface.

Member 3 reported that ESLint and the production build passed and that a live local assessment returned **782 — Strong**. No additional facts about that particular applicant are inferred. The review interaction is implemented in the frontend MVP, while persistent server-side review history is not established.

#### Frontend–backend integration

The React development server uses port 5173 and FastAPI uses port 8000. An initial browser preflight failure was resolved by adding FastAPI `CORSMiddleware` for `http://localhost:5173` and `http://127.0.0.1:5173`, with `GET`, `POST`, and `OPTIONS` allowed. The backend CORS preflight returned HTTP 200, and all eight backend tests continued to pass after the change.

### Implementation and Validation Results

The automated API integration output supplied for the final submission produced the following results:

| Persona | Score | Assessment band | Data-quality confidence | Feature-completeness confidence |
| --- | ---: | --- | ---: | ---: |
| `demo-stable-001` | 836 | Strong | 1.00 | 0.95 |
| `demo-volatile-002` | 485 | Needs Review | 0.61 | 0.95 |
| `demo-seasonal-003` | 509 | Needs Review | 0.96 | 0.95 |

The stable worker received only the **Emergency buffer data unavailable** flag. The volatile worker triggered **High income volatility**, **Irregular income activity**, and **Emergency buffer data unavailable**. The seasonal worker triggered **High income volatility** and **Emergency buffer data unavailable**.

All three persona integration tests passed. The tests verified that scores stayed within 300–900, factor points reconciled with each final score, missing buffer values were handled correctly, explanations were nonempty, risk flags were generated, and feature-completeness confidence remained separate from data-quality confidence. The backend suite returned **8 passed** with one dependency-deprecation warning.

The seasonal persona demonstrates why data quality and financial assessment must remain separate. Its 0.96 data-quality confidence means that the transaction evidence is extensive, sufficiently classified, and well covered; it does not mean the financial pattern is low risk. The same high-quality evidence reveals seasonal income volatility, producing a score of 509 and a **Needs Review** assessment. EarnScore therefore distinguishes “we have reliable evidence” from “the evidence describes a stable earning pattern.”

### Capability status and MVP limitations

| Status | Capabilities |
| --- | --- |
| Implemented and evidenced in Git branches | Simulated datasets; CSV cleaning and normalization; seven features; data-quality metrics; deterministic scoring API; explanations, risk flags, and confidence; React dashboard; local API integration; CORS configuration; automated pipeline, scoring, and integration tests |
| Implemented or reported by a team member | Data-pipeline result of 29 tests passed; dashboard lint and production build results; live local dashboard assessment of 782 — Strong |
| Planned production enhancement | Live bank and Account Aggregator integrations; persistent review history; production authentication and security; advanced audit trails; automated applicant dispute workflow; lender-specific calibration; repayment-outcome validation and monitoring |

The MVP uses simulated transactions and deterministic, explainable rules. It does not perform automated lending approval, claim regulatory certification, or predict a calibrated probability of default. Comparing the three fixed personas demonstrates differences in financial patterns; the current MVP does not implement a general counterfactual-analysis engine. The components were tested locally and across their defined API contract. Because the three feature branches have not been represented here as a single verified release build, this report does not claim final merged-release verification.

### Demonstration scenarios

- **Stable multi-platform worker:** moderate income, regular earnings, multiple sources, and healthy cash flow.
- **High-income but volatile worker:** higher total income with long gaps and concentrated payments.
- **New or seasonal worker:** valid earnings but limited history, producing lower confidence and a request for more information.

These scenarios demonstrate that EarnScore rewards the quality and resilience of earning patterns rather than simply favoring the applicant with the highest income.

## 4. Novelty

### A unified earning identity instead of a salary substitute

EarnScore does more than estimate a monthly salary from bank credits. It constructs a consolidated earning profile from several fragmented sources and evaluates how those sources behave together over time.

### Score and confidence are intentionally separate

Many scoring interfaces present a single authoritative number. EarnScore presents both the financial assessment and the strength of the underlying evidence. A promising pattern supported by incomplete data remains visible, but the system clearly asks the lender for more information.

### Every factor is evidence-backed

A lender can open a factor, read its plain-language explanation, and inspect the values that produced its points. For example, income-consistency points can show that earnings were observed in 11 of 12 months. This makes the result easier to challenge, audit, and explain to an applicant.

### Stability can outweigh absolute income

The design deliberately allows a lower-income but consistent worker to score better than a higher-income worker with extreme volatility. This aligns the assessment with sustainable repayment capacity and makes the system relevant to gig work rather than reproducing salary-based ranking.

### Human judgment is part of the product flow

EarnScore records the lender's review separately from the calculated score. It supports structured decision-making while preventing the score from being presented as an automatic approval or rejection engine.

## 5. Innovation

### Technical innovation

- **Multi-source normalization:** Converts different platform and account formats into one auditable transaction timeline.
- **Transfer and reversal handling:** Reduces false income inflation by identifying duplicates, refunds, reversals, and transfers between an applicant's own accounts.
- **Resilience features:** Measures source concentration, positive-cash-flow frequency, income gaps, volatility, trends, and buffer days rather than relying on one aggregate income figure.
- **Confidence engine:** Changes certainty based on data completeness and quality instead of hiding missing evidence inside the score.
- **Local demo mode:** Uses reproducible fixtures so the full product remains demonstrable without live bank integrations or network access.

### Product innovation

- **Raw-to-understood transformation:** The data pipeline converts scattered simulated payments into a coherent feature payload, and the dashboard presents the resulting API assessment.
- **Counterfactual comparison:** Judges and lenders can compare a stable moderate-income profile with a volatile high-income profile to understand the model's priorities.
- **Explainable risk flags:** The scoring API identifies high income volatility, high expense-to-income ratio, irregular income activity, and unavailable emergency-buffer data using explicit thresholds.
- **Reviewable decision separation:** The MVP interface keeps the local human-review choice and notes distinct from model output, providing a design basis for future persistent audit and evaluation controls.

### Responsible innovation

- Uses financial-behavior signals relevant to the assessment purpose.
- Excludes protected attributes and unnecessary personal data.
- Makes data gaps and uncertainty visible.
- Keeps human review visible in the decision flow.
- Presents understandable factor evidence; a formal applicant-dispute workflow remains a future enhancement.

## 6. Market Research

### Market need

India's platform and gig workforce is expanding while underwriting processes remain primarily designed around formal salary employment. NITI Aayog estimated approximately **7.7 million gig workers in 2020–21** and projected that the workforce could reach **23.5 million by 2029–30**. This growth creates a large population whose work is digitally recorded but whose income may not fit conventional documentation.

At the same time, bank-account and digital-payment adoption has increased the amount of consentable cash-flow evidence available for analysis. India's Account Aggregator framework also provides a regulated direction for consent-based financial-data sharing. These developments make cash-flow underwriting more practical than it was when credit assessment depended mainly on paper salary records and prior loans.

### Target customers

The initial business-to-business customers are:

- NBFCs and digital lenders serving self-employed or new-to-credit applicants
- Banks developing small-ticket personal or productive-asset loans
- Gig platforms offering worker benefits or embedded financial products
- FinTech infrastructure providers that want an explainable gig-income assessment module
- Cooperatives and financial-inclusion programs evaluating non-salaried borrowers

### Competitive landscape

| Category | Typical strength | Gap EarnScore addresses |
| --- | --- | --- |
| Traditional credit bureaus | Established repayment-history data and lender acceptance | Limited evidence for people with little or no formal borrowing history |
| Bank-statement analytics providers | Transaction categorization and financial ratios | May provide analytics without a gig-worker-specific, judgeable earning-resilience narrative |
| Alternative-data scoring companies | Broader digital signals and automated risk models | Can be difficult for applicants or reviewers to interpret; some signals may raise privacy concerns |
| Lender-specific underwriting models | Optimized for one lender's portfolio | Often difficult to reuse across institutions and may remain hidden from front-line reviewers |
| EarnScore | Gig-income consolidation, confidence separation, evidence-backed explanations, and human review | Requires outcome-data calibration and integrations before production lending use |

### Positioning

EarnScore should initially be positioned as an **underwriting intelligence layer**, not as a lender or replacement for a credit bureau. It complements bureau history with current cash-flow evidence and gives analysts a consistent way to review non-salaried applicants.

### Business model

A production version could use a tiered B2B model:

- API fee per completed applicant analysis
- Monthly subscription for lender dashboard users
- Enterprise pricing for private deployment, custom policy rules, monitoring, and audit support
- Platform partnerships for embedded worker financial-wellness or credit-readiness tools

### Go-to-market sequence

1. Pilot with one lender or gig platform using historical, consented, de-identified data.
2. Validate whether EarnScore features improve review coverage and decision consistency.
3. Calibrate against repayment outcomes without removing explainability.
4. Run fairness, stability, privacy, and regulatory assessments.
5. Launch as a decision-support API and dashboard for a narrowly defined credit product.

### Research references

1. NITI Aayog, *India's Booming Gig and Platform Economy: Perspectives and Recommendations on the Future of Work* (June 2022): gig-workforce estimates and projections.
   <https://www.niti.gov.in/sites/default/files/2022-06/Policy_Brief_India%27s_Booming_Gig_and_Platform_Economy_27062022.pdf>
2. Reserve Bank of India, *Non-Banking Financial Company – Account Aggregator (Reserve Bank) Directions, 2016*: the regulatory framework for consent-based financial-data aggregation.
   <https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=10598>
3. World Bank, *The Global Findex Database 2021: Financial Inclusion, Digital Payments, and Resilience in the Age of COVID-19*: financial-account ownership and digital-payment context.
   <https://www.worldbank.org/en/publication/globalfindex>
4. International Labour Organization, *World Employment and Social Outlook 2021: The Role of Digital Labour Platforms in Transforming the World of Work* (2021).
   <https://www.ilo.org/publications/flagship-reports/role-digital-labour-platforms-transforming-world-work>

The market figures above should be rechecked against the linked primary publications before external submission or publication. The hackathon MVP does not claim proprietary market validation, customer validation, financial forecasts, regulatory certification, or a production-ready risk model.

## 7. Impact

### Impact on workers

- Gives financially active workers a fairer opportunity to demonstrate earning capacity.
- Reduces dependence on salary slips and previous formal loans as the only acceptable evidence.
- Helps applicants understand which parts of their financial profile are strong, uncertain, or incomplete.
- Can support access to emergency credit, productive assets, education, insurance, and income-smoothing products.

### Impact on lenders

- Expands the assessable applicant pool while preserving structured review.
- Reduces manual effort required to interpret multiple statements and irregular payment patterns.
- Provides consistent features, explanations, and data-quality warnings.
- Produces structured explanations and evidence that could support governance and customer communication when combined with production-grade persistent audit controls.

### Wider economic and social impact

- Supports financial inclusion for workers participating in new forms of employment.
- Helps direct credit toward demonstrated economic activity that traditional documentation overlooks.
- Encourages responsible use of consented cash-flow data instead of intrusive or irrelevant personal signals.
- Can enable more suitable small-ticket credit products for variable-income households.

### Impact measurement

A real pilot should measure both access and safety:

| Dimension | Example metric |
| --- | --- |
| Inclusion | Percentage of previously unscoreable applicants receiving a complete assessment |
| Decision quality | Repayment and delinquency outcomes by score band after calibration |
| Fairness | Approval, error, and outcome differences across legally permitted evaluation groups |
| Explainability | Percentage of decisions with complete factor evidence and reviewer acknowledgement |
| Efficiency | Reduction in average statement-review time |
| Applicant experience | Dispute rate, explanation comprehension, and time to decision |
| Data responsibility | Consent completion, data-retention compliance, and classification-error rate |

### Intended outcome

EarnScore's long-term goal is not to make credit automatic. It is to make real earning capacity visible, understandable, and reviewable. Success means that a reliable worker is no longer excluded merely because modern work does not resemble a traditional salary job, while lenders still receive the evidence and controls needed to make responsible decisions.

---

## Hackathon MVP success criteria

The demonstration is successful when it proves that:

1. Fragmented income from multiple sources can be normalized into one coherent timeline.
2. The same input always produces the same score and factor breakdown.
3. A consistent moderate-income worker can outperform a volatile high-income worker.
4. Incomplete history lowers confidence and requests more data instead of presenting false certainty.
5. Every factor can be explained using visible transaction evidence.
6. The lender can record a local MVP review decision separately from the calculated score.

## Conclusion

EarnScore demonstrates that fragmented gig income can be converted into a consistent, explainable, and reviewable financial profile without relying on opaque personal signals. The implemented prototype joins a tested transaction pipeline, seven transparent financial features, a deterministic scoring API, and a lender-facing dashboard. Its results show the intended behavior: strong transaction coverage increases confidence in the evidence, while income volatility and irregular activity can still produce a cautious assessment.

The immediate value is a clearer decision-support layer for non-salaried applicants. Production deployment would require consent-based integrations, persistent security and audit controls, lender-specific outcome calibration, regulatory review, fairness monitoring, and continued human oversight. Within its hackathon scope, EarnScore provides a credible foundation for making modern earning capacity visible without presenting a prototype score as an automatic lending decision.

