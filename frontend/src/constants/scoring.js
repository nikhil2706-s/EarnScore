/**
 * Score bands aligned exactly with Member 2 backend contract:
 * - Strong: 750–900
 * - Moderate: 600–749
 * - Needs Review: 300–599
 */
export const SCORE_BANDS = {
  STRONG: { label: "Strong", min: 750, max: 900, color: "var(--status-positive)" },
  MODERATE: { label: "Moderate", min: 600, max: 749, color: "var(--status-warning)" },
  NEEDS_REVIEW: { label: "Needs Review", min: 300, max: 599, color: "var(--status-danger)" },
};

/**
 * All 7 possible factor labels matching Member 2's LABELS dictionary.
 */
export const FACTOR_LABELS = {
  active_months_ratio: "Income consistency",
  income_cv: "Income stability",
  positive_cashflow_months_ratio: "Positive cash-flow months",
  expense_to_income_ratio: "Expense management",
  income_trend: "Income growth trend",
  emergency_buffer_days: "Emergency savings buffer",
  source_diversity: "Income source diversity",
};

