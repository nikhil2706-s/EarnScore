import {
  IconApplicants,
  IconScoreAnalysis,
  IconShield,
  IconAlertTriangle
} from './Icons';

export function EmptySummaryCards({ records = [] }) {
  const total = records.length;

  const pending = records.filter(
    record => !record.review || record.review.status === 'pending'
  ).length;

  const validScores = records
    .map(record => record.assessment?.score)
    .filter(Number.isFinite);

  const averageScore = validScores.length
    ? Math.round(validScores.reduce((sum, value) => sum + value, 0) / validScores.length)
    : null;

  const confidences = records
    .map(record => record.assessment?.data_quality?.confidence)
    .filter(Number.isFinite);

  const averageConfidence = confidences.length
    ? Math.round(
        confidences.reduce((sum, value) => sum + value, 0) /
        confidences.length * 100
      )
    : null;

  const riskFlags = records.reduce(
    (sum, record) =>
      sum + (Array.isArray(record.assessment?.risk_flags)
        ? record.assessment.risk_flags.length
        : 0),
    0
  );

  const cards = [
    {
      id: 'active_reviews',
      label: 'Active Reviews',
      value: total ? String(pending) : '—',
      footnote: 'Pending human review · session only',
      icon: IconApplicants,
    },
    {
      id: 'avg_score',
      label: 'Portfolio EarnScore',
      value: averageScore === null ? '— / 900' : `${averageScore} / 900`,
      footnote: `${validScores.length} assessed applicants · session only`,
      icon: IconScoreAnalysis,
    },
    {
      id: 'avg_confidence',
      label: 'Avg Data Confidence',
      value: averageConfidence === null ? 'N/A' : `${averageConfidence}%`,
      footnote: `${confidences.length} records with evidence confidence`,
      icon: IconShield,
    },
    {
      id: 'risk_flags',
      label: 'Reported Risk Flags',
      value: total ? String(riskFlags) : '—',
      footnote: 'Across session assessments',
      icon: IconAlertTriangle,
    },
  ];

  return (
    <div className="summary-cards-grid" aria-label="Session Assessment Summary">
      {cards.map(card => {
        const Icon = card.icon;

        return (
          <div key={card.id} className="summary-card">
            <div className="card-top">
              <span className="card-label">{card.label}</span>
              <div className="card-icon-bubble" aria-hidden="true">
                <Icon />
              </div>
            </div>

            <div className="card-value-placeholder">{card.value}</div>
            <span className="card-footnote">{card.footnote}</span>
          </div>
        );
      })}
    </div>
  );
}
