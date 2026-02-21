from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.api.dependencies.b2b_auth import (
    AuthenticatedEnterpriseClient,
    require_authenticated_b2b_client,
)
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.infra.observability.metrics import increment_counter
from app.services.audit_service import AuditEventCreatePayload, AuditService, AuditServiceError
from app.services.b2b_editorial_service import (
    B2BEditorialConfigData,
    B2BEditorialConfigUpdatePayload,
    B2BEditorialService,
    B2BEditorialServiceError,
)


class ResponseMeta(BaseModel):
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class B2BEditorialConfigApiResponse(BaseModel):
    data: B2BEditorialConfigData
    meta: ResponseMeta


router = APIRouter(prefix="/v1/b2b/editorial", tags=["b2b-editorial"])


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


@router.get(
    "/config",
    response_model=B2BEditorialConfigApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_editorial_config(
    request: Request,
    client: AuthenticatedEnterpriseClient = Depends(require_authenticated_b2b_client),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    try:
        _enforce_limits(client=client, operation="get_config")
        config = B2BEditorialService.get_active_config(db, account_id=client.account_id)
        return {"data": config.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except RateLimitError as error:
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except B2BEditorialServiceError as error:
        status_code = 404 if error.code == "enterprise_account_not_found" else 422
        return _error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )


@router.put(
    "/config",
    response_model=B2BEditorialConfigApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def update_editorial_config(
    request: Request,
    payload: Any = Body(...),
    client: AuthenticatedEnterpriseClient = Depends(require_authenticated_b2b_client),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    try:
        _enforce_limits(client=client, operation="update_config")
        parsed = B2BEditorialConfigUpdatePayload.model_validate(payload)
    except RateLimitError as error:
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except ValidationError as error:
        increment_counter("b2b_editorial_validation_failures_total", 1.0)
        sanitized_errors = _sanitize_validation_errors(error)
        try:
            _record_editorial_audit(
                db,
                request_id=request_id,
                action="b2b_editorial_config_update",
                target_id=None,
                status="failed",
                details={"error_code": "invalid_editorial_config", "errors": sanitized_errors},
            )
            db.commit()
        except AuditServiceError:
            db.rollback()
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_editorial_config",
            message="editorial config validation failed",
            details={"errors": sanitized_errors},
        )

    try:
        saved = B2BEditorialService.upsert_config(
            db,
            account_id=client.account_id,
            credential_id=client.credential_id,
            payload=parsed,
        )
        _record_editorial_audit(
            db,
            request_id=request_id,
            action="b2b_editorial_config_update",
            target_id=str(saved.config_id) if saved.config_id is not None else None,
            status="success",
            details={"version_number": saved.version_number},
        )
        db.commit()
        return {"data": saved.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except B2BEditorialServiceError as error:
        db.rollback()
        increment_counter("b2b_editorial_validation_failures_total", 1.0)
        try:
            _record_editorial_audit(
                db,
                request_id=request_id,
                action="b2b_editorial_config_update",
                target_id=None,
                status="failed",
                details={"error_code": error.code},
            )
            db.commit()
        except AuditServiceError:
            db.rollback()
            return _error_response(
                status_code=503,
                request_id=request_id,
                code="audit_unavailable",
                message="audit service is unavailable",
                details={},
            )
        status_code = 404 if error.code == "enterprise_account_not_found" else 422
        return _error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except AuditServiceError:
        db.rollback()
        return _error_response(
            status_code=503,
            request_id=request_id,
            code="audit_unavailable",
            message="audit service is unavailable",
            details={},
        )
