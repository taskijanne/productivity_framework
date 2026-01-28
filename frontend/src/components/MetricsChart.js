import React, { useState } from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
  Line,
  ComposedChart,
} from 'recharts';

function MetricsChart({ data, xAxisMetric, yAxisMetric, correlations = [] }) {
  const [hoveredPoint, setHoveredPoint] = useState(null);

  // Find the correlation for the current X and Y metrics
  const currentCorrelation = correlations.find(
    (c) =>
      (c.metric_1 === xAxisMetric && c.metric_2 === yAxisMetric) ||
      (c.metric_1 === yAxisMetric && c.metric_2 === xAxisMetric)
  );

  // Calculate trend line data using linear regression
  const calculateTrendLine = (points) => {
    if (points.length < 2) return [];
    
    const n = points.length;
    const sumX = points.reduce((sum, p) => sum + p.x, 0);
    const sumY = points.reduce((sum, p) => sum + p.y, 0);
    const sumXY = points.reduce((sum, p) => sum + p.x * p.y, 0);
    const sumX2 = points.reduce((sum, p) => sum + p.x * p.x, 0);
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    
    const xValues = points.map(p => p.x);
    const minX = Math.min(...xValues);
    const maxX = Math.max(...xValues);
    
    return [
      { x: minX, y: slope * minX + intercept },
      { x: maxX, y: slope * maxX + intercept }
    ];
  };

  // Check if X-axis is Time
  const isTimeXAxis = xAxisMetric === 'Time';

  // Transform the API response data into chart-friendly format
  const chartData = data.map((interval) => {
    const xMetric = isTimeXAxis ? null : interval.metrics.find((m) => m.metric_type === xAxisMetric);
    const yMetric = interval.metrics.find((m) => m.metric_type === yAxisMetric);

    return {
      interval_number: interval.interval_number,
      start_time: interval.start_time,
      end_time: interval.end_time,
      x: isTimeXAxis ? interval.interval_number : (xMetric ? xMetric.mean_value : 0),
      y: yMetric ? yMetric.mean_value : 0,
      xMetricData: xMetric,
      yMetricData: yMetric,
    };
  });

  // Generate colors for each point based on interval number
  const colors = [
    '#8884d8',
    '#82ca9d',
    '#ffc658',
    '#ff7300',
    '#00C49F',
    '#FFBB28',
    '#FF8042',
    '#0088FE',
  ];

  const getColor = (index) => colors[index % colors.length];

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const point = payload[0].payload;
      return (
        <div className="chart-tooltip">
          <p className="tooltip-title">Interval {point.interval_number}</p>
          <p className="tooltip-time">
            {point.start_time} → {point.end_time}
          </p>
          <div className="tooltip-metrics">
            {isTimeXAxis ? (
              <div className="tooltip-metric">
                <strong>Interval:</strong>
                <span>{point.interval_number}</span>
              </div>
            ) : (
              <div className="tooltip-metric">
                <strong>{xAxisMetric.replace(/_/g, ' ')}:</strong>
                <span>{point.x?.toFixed(2)}</span>
              </div>
            )}
            <div className="tooltip-metric">
              <strong>{yAxisMetric.replace(/_/g, ' ')}:</strong>
              <span>{point.y?.toFixed(2)}</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  const handleMouseEnter = (data) => {
    setHoveredPoint(data);
  };

  const handleMouseLeave = () => {
    setHoveredPoint(null);
  };

  const formatAxisLabel = (metric) => {
    return metric.replace(/_/g, ' ');
  };

  // Calculate trend line
  const trendLineData = calculateTrendLine(chartData);

  return (
    <div className="metrics-chart-container">
      <h3>Metrics Comparison Chart</h3>
      {!isTimeXAxis && currentCorrelation && (
        <div className="correlation-coefficient">
          Pearson r = <span className={currentCorrelation.pearson_coefficient >= 0 ? 'positive' : 'negative'}>
            {currentCorrelation.pearson_coefficient.toFixed(4)}
          </span>
        </div>
      )}
      
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart
            margin={{ top: 20, right: 30, bottom: 60, left: 80 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#444" />
            <XAxis
              type="number"
              dataKey="x"
              name={xAxisMetric}
              tick={{ fill: '#ccc' }}
              tickFormatter={(value) => isTimeXAxis ? Math.round(value) : value.toFixed(2)}
              label={{
                value: isTimeXAxis ? 'Time (Interval)' : formatAxisLabel(xAxisMetric),
                position: 'bottom',
                offset: 40,
                fill: '#ccc',
              }}
              domain={['dataMin', 'dataMax']}
            />
            <YAxis
              type="number"
              dataKey="y"
              name={yAxisMetric}
              tick={{ fill: '#ccc' }}
              tickFormatter={(value) => value.toFixed(2)}
              label={{
                value: formatAxisLabel(yAxisMetric),
                angle: -90,
                position: 'left',
                offset: 55,
                fill: '#ccc',
              }}
              domain={['dataMin', 'dataMax']}
            />
            <Tooltip content={<CustomTooltip />} />
            {trendLineData.length > 0 && (
              <Line
                data={trendLineData}
                type="linear"
                dataKey="y"
                stroke="#e94560"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                legendType="none"
                isAnimationActive={false}
              />
            )}
            <Scatter
              data={chartData}
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={getColor(index)}
                  stroke={hoveredPoint?.interval_number === entry.interval_number ? '#fff' : 'none'}
                  strokeWidth={hoveredPoint?.interval_number === entry.interval_number ? 2 : 0}
                  r={hoveredPoint?.interval_number === entry.interval_number ? 10 : 7}
                />
              ))}
            </Scatter>
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {!isTimeXAxis && currentCorrelation && (
        <div className="correlation-info">
          <div className="correlation-header">
            <h4>Correlation Analysis</h4>
            <span className={`correlation-badge ${currentCorrelation.pearson_coefficient >= 0 ? 'positive' : 'negative'}`}>
              r = {currentCorrelation.pearson_coefficient.toFixed(4)}
            </span>
          </div>
          <div className="correlation-details">
            <p><strong>P-value:</strong> {currentCorrelation.p_value.toFixed(4)}</p>
            <p><strong>Sample Size:</strong> {currentCorrelation.sample_size}</p>
            <p className="interpretation"><strong>Interpretation:</strong> {currentCorrelation.interpretation}</p>
          </div>
        </div>
      )}

      <div className="chart-legend">
        {chartData.map((point, index) => (
          <div
            key={point.interval_number}
            className={`legend-item ${hoveredPoint?.interval_number === point.interval_number ? 'highlighted' : ''}`}
            onMouseEnter={() => setHoveredPoint(point)}
            onMouseLeave={() => setHoveredPoint(null)}
          >
            <span
              className="legend-color"
              style={{ backgroundColor: getColor(index) }}
            ></span>
            <span className="legend-label">Interval {point.interval_number}</span>
          </div>
        ))}
      </div>

      {hoveredPoint && (
        <div className="detailed-info">
          <h4>Interval {hoveredPoint.interval_number} Details</h4>
          <div className="info-grid">
            <div className="info-section">
              <h5>Time Range</h5>
              <p><strong>Start:</strong> {hoveredPoint.start_time}</p>
              <p><strong>End:</strong> {hoveredPoint.end_time}</p>
            </div>
            
            {!isTimeXAxis && hoveredPoint.xMetricData && (
              <div className="info-section">
                <h5>{xAxisMetric.replace(/_/g, ' ')}</h5>
                <div className="metric-details">
                  <p><strong>Mean Value:</strong> {hoveredPoint.xMetricData.mean_value?.toFixed(2)}</p>
                  <p><strong>Observations:</strong> {hoveredPoint.xMetricData.amount_of_observations}</p>
                  <p><strong>Z-Score:</strong> {hoveredPoint.xMetricData.z_score?.toFixed(2)}</p>
                  <p><strong>Z-Score Mean:</strong> {hoveredPoint.xMetricData.z_score_mean?.toFixed(2)}</p>
                  <p><strong>Z-Score Std:</strong> {hoveredPoint.xMetricData.z_score_std?.toFixed(2)}</p>
                  {hoveredPoint.xMetricData.min_timestamp && (
                    <p><strong>Min Timestamp:</strong> {hoveredPoint.xMetricData.min_timestamp}</p>
                  )}
                  {hoveredPoint.xMetricData.max_timestamp && (
                    <p><strong>Max Timestamp:</strong> {hoveredPoint.xMetricData.max_timestamp}</p>
                  )}
                </div>
              </div>
            )}
            
            {hoveredPoint.yMetricData && (
              <div className="info-section">
                <h5>{yAxisMetric.replace(/_/g, ' ')}</h5>
                <div className="metric-details">
                  <p><strong>Mean Value:</strong> {hoveredPoint.yMetricData.mean_value?.toFixed(2)}</p>
                  <p><strong>Observations:</strong> {hoveredPoint.yMetricData.amount_of_observations}</p>
                  <p><strong>Z-Score:</strong> {hoveredPoint.yMetricData.z_score?.toFixed(2)}</p>
                  <p><strong>Z-Score Mean:</strong> {hoveredPoint.yMetricData.z_score_mean?.toFixed(2)}</p>
                  <p><strong>Z-Score Std:</strong> {hoveredPoint.yMetricData.z_score_std?.toFixed(2)}</p>
                  {hoveredPoint.yMetricData.min_timestamp && (
                    <p><strong>Min Timestamp:</strong> {hoveredPoint.yMetricData.min_timestamp}</p>
                  )}
                  {hoveredPoint.yMetricData.max_timestamp && (
                    <p><strong>Max Timestamp:</strong> {hoveredPoint.yMetricData.max_timestamp}</p>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default MetricsChart;
