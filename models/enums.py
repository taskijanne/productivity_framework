"""
Enums for the AI Productivity Framework.
"""

from enum import Enum


class ObservationType(str, Enum):
    """Enum for allowed observation types."""
    SATISFACTION = "SATISFACTION"
    TEAM_SIZE_CHANGE = "TEAM_SIZE_CHANGE"
    DEPLOYMENT = "DEPLOYMENT"
    DEPLOYMENT_FAILURE = "DEPLOYMENT_FAILURE"
    DEPLOYMENT_FAILURE_FIX = "DEPLOYMENT_FAILURE_FIX"
    LINES_OF_CODE = "LINES_OF_CODE"
    COMMIT = "COMMIT"
    COMMUNICATION_EVENT = "COMMUNICATION_EVENT"
    PERCEIVED_PRODUCTIVITY = "PERCEIVED_PRODUCTIVITY"
    WORK_SESSION = "WORK_SESSION"
    AI_SUGGESTION_RESULT = "AI_SUGGESTION_RESULT"
    LINES_OF_CODE_AI = "LINES_OF_CODE_AI"


class MetricType(str, Enum):
    """Enum for allowed metric types with descriptions."""
    SATISFACTION = "SATISFACTION"
    RETENTION = "RETENTION"
    DEPLOYMENT_FREQUENCY = "DEPLOYMENT_FREQUENCY"
    CHANGE_FAILURE_RATE = "CHANGE_FAILURE_RATE"
    MEAN_TIME_TO_RECOVER = "MEAN_TIME_TO_RECOVER"
    LINES_OF_CODE = "LINES_OF_CODE"
    NUMBER_OF_COMMITS = "NUMBER_OF_COMMITS"
    COMMUNICATION_FREQUENCY = "COMMUNICATION_FREQUENCY"
    PERCEIVED_PRODUCTIVITY = "PERCEIVED_PRODUCTIVITY"
    LACK_OF_INTERRUPTIONS = "LACK_OF_INTERRUPTIONS"
    LEAD_TIME_FOR_CHANGES = "LEAD_TIME_FOR_CHANGES"
    AI_ACCEPTANCE_RATE = "AI_ACCEPTANCE_RATE"
    AI_CODE_VOLUME = "AI_CODE_VOLUME"
    AI_REWORK_RATE = "AI_REWORK_RATE"
    
    @property
    def description(self) -> str:
        """Get the description for this metric type."""
        descriptions = {
            "SATISFACTION": "Developer satisfaction scores",
            "RETENTION": "Team retention rate",
            "DEPLOYMENT_FREQUENCY": "Number of DAILY deployments",
            "CHANGE_FAILURE_RATE": "Rate of deployment failures",
            "MEAN_TIME_TO_RECOVER": "Average recovery time from failures (minutes)",
            "LINES_OF_CODE": "Lines of code written",
            "NUMBER_OF_COMMITS": "Number of commits",
            "COMMUNICATION_FREQUENCY": "Communication event frequency",
            "PERCEIVED_PRODUCTIVITY": "Self-reported productivity",
            "LACK_OF_INTERRUPTIONS": "Uninterrupted work session quality",
            "LEAD_TIME_FOR_CHANGES": "Time from commit to deployment (minutes)",
            "AI_ACCEPTANCE_RATE": "Rate of AI suggestions accepted",
            "AI_CODE_VOLUME": "Ratio of AI-generated code",
            "AI_REWORK_RATE": "Rate of AI-generated code requiring rework"
        }
        return descriptions.get(self.value, "No description available")
    
    @classmethod
    def get_all_with_descriptions(cls) -> dict:
        """Get all metric types with their descriptions."""
        return {
            "metric_types": [metric.value for metric in cls],
            "descriptions": {metric.value: metric.description for metric in cls}
        }

