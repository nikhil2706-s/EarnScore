

export function Header({
  title = "Underwriting & Applicant Overview",
  onBack,
  showBack = false,
  onLogout
}) {
  return (
    <header className="dashboard-header">
      <div className="header-title-group">
        <div className="header-title-row">
          {showBack && (
            <button
              type="button"
              className="header-back-btn"
              onClick={onBack}
              aria-label="Go to previous page"
              title="Go back"
            >
              &larr;
            </button>
          )}
          <h1>{title}</h1>
        </div>
        <span className="header-subtitle">
          Decision-support evaluation for non-traditional gig earners
        </span>
      </div>

      <div className="header-actions">
        <div className="mode-badge" title="Decision Support Mode Active">
          <span className="mode-dot" aria-hidden="true"></span>
          <span>Decision Support</span>
        </div>

        <div className="user-profile-badge">
          <div className="avatar" aria-hidden="true">
            LR
          </div>
          <span className="user-role">Lender Reviewer</span>
        </div>

        <button
          type="button"
          className="header-logout-btn"
          onClick={onLogout}
          aria-label="Log out"
        >
          Log out
        </button>
      </div>
    </header>
  );
}
