"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.domain.llm.runtime.errors import AIEngineError, RateLimitExceededError
from app.infra.llm.rate_limiter import RateLimiter
from app.infra.observability.metrics import increment_counter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/ai", tags=["ai"])


def _check_rate_limit(user_id: int) -> None:
    """Check rate limit and raise if exceeded."""
    limiter = RateLimiter.get_instance()
    result = limiter.check_rate_limit(user_id)
    if not result.allowed:
        logger.warning(
            "ai_rate_limit_exceeded user_id=%d current_count=%d limit=%d retry_after_ms=%d",
            user_id,
            result.current_count,
            result.limit,
            result.retry_after_ms or 0,
        )
        increment_counter("ai_engine_rate_limit_exceeded_total", 1.0)
        raise RateLimitExceededError(
            retry_after_ms=result.retry_after_ms or 60000,
            user_id=user_id,
        )


def _resolve_trace_id(request: Request, body_trace_id: str | None) -> str:
    """Resolve trace_id from request or generate new one."""
    if body_trace_id:
        return body_trace_id
    trace_header = request.headers.get("X-Trace-Id")
    if trace_header:
        return trace_header
    return f"trace_{uuid.uuid4().hex[:16]}"


def _build_error_response(
    error: AIEngineError,
    request_id: str,
    trace_id: str,
) -> JSONResponse:
    """Build error response from AIEngineError."""
    return JSONResponse(
        status_code=error.status_code,
        content={
            "error": {
                **error.to_dict(),
                "request_id": request_id,
                "trace_id": trace_id,
            }
        },
    )
