import { FACTOR_LABELS } from '../constants/scoring';

/**
 * ScoreFactorBars dynamically renders factor contributions from the backend API.
 * 
 * Member 2 dynamically returns 6 or 7 factors depending on whether emergency_buffer_days
 * is available:
 * - Active factors each have: { key, label, points, max_points, explanation, evidence }
 * - Dynamic max_points are calculated by Member 2 using weight proportions of 600 points.
 * 
 * When factors is null or empty, an unassessed placeholder state is displayed using
 * all 7 canonical labels without hardcoded points or fixed max allocations.
 */
export function ScoreFactorBars({ factors = null }) {
  const isLoaded = Array.isArray(factors) && factors.length > 0;

  // Fallback empty-state factor list (all 7 possible categories)
  const placeholderFactors = Object.entries(FACTOR_LABELS).map(([key, label]) => ({
    key,
    label,
    points: null,
    max_points: null,
  }));

  const factorItems = isLoaded ? factors : placeholderFactors;

  return (
    <div className="factor-bars-list" role="region" aria-label="Dynamic Factor Contributions">
      {factorItems.map((factor) => {
        const hasPoints = typeof factor.points === 'number' && typeof factor.max_points === 'number';
        const pointsDisplay = hasPoints
          ? `${factor.points} / ${factor.max_points} pts`
          : '— pts';

        const percentage = hasPoints && factor.max_points > 0
          ? Math.min(100, Math.max(0, (factor.points / factor.max_points) * 100))
          : 0;

        return (
          <div key={factor.key} className="factor-item" title={factor.explanation || factor.label}>
            <div className="factor-top-line">
              <span className="factor-title">{factor.label}</span>
              <span className="factor-score-ratio">{pointsDisplay}</span>
            </div>
            <div className="factor-progress-track" aria-hidden="true">
              <div
                className="factor-progress-fill"
                style={{ width: `${percentage}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
