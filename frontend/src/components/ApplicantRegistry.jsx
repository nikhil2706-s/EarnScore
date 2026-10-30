export function ApplicantRegistry({ records = [], onSelect, selectedId = null }) {
  return (
    <section className="panel-card" aria-label="Session Applicant Registry">
      <div className="section-header">
        <h2 className="section-title">Applicant Registry</h2>
        <span className="section-badge">Session Only</span>
      </div>

      <p className="empty-state-text">
        Successfully assessed applicants appear here until the page is refreshed.
        Records are not saved to a database.
      </p>

      {records.length === 0 ? (
        <p>No matching assessments. Analyze a demo worker or upload a CSV.</p>
      ) : (
        <div style={{ display: 'grid', gap: '0.75rem' }}>
          {records.map(record => (
            <div
              key={record.applicantId}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '1rem',
                padding: '0.85rem',
                border: '1px solid var(--border-subtle)',
                borderRadius: '8px',
                flexWrap: 'wrap'
              }}
            >
              <div>
                <strong>{record.applicantId}</strong>
                <p style={{ margin: '0.25rem 0' }}>
                  EarnScore: {record.assessment.score} / 900
                  {' | '}
                  {record.assessment.band}
                </p>
                <small>
                  Review: {record.review?.status ?? 'pending'}
                </small>
              </div>

              <button
                type="button"
                className="btn-secondary"
                disabled={selectedId === record.applicantId}
                onClick={() => onSelect(record)}
              >
                {selectedId === record.applicantId ? 'Selected' : 'View Assessment'}
              </button>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
