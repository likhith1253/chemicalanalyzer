import React, { useRef, useState } from 'react';
import './FileUpload.css';

const FileUpload = ({ onFileUpload, isLoading, uploadProgress }) => {
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileSelect = (file) => {
    if (!file) return;
    
    // Check if file is CSV (by extension or MIME type)
    const isCsv = file.name.toLowerCase().endsWith('.csv') || 
                  file.type === 'text/csv' || 
                  file.type === 'application/vnd.ms-excel' ||
                  file.type === 'application/csv';
    
    if (isCsv) {
      onFileUpload(file);
    } else {
      alert('Please select a valid CSV file (.csv extension required)');
    }
  };

  const handleFileInputChange = (e) => {
    const file = e.target.files[0];
    handleFileSelect(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const file = e.dataTransfer.files[0];
    handleFileSelect(file);
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="file-upload">
      <div 
        className={`upload-area ${isDragging ? 'dragging' : ''} ${isLoading ? 'loading' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileInputChange}
          disabled={isLoading}
        />
        
        {isLoading ? (
          <div className="upload-loading">
            <div className="loading-spinner"></div>
            <h3>Uploading and analyzing...</h3>
            <p>Please wait while we process your data</p>
            {uploadProgress > 0 && (
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
                <span className="progress-text">{uploadProgress}%</span>
              </div>
            )}
          </div>
        ) : (
          <div className="upload-content">
            <div className="upload-icon">📊</div>
            <h3>Upload CSV File</h3>
            <p>Drag and drop your CSV file here or click to browse</p>
            <p className="file-hint">Supported format: CSV files with equipment data</p>
            <button className="browse-btn" onClick={handleBrowseClick}>
              📁 Browse Files
            </button>
          </div>
        )}
      </div>
      
      <div className="upload-info">
        <div className="info-card">
          <h4>Expected CSV Format:</h4>
          <ul>
            <li>Columns: equipment_name, type, flowrate, pressure, temperature</li>
            <li>First row should contain headers</li>
            <li>Numeric values for flowrate, pressure, temperature</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;
