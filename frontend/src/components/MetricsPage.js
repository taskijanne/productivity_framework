import React, { useState, useEffect } from 'react';
import MetricsChart from './MetricsChart';

const API_BASE_URL = 'http://localhost:8000';

function MetricsPage() {
  const [metricTypes, setMetricTypes] = useState([]);
  const [xAxisMetric, setXAxisMetric] = useState('');
  const [yAxisMetric, setYAxisMetric] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [intervals, setIntervals] = useState(1);
  const [results, setResults] = useState(null);
  const [correlations, setCorrelations] = useState([]);
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
        // API returns { metric_types: [...], descriptions: {...} }
        const types = data.metric_types || [];
        setMetricTypes(types);
        // Set defaults if available
        if (types.length >= 2) {
          setXAxisMetric(types[0]);
          setYAxisMetric(types[1]);
        } else if (types.length === 1) {
          setXAxisMetric(types[0]);
          setYAxisMetric(types[0]);
        }
      } catch (err) {
        setError('Failed to load metric types. Make sure the backend is running.');
        console.error('Error fetching metric types:', err);
      }
    };

    fetchMetricTypes();

    // Set default dates (last 30 days)
    const today = new Date();
    const thirtyDaysAgo = new Date(today);
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    
    setEndDate(formatDateForInput(today));
    setStartDate(formatDateForInput(thirtyDaysAgo));
  }, []);

  const formatDateForInput = (date) => {
    return date.toISOString().split('T')[0];
  };

  const formatDateTimeForAPI = (dateStr) => {
    return `${dateStr}T00:00:00`;
  };

  const handleCalculate = async () => {
    if (!xAxisMetric || !yAxisMetric || !startDate || !endDate) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const metricTypesParam = `${xAxisMetric},${yAxisMetric}`;
      const startTimeParam = formatDateTimeForAPI(startDate);
      const endTimeParam = formatDateTimeForAPI(endDate);
      
      const url = `${API_BASE_URL}/metrics?metric_types=${metricTypesParam}&start_time=${startTimeParam}&end_time=${endTimeParam}&intervals=${intervals}`;
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`API request failed: ${response.statusText}`);
      }
      
      const data = await response.json();
      // API returns { intervals: [...], correlations: [...] }
      setResults(data.intervals || data);
      setCorrelations(data.correlations || []);
    } catch (err) {
      setError(`Error fetching metrics: ${err.message}`);
      console.error('Error fetching metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="metrics-page">
      <h2>Metrics Analysis</h2>
      
      <div className="metrics-form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="x-axis-metric">X-Axis Metric</label>
            <select
              id="x-axis-metric"
              value={xAxisMetric}
              onChange={(e) => setXAxisMetric(e.target.value)}
            >
              <option value="">Select metric...</option>
              {metricTypes.map((type) => (
                <option key={type} value={type}>
                  {type.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="y-axis-metric">Y-Axis Metric</label>
            <select
              id="y-axis-metric"
              value={yAxisMetric}
              onChange={(e) => setYAxisMetric(e.target.value)}
            >
              <option value="">Select metric...</option>
              {metricTypes.map((type) => (
                <option key={type} value={type}>
                  {type.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>
        </div>

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
            <label htmlFor="intervals">Intervals</label>
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

        <div className="form-actions">
          <button 
            className="calculate-btn" 
            onClick={handleCalculate}
            disabled={loading}
          >
            {loading ? 'Calculating...' : 'Calculate'}
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
          <MetricsChart 
            data={results} 
            xAxisMetric={xAxisMetric} 
            yAxisMetric={yAxisMetric}
            correlations={correlations}
          />
        </div>
      )}
    </div>
  );
}

export default MetricsPage;
