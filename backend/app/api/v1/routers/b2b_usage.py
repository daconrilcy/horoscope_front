from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies.b2b_auth import (
    AuthenticatedEnterpriseClient,
    require_authenticated_b2b_client,
)
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.audit_service import AuditEventCreatePayload, AuditService, AuditServiceError
from app.services.b2b_usage_service import (
    B2BUsageService,
    B2BUsageServiceError,
    B2BUsageSummaryData,
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


class B2BUsageSummaryApiResponse(BaseModel):
    data: B2BUsageSummaryData
    meta: ResponseMeta


router = APIRouter(prefix="/v1/b2b/usage", tags=["b2b-usage"])


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
    check_rate_limit(key=f"b2b_usage:global:{operation}", limit=240, window_seconds=60)
    check_rate_limit(
        key=f"b2b_usage:account:{client.account_id}:{operation}",
        limit=120,
        window_seconds=60,
    )
    check_rate_limit(
        key=f"b2b_usage:credential:{client.credential_id}:{operation}",
        limit=60,
        window_seconds=60,
    )


def _record_usage_audit(
    db: Session,
    *,
    request_id: str,
    action: str,
    status: str,
    account_id: int,
    credential_id: int,
    details: dict[str, object],
) -> None:
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=None,
            actor_role="enterprise_client",
            action=action,
            target_type="enterprise_usage",
            target_id=str(credential_id),
            status=status,
            details={"account_id": account_id, **details},
        ),
    )


@router.get(
    "/summary",
    response_model=B2BUsageSummaryApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def get_b2b_usage_summary(
    request: Request,
    client: AuthenticatedEnterpriseClient = Depends(require_authenticated_b2b_client),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    try:
        _enforce_limits(client=client, operation="summary")
        summary = B2BUsageService.get_usage_summary(
            db,
            account_id=client.account_id,
            credential_id=client.credential_id,
        )
        _record_usage_audit(
            db,
            request_id=request_id,
            action="b2b_usage_summary_read",
            status="success",
            account_id=client.account_id,
            credential_id=client.credential_id,
            details={},
        )
        db.commit()
        return {"data": summary.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except RateLimitError as error:
        db.rollback()
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except B2BUsageServiceError as error:
        db.rollback()
        try:
            _record_usage_audit(
                db,
                request_id=request_id,
                action="b2b_usage_summary_read",
                status="failed",
                account_id=client.account_id,
                credential_id=client.credential_id,
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
        status_code = 429 if error.code == "b2b_quota_exceeded" else 422
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
