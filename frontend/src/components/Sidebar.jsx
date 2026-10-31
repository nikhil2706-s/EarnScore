
import {
  IconOverview,
  IconApplicants,
  IconScoreAnalysis,
  IconSettings
} from './Icons';

export function Sidebar({ activeTab, onTabChange }) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: IconOverview },
    { id: 'applicants', label: 'Applicants', icon: IconApplicants },
    { id: 'analysis', label: 'Score Analysis', icon: IconScoreAnalysis },
    { id: 'settings', label: 'Settings', icon: IconSettings },
  ];

  return (
    <aside className="sidebar" aria-label="Main Navigation">
      <div className="sidebar-header">
        <div className="brand-icon" aria-hidden="true">
          ES
        </div>
        <div className="brand-info">
          <span className="brand-name">EarnScore</span>
          <span className="brand-badge">Lender Portal</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              type="button"
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => onTabChange(item.id)}
              aria-current={isActive ? 'page' : undefined}
            >
              <span className="nav-icon" aria-hidden="true">
                <Icon />
              </span>
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="guardrail-pill">
          <strong>Decision Support Only</strong>
          Scores reward earning resilience and consistency. Lending decisions require human verification.
        </div>
      </div>
    </aside>
  );
}
