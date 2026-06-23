"""Health check endpoint with dependency status."""

from __future__ import annotations

import logging
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from app.infra.db.session import engine

logger = logging.getLogger(__name__)

router = APIRouter()


class ServiceStatus(BaseModel):
    """Status of an individual service."""

    status: Literal["ok", "error"]
    message: str | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: Literal["healthy", "degraded", "unhealthy"]
    services: dict[str, ServiceStatus]


def _check_db() -> ServiceStatus:
    """Check database connection."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return ServiceStatus(status="ok")
    except Exception as e:
        logger.warning("health_check_db_error error=%s", str(e))
        return ServiceStatus(status="error", message=str(e)[:100])


@router.get("/health", tags=["health"], response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    """
    Health check endpoint.

    Returns aggregate status of all dependencies:
    - healthy: All services are OK
    - degraded: Some non-critical services have issues
    - unhealthy: Critical services (db) have issues
    """
    db_status = _check_db()

    services = {
        "db": db_status,
    }

    if db_status.status == "error":
        overall = "unhealthy"
    else:
        overall = "healthy"

    return HealthResponse(status=overall, services=services)
