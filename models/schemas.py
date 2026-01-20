"""
Pydantic schemas for the AI Productivity Framework.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


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
    min_timestamp: Optional[str] = None
    max_timestamp: Optional[str] = None


class MetricWeight(BaseModel):
    """Model for a metric with its weight in CPS calculation."""
    metric: str = Field(..., description="Metric type from MetricType enum")
    weight: float = Field(..., ge=0.0, le=1.0, description="Weight for this metric (0-1)")


class CPSRequest(BaseModel):
    """Model for Composite Productivity Score calculation request."""
    start_time: str = Field(..., description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS)")
    end_time: str = Field(..., description="End time in ISO format (YYYY-MM-DDTHH:MM:SS)")
    metrics: List[MetricWeight] = Field(..., min_length=1, description="List of metrics with weights")


class CPSMetricResult(BaseModel):
    """Model for individual metric result in CPS calculation."""
    metric_type: str
    weight: float
    z_score: float
    z_score_weighted: float
    mean_value: Optional[float] = None
    amount_of_observations: int
    z_score_mean: Optional[float] = None
    z_score_std: Optional[float] = None
    start_time: str
    end_time: str
    min_timestamp: Optional[str] = None
    max_timestamp: Optional[str] = None


class CPSResponse(BaseModel):
    """Model for Composite Productivity Score calculation response."""
    cps: float = Field(..., description="Composite Productivity Score")
    metrics: List[CPSMetricResult] = Field(..., description="Individual metric results with weights")
