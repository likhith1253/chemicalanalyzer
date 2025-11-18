import React, { useState, useEffect } from 'react';
import { datasetAPI, getCurrentUser } from '../api/client';
import FileUpload from '../components/FileUpload';
import SummaryCards from '../components/SummaryCards';
import TypeDistributionChart from '../components/TypeDistributionChart';
import EquipmentTable from '../components/EquipmentTable';
import './DashboardPage.css';

const DashboardPage = () => {
  const [dataset, setDataset] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const currentUser = getCurrentUser();
    if (currentUser) {
      setUser(currentUser);
    } else {
      const token = localStorage.getItem('auth_token');
      if (token) {
        setUser({ username: 'User' });
      }
    }
  }, []);

  const handleFileUpload = async (file) => {
    if (!file) return;
    
    setIsLoading(true);
    setUploadProgress(0);
    
    try {
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);
      
      const response = await datasetAPI.uploadCsv(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // Backend returns data directly
      setDataset(response || {});
      
      setTimeout(() => {
        setUploadProgress(0);
      }, 1000);
      
    } catch (error) {
      console.error('Upload error:', error);
      setUploadProgress(0);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    if (!dataset?.id) return;
    
    try {
      const data = await datasetAPI.fetchDatasetDetail(dataset.id);
      setDataset(data || {});
    } catch (error) {
      console.error('Refresh error:', error);
    }
  };

  const handleDownloadPdf = async () => {
    if (!dataset?.id) return;
    
    try {
      await datasetAPI.downloadPdfReport(dataset.id);
    } catch (error) {
      console.error('PDF download error:', error);
    }
  };

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Dashboard 📊</h1>
          <p className="page-subtitle">Upload and analyze your chemical equipment data</p>
        </div>
        <div className="header-actions">
          {dataset?.id && (
            <>
              <button 
                className="action-btn refresh-btn"
                onClick={handleRefresh}
                disabled={isLoading}
                title="Refresh data"
              >
                🔄 Refresh
              </button>
              <button 
                className="action-btn pdf-btn"
                onClick={handleDownloadPdf}
                disabled={isLoading}
                title="Download PDF report"
              >
                📄 Download PDF
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
            isLoading={isLoading}
            uploadProgress={uploadProgress}
          />
        </section>

        {/* Summary Cards */}
        {dataset && dataset.id && (
          <section className="dashboard-section summary-section">
            <h2 className="section-title">Summary Statistics</h2>
            <SummaryCards data={dataset} />
          </section>
        )}

        {/* Charts Section */}
        {dataset && dataset.id && dataset.type_distribution && (
          <section className="dashboard-section charts-section">
            <h2 className="section-title">Type Distribution</h2>
            <div className="chart-wrapper">
              <TypeDistributionChart data={dataset} />
            </div>
          </section>
        )}

        {/* Table Section */}
        {dataset && dataset.id && dataset.preview_rows && dataset.preview_rows.length > 0 && (
          <section className="dashboard-section table-section">
            <h2 className="section-title">Equipment Data Preview</h2>
            <EquipmentTable 
              data={dataset.preview_rows}
              title=""
              showPagination={true}
            />
          </section>
        )}

        {/* Empty State */}
        {!dataset && !isLoading && (
          <div className="empty-state">
            <div className="empty-icon">📊</div>
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
        {isLoading && (
          <div className="loading-state">
            <div className="loading-spinner-large"></div>
            <p>Processing your file...</p>
            {uploadProgress > 0 && (
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${uploadProgress}%` }}></div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
