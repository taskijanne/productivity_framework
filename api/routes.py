"""
API routes for the AI Productivity Framework.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import sqlite3
from datetime import datetime

from models import ObservationType, Observation, MetricType, MetricResult
from database import get_db_connection
from services import calculate_metric


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


@router.get("/metrics", response_model=MetricResult)
def get_metrics(
    metric_type: str = Query(..., description="Type of metric to calculate"),
    start_time: str = Query(..., description="Start time (ISO format: YYYY-MM-DDTHH:MM:SS)"),
    end_time: str = Query(..., description="End time (ISO format: YYYY-MM-DDTHH:MM:SS)")
):
    """
    Calculate a specific metric for a given time period.
    
    Args:
        metric_type: The type of metric to calculate (e.g., SATISFACTION, RETENTION)
        start_time: Start of the time period in ISO format (YYYY-MM-DDTHH:MM:SS)
        end_time: End of the time period in ISO format (YYYY-MM-DDTHH:MM:SS)
    
    Returns:
        MetricResult: Calculated metric including mean_value, amount_of_observations,
                     z_score, z_score_mean, and z_score_std
    """
    try:
        # Validate metric type
        if metric_type not in [mt.value for mt in MetricType]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid metric type. Must be one of: {', '.join([mt.value for mt in MetricType])}"
            )
        
        # Validate and normalize timestamp format
        def validate_and_normalize_timestamp(ts: str) -> str:
            """Validate timestamp and convert to SQLite format."""
            try:
                # Try parsing ISO 8601 format with T separator
                if 'T' in ts:
                    dt = datetime.fromisoformat(ts.replace('Z', ''))
                else:
                    # Try parsing space-separated format
                    dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                
                # Return in SQLite-compatible format (space separator)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                raise ValueError(f"Invalid timestamp format: {ts}. Expected format: YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD HH:MM:SS")
        
        normalized_start = validate_and_normalize_timestamp(start_time)
        normalized_end = validate_and_normalize_timestamp(end_time)
        
        # Calculate metric
        result = calculate_metric(metric_type, normalized_start, normalized_end)
        
        # Add metadata to result (return original format)
        result["metric_type"] = metric_type
        result["start_time"] = start_time
        result["end_time"] = end_time
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating metric: {str(e)}")
