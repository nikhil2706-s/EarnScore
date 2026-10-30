import { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { SearchFilterBar } from './components/SearchFilterBar';
import { EmptySummaryCards } from './components/EmptySummaryCards';
import { AssessmentInputForm } from './components/AssessmentInputForm';
import { StatusBanner } from './components/StatusBanner';
import { ApplicantAssessmentLayout } from './components/ApplicantAssessmentLayout';
import { scoreApplicant, scoreUploadedCsv } from './services/api';
import { CsvUploadForm } from './components/CsvUploadForm';
import { DemoApplicantSelector } from './components/DemoApplicantSelector';
import { extractFinancialData } from './services/financialData';
import './App.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [riskFilter, setRiskFilter] = useState('all');

  // API State
  const [apiState, setApiState] = useState({
    isLoading: false,
    error: null,
    success: false,
    disclaimer: null,
  });

  // Current evaluated applicant payload from Member 2 backend
  const [assessedApplicant, setAssessedApplicant] = useState(null);
  const [financialData, setFinancialData] = useState(null);

  const handleResetFilters = () => {
    setSearchQuery('');
    setStatusFilter('all');
    setRiskFilter('all');
  };

  const handleScoreSubmit = async (requestPayload) => {
    setFinancialData(null);
    setApiState({
      isLoading: true,
      error: null,
      success: false,
      disclaimer: null,
    });

    try {
      // Call Member 2's backend service POST /score
      const response = await scoreApplicant(requestPayload);

      setAssessedApplicant(response);
      setApiState({
        isLoading: false,
        error: null,
        success: true,
        disclaimer: response.disclaimer,
      });
    } catch (err) {
      setAssessedApplicant(null);
      setApiState({
        isLoading: false,
        error: err,
        success: false,
        disclaimer: null,
      });
    }
  };

  const handleCsvUpload = async (file) => {
    setFinancialData(null);
    setAssessedApplicant(null);
    setApiState({
      isLoading: true,
      error: null,
      success: false,
      disclaimer: null,
    });

    try {
      const financial = await extractFinancialData(file);
      const response = await scoreUploadedCsv(file);
      setFinancialData(financial);
      setAssessedApplicant(response);
      setApiState({
        isLoading: false,
        error: null,
        success: true,
        disclaimer: response.disclaimer,
      });
    } catch (error) {
      setAssessedApplicant(null);
      setFinancialData(null);
      setApiState({
        isLoading: false,
        error,
        success: false,
        disclaimer: null,
      });
    }
  };

  const handleDismissBanner = () => {
    setApiState((prev) => ({ ...prev, error: null, success: false }));
  };

  const getHeaderTitle = () => {
    switch (activeTab) {
      case 'applicants':
        return 'Applicant Registry & Queue';
      case 'analysis':
        return 'EarnScore Factor & Cash-Flow Analysis';
      case 'settings':
        return 'Lending Parameters & Guardrail Configuration';
      case 'overview':
      default:
        return 'Lender Underwriting & Portfolio Overview';
    }
  };

  return (
    <div className="app-container">
      {/* Navigation Sidebar */}
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main Content Area */}
      <div className="main-wrapper">
        <Header title={getHeaderTitle()} />

        <main className="dashboard-content">
          {/* Summary Metric Cards (Empty states / placeholders) */}
          <EmptySummaryCards />

          {/* Status Banner for Loading, Network Errors, and Validation Errors */}
          <StatusBanner state={apiState} onDismiss={handleDismissBanner} />

          {/* Validated Feature Evaluation Form */}
          <DemoApplicantSelector
            onUpload={handleCsvUpload}
            isLoading={apiState.isLoading}
          />

          <CsvUploadForm
            onUpload={handleCsvUpload}
            isLoading={apiState.isLoading}
          />

          <AssessmentInputForm
            onSubmit={handleScoreSubmit}
            isLoading={apiState.isLoading}
          />

          {/* Search and Filtering Controls */}
          <SearchFilterBar
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            statusFilter={statusFilter}
            onStatusFilterChange={setStatusFilter}
            riskFilter={riskFilter}
            onRiskFilterChange={setRiskFilter}
            onReset={handleResetFilters}
          />

          {/* Detailed Assessment & Score Gauge Layout */}
          <ApplicantAssessmentLayout
            applicant={assessedApplicant}
            financialData={financialData}
            onReviewSubmit={(reviewData) => {
              // Local review action; clearly indicated as unsaved in UI
              console.info('Human review recorded locally:', reviewData);
            }}
          />
        </main>
      </div>
    </div>
  );
}
