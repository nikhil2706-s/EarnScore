import { IconShield } from './Icons';

/**
 * DataQualityIndicators reflects coverage, transaction completeness, and data confidence.
 * 
 * Crucial distinction:
 * - scoreConfidence: Feature completeness according to Member 2's model weights (0.0 to 1.0).
 * - data_quality.confidence: Record integrity, coverage, and classification confidence from Member 1.
 * 
 * When data is not loaded, it displays unassessed empty states rather than hardcoded 12 months.
 */
export function DataQualityIndicators({ quality = null, scoreConfidence = null }) {
  const metrics = [
    {
      id: 'score_confidence',
      label: 'Feature Completeness',
      value: typeof scoreConfidence === 'number' ? `${Math.round(scoreConfidence * 100)}%` : '—',
      subtext: 'Proportion of available model features',
    },
    {
      id: 'data_confidence',
      label: 'Data Integrity Confidence',
      value: typeof quality?.confidence === 'number' ? `${Math.round(quality.confidence * 100)}%` : '—',
      subtext: 'Evidence completeness & tenure audit',
    },
    {
      id: 'coverage',
      label: 'Coverage Period',
      value: quality?.coverage_months ? `${quality.coverage_months} mo` : '—',
      subtext: quality?.missing_months ? `${quality.missing_months} missing month(s)` : 'Observed transaction tenure',
    },
    {
      id: 'transactions',
      label: 'Verified Transactions',
      value: quality?.total_transactions ? `${quality.total_transactions}` : '—',
      subtext: 'Normalized ledger count',
    },
    {
      id: 'unclassified',
      label: 'Unclassified Ratio',
      value: typeof quality?.unclassified_ratio === 'number' ? `${(quality.unclassified_ratio * 100).toFixed(1)}%` : '—',
      subtext: 'Transactions lacking verified platform tag',
    },
  ];

  return (
    <div className="panel-card" aria-label="Data Quality and Evidence Confidence">
      <div className="section-header">
        <h2 className="section-title">
          <IconShield className="text-info" />
          <span>Evidence Integrity & Completeness Audit</span>
        </h2>
        <span className="section-badge">Quality Metrics</span>
      </div>

      <div className="quality-indicators-grid">
        {metrics.map((metric) => (
          <div key={metric.id} className="quality-metric-item">
            <span className="quality-label">{metric.label}</span>
            <span className="quality-value">{metric.value}</span>
            <span className="quality-subtext">{metric.subtext}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
