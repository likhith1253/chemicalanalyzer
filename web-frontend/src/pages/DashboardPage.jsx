import React, { useState, useEffect } from 'react';
import { datasetAPI, getCurrentUser } from '../api/client';
import FileUpload from '../components/FileUpload';
import SummaryCards from '../components/SummaryCards';
import AIInsightsCard from '../components/AIInsightsCard';
import TypeDistributionChart from '../components/TypeDistributionChart';
import EquipmentTable from '../components/EquipmentTable';
import './DashboardPage.css';

const DashboardPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Get current user
    const curr = getCurrentUser();
    if (curr) {
      setUser(curr);
    } else {
      const token = sessionStorage.getItem('auth_token');
      if (token) {
        setUser({ username: 'User' });
      }
    }
  }, []);

  const handleFileUpload = async (file) => {
    if (!file) return;

    setLoading(true);
    setProgress(0);

    try {
      // Fake progress
      const interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(interval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response = await datasetAPI.uploadCsv(file);

      clearInterval(interval);
      setProgress(100);

      // Set data
      setData(response || {});

      setTimeout(() => {
        setProgress(0);
      }, 1000);

    } catch (error) {
      console.error('Upload error:', error);
      setProgress(0);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    if (!data?.id) return;

    try {
      const res = await datasetAPI.fetchDatasetDetail(data.id);
      setData(res || {});
    } catch (error) {
      console.error('Refresh error:', error);
    }
  };

  const handleDownloadPdf = async () => {
    if (!data?.id) return;

    try {
      await datasetAPI.downloadPdfReport(data.id);
    } catch (error) {
      console.error('PDF error:', error);
    }
  };

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Upload and analyze your chemical equipment data</p>
        </div>
        <div className="header-actions">
          {data?.id && (
            <>
              <button
                className="action-btn refresh-btn"
                onClick={handleRefresh}
                disabled={loading}
                title="Refresh data"
              >
                Refresh
              </button>
              <button
                className="action-btn pdf-btn"
                onClick={handleDownloadPdf}
                disabled={loading}
                title="Download PDF report"
              >
                Download PDF
              </button>
            </>
          )}
        </div>
      </div>

      <div className="dashboard-content">
        {/* Upload Section */}
        <section className="dashboard-section upload-section">
          <h2 className="section-title">Upload CSV File</h2>
          <FileUpload
            onFileUpload={handleFileUpload}
            isLoading={loading}
            uploadProgress={progress}
          />
        </section>

        {/* Summary Cards */}
        {data && data.id && (
          <section className="dashboard-section summary-section">
            <h2 className="section-title">Summary Statistics</h2>
            <SummaryCards data={data} />
          </section>
        )}

        {/* AI Insights Card */}
        {data && data.id && (
          <section className="dashboard-section ai-insights-section">
            <AIInsightsCard datasetId={data.id} />
          </section>
        )}

        {/* Charts Section */}
        {data && data.id && data.type_distribution && (
          <section className="dashboard-section charts-section">
            <h2 className="section-title">Type Distribution</h2>
            <div className="chart-wrapper">
              <TypeDistributionChart data={data} />
            </div>
          </section>
        )}

        {/* Table Section */}
        {data && data.id && data.preview_rows && data.preview_rows.length > 0 && (
          <section className="dashboard-section table-section">
            <h2 className="section-title">Equipment Data Preview</h2>
            <EquipmentTable
              data={data.preview_rows}
              title=""
              showPagination={true}
            />
          </section>
        )}

        {/* Empty State */}
        {!data && !loading && (
          <div className="empty-state">
            <div className="empty-icon"></div>
            <h3>No Data Available</h3>
            <p>Upload a CSV file to start analyzing your chemical equipment data</p>
            <div className="empty-hint">
              <p>Expected CSV format:</p>
              <ul>
                <li>Columns: Equipment Name, Type, Flowrate, Pressure, Temperature</li>
                <li>First row should contain headers</li>
                <li>Numeric values for flowrate, pressure, temperature</li>
              </ul>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="loading-state">
            <div className="loading-spinner-large"></div>
            <p>Processing your file...</p>
            {progress > 0 && (
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${progress}%` }}></div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
