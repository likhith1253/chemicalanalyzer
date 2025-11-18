import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { datasetAPI } from '../api/client';
import SummaryCards from '../components/SummaryCards';
import TypeDistributionChart from '../components/TypeDistributionChart';
import EquipmentTable from '../components/EquipmentTable';
import './HistoryPage.css';

const HistoryPage = () => {
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  
  const navigate = useNavigate();

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    setIsLoading(true);
    try {
      const data = await datasetAPI.fetchDatasets();
      setDatasets(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching datasets:', error);
      setDatasets([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDatasetSelect = async (dataset) => {
    if (selectedDataset?.id === dataset.id) {
      setSelectedDataset(null);
      return;
    }

    setIsDetailLoading(true);
    try {
      const data = await datasetAPI.fetchDatasetDetail(dataset.id);
      setSelectedDataset(data || {});
    } catch (error) {
      console.error('Error fetching dataset details:', error);
      setSelectedDataset(null);
    } finally {
      setIsDetailLoading(false);
    }
  };

  const handleDownloadPdf = async (datasetId) => {
    if (!datasetId) return;
    
    try {
      await datasetAPI.downloadPdfReport(datasetId);
    } catch (error) {
      console.error('PDF download error:', error);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  return (
    <div className="history-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Dataset History 📚</h1>
          <p className="page-subtitle">View and analyze your previously uploaded datasets</p>
        </div>
        <div className="header-actions">
          <button 
            className="action-btn refresh-btn"
            onClick={fetchDatasets} 
            disabled={isLoading}
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      <div className="history-content">
        {/* Datasets List */}
        <section className="history-section datasets-section">
          <h2 className="section-title">
            Recent Datasets
            <span className="dataset-count">({datasets.length})</span>
          </h2>
          
          {isLoading ? (
            <div className="loading-state">
              <div className="loading-spinner-large"></div>
              <p>Loading datasets...</p>
            </div>
          ) : datasets.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📂</div>
              <h3>No datasets found</h3>
              <p>Upload some data on the dashboard to see it here</p>
              <button 
                className="action-btn refresh-btn"
                onClick={() => navigate('/dashboard')}
              >
                Go to Dashboard
              </button>
            </div>
          ) : (
            <div className="datasets-grid">
              {datasets.map((dataset) => (
                <div
                  key={dataset.id}
                  className={`dataset-card ${selectedDataset?.id === dataset.id ? 'selected' : ''}`}
                  onClick={() => handleDatasetSelect(dataset)}
                >
                  <div className="dataset-card-header">
                    <h3 className="dataset-name">{dataset.name || 'Unnamed Dataset'}</h3>
                    <span className="dataset-id">#{dataset.id}</span>
                  </div>
                  
                  <div className="dataset-card-meta">
                    <div className="meta-item">
                      <span className="meta-label">📄 File:</span>
                      <span className="meta-value">{dataset.original_filename || 'N/A'}</span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label">📅 Date:</span>
                      <span className="meta-value">{formatDate(dataset.uploaded_at)}</span>
                    </div>
                  </div>
                  
                  <div className="dataset-card-stats">
                    <div className="stat-item">
                      <span className="stat-label">Records:</span>
                      <span className="stat-value">{dataset.total_count || 0}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Avg Flow:</span>
                      <span className="stat-value">
                        {dataset.avg_flowrate ? Number(dataset.avg_flowrate).toFixed(2) : 'N/A'}
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Avg Pressure:</span>
                      <span className="stat-value">
                        {dataset.avg_pressure ? Number(dataset.avg_pressure).toFixed(2) : 'N/A'}
                      </span>
                    </div>
                  </div>
                  
                  <div className="dataset-card-actions">
                    <button
                      className="card-action-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDownloadPdf(dataset.id);
                      }}
                      title="Download PDF"
                    >
                      📄 PDF
                    </button>
                    <div className="card-arrow">
                      {selectedDataset?.id === dataset.id ? '▼' : '▶'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Selected Dataset Details */}
        {selectedDataset && selectedDataset.id && (
          <section className="history-section detail-section">
            {isDetailLoading ? (
              <div className="loading-state">
                <div className="loading-spinner-large"></div>
                <p>Loading dataset details...</p>
              </div>
            ) : (
              <>
                <div className="detail-header">
                  <div>
                    <h2 className="detail-title">{selectedDataset.name || 'Dataset Details'}</h2>
                    <p className="detail-subtitle">Detailed analysis and visualization</p>
                  </div>
                  <button
                    className="action-btn pdf-btn"
                    onClick={() => handleDownloadPdf(selectedDataset.id)}
                  >
                    📄 Download PDF Report
                  </button>
                </div>

                <div className="detail-content">
                  <div className="detail-section-item">
                    <h3 className="section-title">Summary Statistics</h3>
                    <SummaryCards data={selectedDataset} />
                  </div>

                  {selectedDataset.type_distribution && (
                    <div className="detail-section-item">
                      <h3 className="section-title">Type Distribution</h3>
                      <div className="chart-wrapper">
                        <TypeDistributionChart data={selectedDataset} />
                      </div>
                    </div>
                  )}

                  {selectedDataset.preview_rows && selectedDataset.preview_rows.length > 0 && (
                    <div className="detail-section-item">
                      <h3 className="section-title">Equipment Data Preview</h3>
                      <EquipmentTable 
                        data={selectedDataset.preview_rows}
                        title=""
                        showPagination={true}
                      />
                    </div>
                  )}
                </div>
              </>
            )}
          </section>
        )}
      </div>
    </div>
  );
};

export default HistoryPage;
