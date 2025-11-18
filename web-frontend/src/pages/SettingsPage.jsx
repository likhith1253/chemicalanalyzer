import React from 'react';
import './SettingsPage.css';

const SettingsPage = () => {
  return (
    <div className="settings-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Settings ⚙️</h1>
          <p className="page-subtitle">Manage your account and application settings</p>
        </div>
      </div>

      <div className="settings-content">
        <section className="settings-section">
          <h2 className="section-title">Account Settings</h2>
          <div className="settings-card">
            <p>Settings functionality coming soon...</p>
          </div>
        </section>
      </div>
    </div>
  );
};

export default SettingsPage;

