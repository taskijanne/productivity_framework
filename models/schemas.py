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
    z_score: Optional[float] = None
    z_score_mean: Optional[float] = None
    z_score_std: Optional[float] = None
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


class IntervalMetricResult(BaseModel):
    """Model for metric calculation result within a specific interval."""
    interval_number: int = Field(..., description="Interval number (1-based)")
    metric_type: str
    start_time: str
    end_time: str
    mean_value: float
    amount_of_observations: int
    z_score: Optional[float] = None
    z_score_mean: Optional[float] = None
    z_score_std: Optional[float] = None
    min_timestamp: Optional[str] = None
    max_timestamp: Optional[str] = None


class SingleMetricResult(BaseModel):
    """Model for a single metric result within an interval."""
    metric_type: str
    mean_value: float
    amount_of_observations: int
    z_score: Optional[float] = None
    z_score_mean: Optional[float] = None
    z_score_std: Optional[float] = None
    min_timestamp: Optional[str] = None
    max_timestamp: Optional[str] = None


class CorrelationResult(BaseModel):
    """Model for correlation between two metrics across intervals."""
    metric_1: str = Field(..., description="First metric type")
    metric_2: str = Field(..., description="Second metric type")
    pearson_coefficient: float = Field(..., description="Pearson correlation coefficient (-1 to 1)")
    p_value: float = Field(..., description="Statistical significance (p-value)")
    sample_size: int = Field(..., description="Number of intervals used in calculation")
    interpretation: str = Field(..., description="Human-readable interpretation of the correlation")


class IntervalMetricsResult(BaseModel):
    """Model for multiple metrics calculation results within a specific interval."""
    interval_number: int = Field(..., description="Interval number (1-based)")
    start_time: str = Field(..., description="Start time of the interval")
    end_time: str = Field(..., description="End time of the interval")
    metrics: List[SingleMetricResult] = Field(..., description="List of metric results for this interval")


class MetricsResponse(BaseModel):
    """Model for the complete metrics response including intervals and correlations."""
    intervals: List[IntervalMetricsResult] = Field(..., description="List of interval results")
    correlations: Optional[List[CorrelationResult]] = Field(None, description="Correlations between metrics (only when multiple metrics and intervals > 1)")


class CPSIntervalRequest(BaseModel):
    """Model for Composite Productivity Score calculation request with intervals support."""
    start_time: str = Field(..., description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS)")
    end_time: str = Field(..., description="End time in ISO format (YYYY-MM-DDTHH:MM:SS)")
    intervals: int = Field(1, gt=0, description="Number of intervals to divide the time period into (default: 1)")
    metrics: List[MetricWeight] = Field(..., min_length=1, description="List of metrics with weights")


class CPSIntervalMetricResult(BaseModel):
    """Model for individual metric result in CPS interval calculation."""
    metric_type: str
    weight: float
    z_score: float
    z_score_weighted: float
    mean_value: float
    amount_of_observations: int
    z_score_mean: float
    z_score_std: float
    min_timestamp: Optional[str] = None
    max_timestamp: Optional[str] = None


class CPSIntervalResult(BaseModel):
    """Model for CPS calculation result within a specific interval."""
    interval_number: int = Field(..., description="Interval number (1-based)")
    start_time: str = Field(..., description="Start time of the interval")
    end_time: str = Field(..., description="End time of the interval")
    cps: float = Field(..., description="Composite Productivity Score for this interval")
    metrics: List[CPSIntervalMetricResult] = Field(..., description="Individual metric results with weights")


class CPSIntervalResponse(BaseModel):
    """Model for Composite Productivity Score calculation response with intervals."""
    intervals: List[CPSIntervalResult] = Field(..., description="List of interval CPS results")
