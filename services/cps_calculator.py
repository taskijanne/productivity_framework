"""
Composite Productivity Score (CPS) calculation service.

This module calculates a weighted composite score based on multiple metrics.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from services.metrics_calculator import calculate_metric


def calculate_cps(
    start_time: str,
    end_time: str,
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
            metric_result = calculate_metric(
                metric_type=metric_type,
                start_time=interval_start_str,
                end_time=interval_end_str,
                db_name=db_name
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
