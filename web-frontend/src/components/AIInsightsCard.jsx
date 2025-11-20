import React, { useState } from 'react';
import { datasetAPI } from '../api/client';
import './AIInsightsCard.css';

const AIInsightsCard = ({ datasetId }) => {
  const [insights, setInsights] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [displayedText, setDisplayedText] = useState('');

  const handleGenerateInsights = async () => {
    if (!datasetId) return;
    
    setIsLoading(true);
    setIsGenerating(true);
    setError(null);
    setInsights('');
    setDisplayedText('');

    try {
      const response = await datasetAPI.analyzeDataset(datasetId);
      const insightsText = response.insights || '';
      setInsights(insightsText);
      
      // Typewriter effect
      let currentIndex = 0;
      const typingInterval = setInterval(() => {
        if (currentIndex < insightsText.length) {
          setDisplayedText(insightsText.substring(0, currentIndex + 1));
          currentIndex++;
        } else {
          clearInterval(typingInterval);
          setIsGenerating(false);
        }
      }, 20); // Adjust speed here (lower = faster)
      
    } catch (err) {
      setError(err.response?.data?.detail || err.response?.data?.error || 'Service unavailable. Please check your API configuration.');
      setIsGenerating(false);
    } finally {
      setIsLoading(false);
    }
  };

  if (!datasetId) {
    return null;
  }

  return (
    <div className="ai-insights-card">
      <div className="ai-card-header">
        <div className="ai-card-icon">
          <span>✨</span>
        </div>
        <div className="ai-card-title-section">
          <h3 className="ai-card-title">AI Insights</h3>
          <p className="ai-card-subtitle">Get intelligent analysis of your equipment data</p>
        </div>
      </div>

      <div className="ai-card-content">
        {!insights && !error && !isLoading && (
          <div className="ai-card-empty">
            <p>Click the button below to generate AI-powered insights based on your equipment statistics.</p>
          </div>
        )}

        {isLoading && !insights && (
          <div className="ai-card-loading">
            <div className="ai-loading-spinner"></div>
            <p>Generating insights...</p>
          </div>
        )}

        {error && (
          <div className="ai-card-error">
            <div className="error-icon">⚠️</div>
            <p className="error-message">{error}</p>
            <p className="error-hint">Make sure GOOGLE_GEMINI_API_KEY is configured in your backend environment.</p>
          </div>
        )}

        {insights && (
          <div className="ai-card-insights">
            <div className="insights-text">
              {isGenerating ? (
                <span>{displayedText}<span className="typing-cursor">|</span></span>
              ) : (
                <span>{insights}</span>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="ai-card-actions">
        <button
          className="ai-generate-btn"
          onClick={handleGenerateInsights}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <span className="btn-spinner"></span>
              Generating...
            </>
          ) : (
            <>
              ✨ Generate AI Analysis
            </>
          )}
        </button>
        {insights && !isGenerating && (
          <button
            className="ai-regenerate-btn"
            onClick={handleGenerateInsights}
            disabled={isLoading}
          >
            🔄 Regenerate
          </button>
        )}
      </div>
    </div>
  );
};

export default AIInsightsCard;

