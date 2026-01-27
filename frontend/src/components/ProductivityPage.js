import React, { useState, useEffect } from 'react';
import ProductivityCharts from './ProductivityCharts';

const API_BASE_URL = 'http://localhost:8000';

function ProductivityPage() {
  const [metricTypes, setMetricTypes] = useState([]);
  const [metricDescriptions, setMetricDescriptions] = useState({});
  const [selectedMetrics, setSelectedMetrics] = useState([
    { metric: 'LEAD_TIME_FOR_CHANGES', weight: 1.0 },
    { metric: 'CHANGE_FAILURE_RATE', weight: 1.0 },
    { metric: 'MEAN_TIME_TO_RECOVER', weight: 1.0 },
    { metric: 'DEPLOYMENT_FREQUENCY', weight: 1.0 },
  ]);
  const [startDate, setStartDate] = useState('2025-01-01');
  const [endDate, setEndDate] = useState('2025-12-31');
  const [intervals, setIntervals] = useState(12);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch available metric types on component mount
  useEffect(() => {
    const fetchMetricTypes = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/metric_types`);
        if (!response.ok) {
          throw new Error('Failed to fetch metric types');
        }
        const data = await response.json();
        const types = data.metric_types || [];
        setMetricTypes(types);
        setMetricDescriptions(data.descriptions || {});
      } catch (err) {
        setError('Failed to load metric types. Make sure the backend is running.');
        console.error('Error fetching metric types:', err);
      }
    };

    fetchMetricTypes();
  }, []);

  const formatDateForInput = (date) => {
    return date.toISOString().split('T')[0];
  };

  const formatDateTimeForAPI = (dateStr, isEnd = false) => {
    if (isEnd) {
      return `${dateStr}T23:59:59`;
    }
    return `${dateStr}T00:00:00`;
  };

  const handleAddMetric = () => {
    if (metricTypes.length === 0) return;
    
    // Find first metric not already selected
    const availableMetric = metricTypes.find(
      (m) => !selectedMetrics.some((sm) => sm.metric === m)
    );
    
    if (availableMetric) {
      setSelectedMetrics([
        ...selectedMetrics,
        { metric: availableMetric, weight: 1.0 }
      ]);
    }
  };

  const handleRemoveMetric = (index) => {
    setSelectedMetrics(selectedMetrics.filter((_, i) => i !== index));
  };

  const handleMetricChange = (index, field, value) => {
    const updated = [...selectedMetrics];
    if (field === 'weight') {
      // Ensure weight is between 0 and 1
      value = Math.max(0, Math.min(1, parseFloat(value) || 0));
    }
    updated[index] = { ...updated[index], [field]: value };
    setSelectedMetrics(updated);
  };

  const handleCalculate = async () => {
    if (selectedMetrics.length === 0) {
      setError('Please add at least one metric');
      return;
    }
    if (!startDate || !endDate) {
      setError('Please fill in start and end dates');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const requestBody = {
        start_time: formatDateTimeForAPI(startDate),
        end_time: formatDateTimeForAPI(endDate, true),
        intervals: intervals,
        metrics: selectedMetrics.map((m) => ({
          metric: m.metric,
          weight: m.weight
        }))
      };

      const response = await fetch(`${API_BASE_URL}/cps`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.statusText}`);
      }
      
      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(`Error calculating CPS: ${err.message}`);
      console.error('Error calculating CPS:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddAllMetrics = () => {
    const allMetrics = metricTypes.map((m) => ({
      metric: m,
      weight: 1.0
    }));
    setSelectedMetrics(allMetrics);
  };

  const handleClearMetrics = () => {
    setSelectedMetrics([]);
  };

  return (
    <div className="productivity-page">
      <h2>Productivity Analysis (CPS)</h2>
      <p className="page-description">
        Calculate the Composite Productivity Score (CPS) by selecting metrics and assigning weights.
        The CPS aggregates z-scores of selected metrics to measure overall productivity trends.
      </p>
      
      <div className="productivity-form">
        <div className="form-section">
          <h3>Time Range & Intervals</h3>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="start-date">Start Date</label>
              <input
                type="date"
                id="start-date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="end-date">End Date</label>
              <input
                type="date"
                id="end-date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="intervals">Number of Intervals</label>
              <input
                type="number"
                id="intervals"
                min="1"
                max="100"
                value={intervals}
                onChange={(e) => setIntervals(Math.max(1, parseInt(e.target.value) || 1))}
              />
            </div>
          </div>
        </div>

        <div className="form-section">
          <div className="metrics-header">
            <h3>Metrics & Weights</h3>
            <div className="metrics-actions">
              <button 
                className="secondary-btn"
                onClick={handleAddAllMetrics}
                disabled={selectedMetrics.length === metricTypes.length}
              >
                Add All
              </button>
              <button 
                className="secondary-btn"
                onClick={handleClearMetrics}
                disabled={selectedMetrics.length === 0}
              >
                Clear All
              </button>
              <button 
                className="secondary-btn add-metric-btn"
                onClick={handleAddMetric}
                disabled={selectedMetrics.length >= metricTypes.length}
              >
                + Add Metric
              </button>
            </div>
          </div>

          {selectedMetrics.length === 0 ? (
            <div className="no-metrics-message">
              No metrics selected. Click "Add Metric" or "Add All" to get started.
            </div>
          ) : (
            <div className="selected-metrics-list">
              {selectedMetrics.map((sm, index) => (
                <div key={index} className="metric-row">
                  <div className="metric-select-group">
                    <label>Metric</label>
                    <select
                      value={sm.metric}
                      onChange={(e) => handleMetricChange(index, 'metric', e.target.value)}
                    >
                      {metricTypes.map((type) => (
                        <option 
                          key={type} 
                          value={type}
                          disabled={selectedMetrics.some((m, i) => i !== index && m.metric === type)}
                        >
                          {type.replace(/_/g, ' ')}
                        </option>
                      ))}
                    </select>
                    {metricDescriptions[sm.metric] && (
                      <span className="metric-description">
                        {metricDescriptions[sm.metric]}
                      </span>
                    )}
                  </div>
                  
                  <div className="weight-group">
                    <label>Weight (0-1)</label>
                    <input
                      type="number"
                      step="0.1"
                      min="0"
                      max="1"
                      value={sm.weight}
                      onChange={(e) => handleMetricChange(index, 'weight', e.target.value)}
                    />
                  </div>
                  
                  <button 
                    className="remove-metric-btn"
                    onClick={() => handleRemoveMetric(index)}
                    title="Remove metric"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="form-actions">
          <button 
            className="calculate-btn" 
            onClick={handleCalculate}
            disabled={loading || selectedMetrics.length === 0}
          >
            {loading ? 'Calculating...' : 'Calculate CPS'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {results && (
        <div className="results-section">
          <ProductivityCharts 
            data={results}
            selectedMetrics={selectedMetrics}
          />
        </div>
      )}
    </div>
  );
}

export default ProductivityPage;
