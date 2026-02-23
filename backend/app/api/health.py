"""Health check endpoint with dependency status."""

from __future__ import annotations

import logging
import threading
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


_redis_client: "object | None" = None
_redis_client_lock = threading.Lock()


def _get_redis_client() -> "object | None":
    """Get or create Redis client for health checks (thread-safe, double-checked locking)."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    with _redis_client_lock:
        if _redis_client is not None:
            return _redis_client

        try:
            from app.ai_engine.config import ai_engine_settings

            if not ai_engine_settings.redis_url:
                return None

            import redis

            _redis_client = redis.from_url(
                ai_engine_settings.redis_url,
                decode_responses=False,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
            )
            return _redis_client
        except ImportError:
            return None
        except Exception:
            return None


def _check_redis() -> ServiceStatus:
    """Check Redis connection."""
    try:
        from app.ai_engine.config import ai_engine_settings

        if not ai_engine_settings.redis_url:
            return ServiceStatus(status="ok", message="not configured")

        client = _get_redis_client()
        if client is None:
            return ServiceStatus(status="ok", message="redis not installed")

        client.ping()  # type: ignore[union-attr]
        return ServiceStatus(status="ok")
    except ImportError:
        return ServiceStatus(status="ok", message="redis not installed")
    except Exception as e:
        logger.warning("health_check_redis_error error=%s", str(e))
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
    redis_status = _check_redis()

    services = {
        "db": db_status,
        "redis": redis_status,
    }

    if db_status.status == "error":
        overall = "unhealthy"
    elif redis_status.status == "error":
        overall = "degraded"
    else:
        overall = "healthy"

    return HealthResponse(status=overall, services=services)
