"""
Metrics calculation service for the AI Productivity Framework.

This module contains logic for calculating various productivity metrics
based on observations stored in the database.
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional
from database import get_db_connection
from models.enums import MetricType
import time


def calculate_metric(
    metric_type: str,
    start_time: str,
    end_time: str,
    db_name: str = "productivity_framework.db"
) -> Dict[str, Any]:
    """
    Calculate a metric for a given time period.
    
    Args:
        metric_type: The type of metric to calculate
        start_time: Start of the time period (ISO format)
        end_time: End of the time period (ISO format)
        db_name: Name of the database file
        
    Returns:
        Dictionary containing metric results including mean_value, amount_of_observations,
        z_score, z_score_mean, and z_score_std
    """
    # Validate metric type
    try:
        metric_enum = MetricType(metric_type)
    except ValueError:
        raise ValueError(f"Invalid metric type: {metric_type}")
    
    # Route to appropriate calculation function
    calculators = {
        MetricType.SATISFACTION: calculate_satisfaction,
        MetricType.RETENTION: calculate_retention,
        MetricType.DEPLOYMENT_FREQUENCY: calculate_deployment_frequency,
        MetricType.CHANGE_FAILURE_RATE: calculate_change_failure_rate,
        MetricType.MEAN_TIME_TO_RECOVER: calculate_mean_time_to_recover,
        MetricType.LINES_OF_CODE: calculate_lines_of_code,
        MetricType.NUMBER_OF_COMMITS: calculate_number_of_commits,
        MetricType.COMMUNICATION_FREQUENCY: calculate_communication_frequency,
        MetricType.PERCEIVED_PRODUCTIVITY: calculate_perceived_productivity,
        MetricType.LACK_OF_INTERRUPTIONS: calculate_lack_of_interruptions,
        MetricType.LEAD_TIME_FOR_CHANGES: calculate_lead_time_for_changes,
        MetricType.AI_ACCEPTANCE_RATE: calculate_ai_acceptance_rate,
        MetricType.LINES_OF_CODE_AI: calculate_lines_of_code_ai,
        MetricType.AI_REWORK_RATE: calculate_ai_rework_rate,
    }
    
    calculator = calculators[metric_enum]
    result = calculator(start_time, end_time, db_name)
    
    # Apply z-score inversion for metrics where lower values are better
    if MetricType.is_inverted_metric(metric_type):
        result['z_score'] = -result['z_score']
    
    return result


def _calculate_z_score_metrics(
    timeframe_values: pd.Series,
    population_values: pd.Series,
    min_timestamp: Optional[str] = None,
    max_timestamp: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate z-score and related metrics.
    
    Args:
        timeframe_values: Values within the specified timeframe
        population_values: All values (population)
        min_timestamp: Optional minimum timestamp of actual data in timeframe
        max_timestamp: Optional maximum timestamp of actual data in timeframe
        
    Returns:
        Dictionary with mean_value, amount_of_observations, z_score, z_score_mean, z_score_std,
        and optionally min_timestamp and max_timestamp
    """
    if len(timeframe_values) == 0:
        result = {
            "mean_value": 0.0,
            "amount_of_observations": 0,
            "z_score": 0.0,
            "z_score_mean": 0.0,
            "z_score_std": 0.0
        }
        if min_timestamp is not None:
            result["min_timestamp"] = min_timestamp
        if max_timestamp is not None:
            result["max_timestamp"] = max_timestamp
        return result

    mean_value = float(timeframe_values.mean())
    amount_of_observations = len(timeframe_values)
    
    population_mean = float(population_values.mean())
    population_std = float(population_values.std())
    
    # Handle NaN values from pandas (e.g., when std of single value)
    if pd.isna(population_mean):
        population_mean = 0.0
    if pd.isna(population_std) or population_std == 0:
        population_std = 0.0
    
    # Calculate z-score (avoid division by zero)
    if population_std > 0:
        z_score = (mean_value - population_mean) / population_std
    else:
        z_score = 0.0
    
    result = {
        "mean_value": mean_value,
        "amount_of_observations": amount_of_observations,
        "z_score": z_score,
        "z_score_mean": population_mean,
        "z_score_std": population_std
    }
    
    if min_timestamp is not None:
        result["min_timestamp"] = min_timestamp
    if max_timestamp is not None:
        result["max_timestamp"] = max_timestamp
    
    return result


def _get_observations_df(
    observation_type: str,
    db_name: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> pd.DataFrame:
    """
    Get observations from database as a pandas DataFrame.
    
    Args:
        observation_type: Type of observation to retrieve
        db_name: Database name
        start_time: Optional start time filter
        end_time: Optional end time filter
        
    Returns:
        DataFrame with observations
    """
    conn = get_db_connection(db_name)
    
    query = "SELECT * FROM observations WHERE type = ?"
    params = [observation_type]
    
    if start_time and end_time:
        query += " AND timestamp BETWEEN ? AND ?"
        params.extend([start_time, end_time])
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df


def calculate_satisfaction(start_time: str, end_time: str, db_name: str) -> Dict[str, Any]:
    """Calculate SATISFACTION metric based on SATISFACTION observations."""
    timeframe_df = _get_observations_df("SATISFACTION", db_name, start_time, end_time)
    population_df = _get_observations_df("SATISFACTION", db_name)
    
    result = _calculate_z_score_metrics(timeframe_df['value'], population_df['value'])
    return result


def calculate_retention(start_time: str, end_time: str, db_name: str) -> Dict[str, Any]:
    """Calculate RETENTION metric based on TEAM_SIZE_CHANGE observations."""
    timeframe_df = _get_observations_df("TEAM_SIZE_CHANGE", db_name, start_time, end_time)
    population_df = _get_observations_df("TEAM_SIZE_CHANGE", db_name)
    
    result = _calculate_z_score_metrics(timeframe_df['value'], population_df['value'])
    return result


def calculate_deployment_frequency(start_time: str, end_time: str, db_name: str) -> Dict[str, Any]:
    """
    Calculate DEPLOYMENT_FREQUENCY metric based on daily deployment count.
    For each day in the period, count the number of deployments (0 if none).
    """
    conn = get_db_connection(db_name)
    
    # Get deployments in timeframe
    deployments_tf = pd.read_sql_query(
        "SELECT timestamp FROM observations WHERE type = 'DEPLOYMENT' AND timestamp BETWEEN ? AND ?",
        conn, params=[start_time, end_time]
    )
    
    # Get all deployments for population
    deployments_pop = pd.read_sql_query(
        "SELECT timestamp FROM observations WHERE type = 'DEPLOYMENT'", conn
    )
    
    conn.close()
    
    def calculate_daily_counts(deployments_df, period_start, period_end, use_actual_data_range=False):
        """
        Calculate deployment count for each day in the period.
        Returns a series with one value per day (0 for days with no deployments).
        
        Args:
            deployments_df: DataFrame with deployment timestamps
            period_start: Start of period
            period_end: End of period
            use_actual_data_range: If True, only count days between actual min/max data timestamps
        """
        if deployments_df.empty:
            # Return empty series if no data
            return pd.Series([]), None, None
        
        # Convert timestamps to datetime and extract date
        deployments_df['timestamp'] = pd.to_datetime(deployments_df['timestamp'])
        deployments_df['date'] = deployments_df['timestamp'].dt.date
        
        if use_actual_data_range:
            # Use actual data range instead of requested range
            actual_min = deployments_df['timestamp'].min()
            actual_max = deployments_df['timestamp'].max()
            period_start_dt = actual_min
            period_end_dt = actual_max
            min_timestamp = actual_min.strftime('%Y-%m-%d %H:%M:%S')
            max_timestamp = actual_max.strftime('%Y-%m-%d %H:%M:%S')
        else:
            period_start_dt = pd.to_datetime(period_start)
            period_end_dt = pd.to_datetime(period_end)
            min_timestamp = None
            max_timestamp = None
        
        # Generate all dates in the period
        date_range = pd.date_range(start=period_start_dt.date(), end=period_end_dt.date(), freq='D')
        
        # Count deployments per day
        daily_counts = deployments_df.groupby('date').size()
        
        # Create series with all dates, filling missing dates with 0
        all_dates_counts = []
        for date in date_range:
            count = daily_counts.get(date.date(), 0)
            all_dates_counts.append(float(count))
        
        return pd.Series(all_dates_counts), min_timestamp, max_timestamp
    
    # Calculate timeframe values using actual data range
    timeframe_values, min_timestamp, max_timestamp = calculate_daily_counts(
        deployments_tf, start_time, end_time, use_actual_data_range=True
    )
    
    # For population, use the full span of all data
    if not deployments_pop.empty:
        deployments_pop['timestamp'] = pd.to_datetime(deployments_pop['timestamp'])
        pop_start = deployments_pop['timestamp'].min().strftime('%Y-%m-%d %H:%M:%S')
        pop_end = deployments_pop['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S')
        population_values, _, _ = calculate_daily_counts(deployments_pop, pop_start, pop_end, use_actual_data_range=False)
    else:
        # If no deployments at all, return at least one observation of 0
        population_values = pd.Series([0.0])
    
    result = _calculate_z_score_metrics(timeframe_values, population_values, min_timestamp, max_timestamp)
    return result


def calculate_change_failure_rate(start_time: str, end_time: str, db_name: str) -> Dict[str, Any]:
    """
    Calculate CHANGE_FAILURE_RATE metric.
    Rate = (Number of DEPLOYMENT_FAILURE) / (Total DEPLOYMENT)
    For each deployment in the timeframe, we check if it resulted in a failure (value=1) or not (value=0).
    
    DEPLOYMENT is the "resolving observation" - we get all deployments in the timeframe
    and check if each has a corresponding failure (which may occur later).
    """
    conn = get_db_connection(db_name)
    
    # Get all deployments in timeframe - this is the "resolving observation"
    deployments_tf = pd.read_sql_query(
        "SELECT id, timestamp FROM observations WHERE type = 'DEPLOYMENT' AND timestamp BETWEEN ? AND ?",
        conn, params=[start_time, end_time]
    )
    
    # Get all failures (regardless of timestamp) to check against deployments
    failures_tf = pd.read_sql_query(
        "SELECT deployment_id, timestamp FROM observations WHERE type = 'DEPLOYMENT_FAILURE'",
        conn
    )
    
    # Get all deployments and failures for population
    deployments_pop = pd.read_sql_query(
        "SELECT id, timestamp FROM observations WHERE type = 'DEPLOYMENT'", conn
    )
    failures_pop = pd.read_sql_query(
        "SELECT deployment_id, timestamp FROM observations WHERE type = 'DEPLOYMENT_FAILURE'", conn
    )
    
    conn.close()
    
    def calculate_failure_indicators(deployments_df, failures_df):
        """
        For each deployment, return 1 if it failed, 0 if it succeeded.
        This gives us individual observations rather than a single rate.
        """
        failure_indicators = []
        
        for _, deployment in deployments_df.iterrows():
            deployment_id = deployment['id']
            # Check if this deployment has a corresponding failure
            has_failure = deployment_id in failures_df['deployment_id'].values
            failure_indicators.append(1.0 if has_failure else 0.0)
        
        return pd.Series(failure_indicators)
    
    timeframe_values = calculate_failure_indicators(deployments_tf, failures_tf)
    population_values = calculate_failure_indicators(deployments_pop, failures_pop)
    
    result = _calculate_z_score_metrics(timeframe_values, population_values)
    return result


def calculate_mean_time_to_recover(start_time: str, end_time: str, db_name: str) -> Dict[str, Any]:
    """
    Calculate MEAN_TIME_TO_RECOVER metric.
    Average time (in minutes) between DEPLOYMENT_FAILURE and DEPLOYMENT_FAILURE_FIX.
    
    Only DEPLOYMENT_FAILURE_FIX needs to be within the timeframe - the related DEPLOYMENT_FAILURE can be earlier.
    """
    conn = get_db_connection(db_name)
    
    # Get fixes in timeframe - this is the "resolving observation"
    fixes_tf = pd.read_sql_query(
        """SELECT deployment_failure_id, timestamp 
           FROM observations 
           WHERE type = 'DEPLOYMENT_FAILURE_FIX' AND timestamp BETWEEN ? AND ?""",
        conn, params=[start_time, end_time]
    )
    
    # Get the failures related to fixes in timeframe (regardless of failure timestamp)
    if not fixes_tf.empty:
        failure_ids = fixes_tf['deployment_failure_id'].dropna().unique().tolist()
        if failure_ids:
            placeholders = ','.join(['?' for _ in failure_ids])
            # Match on deployment_failure_id or id
            failures_tf = pd.read_sql_query(
                f"""SELECT id, deployment_failure_id, timestamp 
                   FROM observations 
                   WHERE type = 'DEPLOYMENT_FAILURE' 
                   AND (deployment_failure_id IN ({placeholders}) OR id IN ({placeholders}))""",
                conn, params=failure_ids + failure_ids
            )
        else:
            failures_tf = pd.DataFrame(columns=['id', 'deployment_failure_id', 'timestamp'])
    else:
        failures_tf = pd.DataFrame(columns=['id', 'deployment_failure_id', 'timestamp'])
    
    # Get all failures and fixes for population
    failures_pop = pd.read_sql_query(
        """SELECT id, deployment_failure_id, timestamp 
           FROM observations 
           WHERE type = 'DEPLOYMENT_FAILURE'""", conn
    )
    fixes_pop = pd.read_sql_query(
        """SELECT deployment_failure_id, timestamp 
           FROM observations 
           WHERE type = 'DEPLOYMENT_FAILURE_FIX'""", conn
    )
    
    conn.close()
    
    def calculate_recovery_times(failures_df, fixes_df):
        """Calculate recovery times for failure-fix pairs."""
        recovery_times = []
        
        for _, fix in fixes_df.iterrows():
            fix_failure_id = fix['deployment_failure_id']
            # Find the matching failure
            matching_failures = failures_df[
                (failures_df['deployment_failure_id'] == fix_failure_id) | 
                (failures_df['id'] == fix_failure_id)
            ]
            
            if not matching_failures.empty:
                failure_time = pd.to_datetime(matching_failures.iloc[0]['timestamp'])
                fix_time = pd.to_datetime(fix['timestamp'])
                recovery_minutes = (fix_time - failure_time).total_seconds() / 60
                recovery_times.append(recovery_minutes)
        
        return pd.Series(recovery_times)
    
    timeframe_values = calculate_recovery_times(failures_tf, fixes_tf)
    population_values = calculate_recovery_times(failures_pop, fixes_pop)
    
    result = _calculate_z_score_metrics(timeframe_values, population_values)
    return result


def calculate_lines_of_code(start_time: str, end_time: str, db_name: str) -> Dict[str, Any]:
    """
    Calculate LINES_OF_CODE metric based on daily sum of lines of code.
    For each day in the period, sum the lines of code (0 if none).
    """
    conn = get_db_connection(db_name)
    
    # Get lines of code in timeframe
    loc_tf = pd.read_sql_query(
        "SELECT timestamp, value FROM observations WHERE type = 'LINES_OF_CODE' AND timestamp BETWEEN ? AND ?",
        conn, params=[start_time, end_time]
    )
    
    # Get all lines of code for population
    loc_pop = pd.read_sql_query(
        "SELECT timestamp, value FROM observations WHERE type = 'LINES_OF_CODE'", conn
    )
    
    conn.close()
    
    def calculate_daily_sums(df, period_start, period_end, use_actual_data_range=False):
        """
        Calculate sum of lines of code for each day in the period.
        Returns a series with one value per day (0 for days with no data).
        """
        if df.empty:
            return pd.Series([]), None, None
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        if use_actual_data_range:
            actual_min = df['timestamp'].min()
            actual_max = df['timestamp'].max()
            period_start_dt = actual_min
            period_end_dt = actual_max
            min_timestamp = actual_min.strftime('%Y-%m-%d %H:%M:%S')
            max_timestamp = actual_max.strftime('%Y-%m-%d %H:%M:%S')
        else:
            period_start_dt = pd.to_datetime(period_start)
            period_end_dt = pd.to_datetime(period_end)
            min_timestamp = None
            max_timestamp = None
        
        date_range = pd.date_range(start=period_start_dt.date(), end=period_end_dt.date(), freq='D')
        
        # Sum values per day
        daily_sums = df.groupby('date')['value'].sum()
        
        all_dates_sums = []
        for date in date_range:
            total = daily_sums.get(date.date(), 0)
            all_dates_sums.append(float(total))
        
        return pd.Series(all_dates_sums), min_timestamp, max_timestamp
    
    timeframe_values, min_timestamp, max_timestamp = calculate_daily_sums(
        loc_tf, start_time, end_time, use_actual_data_range=True
    )
    
    if not loc_pop.empty:
        loc_pop['timestamp'] = pd.to_datetime(loc_pop['timestamp'])
        pop_start = loc_pop['timestamp'].min().strftime('%Y-%m-%d %H:%M:%S')
        pop_end = loc_pop['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S')
        population_values, _, _ = calculate_daily_sums(loc_pop, pop_start, pop_end, use_actual_data_range=False)
    else:
        population_values = pd.Series([0.0])
    
    result = _calculate_z_score_metrics(timeframe_values, population_values, min_timestamp, max_timestamp)
    return result


def calculate_number_of_commits(start_time: str, end_time: str, db_name: str) -> Dict[str, Any]:
    """
    Calculate NUMBER_OF_COMMITS metric based on daily commit count.
    For each day in the period, count the number of commits (0 if none).
    """
    conn = get_db_connection(db_name)
    
    # Get commits in timeframe
    commits_tf = pd.read_sql_query(
        "SELECT timestamp FROM observations WHERE type = 'COMMIT' AND timestamp BETWEEN ? AND ?",
        conn, params=[start_time, end_time]
    )
    
    # Get all commits for population
    commits_pop = pd.read_sql_query(
        "SELECT timestamp FROM observations WHERE type = 'COMMIT'", conn
    )
    
    conn.close()
    
    def calculate_daily_counts(commits_df, period_start, period_end, use_actual_data_range=False):
        """
        Calculate commit count for each day in the period.
        Returns a series with one value per day (0 for days with no commits).
        
        Args:
            commits_df: DataFrame with commit timestamps
            period_start: Start of period
            period_end: End of period
            use_actual_data_range: If True, only count days between actual min/max data timestamps
        """
        if commits_df.empty:
            # Return empty series if no data
            return pd.Series([]), None, None
        
        # Convert timestamps to datetime and extract date
        commits_df['timestamp'] = pd.to_datetime(commits_df['timestamp'])
        commits_df['date'] = commits_df['timestamp'].dt.date
        
        if use_actual_data_range:
            # Use actual data range instead of requested range
            actual_min = commits_df['timestamp'].min()
            actual_max = commits_df['timestamp'].max()
            period_start_dt = actual_min
            period_end_dt = actual_max
            min_timestamp = actual_min.strftime('%Y-%m-%d %H:%M:%S')
            max_timestamp = actual_max.strftime('%Y-%m-%d %H:%M:%S')
        else:
            period_start_dt = pd.to_datetime(period_start)
            period_end_dt = pd.to_datetime(period_end)
            min_timestamp = None
            max_timestamp = None
        
        # Generate all dates in the period
        date_range = pd.date_range(start=period_start_dt.date(), end=period_end_dt.date(), freq='D')
        
        # Count commits per day
        daily_counts = commits_df.groupby('date').size()
        
        # Create series with all dates, filling missing dates with 0
        all_dates_counts = []
        for date in date_range:
            count = daily_counts.get(date.date(), 0)
            all_dates_counts.append(float(count))
        
        return pd.Series(all_dates_counts), min_timestamp, max_timestamp
    
    # Calculate timeframe values using actual data range
    timeframe_values, min_timestamp, max_timestamp = calculate_daily_counts(
        commits_tf, start_time, end_time, use_actual_data_range=True
    )
    
    # For population, use the full span of all data
    if not commits_pop.empty:
        commits_pop['timestamp'] = pd.to_datetime(commits_pop['timestamp'])
        pop_start = commits_pop['timestamp'].min().strftime('%Y-%m-%d %H:%M:%S')
        pop_end = commits_pop['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S')
        population_values, _, _ = calculate_daily_counts(commits_pop, pop_start, pop_end, use_actual_data_range=False)
    else:
        # If no commits at all, return at least one observation of 0
        population_values = pd.Series([0.0])
    
    result = _calculate_z_score_metrics(timeframe_values, population_values, min_timestamp, max_timestamp)
    return result


def calculate_communication_frequency(start_time: str, end_time: str, db_name: str) -> Dict[str, Any]:
    """Calculate COMMUNICATION_FREQUENCY metric based on COMMUNICATION_EVENT observations."""
    timeframe_df = _get_observations_df("COMMUNICATION_EVENT", db_name, start_time, end_time)
    population_df = _get_observations_df("COMMUNICATION_EVENT", db_name)
    
    result = _calculate_z_score_metrics(timeframe_df['value'], population_df['value'])
    return result


def calculate_perceived_productivity(start_time: str, end_time: str, db_name: str) -> Dict[str, Any]:
    """Calculate PERCEIVED_PRODUCTIVITY metric based on PERCEIVED_PRODUCTIVITY observations."""
    timeframe_df = _get_observations_df("PERCEIVED_PRODUCTIVITY", db_name, start_time, end_time)
    population_df = _get_observations_df("PERCEIVED_PRODUCTIVITY", db_name)
    
    result = _calculate_z_score_metrics(timeframe_df['value'], population_df['value'])
    return result


def calculate_lack_of_interruptions(start_time: str, end_time: str, db_name: str) -> Dict[str, Any]:
    """Calculate LACK_OF_INTERRUPTIONS metric based on WORK_SESSION observations."""
    timeframe_df = _get_observations_df("WORK_SESSION", db_name, start_time, end_time)
    population_df = _get_observations_df("WORK_SESSION", db_name)
    
    result = _calculate_z_score_metrics(timeframe_df['value'], population_df['value'])
    return result


def calculate_lead_time_for_changes(start_time: str, end_time: str, db_name: str) -> Dict[str, Any]:
    """
    Calculate LEAD_TIME_FOR_CHANGES metric.
    Average time (in minutes) between COMMIT and DEPLOYMENT for commits with deployment references.
    
    Only DEPLOYMENT needs to be within the timeframe - the related COMMIT can be earlier.
    """
    conn = get_db_connection(db_name)
    
    # Get deployments in timeframe - this is the "resolving observation"
    deployments_tf = pd.read_sql_query(
        """SELECT id, timestamp 
           FROM observations 
           WHERE type = 'DEPLOYMENT' AND timestamp BETWEEN ? AND ?""",
        conn, params=[start_time, end_time]
    )
    
    # Get commits that reference deployments in timeframe (regardless of commit timestamp)
    if not deployments_tf.empty:
        deployment_ids = deployments_tf['id'].tolist()
        placeholders = ','.join(['?' for _ in deployment_ids])
        commits_tf = pd.read_sql_query(
            f"""SELECT commit_hash, deployment_id, timestamp 
               FROM observations 
               WHERE type = 'COMMIT' AND deployment_id IN ({placeholders})""",
            conn, params=deployment_ids
        )
    else:
        commits_tf = pd.DataFrame(columns=['commit_hash', 'deployment_id', 'timestamp'])
    
    # Get all commits and deployments for population
    commits_pop = pd.read_sql_query(
        """SELECT commit_hash, deployment_id, timestamp 
           FROM observations 
           WHERE type = 'COMMIT' AND deployment_id IS NOT NULL""", conn
    )
    deployments_pop = pd.read_sql_query(
        """SELECT id, timestamp 
           FROM observations 
           WHERE type = 'DEPLOYMENT'""", conn
    )
    
    conn.close()
    
    def calculate_lead_times(commits_df, deployments_df):
        """Calculate lead times for commit-deployment pairs using vectorized operations."""
        if commits_df.empty or deployments_df.empty:
            return pd.Series([])
        
        # Prepare deployments dataframe with timestamp as index for fast lookup
        deployments_lookup = deployments_df.set_index('id')['timestamp']
        
        # Merge commits with deployments on deployment_id
        commits_with_deployments = commits_df.copy()
        commits_with_deployments['deployment_timestamp'] = commits_with_deployments['deployment_id'].map(deployments_lookup)
        
        # Filter out commits without matching deployment
        commits_with_deployments = commits_with_deployments.dropna(subset=['deployment_timestamp'])
        
        # Vectorized datetime conversion and calculation
        commit_times = pd.to_datetime(commits_with_deployments['timestamp'])
        deployment_times = pd.to_datetime(commits_with_deployments['deployment_timestamp'])
        lead_times = (deployment_times - commit_times).dt.total_seconds() / 60
        
        return lead_times
    
    timeframe_values = calculate_lead_times(commits_tf, deployments_tf)
    population_values = calculate_lead_times(commits_pop, deployments_pop)
    
    result = _calculate_z_score_metrics(timeframe_values, population_values)
    return result


def calculate_ai_acceptance_rate(start_time: str, end_time: str, db_name: str) -> Dict[str, Any]:
    """Calculate AI_ACCEPTANCE_RATE metric based on AI_SUGGESTION_RESULT observations."""
    timeframe_df = _get_observations_df("AI_SUGGESTION_RESULT", db_name, start_time, end_time)
    population_df = _get_observations_df("AI_SUGGESTION_RESULT", db_name)
    
    result = _calculate_z_score_metrics(timeframe_df['value'], population_df['value'])
    return result


def calculate_lines_of_code_ai(start_time: str, end_time: str, db_name: str) -> Dict[str, Any]:
    """
    Calculate LINES_OF_CODE_AI metric based on daily sum of AI-generated lines of code.
    For each day in the period, sum the AI lines of code (0 if none).
    """
    conn = get_db_connection(db_name)
    
    # Get AI lines of code in timeframe
    loc_ai_tf = pd.read_sql_query(
        "SELECT timestamp, value FROM observations WHERE type = 'LINES_OF_CODE_AI' AND timestamp BETWEEN ? AND ?",
        conn, params=[start_time, end_time]
    )
    
    # Get all AI lines of code for population
    loc_ai_pop = pd.read_sql_query(
        "SELECT timestamp, value FROM observations WHERE type = 'LINES_OF_CODE_AI'", conn
    )
    
    conn.close()
    
    def calculate_daily_sums(df, period_start, period_end, use_actual_data_range=False):
        """
        Calculate sum of AI lines of code for each day in the period.
        Returns a series with one value per day (0 for days with no data).
        """
        if df.empty:
            return pd.Series([]), None, None
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        if use_actual_data_range:
            actual_min = df['timestamp'].min()
            actual_max = df['timestamp'].max()
            period_start_dt = actual_min
            period_end_dt = actual_max
            min_timestamp = actual_min.strftime('%Y-%m-%d %H:%M:%S')
            max_timestamp = actual_max.strftime('%Y-%m-%d %H:%M:%S')
        else:
            period_start_dt = pd.to_datetime(period_start)
            period_end_dt = pd.to_datetime(period_end)
            min_timestamp = None
            max_timestamp = None
        
        date_range = pd.date_range(start=period_start_dt.date(), end=period_end_dt.date(), freq='D')
        
        # Sum values per day
        daily_sums = df.groupby('date')['value'].sum()
        
        all_dates_sums = []
        for date in date_range:
            total = daily_sums.get(date.date(), 0)
            all_dates_sums.append(float(total))
        
        return pd.Series(all_dates_sums), min_timestamp, max_timestamp
    
    timeframe_values, min_timestamp, max_timestamp = calculate_daily_sums(
        loc_ai_tf, start_time, end_time, use_actual_data_range=True
    )
    
    if not loc_ai_pop.empty:
        loc_ai_pop['timestamp'] = pd.to_datetime(loc_ai_pop['timestamp'])
        pop_start = loc_ai_pop['timestamp'].min().strftime('%Y-%m-%d %H:%M:%S')
        pop_end = loc_ai_pop['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S')
        population_values, _, _ = calculate_daily_sums(loc_ai_pop, pop_start, pop_end, use_actual_data_range=False)
    else:
        population_values = pd.Series([0.0])
    
    result = _calculate_z_score_metrics(timeframe_values, population_values, min_timestamp, max_timestamp)
    return result


def calculate_ai_rework_rate(start_time: str, end_time: str, db_name: str) -> Dict[str, Any]:
    """
    Calculate AI_REWORK_RATE metric.
    For each commit, return 1 if it's a rework commit (ai_rework_commit = 1), 0 otherwise.
    """
    conn = get_db_connection(db_name)
    
    # Get timeframe data - individual commits
    commits_tf = pd.read_sql_query(
        "SELECT ai_rework_commit FROM observations WHERE type = 'COMMIT' AND timestamp BETWEEN ? AND ?",
        conn, params=[start_time, end_time]
    )
    
    # Get population data
    commits_pop = pd.read_sql_query(
        "SELECT ai_rework_commit FROM observations WHERE type = 'COMMIT'", conn
    )
    
    conn.close()
    
    def calculate_rework_indicators(commits_df):
        """
        For each commit, return 1 if it's a rework commit, 0 otherwise.
        This gives us individual observations rather than a single rate.
        """
        # Convert ai_rework_commit to 1.0 or 0.0
        rework_indicators = commits_df['ai_rework_commit'].fillna(0).astype(float)
        return rework_indicators
    
    timeframe_values = calculate_rework_indicators(commits_tf)
    population_values = calculate_rework_indicators(commits_pop)
    
    result = _calculate_z_score_metrics(timeframe_values, population_values)
    return result
