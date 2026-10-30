import { useState } from 'react';
import { IconCheckCircle, IconQuestionMark, IconXCircle, IconAlertTriangle } from './Icons';

/**
 * HumanReviewPanel allows a human underwriter to record an approval,
 * request-more-data, or decline decision with review notes.
 * 
 * IMPORTANT:
 * As mandated, this state is LOCAL ONLY. The backend does not yet persist review
 * decisions in the /score endpoint. This is explicitly surfaced to the underwriter.
 */
export function HumanReviewPanel({ onDecisionSubmit = () => {} }) {
  const [decision, setDecision] = useState(null); // 'approve' | 'more_data' | 'decline'
  const [notes, setNotes] = useState('');
  const [statusMessage, setStatusMessage] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!decision) {
      setStatusMessage({ type: 'error', text: 'Please select a decision action.' });
      return;
    }
    
    // Explicitly labeled as local-only unsaved review
    onDecisionSubmit({ decision, notes, submittedAt: new Date().toISOString() });
    setStatusMessage({
      type: 'warning',
      text: `Decision (${decision.toUpperCase()}) recorded in local session only. NOTE: Decision persistence endpoint is scheduled for integration in the review pipeline.`,
    });
  };

  return (
    <div className="panel-card" aria-label="Human Review and Decision Panel">
      <div className="section-header">
        <h2 className="section-title">
          <span>Human Underwriting Decision</span>
        </h2>
        <span className="section-badge" style={{ color: 'var(--status-warning)' }}>
          Local Session (Unsaved to DB)
        </span>
      </div>

      <form className="review-form" onSubmit={handleSubmit}>
        <div className="decision-button-group" role="group" aria-label="Lender Decision Options">
          <button
            type="button"
            className={`decision-btn ${decision === 'approve' ? 'active-approve' : ''}`}
            onClick={() => {
              setDecision('approve');
              setStatusMessage(null);
            }}
            aria-pressed={decision === 'approve'}
          >
            <IconCheckCircle />
            <span>Approve Facility</span>
          </button>

          <button
            type="button"
            className={`decision-btn ${decision === 'more_data' ? 'active-more_data' : ''}`}
            onClick={() => {
              setDecision('more_data');
              setStatusMessage(null);
            }}
            aria-pressed={decision === 'more_data'}
          >
            <IconQuestionMark />
            <span>Request More Data</span>
          </button>

          <button
            type="button"
            className={`decision-btn ${decision === 'decline' ? 'active-decline' : ''}`}
            onClick={() => {
              setDecision('decline');
              setStatusMessage(null);
            }}
            aria-pressed={decision === 'decline'}
          >
            <IconXCircle />
            <span>Decline Application</span>
          </button>
        </div>

        <div>
          <label htmlFor="review-notes" className="sr-only" style={{ display: 'none' }}>
            Underwriter Audit Notes
          </label>
          <textarea
            id="review-notes"
            className="review-notes-area"
            placeholder="Record justification, mitigating circumstances, or specific verification requirements (e.g., additional platform statements, tax filings)..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            aria-label="Underwriter review notes"
          />
        </div>

        {statusMessage && (
          <div
            style={{
              fontSize: '0.8rem',
              padding: '0.5rem 0.75rem',
              borderRadius: '6px',
              backgroundColor: statusMessage.type === 'error'
                ? 'rgba(239, 68, 68, 0.15)'
                : 'rgba(245, 158, 11, 0.15)',
              color: statusMessage.type === 'error' ? 'var(--status-danger)' : 'var(--status-warning)',
              border: `1px solid ${statusMessage.type === 'error' ? 'var(--status-danger)' : 'var(--status-warning)'}`,
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
            role="status"
          >
            <IconAlertTriangle className="w-4 h-4" />
            <span>{statusMessage.text}</span>
          </div>
        )}

        <div className="review-actions-bar">
          <span className="review-notice">
            The calculated EarnScore remains immutable; human review overrides do not alter feature math.
          </span>
          <button
            type="submit"
            className="btn-primary"
            disabled={!decision}
          >
            Record Decision (Local)
          </button>
        </div>
      </form>
    </div>
  );
}
