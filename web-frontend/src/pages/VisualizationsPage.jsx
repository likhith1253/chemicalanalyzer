import React, { useState, useEffect } from 'react';
import { datasetAPI } from '../api/client';
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
import { Bar, Pie, Line } from 'react-chartjs-2';
import './VisualizationsPage.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const VisualizationsPage = () => {
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    setIsLoading(true);
    try {
      const data = await datasetAPI.fetchDatasets();
      setDatasets(Array.isArray(data) ? data : []);
      // Auto-select first dataset if available
      if (data && data.length > 0 && !selectedDataset) {
        loadDatasetDetails(data[0].id);
      }
    } catch (error) {
      console.error('Error fetching datasets:', error);
      setDatasets([]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadDatasetDetails = async (datasetId) => {
    try {
      const data = await datasetAPI.fetchDatasetDetail(datasetId);
      setSelectedDataset(data || {});
    } catch (error) {
      console.error('Error loading dataset details:', error);
    }
  };

  const handleDatasetChange = (e) => {
    const datasetId = parseInt(e.target.value);
    if (datasetId) {
      loadDatasetDetails(datasetId);
    } else {
      setSelectedDataset(null);
    }
  };

  // Prepare chart data from selected dataset
  const prepareChartData = () => {
    if (!selectedDataset || !selectedDataset.preview_rows) {
      return null;
    }

    const rows = selectedDataset.preview_rows || [];
    const flowrates = rows.map(r => Number(r.flowrate) || 0).filter(v => v > 0);
    const pressures = rows.map(r => Number(r.pressure) || 0).filter(v => v > 0);
    const temperatures = rows.map(r => Number(r.temperature) || 0).filter(v => v > 0);

    return {
      flowrates,
      pressures,
      temperatures,
      typeDistribution: selectedDataset.type_distribution || {}
    };
  };

  const chartData = prepareChartData();

  // Flowrate Distribution Chart
  const flowrateChartData = chartData ? {
    labels: chartData.flowrates.map((_, i) => `Record ${i + 1}`),
    datasets: [{
      label: 'Flowrate',
      data: chartData.flowrates,
      backgroundColor: 'rgba(102, 126, 234, 0.6)',
      borderColor: 'rgba(102, 126, 234, 1)',
      borderWidth: 2,
    }]
  } : null;

  // Pressure Distribution Chart
  const pressureChartData = chartData ? {
    labels: chartData.pressures.map((_, i) => `Record ${i + 1}`),
    datasets: [{
      label: 'Pressure',
      data: chartData.pressures,
      backgroundColor: 'rgba(237, 137, 54, 0.6)',
      borderColor: 'rgba(237, 137, 54, 1)',
      borderWidth: 2,
    }]
  } : null;

  // Temperature Distribution Chart
  const temperatureChartData = chartData ? {
    labels: chartData.temperatures.map((_, i) => `Record ${i + 1}`),
    datasets: [{
      label: 'Temperature',
      data: chartData.temperatures,
      backgroundColor: 'rgba(159, 122, 234, 0.6)',
      borderColor: 'rgba(159, 122, 234, 1)',
      borderWidth: 2,
    }]
  } : null;

  // Type Distribution Pie Chart
  const typePieChartData = chartData && chartData.typeDistribution ? {
    labels: Object.keys(chartData.typeDistribution),
    datasets: [{
      data: Object.values(chartData.typeDistribution),
      backgroundColor: [
        'rgba(102, 126, 234, 0.8)',
        'rgba(72, 187, 120, 0.8)',
        'rgba(237, 137, 54, 0.8)',
        'rgba(159, 122, 234, 0.8)',
        'rgba(255, 107, 107, 0.8)',
        'rgba(56, 178, 172, 0.8)',
      ],
      borderWidth: 2,
      borderColor: '#fff',
    }]
  } : null;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        font: {
          size: 16,
          weight: '600',
        },
        padding: {
          bottom: 20,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
      x: {
        grid: {
          display: false,
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
      },
      title: {
        display: true,
        font: {
          size: 16,
          weight: '600',
        },
        padding: {
          bottom: 20,
        },
      },
    },
  };

  return (
    <div className="visualizations-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Visualizations 📈</h1>
          <p className="page-subtitle">Interactive charts and data visualizations</p>
        </div>
        <div className="header-actions">
          <select
            className="dataset-select"
            value={selectedDataset?.id || ''}
            onChange={handleDatasetChange}
            disabled={isLoading || datasets.length === 0}
          >
            <option value="">Select a dataset...</option>
            {datasets.map(ds => (
              <option key={ds.id} value={ds.id}>
                {ds.name} (ID: {ds.id})
              </option>
            ))}
          </select>
          <button 
            className="action-btn refresh-btn"
            onClick={fetchDatasets}
            disabled={isLoading}
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      <div className="visualizations-content">
        {isLoading ? (
          <div className="loading-state">
            <div className="loading-spinner-large"></div>
            <p>Loading datasets...</p>
          </div>
        ) : !selectedDataset ? (
          <div className="empty-state">
            <div className="empty-icon">📈</div>
            <h3>No Dataset Selected</h3>
            <p>Select a dataset from the dropdown above to view visualizations</p>
          </div>
        ) : (
          <>
            {/* Flowrate Distribution */}
            {flowrateChartData && (
              <section className="viz-section">
                <h2 className="section-title">Flowrate Distribution</h2>
                <div className="chart-container">
                  <Bar data={flowrateChartData} options={{ ...chartOptions, plugins: { ...chartOptions.plugins, title: { ...chartOptions.plugins.title, text: 'Flowrate Values by Record' } } }} />
                </div>
              </section>
            )}

            {/* Pressure Distribution */}
            {pressureChartData && (
              <section className="viz-section">
                <h2 className="section-title">Pressure Distribution</h2>
                <div className="chart-container">
                  <Bar data={pressureChartData} options={{ ...chartOptions, plugins: { ...chartOptions.plugins, title: { ...chartOptions.plugins.title, text: 'Pressure Values by Record' } } }} />
                </div>
              </section>
            )}

            {/* Temperature Distribution */}
            {temperatureChartData && (
              <section className="viz-section">
                <h2 className="section-title">Temperature Distribution</h2>
                <div className="chart-container">
                  <Bar data={temperatureChartData} options={{ ...chartOptions, plugins: { ...chartOptions.plugins, title: { ...chartOptions.plugins.title, text: 'Temperature Values by Record' } } }} />
                </div>
              </section>
            )}

            {/* Type Distribution Pie Chart */}
            {typePieChartData && (
              <section className="viz-section">
                <h2 className="section-title">Equipment Type Distribution</h2>
                <div className="chart-container">
                  <Pie data={typePieChartData} options={{ ...pieChartOptions, plugins: { ...pieChartOptions.plugins, title: { ...pieChartOptions.plugins.title, text: 'Equipment Types' } } }} />
                </div>
              </section>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default VisualizationsPage;

