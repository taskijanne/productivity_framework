import React from 'react';
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
  Cell,
} from 'recharts';

// Color palette for different metrics
const METRIC_COLORS = {
  'LEAD_TIME_FOR_CHANGES': '#8884d8',
  'CHANGE_FAILURE_RATE': '#82ca9d',
  'MEAN_TIME_TO_RECOVER': '#ffc658',
  'DEPLOYMENT_FREQUENCY': '#ff7300',
  'DEFAULT_0': '#00C49F',
  'DEFAULT_1': '#FFBB28',
  'DEFAULT_2': '#FF8042',
  'DEFAULT_3': '#0088FE',
  'DEFAULT_4': '#e94560',
  'DEFAULT_5': '#a855f7',
};

const getMetricColor = (metricType, index) => {
  return METRIC_COLORS[metricType] || METRIC_COLORS[`DEFAULT_${index % 6}`] || '#8884d8';
};

function ProductivityCharts({ data, selectedMetrics }) {
  if (!data || !data.intervals || data.intervals.length === 0) {
    return (
      <div className="no-data-message">
        No data available for the selected parameters.
      </div>
    );
  }

  const { intervals } = data;

  // Format date for display
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // Prepare data for CPS line chart
  const cpsChartData = intervals.map((interval) => ({
    name: `#${interval.interval_number}`,
    date: formatDate(interval.start_time),
    fullDate: interval.start_time,
    cps: interval.cps,
    interval_number: interval.interval_number,
  }));

  // Get unique metric types from the data
  const metricTypesInData = intervals[0]?.metrics.map((m) => m.metric_type) || [];

  // Prepare data for stacked bar chart with proper diverging stacks from y=0
  // Positive values stack upward, negative values stack downward - both from y=0
  const stackedChartData = intervals.map((interval) => {
    const dataPoint = {
      name: `#${interval.interval_number}`,
      date: formatDate(interval.start_time),
      fullDate: interval.start_time,
      interval_number: interval.interval_number,
    };

    // For each metric, create _pos and _neg keys
    // Positive metrics go into positive stack, negative into negative stack
    interval.metrics.forEach((metric) => {
      const value = metric.z_score_weighted;
      if (value >= 0) {
        dataPoint[`${metric.metric_type}_pos`] = value;
        dataPoint[`${metric.metric_type}_neg`] = 0;
      } else {
        dataPoint[`${metric.metric_type}_pos`] = 0;
        dataPoint[`${metric.metric_type}_neg`] = value;
      }
      // Store additional info for tooltip
      dataPoint[`${metric.metric_type}_value`] = value;
      dataPoint[`${metric.metric_type}_mean`] = metric.mean_value;
      dataPoint[`${metric.metric_type}_obs`] = metric.amount_of_observations;
    });

    return dataPoint;
  });

  // Custom tooltip for CPS chart
  const CPSTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const dataPoint = payload[0].payload;
      return (
        <div className="chart-tooltip">
          <p className="tooltip-title">Interval {dataPoint.interval_number}</p>
          <p className="tooltip-time">{dataPoint.fullDate}</p>
          <div className="tooltip-metrics">
            <div className="tooltip-metric">
              <strong>CPS:</strong>
              <span className={dataPoint.cps >= 0 ? 'positive-value' : 'negative-value'}>
                {dataPoint.cps.toFixed(4)}
              </span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  // Custom tooltip for stacked bar chart
  const StackedTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const dataPoint = payload[0].payload;
      return (
        <div className="chart-tooltip stacked-tooltip">
          <p className="tooltip-title">Interval {dataPoint.interval_number}</p>
          <p className="tooltip-time">{dataPoint.fullDate}</p>
          <div className="tooltip-metrics">
            {metricTypesInData.map((metricType, index) => {
              const value = dataPoint[`${metricType}_value`];
              const mean = dataPoint[`${metricType}_mean`];
              const obs = dataPoint[`${metricType}_obs`];
              return (
                <div key={metricType} className="tooltip-metric-detail">
                  <div 
                    className="tooltip-metric-color" 
                    style={{ backgroundColor: getMetricColor(metricType, index) }}
                  />
                  <div className="tooltip-metric-info">
                    <strong>{metricType.replace(/_/g, ' ')}</strong>
                    <span className={value >= 0 ? 'positive-value' : 'negative-value'}>
                      Z: {value?.toFixed(4)}
                    </span>
                    <span className="metric-mean">Mean: {mean?.toFixed(2)} ({obs} obs)</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      );
    }
    return null;
  };

  // Calculate summary statistics
  const avgCPS = intervals.reduce((sum, i) => sum + i.cps, 0) / intervals.length;
  const maxCPS = Math.max(...intervals.map((i) => i.cps));
  const minCPS = Math.min(...intervals.map((i) => i.cps));
  const trend = intervals.length > 1 
    ? intervals[intervals.length - 1].cps - intervals[0].cps 
    : 0;

  return (
    <div className="productivity-charts">
      {/* Summary Statistics */}
      <div className="cps-summary">
        <div className="summary-card">
          <span className="summary-label">Average CPS</span>
          <span className={`summary-value ${avgCPS >= 0 ? 'positive' : 'negative'}`}>
            {avgCPS.toFixed(4)}
          </span>
        </div>
        <div className="summary-card">
          <span className="summary-label">Max CPS</span>
          <span className={`summary-value ${maxCPS >= 0 ? 'positive' : 'negative'}`}>
            {maxCPS.toFixed(4)}
          </span>
        </div>
        <div className="summary-card">
          <span className="summary-label">Min CPS</span>
          <span className={`summary-value ${minCPS >= 0 ? 'positive' : 'negative'}`}>
            {minCPS.toFixed(4)}
          </span>
        </div>
        <div className="summary-card">
          <span className="summary-label">Trend</span>
          <span className={`summary-value ${trend >= 0 ? 'positive' : 'negative'}`}>
            {trend >= 0 ? '↑' : '↓'} {Math.abs(trend).toFixed(4)}
          </span>
        </div>
      </div>

      {/* CPS Line Chart */}
      <div className="chart-section">
        <h3>Composite Productivity Score (CPS) Over Time</h3>
        <p className="chart-description">
          The CPS combines weighted z-scores of all selected metrics. 
          Positive values indicate above-average performance.
        </p>
        <div className="chart-wrapper">
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={cpsChartData} margin={{ top: 20, right: 30, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis 
                dataKey="date" 
                tick={{ fill: '#ccc' }}
                axisLine={{ stroke: '#444' }}
              />
              <YAxis 
                tick={{ fill: '#ccc' }}
                axisLine={{ stroke: '#444' }}
                tickFormatter={(value) => value.toFixed(2)}
              />
              <Tooltip content={<CPSTooltip />} />
              <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
              <Line
                type="monotone"
                dataKey="cps"
                stroke="#e94560"
                strokeWidth={3}
                dot={{ fill: '#e94560', strokeWidth: 2, r: 6 }}
                activeDot={{ r: 8, stroke: '#fff', strokeWidth: 2 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Stacked Bar Chart for Z-Scores */}
      <div className="chart-section">
        <h3>Metric Z-Score Contributions by Interval</h3>
        <p className="chart-description">
          Each bar shows the weighted z-score contribution of each metric. 
          Positive z-scores stack upward, negative z-scores stack downward from zero.
        </p>
        
        {/* Custom Legend */}
        <div className="stacked-legend">
          {metricTypesInData.map((metricType, index) => (
            <div key={metricType} className="legend-item">
              <div 
                className="legend-color" 
                style={{ backgroundColor: getMetricColor(metricType, index) }}
              />
              <span className="legend-label">{metricType.replace(/_/g, ' ')}</span>
            </div>
          ))}
        </div>

        <div className="chart-wrapper">
          <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={stackedChartData} margin={{ top: 20, right: 30, bottom: 20, left: 20 }} barCategoryGap="20%">
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis 
                xAxisId="main"
                dataKey="date" 
                tick={{ fill: '#ccc' }}
                axisLine={{ stroke: '#444' }}
              />
              <XAxis 
                xAxisId="overlay"
                dataKey="date" 
                hide={true}
              />
              <YAxis 
                tick={{ fill: '#ccc' }}
                axisLine={{ stroke: '#444' }}
                tickFormatter={(value) => value.toFixed(2)}
                label={{
                  value: 'Z-Score (Weighted)',
                  angle: -90,
                  position: 'insideLeft',
                  fill: '#ccc',
                }}
              />
              <Tooltip content={<StackedTooltip />} />
              <ReferenceLine y={0} stroke="#888" strokeWidth={2} xAxisId="main" />
              
              {/* Positive stack - uses main X axis */}
              {metricTypesInData.map((metricType, index) => (
                <Bar
                  key={`${metricType}_pos`}
                  dataKey={`${metricType}_pos`}
                  xAxisId="main"
                  stackId="positive"
                  fill={getMetricColor(metricType, index)}
                  name={metricType.replace(/_/g, ' ')}
                />
              ))}
              
              {/* Negative stack - uses overlay X axis to appear at same position */}
              {metricTypesInData.map((metricType, index) => (
                <Bar
                  key={`${metricType}_neg`}
                  dataKey={`${metricType}_neg`}
                  xAxisId="overlay"
                  stackId="negative"
                  fill={getMetricColor(metricType, index)}
                  name={metricType.replace(/_/g, ' ')}
                />
              ))}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Interval Data Table */}
      <div className="interval-details">
        <h3>Interval Details</h3>
        <div className="table-wrapper">
          <table className="interval-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Period</th>
                <th>CPS</th>
                {metricTypesInData.map((metricType) => (
                  <th key={metricType}>
                    {metricType.replace(/_/g, ' ').split(' ').map(w => w[0]).join('')}
                    <span className="th-tooltip">{metricType.replace(/_/g, ' ')}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {intervals.map((interval) => (
                <tr key={interval.interval_number}>
                  <td>{interval.interval_number}</td>
                  <td className="period-cell">
                    {formatDate(interval.start_time)} - {formatDate(interval.end_time)}
                  </td>
                  <td className={interval.cps >= 0 ? 'positive-value' : 'negative-value'}>
                    {interval.cps.toFixed(3)}
                  </td>
                  {metricTypesInData.map((metricType) => {
                    const metric = interval.metrics.find((m) => m.metric_type === metricType);
                    const value = metric?.z_score_weighted ?? 0;
                    return (
                      <td 
                        key={metricType}
                        className={value >= 0 ? 'positive-value' : 'negative-value'}
                      >
                        {value.toFixed(3)}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default ProductivityCharts;
