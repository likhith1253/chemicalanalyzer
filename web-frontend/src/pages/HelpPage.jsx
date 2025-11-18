import React from 'react';
import './HelpPage.css';

const HelpPage = () => {
  return (
    <div className="help-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Help & Documentation ❓</h1>
          <p className="page-subtitle">Get help using ChemViz</p>
        </div>
      </div>

      <div className="help-content">
        <section className="help-section">
          <h2 className="section-title">Getting Started</h2>
          <div className="help-card">
            <h3>1. Upload CSV File</h3>
            <p>Go to the Dashboard and upload a CSV file with the following columns:</p>
            <ul>
              <li><strong>Equipment Name</strong> - Name of the equipment</li>
              <li><strong>Type</strong> - Type of equipment (e.g., Pump, Valve, Tank)</li>
              <li><strong>Flowrate</strong> - Flow rate value (numeric)</li>
              <li><strong>Pressure</strong> - Pressure value (numeric)</li>
              <li><strong>Temperature</strong> - Temperature value (numeric)</li>
            </ul>
          </div>

          <div className="help-card">
            <h3>2. View Analysis</h3>
            <p>After uploading, you'll see:</p>
            <ul>
              <li>Summary statistics (total count, averages)</li>
              <li>Type distribution chart</li>
              <li>Preview table with first 100 rows</li>
            </ul>
          </div>

          <div className="help-card">
            <h3>3. Download Reports</h3>
            <p>Click the "Download PDF" button to generate a comprehensive PDF report of your dataset.</p>
          </div>
        </section>

        <section className="help-section">
          <h2 className="section-title">Features</h2>
          <div className="help-card">
            <h3>Dashboard</h3>
            <p>Upload CSV files and view real-time analysis results.</p>
          </div>

          <div className="help-card">
            <h3>History</h3>
            <p>View your last 5 uploaded datasets and their details.</p>
          </div>

          <div className="help-card">
            <h3>Visualizations</h3>
            <p>Interactive charts showing flowrate, pressure, temperature distributions, and equipment type breakdown.</p>
          </div>
        </section>
      </div>
    </div>
  );
};

export default HelpPage;

