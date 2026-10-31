import { IconSearch, IconFilter } from './Icons';

export function SearchFilterBar({
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  riskFilter,
  onRiskFilterChange,
  onReset
}) {
  return (
    <div className="filter-panel" role="search" aria-label="Applicant Filter Bar">
      <div className="search-box">
        <span className="search-icon" aria-hidden="true">
          <IconSearch />
        </span>
        <input
          type="search"
          className="search-input"
          placeholder="Search by Applicant ID or reference..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          aria-label="Search applicants"
        />
      </div>

      <div className="filter-controls">
        <label htmlFor="status-select" className="sr-only" style={{ display: 'none' }}>Review Status</label>
        <select
          id="status-select"
          className="filter-select"
          value={statusFilter}
          onChange={(e) => onStatusFilterChange(e.target.value)}
          aria-label="Filter by review status"
        >
          <option value="all">Status: All Records</option>
          <option value="pending">Pending Human Review</option>
          <option value="approved">Approved</option>
          <option value="declined">Declined</option>
          <option value="more_data">More Data Requested</option>
        </select>

        <label htmlFor="risk-select" className="sr-only" style={{ display: 'none' }}>Score Band</label>
        <select
          id="risk-select"
          className="filter-select"
          value={riskFilter}
          onChange={(e) => onRiskFilterChange(e.target.value)}
          aria-label="Filter by score band"
        >
          <option value="all">Score Band: All</option>
          <option value="strong">Strong (750–900)</option>
          <option value="moderate">Moderate (600–749)</option>
          <option value="needs_review">Needs Review (300–599)</option>
        </select>

        <button
          type="button"
          className="btn-secondary"
          onClick={onReset}
          aria-label="Reset filters"
        >
          <IconFilter />
          <span>Reset</span>
        </button>
      </div>
    </div>
  );
}
