"""
FastAPI application for the AI Productivity Framework.

This application provides REST API endpoints to access productivity metrics
stored in the SQLite database.
"""

from fastapi import FastAPI, HTTPException
from typing import List, Optional
import sqlite3
from pydantic import BaseModel
from datetime import datetime


app = FastAPI(
    title="AI Productivity Framework API",
    description="API for accessing productivity metrics and observations",
    version="1.0.0"
)


class Observation(BaseModel):
    """Model for an observation record."""
    id: int
    type: str
    timestamp: str
    value: float
    commit_hash: Optional[str] = None
    deployment_id: Optional[int] = None
    deployment_failure_id: Optional[int] = None
    ai_rework_commit: Optional[int] = None


def get_db_connection(db_name="productivity_framework.db"):
    """Create a database connection."""
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/")
def read_root():
    """Root endpoint providing API information."""
    return {
        "message": "Welcome to AI Productivity Framework API",
        "version": "1.0.0",
        "endpoints": {
            "/observations": "Get all observations",
            "/docs": "Interactive API documentation"
        }
    }


@app.get("/observations", response_model=List[Observation])
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


@app.get("/metrics")
def get_metric_types():
    """
    Get a list of all available observation types.
    
    Returns:
        dict: Dictionary containing list of observation types
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT type FROM observations ORDER BY type")
        rows = cursor.fetchall()
        conn.close()
        
        metric_types = [row["type"] for row in rows]
        
        return {"metric_types": metric_types}
        
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
