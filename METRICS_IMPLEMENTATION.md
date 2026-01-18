# Metrics Calculation Implementation

## Overview

I've successfully implemented comprehensive metrics calculation support for the AI Productivity Framework. The implementation includes 14 different metric types with statistical analysis capabilities.

## Changes Made

### 1. **MetricType Enum** (`models/enums.py`)
Added 14 metric types:
- SATISFACTION
- RETENTION
- DEPLOYMENT_FREQUENCY
- CHANGE_FAILURE_RATE
- MEAN_TIME_TO_RECOVER
- LINES_OF_CODE
- NUMBER_OF_COMMITS
- COMMUNICATION_FREQUENCY
- PERCEIVED_PRODUCTIVITY
- LACK_OF_INTERRUPTIONS
- LEAD_TIME_FOR_CHANGES
- AI_ACCEPTANCE_RATE
- AI_CODE_VOLUME
- AI_REWORK_RATE

### 2. **MetricResult Schema** (`models/schemas.py`)
Added Pydantic model for metric responses with fields:
- `metric_type`: Type of metric calculated
- `start_time`: Start of time period
- `end_time`: End of time period
- `mean_value`: Average value for the timeframe
- `amount_of_observations`: Number of observations in timeframe
- `z_score`: Standardized score (mean_value - population_mean) / population_std
- `z_score_mean`: Population mean
- `z_score_std`: Population standard deviation

### 3. **Metrics Calculator** (`services/metrics_calculator.py`)
Created comprehensive calculation module using pandas and numpy:

#### Core Functions:
- `calculate_metric()`: Main entry point that routes to specific calculators
- `_calculate_z_score_metrics()`: Calculates statistical metrics and z-scores
- `_get_observations_df()`: Retrieves observations as pandas DataFrame

#### Metric-Specific Calculators:

**Simple Observation-Based Metrics:**
- `calculate_satisfaction()`: Based on SATISFACTION observations
- `calculate_lines_of_code()`: Based on LINES_OF_CODE observations
- `calculate_number_of_commits()`: Based on COMMIT observations
- `calculate_communication_frequency()`: Based on COMMUNICATION_EVENT observations
- `calculate_perceived_productivity()`: Based on PERCEIVED_PRODUCTIVITY observations
- `calculate_lack_of_interruptions()`: Based on WORK_SESSION observations
- `calculate_ai_acceptance_rate()`: Based on AI_SUGGESTION_RESULT observations

**Special Metric Type Mappings:**
- `calculate_retention()`: Based on TEAM_SIZE_CHANGE observations

**Complex Calculated Metrics:**
- `calculate_change_failure_rate()`: Ratio of DEPLOYMENT_FAILURE to total DEPLOYMENT
- `calculate_deployment_frequency()`: Based on DEPLOYMENT observations
- `calculate_mean_time_to_recover()`: Time between DEPLOYMENT_FAILURE and DEPLOYMENT_FAILURE_FIX pairs (in minutes)
- `calculate_lead_time_for_changes()`: Time between COMMIT and DEPLOYMENT for commits with deployment references (in minutes)
- `calculate_ai_code_volume()`: Ratio of LINES_OF_CODE_AI to total LINES_OF_CODE
- `calculate_ai_rework_rate()`: Ratio of COMMIT with ai_rework_commit=1 to total COMMIT

### 4. **API Endpoints** (`api/routes.py`)

#### GET `/metric_types`
Returns list of all available metric types with descriptions.

**Response:**
```json
{
  "metric_types": ["SATISFACTION", "RETENTION", ...],
  "descriptions": {
    "SATISFACTION": "Developer satisfaction scores",
    "RETENTION": "Team retention rate",
    ...
  }
}
```

#### GET `/metrics`
Calculate a specific metric for a time period.

**Query Parameters:**
- `metric_type` (required): Type of metric to calculate
- `start_time` (required): Start time (ISO format: YYYY-MM-DD HH:MM:SS)
- `end_time` (required): End time (ISO format: YYYY-MM-DD HH:MM:SS)

**Response Example:**
```json
{
  "metric_type": "SATISFACTION",
  "start_time": "2026-01-01 00:00:00",
  "end_time": "2026-01-31 23:59:59",
  "mean_value": 4.35,
  "amount_of_observations": 25,
  "z_score": 0.82,
  "z_score_mean": 4.20,
  "z_score_std": 0.18
}
```

### 5. **Dependencies** (`requirements.txt`)
Added:
- `pandas>=2.0.0`: For data manipulation and analysis
- `numpy>=1.24.0`: For numerical calculations

## Usage Examples

### 1. Get Available Metric Types
```bash
curl http://localhost:8000/metric_types
```

### 2. Calculate Satisfaction Metric
```bash
curl "http://localhost:8000/metrics?metric_type=SATISFACTION&start_time=2026-01-01%2000:00:00&end_time=2026-01-31%2023:59:59"
```

### 3. Calculate Lead Time for Changes
```bash
curl "http://localhost:8000/metrics?metric_type=LEAD_TIME_FOR_CHANGES&start_time=2026-01-01%2000:00:00&end_time=2026-01-31%2023:59:59"
```

### 4. Calculate AI Rework Rate
```bash
curl "http://localhost:8000/metrics?metric_type=AI_REWORK_RATE&start_time=2026-01-01%2000:00:00&end_time=2026-01-31%2023:59:59"
```

## Statistical Analysis

Each metric calculation provides:

1. **Mean Value**: Average of observations within the specified timeframe
2. **Observation Count**: Number of data points used in calculation
3. **Z-Score**: Standardized score showing how many standard deviations the timeframe mean is from the population mean
   - Formula: `(timeframe_mean - population_mean) / population_std`
   - Positive z-score: Above population average
   - Negative z-score: Below population average
4. **Population Statistics**: Mean and standard deviation of all observations (for context)

## Special Considerations

### Time-Based Metrics
- **MEAN_TIME_TO_RECOVER**: Only considers failure-fix pairs where both events occur within the timeframe
- **LEAD_TIME_FOR_CHANGES**: Only considers commit-deployment pairs where both events occur within the timeframe

### Ratio Metrics
- **CHANGE_FAILURE_RATE**: Calculated as single value (ratio) then treated as mean for z-score
- **AI_CODE_VOLUME**: Calculated as single value (ratio) then treated as mean for z-score
- **AI_REWORK_RATE**: Calculated as single value (ratio) then treated as mean for z-score

## Error Handling

The API provides appropriate error responses:
- **400 Bad Request**: Invalid metric type or parameters
- **500 Internal Server Error**: Database errors or calculation failures

## Testing

To test the implementation:

1. Ensure database has observations of various types
2. Start the API server: `python main.py`
3. Visit `http://localhost:8000/docs` for interactive API documentation
4. Try the `/metric_types` endpoint to see available metrics
5. Use the `/metrics` endpoint with different metric types and time periods

## Future Enhancements

Potential improvements:
- Add caching for frequently calculated metrics
- Support for custom time aggregations (daily, weekly, monthly)
- Trend analysis over multiple time periods
- Visualization endpoints
- Export metrics to CSV/JSON
- Real-time metric updates via WebSocket
