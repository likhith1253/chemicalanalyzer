import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import './TypeDistributionChart.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const TypeDistributionChart = ({ data }) => {
  // Safely handle undefined/null data
  if (!data || !data.type_distribution || typeof data.type_distribution !== 'object') {
    return (
      <div className="chart-empty-state">
        <div className="empty-icon">📊</div>
        <h3>No Type Distribution Data</h3>
        <p>Upload a dataset with equipment types to see the distribution chart</p>
      </div>
    );
  }

  const typeDist = data.type_distribution;
  const types = Object.keys(typeDist);
  const counts = Object.values(typeDist);
  
  if (types.length === 0) {
    return (
      <div className="chart-empty-state">
        <div className="empty-icon">📊</div>
        <h3>No Type Distribution Data</h3>
        <p>Upload a dataset with equipment types to see the distribution chart</p>
      </div>
    );
  }

  // Generate colors for the chart
  const generateColors = (count) => {
    const colors = [
      'rgba(102, 126, 234, 0.8)',
      'rgba(72, 187, 120, 0.8)',
      'rgba(237, 137, 54, 0.8)',
      'rgba(159, 122, 234, 0.8)',
      'rgba(255, 107, 107, 0.8)',
      'rgba(56, 178, 172, 0.8)',
      'rgba(246, 194, 62, 0.8)',
      'rgba(237, 100, 166, 0.8)',
    ];
    
    const borderColors = colors.map(color => color.replace('0.8', '1'));
    
    return {
      backgroundColor: colors.slice(0, count),
      borderColor: borderColors.slice(0, count),
      borderWidth: 2,
    };
  };

  const colors = generateColors(types.length);

  // Bar chart data
  const barChartData = {
    labels: types,
    datasets: [
      {
        label: 'Equipment Count',
        data: counts,
        ...colors,
        borderRadius: 8,
        borderSkipped: false,
      },
    ],
  };

  // Pie chart data
  const pieChartData = {
    labels: types,
    datasets: [
      {
        data: counts,
        ...colors,
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          padding: 15,
          font: {
            size: 12,
            weight: '500',
          },
          color: '#4a5568',
        },
      },
      title: {
        display: true,
        text: 'Equipment Type Distribution',
        font: {
          size: 16,
          weight: '600',
        },
        color: '#2d3748',
        padding: {
          bottom: 20,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: {
          size: 14,
          weight: '600',
        },
        bodyFont: {
          size: 13,
        },
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            const value = context.parsed?.y || context.parsed || 0;
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : '0.0';
            return `${label}: ${value} (${percentage}%)`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
          drawBorder: false,
        },
        ticks: {
          font: {
            size: 12,
          },
          color: '#718096',
        },
      },
      x: {
        grid: {
          display: false,
        },
        ticks: {
          font: {
            size: 12,
          },
          color: '#718096',
        },
      },
    },
  };

  const pieChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          padding: 15,
          font: {
            size: 12,
            weight: '500',
          },
          color: '#4a5568',
        },
      },
      title: {
        display: true,
        text: 'Equipment Type Distribution',
        font: {
          size: 16,
          weight: '600',
        },
        color: '#2d3748',
        padding: {
          bottom: 20,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: {
          size: 14,
          weight: '600',
        },
        bodyFont: {
          size: 13,
        },
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            const value = context.parsed || 0;
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : '0.0';
            return `${label}: ${value} (${percentage}%)`;
          },
        },
      },
    },
  };

  return (
    <div className="type-distribution-chart">
      <div className="chart-container">
        <div className="chart-wrapper">
          <Bar data={barChartData} options={chartOptions} />
        </div>
      </div>
      
      <div className="chart-container">
        <div className="chart-wrapper">
          <Pie data={pieChartData} options={pieChartOptions} />
        </div>
      </div>
    </div>
  );
};

export default TypeDistributionChart;
