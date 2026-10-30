import { useState } from 'react';

const PERSONAS = [
  { id: 'stable', name: 'Stable Worker', file: 'demo-stable-001.csv', description: 'Consistent multi-platform earnings' },
  { id: 'volatile', name: 'Volatile Worker', file: 'demo-volatile-002.csv', description: 'Irregular earnings and income gaps' },
  { id: 'seasonal', name: 'Seasonal Worker', file: 'demo-seasonal-003.csv', description: 'Seasonal fluctuations in earnings' },
];

export function DemoApplicantSelector({ onUpload, isLoading = false }) {
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState('');

  const analyze = async (persona) => {
    if (isLoading) return;
    setSelected(persona.id);
    setError('');

    try {
      const response = await fetch(`/demo-data/${persona.file}`);
      if (!response.ok) throw new Error('Could not load demo CSV');

      const blob = await response.blob();
      const file = new File([blob], persona.file, { type: 'text/csv' });

      await onUpload(file);
    } catch (err) {
      setError(err.message || 'Demo loading failed');
    } finally {
      setSelected(null);
    }
  };

  return (
    <section className="panel-card">
      <div className="section-header">
        <h2 className="section-title">Demo Gig Worker Profiles</h2>
        <span className="section-badge">Simulated Data</span>
      </div>

      <p>Select a worker to analyze their existing simulated transactions.</p>

      <div className="form-grid">
        {PERSONAS.map(persona => (
          <div className="form-group" key={persona.id}>
            <strong>{persona.name}</strong>
            <p>{persona.description}</p>
            <button
              type="button"
              className="btn-primary"
              disabled={isLoading || selected !== null}
              onClick={() => analyze(persona)}
            >
              {selected === persona.id ? 'Analyzing...' : 'Analyze Worker'}
            </button>
          </div>
        ))}
      </div>

      {error && <p role="alert">{error}</p>}
    </section>
  );
}
