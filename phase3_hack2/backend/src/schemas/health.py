"""
Health check response schemas.
"""
from pydantic import BaseModel
from typing import Literal, Optional


class HealthCheckResponse(BaseModel):
    """
    Health check response schema.

    Attributes:
        status: Overall service health status
        database: Database connectivity status
        timestamp: UTC timestamp of health check in ISO 8601 format
        error: Optional error message (only when unhealthy)
    """
    status: Literal["healthy", "unhealthy", "degraded"]
    database: Literal["connected", "disconnected"]
    timestamp: str
    error: Optional[str] = None
