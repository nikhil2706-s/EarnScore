# EarnScore

## Alternative Creditworthiness Score for Gig Workers

**Category:** FinTech  
**Secondary domain:** Alternative Credit Scoring and Financial Inclusion

**Team name:** Winterfell Club
**Team members:**

- Nikhil Upadhyay
- Sharath B S
- Shaikh Asgar

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

1. **Collect with consent:** The applicant uploads supported CSV statements or selects a simulated demo profile. A production version could use consent-based bank and Account Aggregator connections.
2. **Normalize:** EarnScore standardizes dates, amounts, transaction directions, and source names across platforms and accounts.
3. **Clean and classify:** The system detects duplicate records, reversals, refunds, transfers between the applicant's own accounts, income, and expenses.
4. **Build financial features:** It measures active earning months, month-to-month income variation, positive-cash-flow months, expense-to-income ratio, source concentration, recent income trend, and available financial buffer.
5. **Calculate an EarnScore:** A deterministic model starts at 300 and awards up to 600 points across seven explainable financial features.
6. **Measure confidence:** Data coverage, transaction density, classification quality, active earning history, and feature availability produce separate evidence-quality indicators.
7. **Explain the result:** The dashboard displays factor-level points, plain-language explanations, the evidence used, income trends, source mix, and risk flags.
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

- **Raw-to-understood transformation:** The dashboard visually shows how scattered payments become a coherent earning profile.
- **Counterfactual comparison:** Judges and lenders can compare a stable moderate-income profile with a volatile high-income profile to understand the model's priorities.
- **Explainable risk flags:** The product highlights income gaps, source dependence, negative cash-flow periods, sparse history, and classification uncertainty with supporting data.
- **Reviewable decision trail:** Human decisions and notes remain distinct from model output, creating the basis for audit and future model evaluation.

### Responsible innovation

- Uses financial-behavior signals relevant to the assessment purpose.
- Excludes protected attributes and unnecessary personal data.
- Makes data gaps and uncertainty visible.
- Requires explicit human review.
- Provides a path for applicants to understand and dispute the evidence used.

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

1. NITI Aayog, *India's Booming Gig and Platform Economy: Perspectives and Recommendations on the Future of Work* (2022): gig-workforce estimates and projections.  
   <https://www.niti.gov.in/sites/default/files/2022-06/Policy_Brief_India%27s_Booming_Gig_and_Platform_Economy_27062022.pdf>
2. Reserve Bank of India, Account Aggregator directions and financial-data-sharing framework.  
   <https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=10598>
3. World Bank, *The Global Findex Database 2021*: financial-account ownership and digital-payment context.  
   <https://www.worldbank.org/en/publication/globalfindex>
4. International Labour Organization, *World Employment and Social Outlook 2021: The Role of Digital Labour Platforms in Transforming the World of Work*.  
   <https://www.ilo.org/publications/flagship-reports/role-digital-labour-platforms-transforming-world-work>

The market figures above should be rechecked against the linked primary publications before external submission or publication. The hackathon MVP does not claim proprietary market validation or a production-ready risk model.

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
- Creates an auditable record that can support model governance and customer communication.

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
6. The lender makes and records the final decision.

