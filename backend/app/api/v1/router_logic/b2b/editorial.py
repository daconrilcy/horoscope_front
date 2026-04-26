"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.dependencies.b2b_auth import (
    AuthenticatedEnterpriseClient,
)
from app.core.rate_limit import check_rate_limit
from app.services.ops.audit_service import AuditEventCreatePayload, AuditService

router = APIRouter(prefix="/v1/b2b/editorial", tags=["b2b-editorial"])
from app.api.v1.schemas.routers.b2b.editorial import *


def _error_response(
    *,
    status_code: int,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any],
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": request_id,
            }
        },
    )


def _enforce_limits(*, client: AuthenticatedEnterpriseClient, operation: str) -> None:
    check_rate_limit(key=f"b2b_editorial:global:{operation}", limit=180, window_seconds=60)
    check_rate_limit(
        key=f"b2b_editorial:account:{client.account_id}:{operation}",
        limit=90,
        window_seconds=60,
    )
    check_rate_limit(
        key=f"b2b_editorial:credential:{client.credential_id}:{operation}",
        limit=45,
        window_seconds=60,
    )


def _record_editorial_audit(
    db: Session,
    *,
    request_id: str,
    action: str,
    target_id: str | None,
    status: str,
    details: dict[str, object],
) -> None:
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=None,
            actor_role="enterprise_client",
            action=action,
            target_type="enterprise_editorial_config",
            target_id=target_id,
            status=status,
            details=details,
        ),
    )


def _sanitize_validation_errors(error: ValidationError) -> list[dict[str, object]]:
    sanitized: list[dict[str, object]] = []
    for item in error.errors():
        sanitized.append(
            {
                "loc": [str(part) for part in item.get("loc", ())],
                "msg": str(item.get("msg", "")),
                "type": str(item.get("type", "")),
            }
        )
    return sanitized
