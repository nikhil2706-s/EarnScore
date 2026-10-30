import { IconAlertTriangle, IconCheckCircle } from './Icons';

/**
 * StatusBanner presents loading, network-error, API-validation-error,
 * and successful-result states.
 */
export function StatusBanner({ state, onDismiss }) {
  if (!state || (!state.isLoading && !state.error && !state.success)) {
    return null;
  }

  if (state.isLoading) {
    return (
      <div className="status-banner banner-loading" role="status" aria-live="polite">
        <span className="spinner" aria-hidden="true"></span>
        <div className="banner-text">
          <strong>Evaluating Creditworthiness with Member 2 Backend...</strong>
          <span>Calculating weighted factor points across available gig-income attributes.</span>
        </div>
      </div>
    );
  }

  if (state.error) {
    return (
      <div className="status-banner banner-error" role="alert">
        <IconAlertTriangle className="banner-icon text-danger" />
        <div className="banner-text">
          <strong>Evaluation Request Failed ({state.error.name || 'Error'})</strong>
          <span>{state.error.message || 'An unexpected error occurred while communicating with the scoring API.'}</span>
        </div>
        {onDismiss && (
          <button type="button" className="banner-dismiss" onClick={onDismiss} aria-label="Dismiss error">
            ×
          </button>
        )}
      </div>
    );
  }

  if (state.success) {
    return (
      <div className="status-banner banner-success" role="status" aria-live="polite">
        <IconCheckCircle className="banner-icon text-positive" />
        <div className="banner-text">
          <strong>Evaluation Succeeded</strong>
          <span>EarnScore calculated dynamically from Member 2 scoring API. Disclaimer: {state.disclaimer || 'Decision-support output requiring human review.'}</span>
        </div>
        {onDismiss && (
          <button type="button" className="banner-dismiss" onClick={onDismiss} aria-label="Dismiss notification">
            ×
          </button>
        )}
      </div>
    );
  }

  return null;
}
