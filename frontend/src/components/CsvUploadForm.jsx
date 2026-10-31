import { useState } from 'react';

export function CsvUploadForm({ onUpload, isLoading = false }) {
  const [file, setFile] = useState(null);

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!file || isLoading) return;
    onUpload(file);
  };

  return (
    <section className="panel-card">
      <div className="section-header">
        <h2 className="section-title">Automatic CSV Assessment</h2>
        <span className="section-badge">Transaction Upload</span>
      </div>

      <p>
        Upload a gig worker's transaction CSV to automatically
        calculate financial features and generate an EarnScore.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="transaction-csv" className="form-label">
            Select Transaction CSV
          </label>
          <input
            id="transaction-csv"
            type="file"
            accept=".csv,text/csv"
            className="form-input"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            disabled={isLoading}
            required
          />
        </div>

        <button
          type="submit"
          className="btn-primary"
          disabled={!file || isLoading}
        >
          {isLoading ? 'Analyzing Transactions...' : 'Upload & Generate EarnScore'}
        </button>
      </form>
    </section>
  );
}
