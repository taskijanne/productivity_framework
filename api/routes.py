"""
API routes for the AI Productivity Framework.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import sqlite3
import numpy as np
from scipy import stats

from models import ObservationType, Observation, MetricType, MetricResult, CPSRequest, CPSResponse, IntervalMetricResult, IntervalMetricsResult, CorrelationResult, MetricsResponse, CPSIntervalRequest, CPSIntervalResponse
from database import get_db_connection
from services import calculate_metric
from services.cps_calculator import calculate_cps, calculate_cps_with_intervals


def calculate_correlations(interval_results: list, metric_type_list: list) -> list:
    """
    Calculate Pearson correlation coefficients between all pairs of metrics across intervals.
    
    Uses mean_value for correlation calculation.
    
    Args:
        interval_results: List of interval results containing metrics
        metric_type_list: List of metric type strings
        
    Returns:
        List of CorrelationResult dictionaries
    """
    correlations = []
    
    # Extract mean_value for each metric across all intervals
    metric_values = {}
    for metric_type in metric_type_list:
        values = []
        for interval in interval_results:
            for metric in interval["metrics"]:
                if metric["metric_type"] == metric_type:
                    values.append(metric["mean_value"])
                    break
        metric_values[metric_type] = np.array(values)
    
    # Calculate correlation for each pair of metrics
    for i, metric_1 in enumerate(metric_type_list):
        for metric_2 in metric_type_list[i + 1:]:
            values_1 = metric_values[metric_1]
            values_2 = metric_values[metric_2]
            
            # Need at least 3 data points for meaningful correlation
            valid_mask = ~(np.isnan(values_1) | np.isnan(values_2))
            valid_values_1 = values_1[valid_mask]
            valid_values_2 = values_2[valid_mask]
            sample_size = len(valid_values_1)
            
            if sample_size < 3:
                # Not enough data points for correlation
                correlations.append({
                    "metric_1": metric_1,
                    "metric_2": metric_2,
                    "pearson_coefficient": 0.0,
                    "p_value": 1.0,
                    "sample_size": sample_size,
                    "interpretation": "Insufficient data (need at least 3 intervals with observations)"
                })
                continue
            
            # Check for zero variance (constant values)
            if np.std(valid_values_1) == 0 or np.std(valid_values_2) == 0:
                correlations.append({
                    "metric_1": metric_1,
                    "metric_2": metric_2,
                    "pearson_coefficient": 0.0,
                    "p_value": 1.0,
                    "sample_size": sample_size,
                    "interpretation": "Cannot compute correlation: one or both metrics have zero variance"
                })
                continue
            
            # Calculate Pearson correlation using scipy
            r, p_value = stats.pearsonr(valid_values_1, valid_values_2)
            
            # Interpret the correlation
            interpretation = interpret_correlation(r, p_value)
            
            correlations.append({
                "metric_1": metric_1,
                "metric_2": metric_2,
                "pearson_coefficient": round(r, 4),
                "p_value": round(p_value, 4),
                "sample_size": sample_size,
                "interpretation": interpretation
            })
    
    return correlations


def interpret_correlation(r: float, p_value: float) -> str:
    """
    Provide human-readable interpretation of a Pearson correlation coefficient.
    
    Args:
        r: Pearson correlation coefficient (-1 to 1)
        p_value: Statistical significance
        
    Returns:
        Human-readable interpretation string
    """
    # Determine strength
    abs_r = abs(r)
    if abs_r < 0.1:
        strength = "negligible"
    elif abs_r < 0.3:
        strength = "weak"
    elif abs_r < 0.5:
        strength = "moderate"
    elif abs_r < 0.7:
        strength = "strong"
    else:
        strength = "very strong"
    
    # Determine direction
    if r > 0:
        direction = "positive"
    elif r < 0:
        direction = "negative"
    else:
        direction = "no"
    
    # Determine statistical significance
    if p_value < 0.01:
        significance = "highly significant (p < 0.01)"
    elif p_value < 0.05:
        significance = "significant (p < 0.05)"
    elif p_value < 0.1:
        significance = "marginally significant (p < 0.1)"
    else:
        significance = "not statistically significant"
    
    return f"{strength.capitalize()} {direction} correlation, {significance}"


router = APIRouter()


@router.get("/")
def read_root():
    """Root endpoint providing API information."""
    return {
        "message": "Welcome to AI Productivity Framework API",
        "version": "1.0.0",
        "endpoints": {
            "/observations": "Get all observations",
            "/observation_types": "Get all allowed observation types",
            "/metric_types": "Get all available metric types",
            "/metrics": "Calculate metrics for a given time period",
            "/cps": "Calculate Composite Productivity Score (POST)",
            "/docs": "Interactive API documentation"
        }
    }


@router.get("/observations", response_model=List[Observation])
def get_observations(
    type: Optional[str] = None,
    limit: Optional[int] = None
):
    """
    Retrieve all observations from the database.
    
    Args:
        type (str, optional): Filter by observation type
        limit (int, optional): Limit the number of results
    
    Returns:
        List[Observation]: List of all observation records
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query based on parameters
        query = "SELECT id, type, timestamp, value, commit_hash, deployment_id, deployment_failure_id, ai_rework_commit FROM observations"
        params = []
        
        if type:
            query += " WHERE type = ?"
            params.append(type)
        
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert rows to list of dictionaries
        observations = [
            {
                "id": row["id"],
                "type": row["type"],
                "timestamp": row["timestamp"],
                "value": row["value"],
                "commit_hash": row["commit_hash"],
                "deployment_id": row["deployment_id"],
                "deployment_failure_id": row["deployment_failure_id"],
                "ai_rework_commit": row["ai_rework_commit"]
            }
            for row in rows
        ]
        
        return observations
        
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/observation_types")
def get_observation_types():
    """
    Get a list of all allowed observation types.
    
    Returns:
        dict: Dictionary containing list of observation types
    """
    observation_types = [obs_type.value for obs_type in ObservationType]
    return {"observation_types": observation_types}


@router.get("/metric_types")
def get_metric_types():
    """
    Get a list of all available metric types.
    
    Returns:
        dict: Dictionary containing list of metric types with descriptions
    """
    return MetricType.get_all_with_descriptions()


@router.get("/metrics", response_model=MetricsResponse)
def get_metrics(
    metric_types: str = Query(..., description="Comma-separated list of metric types to calculate (e.g., LEAD_TIME_FOR_CHANGES,CHANGE_FAILURE_RATE)"),
    start_time: str = Query(..., description="Start time (ISO format: YYYY-MM-DDTHH:MM:SS)"),
    end_time: str = Query(..., description="End time (ISO format: YYYY-MM-DDTHH:MM:SS)"),
    intervals: int = Query(1, description="Number of intervals to divide the time period into (default: 1)", gt=0)
):
    """
    Calculate one or more metrics for a given time period.
    
    Args:
        metric_types: Comma-separated list of metric types to calculate (e.g., LEAD_TIME_FOR_CHANGES,CHANGE_FAILURE_RATE)
        start_time: Start of the time period in ISO format (YYYY-MM-DDTHH:MM:SS)
        end_time: End of the time period in ISO format (YYYY-MM-DDTHH:MM:SS)
        intervals: Number of intervals to divide the time period into (default: 1).
                   Must be a positive integer not larger than the number 
                   of days between start_time and end_time.
    
    Returns:
        MetricsResponse: Contains intervals (array of interval results with metrics) and 
                         correlations (Pearson correlations between metric pairs when applicable)
    """
    try:
        # Parse and validate metric types
        metric_type_list = [mt.strip() for mt in metric_types.split(',')]
        valid_metric_types = [mt.value for mt in MetricType]
        
        invalid_types = [mt for mt in metric_type_list if mt not in valid_metric_types]
        if invalid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid metric type(s): {', '.join(invalid_types)}. Must be one of: {', '.join(valid_metric_types)}"
            )
        
        # Validate and normalize timestamp format
        def validate_and_normalize_timestamp(ts: str) -> tuple[str, datetime]:
            """Validate timestamp and convert to SQLite format. Returns both normalized string and datetime."""
            try:
                # Try parsing ISO 8601 format with T separator
                if 'T' in ts:
                    dt = datetime.fromisoformat(ts.replace('Z', ''))
                else:
                    # Try parsing space-separated format
                    dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                
                # Return in SQLite-compatible format (space separator) and datetime object
                return dt.strftime("%Y-%m-%d %H:%M:%S"), dt
            except ValueError as e:
                raise ValueError(f"Invalid timestamp format: {ts}. Expected format: YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD HH:MM:SS")
        
        normalized_start, start_dt = validate_and_normalize_timestamp(start_time)
        normalized_end, end_dt = validate_and_normalize_timestamp(end_time)
        
        # Calculate the number of days between start and end
        total_duration = end_dt - start_dt
        total_days = total_duration.days + 1  # Include both start and end days
        
        # Validate intervals is not larger than the number of days
        if intervals > total_days:
            raise HTTPException(
                status_code=400,
                detail=f"Intervals ({intervals}) cannot be larger than the number of days between start_time and end_time ({total_days})"
            )
        
        # Calculate interval duration
        interval_duration = total_duration / intervals
        
        # Calculate metrics for each interval
        interval_results = []
        for i in range(intervals):
            interval_start_dt = start_dt + (interval_duration * i)
            interval_end_dt = start_dt + (interval_duration * (i + 1))
            
            # For the last interval, ensure we use the exact end_time
            if i == intervals - 1:
                interval_end_dt = end_dt
            else:
                # Subtract 1 second from end to avoid overlap
                interval_end_dt = interval_end_dt - timedelta(seconds=1)
            
            interval_start_str = interval_start_dt.strftime("%Y-%m-%d %H:%M:%S")
            interval_end_str = interval_end_dt.strftime("%Y-%m-%d %H:%M:%S")
            
            # Calculate all metrics for this interval
            metrics_for_interval = []
            for metric_type in metric_type_list:
                result = calculate_metric(metric_type, interval_start_str, interval_end_str)
                
                # Add metric type
                result["metric_type"] = metric_type
                
                metrics_for_interval.append(result)
            
            interval_results.append({
                "interval_number": i + 1,
                "start_time": interval_start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                "end_time": interval_end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                "metrics": metrics_for_interval
            })
        
        # Calculate correlations if multiple metrics and intervals > 1
        correlations = None
        if len(metric_type_list) > 1 and intervals > 1:
            correlations = calculate_correlations(interval_results, metric_type_list)
        
        return {
            "intervals": interval_results,
            "correlations": correlations
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating metric: {str(e)}")


@router.post("/cps", response_model=CPSIntervalResponse)
def calculate_composite_productivity_score(request: CPSIntervalRequest):
    """
    Calculate Composite Productivity Score (CPS) as a weighted sum of metric z-scores.
    
    CPS = Σ(weight_i × z_score_i) for i = 1 to n
    
    Args:
        request: CPSIntervalRequest containing start_time, end_time, intervals (optional, default=1), 
                 and metrics with weights
    
    Returns:
        CPSIntervalResponse: Contains array of interval results, each with CPS and detailed 
                             metric results for that interval
        
    Validations:
        - start_time and end_time must be valid timestamps
        - end_time must not be before start_time
        - intervals must be positive and not larger than the number of days
        - metrics array must contain at least one metric
        - all metric values must be valid MetricType enum values
        - weight must be between 0 and 1 (inclusive)
    """
    try:
        # Validate and normalize timestamp format
        def validate_and_normalize_timestamp(ts: str) -> tuple[str, datetime]:
            """Validate timestamp and convert to SQLite format. Returns both normalized string and datetime."""
            try:
                # Try parsing ISO 8601 format with T separator
                if 'T' in ts:
                    dt = datetime.fromisoformat(ts.replace('Z', ''))
                else:
                    # Try parsing space-separated format
                    dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                
                # Return in SQLite-compatible format (space separator) and datetime object
                return dt.strftime("%Y-%m-%d %H:%M:%S"), dt
            except ValueError as e:
                raise ValueError(f"Invalid timestamp format: {ts}. Expected format: YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD HH:MM:SS")
        
        # Validate timestamps
        normalized_start, start_dt = validate_and_normalize_timestamp(request.start_time)
        normalized_end, end_dt = validate_and_normalize_timestamp(request.end_time)
        
        # Validate end_time is not before start_time
        if end_dt < start_dt:
            raise HTTPException(
                status_code=400,
                detail="end_time cannot be before start_time"
            )
        
        # Calculate the number of days between start and end
        total_duration = end_dt - start_dt
        total_days = total_duration.days + 1  # Include both start and end days
        
        # Validate intervals is not larger than the number of days
        if request.intervals > total_days:
            raise HTTPException(
                status_code=400,
                detail=f"Intervals ({request.intervals}) cannot be larger than the number of days between start_time and end_time ({total_days})"
            )
        
        # Validate all metric types
        valid_metrics = [mt.value for mt in MetricType]
        for metric_config in request.metrics:
            if metric_config.metric not in valid_metrics:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid metric type '{metric_config.metric}'. Must be one of: {', '.join(valid_metrics)}"
                )
        
        # Convert request to dict format for service
        metrics_list = [
            {'metric': m.metric, 'weight': m.weight}
            for m in request.metrics
        ]
        
        # Calculate CPS with intervals
        interval_results = calculate_cps_with_intervals(
            start_time=normalized_start,
            end_time=normalized_end,
            intervals=request.intervals,
            metrics=metrics_list
        )
        
        return {"intervals": interval_results}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating CPS: {str(e)}")
