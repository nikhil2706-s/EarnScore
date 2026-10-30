import { useState } from 'react';
import { IconScoreAnalysis } from './Icons';

/**
 * AssessmentInputForm provides a validated form for submitting applicant features
 * to Member 2's backend POST /score endpoint:
 *
 * Requirements:
 * - applicant_id (nonempty string)
 * - analysis_period_months (positive integer)
 * - features.active_months_ratio (0 to 1)
 * - features.income_cv (>= 0)
 * - features.source_diversity (0 to 1)
 * - features.positive_cashflow_months_ratio (0 to 1)
 * - features.expense_to_income_ratio (>= 0)
 * - features.income_trend (number)
 * - features.emergency_buffer_days (optional nonnegative number or empty/null)
 * 
 * Notice: data_quality is omitted unless supplied; backend treats it as optional.
 */
export function AssessmentInputForm({ onSubmit, isLoading = false }) {
  const [formData, setFormData] = useState({
    applicant_id: 'demo-applicant-001',
    analysis_period_months: '12',
    active_months_ratio: '0.92',
    income_cv: '0.21',
    source_diversity: '0.68',
    positive_cashflow_months_ratio: '0.83',
    expense_to_income_ratio: '0.62',
    income_trend: '0.08',
    emergency_buffer_days: '',
  });

  const [validationErrors, setValidationErrors] = useState({});

  const validate = () => {
    const errors = {};

    // 1. applicant_id
    if (!formData.applicant_id || !formData.applicant_id.trim()) {
      errors.applicant_id = 'Applicant ID is required.';
    }

    // 2. analysis_period_months
    const monthsNum = Number(formData.analysis_period_months);
    if (!Number.isInteger(monthsNum) || monthsNum <= 0) {
      errors.analysis_period_months = 'Analysis period must be a positive integer.';
    }

    // 3. active_months_ratio (0 to 1)
    const activeRatio = Number(formData.active_months_ratio);
    if (isNaN(activeRatio) || activeRatio < 0 || activeRatio > 1) {
      errors.active_months_ratio = 'Active months ratio must be between 0.0 and 1.0.';
    }

    // 4. income_cv (>= 0)
    const cv = Number(formData.income_cv);
    if (isNaN(cv) || cv < 0) {
      errors.income_cv = 'Income CV must be non-negative (>= 0).';
    }

    // 5. source_diversity (0 to 1)
    const diversity = Number(formData.source_diversity);
    if (isNaN(diversity) || diversity < 0 || diversity > 1) {
      errors.source_diversity = 'Source diversity must be between 0.0 and 1.0.';
    }

    // 6. positive_cashflow_months_ratio (0 to 1)
    const positiveCf = Number(formData.positive_cashflow_months_ratio);
    if (isNaN(positiveCf) || positiveCf < 0 || positiveCf > 1) {
      errors.positive_cashflow_months_ratio = 'Positive cash-flow ratio must be between 0.0 and 1.0.';
    }

    // 7. expense_to_income_ratio (>= 0)
    const expenseRatio = Number(formData.expense_to_income_ratio);
    if (isNaN(expenseRatio) || expenseRatio < 0) {
      errors.expense_to_income_ratio = 'Expense-to-income ratio must be non-negative (>= 0).';
    }

    // 8. income_trend (number)
    const trend = Number(formData.income_trend);
    if (isNaN(trend)) {
      errors.income_trend = 'Income trend must be a valid number.';
    }

    // 9. emergency_buffer_days (optional nonnegative or empty)
    if (formData.emergency_buffer_days.trim() !== '') {
      const buffer = Number(formData.emergency_buffer_days);
      if (isNaN(buffer) || buffer < 0) {
        errors.emergency_buffer_days = 'Emergency buffer days must be non-negative (>= 0) or left empty.';
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (validationErrors[name]) {
      setValidationErrors((prev) => ({ ...prev, [name]: null }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;

    const payload = {
      applicant_id: formData.applicant_id.trim(),
      analysis_period_months: parseInt(formData.analysis_period_months, 10),
      features: {
        active_months_ratio: parseFloat(formData.active_months_ratio),
        income_cv: parseFloat(formData.income_cv),
        source_diversity: parseFloat(formData.source_diversity),
        positive_cashflow_months_ratio: parseFloat(formData.positive_cashflow_months_ratio),
        expense_to_income_ratio: parseFloat(formData.expense_to_income_ratio),
        income_trend: parseFloat(formData.income_trend),
        emergency_buffer_days: formData.emergency_buffer_days.trim() !== ''
          ? parseFloat(formData.emergency_buffer_days)
          : null,
      },
    };

    onSubmit(payload);
  };

  return (
    <div className="panel-card" aria-label="Feature Evaluation Input Form">
      <div className="section-header">
        <h2 className="section-title">
          <IconScoreAnalysis className="text-info" />
          <span>Financial Feature Evaluation Input</span>
        </h2>
        <span className="section-badge">POST /score Contract</span>
      </div>

      <form className="feature-input-form" onSubmit={handleSubmit} noValidate>
        <div className="form-grid">
          {/* Applicant ID */}
          <div className="form-group">
            <label htmlFor="applicant_id" className="form-label">Applicant ID *</label>
            <input
              id="applicant_id"
              name="applicant_id"
              type="text"
              className={`form-input ${validationErrors.applicant_id ? 'input-error' : ''}`}
              value={formData.applicant_id}
              onChange={handleChange}
              placeholder="e.g. demo-stable-001"
              required
            />
            {validationErrors.applicant_id && (
              <span className="form-error-text">{validationErrors.applicant_id}</span>
            )}
          </div>

          {/* Analysis Period Months */}
          <div className="form-group">
            <label htmlFor="analysis_period_months" className="form-label">Analysis Period (Months) *</label>
            <input
              id="analysis_period_months"
              name="analysis_period_months"
              type="number"
              min="1"
              step="1"
              className={`form-input ${validationErrors.analysis_period_months ? 'input-error' : ''}`}
              value={formData.analysis_period_months}
              onChange={handleChange}
              placeholder="e.g. 12"
              required
            />
            {validationErrors.analysis_period_months && (
              <span className="form-error-text">{validationErrors.analysis_period_months}</span>
            )}
          </div>

          {/* Active Months Ratio */}
          <div className="form-group">
            <label htmlFor="active_months_ratio" className="form-label">Active Months Ratio (0 – 1) *</label>
            <input
              id="active_months_ratio"
              name="active_months_ratio"
              type="number"
              min="0"
              max="1"
              step="0.01"
              className={`form-input ${validationErrors.active_months_ratio ? 'input-error' : ''}`}
              value={formData.active_months_ratio}
              onChange={handleChange}
              placeholder="0.0 to 1.0"
              required
            />
            {validationErrors.active_months_ratio && (
              <span className="form-error-text">{validationErrors.active_months_ratio}</span>
            )}
          </div>

          {/* Income CV */}
          <div className="form-group">
            <label htmlFor="income_cv" className="form-label">Income Volatility (CV &gt;= 0) *</label>
            <input
              id="income_cv"
              name="income_cv"
              type="number"
              min="0"
              step="0.01"
              className={`form-input ${validationErrors.income_cv ? 'input-error' : ''}`}
              value={formData.income_cv}
              onChange={handleChange}
              placeholder="e.g. 0.21"
              required
            />
            {validationErrors.income_cv && (
              <span className="form-error-text">{validationErrors.income_cv}</span>
            )}
          </div>

          {/* Source Diversity */}
          <div className="form-group">
            <label htmlFor="source_diversity" className="form-label">Source Diversity (0 – 1) *</label>
            <input
              id="source_diversity"
              name="source_diversity"
              type="number"
              min="0"
              max="1"
              step="0.01"
              className={`form-input ${validationErrors.source_diversity ? 'input-error' : ''}`}
              value={formData.source_diversity}
              onChange={handleChange}
              placeholder="0.0 to 1.0"
              required
            />
            {validationErrors.source_diversity && (
              <span className="form-error-text">{validationErrors.source_diversity}</span>
            )}
          </div>

          {/* Positive Cashflow Months Ratio */}
          <div className="form-group">
            <label htmlFor="positive_cashflow_months_ratio" className="form-label">Positive Cashflow Ratio (0 – 1) *</label>
            <input
              id="positive_cashflow_months_ratio"
              name="positive_cashflow_months_ratio"
              type="number"
              min="0"
              max="1"
              step="0.01"
              className={`form-input ${validationErrors.positive_cashflow_months_ratio ? 'input-error' : ''}`}
              value={formData.positive_cashflow_months_ratio}
              onChange={handleChange}
              placeholder="0.0 to 1.0"
              required
            />
            {validationErrors.positive_cashflow_months_ratio && (
              <span className="form-error-text">{validationErrors.positive_cashflow_months_ratio}</span>
            )}
          </div>

          {/* Expense to Income Ratio */}
          <div className="form-group">
            <label htmlFor="expense_to_income_ratio" className="form-label">Expense-to-Income Ratio (&gt;= 0) *</label>
            <input
              id="expense_to_income_ratio"
              name="expense_to_income_ratio"
              type="number"
              min="0"
              step="0.01"
              className={`form-input ${validationErrors.expense_to_income_ratio ? 'input-error' : ''}`}
              value={formData.expense_to_income_ratio}
              onChange={handleChange}
              placeholder="e.g. 0.62"
              required
            />
            {validationErrors.expense_to_income_ratio && (
              <span className="form-error-text">{validationErrors.expense_to_income_ratio}</span>
            )}
          </div>

          {/* Income Trend */}
          <div className="form-group">
            <label htmlFor="income_trend" className="form-label">Income Trend (Number) *</label>
            <input
              id="income_trend"
              name="income_trend"
              type="number"
              step="0.01"
              className={`form-input ${validationErrors.income_trend ? 'input-error' : ''}`}
              value={formData.income_trend}
              onChange={handleChange}
              placeholder="e.g. 0.08"
              required
            />
            {validationErrors.income_trend && (
              <span className="form-error-text">{validationErrors.income_trend}</span>
            )}
          </div>

          {/* Emergency Buffer Days (Optional) */}
          <div className="form-group">
            <label htmlFor="emergency_buffer_days" className="form-label">
              Emergency Buffer Days <span className="text-muted">(Optional / Null)</span>
            </label>
            <input
              id="emergency_buffer_days"
              name="emergency_buffer_days"
              type="number"
              min="0"
              step="1"
              className={`form-input ${validationErrors.emergency_buffer_days ? 'input-error' : ''}`}
              value={formData.emergency_buffer_days}
              onChange={handleChange}
              placeholder="Leave blank if unassessed"
            />
            {validationErrors.emergency_buffer_days && (
              <span className="form-error-text">{validationErrors.emergency_buffer_days}</span>
            )}
          </div>
        </div>

        <div className="form-actions-bar">
          <span className="form-note">
            Inputs are strictly validated on both frontend and FastAPI schema before scoring.
          </span>
          <button
            type="submit"
            className="btn-primary"
            disabled={isLoading}
          >
            {isLoading ? (
              <span className="btn-loading-state">
                <span className="spinner" aria-hidden="true"></span>
                <span>Calculating Score...</span>
              </span>
            ) : (
              <span>Request EarnScore Evaluation</span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
