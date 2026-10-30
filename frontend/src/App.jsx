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
import { saveSessionAssessment } from './services/sessionRegistry';
import { ApplicantRegistry } from './components/ApplicantRegistry';
import { filterSessionAssessments } from './services/sessionRegistry';
import './App.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');

  const [pageHistory, setPageHistory] = useState([]);

  const handleNavigation = (tab) => {
    if (tab === activeTab) return;

    setPageHistory(prev => [...prev, activeTab]);
    setActiveTab(tab);
    window.scrollTo(0, 0);
  };

  const handleGoBack = () => {
    if (pageHistory.length === 0) return;

    const previousPage = pageHistory[pageHistory.length - 1];
    setPageHistory(prev => prev.slice(0, -1));
    setActiveTab(previousPage);
    window.scrollTo(0, 0);
  };

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
  const [sessionRecords, setSessionRecords] = useState([]);
  const [financialData, setFinancialData] = useState(null);

  const filteredRecords = filterSessionAssessments(
    sessionRecords,
    searchQuery,
    statusFilter,
    riskFilter
  );

  const handleSelectApplicant = (record) => {
    setAssessedApplicant(record.assessment);
    setFinancialData(record.financialData);
  };

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

      setSessionRecords(prev => saveSessionAssessment(prev, response, null));
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
      setSessionRecords(prev => saveSessionAssessment(prev, response, financial));
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
      <Sidebar activeTab={activeTab} onTabChange={handleNavigation} />

      {/* Main Content Area */}
      <div className="main-wrapper">
        <Header
          title={getHeaderTitle()}
          onBack={handleGoBack}
          showBack={pageHistory.length > 0}
        />

        <main className="dashboard-content">
          {/* Summary Metric Cards (Empty states / placeholders) */}
          {activeTab === 'overview' && (
            <>
              <EmptySummaryCards records={sessionRecords} />

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

            </>
          )}

          {activeTab === 'applicants' && (
            <>
          

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

          <ApplicantRegistry
            records={filteredRecords}
            selectedId={assessedApplicant?.applicant_id ?? null}
            onSelect={handleSelectApplicant}
          />

            </>
          )}

          {activeTab === 'analysis' && (
            <>
          

          {/* Detailed Assessment & Score Gauge Layout */}
          <ApplicantAssessmentLayout
            applicant={assessedApplicant}
            financialData={financialData}
            onReviewSubmit={(reviewData) => {
              const applicantId = assessedApplicant?.applicant_id;
              if (!applicantId) return;

              const statuses = {
                approve: 'approved',
                decline: 'declined',
                more_data: 'more_data',
              };

              setSessionRecords(prev => prev.map(record =>
                record.applicantId === applicantId
                  ? {
                      ...record,
                      review: {
                        ...reviewData,
                        status: statuses[reviewData.decision],
                      },
                    }
                  : record
              ));
            }}
          />

            </>
          )}

          {activeTab === 'settings' && (
            <section className="panel-card">
              <h2 className="section-title">About EarnScore</h2>
              <p>
                EarnScore provides explainable, rule-based financial
                assessments using available earnings and transaction evidence.
              </p>
              <p>
                Scores are decision-support indicators, not credit bureau
                scores or predictions of loan repayment probability.
              </p>
              <p>
                Demo datasets are simulated. Applicant reviews and session
                records are not permanently stored.
              </p>
            </section>
          )}
        </main>
      </div>
    </div>
  );
}
