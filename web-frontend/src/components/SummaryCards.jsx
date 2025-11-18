import React from 'react';
import './SummaryCards.css';

const SummaryCards = ({ data }) => {
  // Safely handle undefined/null data
  if (!data) {
    return null;
  }
  
  const cards = [
    {
      title: 'Total Records',
      value: data.total_count || 0,
      icon: '📊',
      color: '#667eea',
      bgColor: 'rgba(102, 126, 234, 0.1)',
    },
    {
      title: 'Avg Flowrate',
      value: (data.avg_flowrate !== null && data.avg_flowrate !== undefined) ? Number(data.avg_flowrate).toFixed(2) : 'N/A',
      unit: (data.avg_flowrate !== null && data.avg_flowrate !== undefined) ? 'L/min' : '',
      icon: '💧',
      color: '#48bb78',
      bgColor: 'rgba(72, 187, 120, 0.1)',
    },
    {
      title: 'Avg Pressure',
      value: (data.avg_pressure !== null && data.avg_pressure !== undefined) ? Number(data.avg_pressure).toFixed(2) : 'N/A',
      unit: (data.avg_pressure !== null && data.avg_pressure !== undefined) ? 'bar' : '',
      icon: '🔥',
      color: '#ed8936',
      bgColor: 'rgba(237, 137, 54, 0.1)',
    },
    {
      title: 'Avg Temperature',
      value: (data.avg_temperature !== null && data.avg_temperature !== undefined) ? Number(data.avg_temperature).toFixed(2) : 'N/A',
      unit: (data.avg_temperature !== null && data.avg_temperature !== undefined) ? '°C' : '',
      icon: '🌡️',
      color: '#9f7aea',
      bgColor: 'rgba(159, 122, 234, 0.1)',
    },
  ];

  return (
    <div className="summary-cards">
      <div className="cards-grid">
        {cards.map((card, index) => (
          <div
            key={index}
            className="summary-card"
            style={{
              '--card-color': card.color,
              '--card-bg': card.bgColor,
            }}
          >
            <div className="card-icon">
              <span>{card.icon}</span>
            </div>
            <div className="card-content">
              <h3 className="card-title">{card.title}</h3>
              <div className="card-value">
                <span className="value">{card.value}</span>
                {card.unit && <span className="unit">{card.unit}</span>}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {data.type_distribution && Object.keys(data.type_distribution).length > 0 && (
        <div className="type-distribution-summary">
          <h3>Equipment Types</h3>
          <div className="type-tags">
            {Object.entries(data.type_distribution).map(([type, count]) => (
              <div key={type} className="type-tag">
                <span className="type-name">{type}</span>
                <span className="type-count">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SummaryCards;
