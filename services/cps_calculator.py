"""
Composite Productivity Score (CPS) calculation service.

This module calculates a weighted composite score based on multiple metrics.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np
from scipy import stats
from services.metrics_calculator import calculate_metric
from models.enums import MetricType


def calculate_trend(cps_values: List[float]) -> Dict[str, Any]:
    """
    Calculate linear regression trend line for CPS values.
    
    Args:
        cps_values: List of CPS values for each interval
        
    Returns:
        Dictionary containing:
        - slope: Rate of change per interval
        - intercept: Y-intercept of the trend line
        - trend_values: List of trend line values for each interval
        - direction: 'improving', 'declining', or 'stable'
        - interpretation: Human-readable interpretation
    """
    n = len(cps_values)
    if n < 2:
        return {
            'slope': 0.0,
            'intercept': cps_values[0] if n == 1 else 0.0,
            'trend_values': cps_values if n == 1 else [],
            'direction': 'stable',
            'interpretation': 'Insufficient data for trend analysis (need at least 2 intervals)'
        }
    
    # Use interval index (0, 1, 2, ...) as x values
    x_values = np.array(range(n))
    y_values = np.array(cps_values)
    
    # Calculate linear regression using least squares
    sum_x = np.sum(x_values)
    sum_y = np.sum(y_values)
    sum_xy = np.sum(x_values * y_values)
    sum_x2 = np.sum(x_values * x_values)
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
    intercept = (sum_y - slope * sum_x) / n
    
    # Calculate trend line values
    trend_values = [float(slope * x + intercept) for x in x_values]
    
    # Determine direction based on slope
    # Use a small threshold to account for floating point precision
    threshold = 0.01
    if slope > threshold:
        direction = 'improving'
    elif slope < -threshold:
        direction = 'declining'
    else:
        direction = 'stable'
    
    # Calculate total change over all intervals
    total_change = slope * (n - 1)
    
    # Generate human-readable interpretation
    if direction == 'improving':
        interpretation = f"CPS shows an improving trend with a slope of {slope:.4f} per interval. Total improvement over {n} intervals: {total_change:.4f}"
    elif direction == 'declining':
        interpretation = f"CPS shows a declining trend with a slope of {slope:.4f} per interval. Total decline over {n} intervals: {abs(total_change):.4f}"
    else:
        interpretation = f"CPS is relatively stable with minimal change (slope: {slope:.4f})"
    
    return {
        'slope': float(slope),
        'intercept': float(intercept),
        'trend_values': trend_values,
        'direction': direction,
        'interpretation': interpretation
    }


def calculate_cps(
    start_time: str,
    end_time: str,
    project_id: int,
    metrics: List[Dict[str, Any]],
    db_name: str = "productivity_framework.db",
    original_start_time: str = None,
    original_end_time: str = None
) -> Dict[str, Any]:
    """
    Calculate Composite Productivity Score (CPS) as a weighted sum of metric z-scores.
    
    CPS = Σ(weight_i × z_score_i) for i = 1 to n
    
    Args:
        start_time: Start of the time period (normalized/SQLite format)
        end_time: End of the time period (normalized/SQLite format)
        project_id: The project ID to filter observations
        metrics: List of dicts with 'metric' (MetricType) and 'weight' (0-1)
        db_name: Name of the database file
        original_start_time: Original request start_time (for response)
        original_end_time: Original request end_time (for response)
        
    Returns:
        Dictionary containing:
        - cps: The calculated composite productivity score
        - metrics: List of metric results with weight and z_score_weighted
    """
    # Use original times if provided, otherwise use normalized times
    response_start_time = original_start_time if original_start_time else start_time
    response_end_time = original_end_time if original_end_time else end_time
    
    cps_total = 0.0
    metric_results = []
    
    for metric_config in metrics:
        metric_type = metric_config['metric']
        weight = metric_config['weight']
        
        # Calculate the metric (even if weight is 0, for completeness)
        metric_result = calculate_metric(
            metric_type=metric_type,
            start_time=start_time,
            end_time=end_time,
            project_id=project_id,
            db_name=db_name
        )
        
        # Get z-score from result
        z_score = metric_result.get('z_score', 0.0)
        
        # Calculate weighted z-score
        z_score_weighted = weight * z_score
        
        # Add to CPS total
        cps_total += z_score_weighted
        
        # Ensure required fields are present and add CPS-specific fields
        metric_result['metric_type'] = metric_type
        metric_result['weight'] = weight
        metric_result['z_score_weighted'] = z_score_weighted
        
        # Ensure start_time and end_time are in the result (use response times)
        metric_result['start_time'] = response_start_time
        metric_result['end_time'] = response_end_time
        
        metric_results.append(metric_result)
    
    return {
        'cps': cps_total,
        'metrics': metric_results
    }


def calculate_cps_with_intervals(
    start_time: str,
    end_time: str,
    intervals: int,
    project_id: int,
    metrics: List[Dict[str, Any]],
    db_name: str = "productivity_framework.db"
) -> List[Dict[str, Any]]:
    """
    Calculate Composite Productivity Score (CPS) for multiple intervals.
    
    CPS = Σ(weight_i × z_score_i) for i = 1 to n
    
    Args:
        start_time: Start of the time period (normalized/SQLite format)
        end_time: End of the time period (normalized/SQLite format)
        intervals: Number of intervals to divide the time period into
        project_id: The project ID to filter observations
        metrics: List of dicts with 'metric' (MetricType) and 'weight' (0-1)
        db_name: Name of the database file
        
    Returns:
        List of dictionaries, each containing:
        - interval_number: The interval number (1-based)
        - start_time: Interval start time
        - end_time: Interval end time
        - cps: The calculated composite productivity score for this interval
        - metrics: List of metric results with weight and z_score_weighted
    """
    # Parse start and end times
    start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    
    # Calculate interval duration
    total_duration = end_dt - start_dt
    interval_duration = total_duration / intervals
    
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
        
        # Calculate CPS for this interval
        cps_total = 0.0
        metric_results = []
        
        for metric_config in metrics:
            metric_type = metric_config['metric']
            weight = metric_config['weight']
            
            # Calculate the metric
            # Pass the full user-specified date range as the population for z_score calculation
            metric_result = calculate_metric(
                metric_type=metric_type,
                start_time=interval_start_str,
                end_time=interval_end_str,
                project_id=project_id,
                db_name=db_name,
                population_start_time=start_time,
                population_end_time=end_time
            )
            
            # Get z-score from result
            z_score = metric_result.get('z_score', 0.0)
            
            # Calculate weighted z-score
            z_score_weighted = weight * z_score
            
            # Add to CPS total
            cps_total += z_score_weighted
            
            # Build metric result for response
            metric_results.append({
                'metric_type': metric_type,
                'weight': weight,
                'z_score': z_score,
                'z_score_weighted': z_score_weighted,
                'mean_value': metric_result.get('mean_value', 0.0),
                'amount_of_observations': metric_result.get('amount_of_observations', 0),
                'z_score_mean': metric_result.get('z_score_mean', 0.0),
                'z_score_std': metric_result.get('z_score_std', 0.0),
                'min_timestamp': metric_result.get('min_timestamp'),
                'max_timestamp': metric_result.get('max_timestamp')
            })
        
        interval_results.append({
            'interval_number': i + 1,
            'start_time': interval_start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            'end_time': interval_end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            'cps': cps_total,
            'metrics': metric_results
        })
    
    return interval_results


def calculate_predictor_statistics(
    predictor_z_scores: List[float],
    cps_values: List[float]
) -> Dict[str, Any]:
    """
    Calculate statistical relationship between predictor z-scores and CPS values.
    
    Args:
        predictor_z_scores: List of predictor z-scores for each interval
        cps_values: List of CPS values for each interval
        
    Returns:
        Dictionary containing r2, correlation, slope, p_value, and interpretation
    """
    predictor_arr = np.array(predictor_z_scores)
    cps_arr = np.array(cps_values)
    
    # Check for sufficient data
    n = len(predictor_arr)
    if n < 2:
        return {
            'r2': 0.0,
            'correlation': 0.0,
            'slope': 0.0,
            'p_value': 1.0,
            'interpretation': "Insufficient data (need at least 2 intervals for analysis)"
        }
    
    # Check for zero variance
    if np.std(predictor_arr) == 0 or np.std(cps_arr) == 0:
        return {
            'r2': 0.0,
            'correlation': 0.0,
            'slope': 0.0,
            'p_value': 1.0,
            'interpretation': "Cannot compute statistics: predictor or CPS has zero variance"
        }
    
    # Calculate Pearson correlation and p-value
    correlation, p_value = stats.pearsonr(predictor_arr, cps_arr)
    
    # Calculate R² (coefficient of determination)
    r2 = correlation ** 2
    
    # Calculate slope using linear regression
    slope, intercept, r_value, p_val, std_err = stats.linregress(predictor_arr, cps_arr)
    
    # Generate interpretation
    interpretation = _interpret_predictor_statistics(correlation, r2, p_value, n)
    
    return {
        'r2': round(r2, 4),
        'correlation': round(correlation, 4),
        'slope': round(slope, 4),
        'p_value': round(p_value, 4),
        'interpretation': interpretation
    }


def _interpret_predictor_statistics(correlation: float, r2: float, p_value: float, sample_size: int) -> str:
    """
    Generate human-readable interpretation of predictor statistics.
    
    Args:
        correlation: Pearson correlation coefficient
        r2: R-squared value
        p_value: Statistical significance
        sample_size: Number of data points
        
    Returns:
        Human-readable interpretation string
    """
    # Interpret R²
    r2_pct = r2 * 100
    if r2 >= 0.7:
        r2_strength = "strongly"
    elif r2 >= 0.5:
        r2_strength = "moderately"
    elif r2 >= 0.3:
        r2_strength = "weakly"
    else:
        r2_strength = "poorly"
    
    # Interpret correlation direction
    if correlation > 0:
        direction = "positive"
    elif correlation < 0:
        direction = "negative"
    else:
        direction = "no"
    
    # Interpret statistical significance
    if p_value < 0.01:
        significance = "highly significant (p < 0.01)"
    elif p_value < 0.05:
        significance = "significant (p < 0.05)"
    elif p_value < 0.1:
        significance = "marginally significant (p < 0.1)"
    else:
        significance = "not statistically significant"
    
    return (
        f"The predictor {r2_strength} explains CPS variance (R²={r2_pct:.1f}%), "
        f"with a {direction} correlation. The relationship is {significance}. "
        f"Based on {sample_size} intervals."
    )


def calculate_cps_with_predictor(
    start_time: str,
    end_time: str,
    intervals: int,
    project_id: int,
    metrics: List[Dict[str, Any]],
    predictor: str,
    db_name: str = "productivity_framework.db"
) -> Dict[str, Any]:
    """
    Calculate CPS with intervals and analyze predictor relationship.
    
    Args:
        start_time: Start of the time period (normalized/SQLite format)
        end_time: End of the time period (normalized/SQLite format)
        intervals: Number of intervals to divide the time period into
        project_id: The project ID to filter observations
        metrics: List of dicts with 'metric' (MetricType) and 'weight' (0-1)
        predictor: The predictor metric type to analyze
        db_name: Name of the database file
        
    Returns:
        Dictionary containing:
        - intervals: List of CPS interval results
        - predictor: Predictor analysis with intervals and statistics
    """
    # First calculate CPS for all intervals
    interval_results = calculate_cps_with_intervals(
        start_time=start_time,
        end_time=end_time,
        intervals=intervals,
        project_id=project_id,
        metrics=metrics,
        db_name=db_name
    )
    
    # Parse start and end times for predictor calculation
    start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    
    # Calculate interval duration
    total_duration = end_dt - start_dt
    interval_duration = total_duration / intervals
    
    # Calculate predictor metric for each interval
    predictor_intervals = []
    predictor_z_scores = []
    cps_values = []
    
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
        
        # Calculate predictor metric for this interval
        predictor_result = calculate_metric(
            metric_type=predictor,
            start_time=interval_start_str,
            end_time=interval_end_str,
            project_id=project_id,
            db_name=db_name,
            population_start_time=start_time,
            population_end_time=end_time
        )
        
        z_score = predictor_result.get('z_score', 0.0)
        
        # For predictor analysis, we do NOT invert the z-score.
        # This gives intuitive interpretation: e.g., "high rework → low CPS" (negative correlation)
        # The calculate_metric function already inverted it, so we reverse that here.
        if MetricType.is_inverted_metric(predictor):
            z_score = -z_score
        
        predictor_intervals.append({
            'interval_number': i + 1,
            'z_score': z_score
        })
        
        predictor_z_scores.append(z_score)
        cps_values.append(interval_results[i]['cps'])
    
    # Calculate statistics between predictor and CPS
    statistics = calculate_predictor_statistics(predictor_z_scores, cps_values)
    
    # Calculate trend from CPS values
    trend = calculate_trend(cps_values)
    
    return {
        'intervals': interval_results,
        'trend': trend,
        'predictor': {
            'metric_type': predictor,
            'intervals': predictor_intervals,
            'statistics': statistics
        }
    }
