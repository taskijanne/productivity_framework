"""
Pydantic schemas for the AI Productivity Framework.
"""

from pydantic import BaseModel
from typing import Optional


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


class MetricResult(BaseModel):
    """Model for metric calculation result."""
    metric_type: str
    start_time: str
    end_time: str
    mean_value: float
    amount_of_observations: int
    z_score: float
    z_score_mean: float
    z_score_std: float
