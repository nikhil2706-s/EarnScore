import { ScoreGauge } from './ScoreGauge';
import { ScoreFactorBars } from './ScoreFactorBars';
import { RiskFlags } from './RiskFlags';
import { DataQualityIndicators } from './DataQualityIndicators';
import { HumanReviewPanel } from './HumanReviewPanel';
import { IconEmptyBox } from './Icons';

/**
 * ApplicantAssessmentLayout structures the detailed assessment view.
 * 
 * Accurately aligns with Member 2 backend contract:
 * - Dynamic factors array (6 or 7 elements)
 * - Three score bands: Strong (750–900), Moderate (600–749), Needs Review (300–599)
 * - Risk flags array from API (string list)
 * - Score confidence (feature completeness) + Data quality confidence (evidence completeness)
 * - Dynamic coverage tenure (no hardcoded 12 months)
 */
export function ApplicantAssessmentLayout({
  applicant = null,
  onReviewSubmit = () => {}
}) {
  const isAssessmentLoaded = Boolean(applicant && typeof applicant.score === 'number');

  return (
    <div className="assessment-layout" aria-label="Applicant Detailed Assessment">
      {/* Left Column: Gauge & Dynamic Factor Breakdown */}
      <div className="assessment-card">
        <div className="section-header">
          <h2 className="section-title">
            <span>Creditworthiness Assessment</span>
          </h2>
          <span className="section-badge">Model 1.0</span>
        </div>

        <ScoreGauge
          score={applicant?.score ?? null}
          band={applicant?.band ?? null}
        />

        <div className="section-header" style={{ marginTop: '0.5rem' }}>
          <h3 className="section-title" style={{ fontSize: '0.9rem' }}>
            <span>Factor Point Breakdown</span>
          </h3>
          <span className="section-badge">
            {isAssessmentLoaded ? `${applicant?.factors?.length ?? 0} Factors Assessed` : 'Dynamic Allocation'}
          </span>
        </div>

        <ScoreFactorBars factors={applicant?.factors ?? null} />
      </div>

      {/* Right Column: Evidence Timeline / Overview, Risk Flags, Quality, and Review */}
      <div className="assessment-details-column">
        {/* Evidence & Cash Flow Trend Placeholder */}
        <div className="panel-card">
          <div className="section-header">
            <h2 className="section-title">
              <span>Earnings & Cash-Flow Evidence</span>
            </h2>
            <span className="section-badge">
              {applicant?.analysis_period_months ? `${applicant.analysis_period_months}-Month Window` : 'Timeline'}
            </span>
          </div>

          <div className="empty-state-box">
            <div className="empty-state-icon" aria-hidden="true">
              <IconEmptyBox />
            </div>
            <span className="empty-state-heading">
              {isAssessmentLoaded ? "Transaction Stream Loaded" : "No Transaction History Loaded"}
            </span>
            <p className="empty-state-text">
              Normalized gig earnings timeline, monthly net cash-flow comparisons, and platform source breakdown will appear here once an applicant or CSV file is selected.
            </p>
          </div>
        </div>

        {/* Risk Flags */}
        <RiskFlags
          flags={applicant?.risk_flags ?? null}
          isAssessmentLoaded={isAssessmentLoaded}
        />

        {/* Data Quality & Feature Completeness */}
        <DataQualityIndicators
          quality={applicant?.data_quality ?? null}
          scoreConfidence={applicant?.confidence ?? null}
        />

        {/* Human Review Decision Panel */}
        <HumanReviewPanel onDecisionSubmit={onReviewSubmit} />
      </div>
    </div>
  );
}
