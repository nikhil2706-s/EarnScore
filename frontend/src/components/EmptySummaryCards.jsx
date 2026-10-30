
import {
  IconApplicants,
  IconScoreAnalysis,
  IconShield,
  IconAlertTriangle
} from './Icons';

export function EmptySummaryCards() {
  const cards = [
    {
      id: 'active_reviews',
      label: 'Active Reviews',
      placeholder: '—',
      footnote: 'No applicant selected',
      icon: IconApplicants,
    },
    {
      id: 'avg_consistency',
      label: 'Portfolio EarnScore',
      placeholder: '— / 900',
      footnote: 'Awaiting pipeline data',
      icon: IconScoreAnalysis,
    },
    {
      id: 'avg_confidence',
      label: 'Avg Data Confidence',
      placeholder: '— %',
      footnote: 'Evidence verification metric',
      icon: IconShield,
    },
    {
      id: 'flagged_risk',
      label: 'Open Risk Flags',
      placeholder: '—',
      footnote: '0 critical escalations',
      icon: IconAlertTriangle,
    },
  ];

  return (
    <div className="summary-cards-grid" aria-label="Portfolio Metric Summary Cards">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div key={card.id} className="summary-card">
            <div className="card-top">
              <span className="card-label">{card.label}</span>
              <div className="card-icon-bubble" aria-hidden="true">
                <Icon />
              </div>
            </div>
            <div className="card-value-placeholder">{card.placeholder}</div>
            <span className="card-footnote">{card.footnote}</span>
          </div>
        );
      })}
    </div>
  );
}
