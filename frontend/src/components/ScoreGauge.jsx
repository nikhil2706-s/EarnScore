/**
 * ScoreGauge renders a radial semicircular gauge for the 300 to 900 EarnScore scale.
 * 
 * Score bands aligned with Member 2 backend contract:
 * - Strong: 750–900
 * - Moderate: 600–749
 * - Needs Review: 300–599
 * 
 * When score is null/undefined, presents an accessible, clean empty-state outline.
 */
export function ScoreGauge({ score = null, band = null }) {
  const radius = 90;
  const strokeWidth = 16;
  const circumference = Math.PI * radius; // ~282.74

  let strokeDashoffset = circumference;
  let displayScore = "—";
  let displayBand = band || "Awaiting Assessment";

  if (typeof score === 'number' && !isNaN(score)) {
    const clamped = Math.max(300, Math.min(900, score));
    const ratio = (clamped - 300) / 600; // 0.0 to 1.0
    strokeDashoffset = circumference * (1 - ratio);
    displayScore = clamped.toString();

    if (!band) {
      if (clamped >= 750) displayBand = "Strong";
      else if (clamped >= 600) displayBand = "Moderate";
      else displayBand = "Needs Review";
    }
  }

  return (
    <div className="gauge-container" aria-label={`Score Gauge: ${displayScore} on 300 to 900 scale`}>
      <svg className="gauge-svg" viewBox="0 0 240 135" role="img" aria-hidden="true">
        <defs>
          <linearGradient id="gauge-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#ef4444" />
            <stop offset="45%" stopColor="#f59e0b" />
            <stop offset="75%" stopColor="#06b6d4" />
            <stop offset="100%" stopColor="#10b981" />
          </linearGradient>
        </defs>

        {/* Background track arc */}
        <path
          className="gauge-track"
          d="M 30,115 A 90,90 0 0,1 210,115"
          strokeWidth={strokeWidth}
        />

        {/* Score indicator arc */}
        <path
          className="gauge-value-bar"
          d="M 30,115 A 90,90 0 0,1 210,115"
          strokeWidth={strokeWidth}
          style={{ strokeDashoffset }}
        />
      </svg>

      <div className="gauge-center-text">
        <span className="gauge-score-placeholder">{displayScore}</span>
        <span className="gauge-scale-label">Scale: 300 – 900</span>
      </div>

      <div className="gauge-scale-ticks">
        <span>300 (Min)</span>
        <span>600 (Moderate)</span>
        <span>750 (Strong)</span>
        <span>900</span>
      </div>

      <div className="score-band-pill" aria-label={`Score Band: ${displayBand}`}>
        {displayBand}
      </div>
    </div>
  );
}
