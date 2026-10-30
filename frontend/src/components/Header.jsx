

export function Header({ title = "Underwriting & Applicant Overview" }) {
  return (
    <header className="dashboard-header">
      <div className="header-title-group">
        <h1>{title}</h1>
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
      </div>
    </header>
  );
}
