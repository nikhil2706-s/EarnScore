import { IconAlertTriangle, IconCheckCircle, IconEmptyBox } from './Icons';

/**
 * RiskFlags displays risk notifications returned by Member 2's backend.
 * 
 * Crucially distinguishes three states:
 * 1. assessmentLoaded === false: No assessment loaded yet (empty state).
 * 2. assessmentLoaded === true && flags.length === 0: Clean profile with no risk flags raised.
 * 3. assessmentLoaded === true && flags.length > 0: Specific flags returned by the model.
 * 
 * Flags from Member 2 are strings such as:
 * - "High income volatility"
 * - "High expense-to-income ratio"
 * - "Irregular income activity"
 * - "Emergency buffer data unavailable"
 */
export function RiskFlags({ flags = null, isAssessmentLoaded = false }) {
  if (!isAssessmentLoaded) {
    return (
      <div className="panel-card" aria-label="Risk Flags Panel">
        <div className="section-header">
          <h2 className="section-title">
            <IconAlertTriangle />
            <span>Risk Indicators</span>
          </h2>
          <span className="section-badge">Awaiting Assessment</span>
        </div>

        <div className="empty-state-box">
          <div className="empty-state-icon" aria-hidden="true">
            <IconEmptyBox />
          </div>
          <span className="empty-state-heading">No Assessment Loaded</span>
          <p className="empty-state-text">
            Risk indicators such as income volatility, high expense-to-income ratio, or unverified buffer data will appear here once an applicant analysis is run.
          </p>
        </div>
      </div>
    );
  }

  const hasFlags = Array.isArray(flags) && flags.length > 0;

  return (
    <div className="panel-card" aria-label="Risk Flags Panel">
      <div className="section-header">
        <h2 className="section-title">
          <IconAlertTriangle className={hasFlags ? "text-warning" : "text-muted"} />
          <span>Risk Indicators</span>
        </h2>
        <span className="section-badge" style={{ color: hasFlags ? "var(--status-warning)" : "var(--status-positive)" }}>
          {hasFlags ? `${flags.length} Flagged` : "0 Flags (Clear)"}
        </span>
      </div>

      {hasFlags ? (
        <div className="risk-flags-grid">
          {flags.map((flag, idx) => {
            const flagText = typeof flag === 'string' ? flag : flag.title || flag.description || 'Risk Alert';
            return (
              <div key={idx} className="risk-flag-placeholder" style={{ borderColor: 'rgba(245, 158, 11, 0.3)' }}>
                <span className="flag-icon" style={{ color: 'var(--status-warning)' }} aria-hidden="true">
                  <IconAlertTriangle />
                </span>
                <div className="flag-content">
                  <span className="flag-title" style={{ color: 'var(--text-primary)' }}>{flagText}</span>
                  <span className="flag-desc">Threshold triggered during model evaluation</span>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="empty-state-box" style={{ borderColor: 'rgba(16, 185, 129, 0.3)' }}>
          <div className="empty-state-icon" style={{ color: 'var(--status-positive)', backgroundColor: 'rgba(16, 185, 129, 0.1)' }} aria-hidden="true">
            <IconCheckCircle />
          </div>
          <span className="empty-state-heading" style={{ color: 'var(--status-positive)' }}>No Risk Flags Triggered</span>
          <p className="empty-state-text">
            All evaluated cash-flow and stability features met baseline lending safety guidelines.
          </p>
        </div>
      )}
    </div>
  );
}
