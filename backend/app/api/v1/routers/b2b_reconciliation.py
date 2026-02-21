from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Body, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.audit_service import AuditEventCreatePayload, AuditService, AuditServiceError
from app.services.b2b_reconciliation_service import (
    B2BReconciliationService,
    B2BReconciliationServiceError,
    ReconciliationActionPayload,
    ReconciliationActionResultData,
    ReconciliationIssueDetailData,
    ReconciliationIssueListData,
    ReconciliationSeverity,
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


class ReconciliationIssueListApiResponse(BaseModel):
    data: ReconciliationIssueListData
    meta: ResponseMeta


class ReconciliationIssueDetailApiResponse(BaseModel):
    data: ReconciliationIssueDetailData
    meta: ResponseMeta


class ReconciliationActionApiResponse(BaseModel):
    data: ReconciliationActionResultData
    meta: ResponseMeta


router = APIRouter(prefix="/v1/ops/b2b/reconciliation", tags=["ops-b2b-reconciliation"])


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


def _ensure_ops_role(*, user: AuthenticatedUser, request_id: str) -> JSONResponse | None:
    if user.role != "ops":
        return _error_response(
            status_code=403,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "ops", "actual_role": user.role},
        )
    return None


def _enforce_limits(*, user: AuthenticatedUser, operation: str) -> None:
    check_rate_limit(key=f"b2b_reconciliation:global:{operation}", limit=120, window_seconds=60)
    check_rate_limit(
        key=f"b2b_reconciliation:role:{user.role}:{operation}",
        limit=60,
        window_seconds=60,
    )
    check_rate_limit(
        key=f"b2b_reconciliation:user:{user.id}:{operation}",
        limit=30,
        window_seconds=60,
    )


def _record_reconciliation_audit(
    db: Session,
    *,
    request_id: str,
    user: AuthenticatedUser,
    action: str,
    status: str,
    target_id: str | None,
    details: dict[str, object],
) -> None:
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=user.id,
            actor_role=user.role,
            action=action,
            target_type="enterprise_billing_reconciliation",
            target_id=target_id,
            status=status,
            details=details,
        ),
    )


@router.get(
    "/issues",
    response_model=ReconciliationIssueListApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def list_reconciliation_issues(
    request: Request,
    account_id: int | None = Query(default=None),
    period_start: date | None = Query(default=None),
    period_end: date | None = Query(default=None),
    severity: ReconciliationSeverity | None = Query(default=None),
    limit: int = Query(default=20),
    offset: int = Query(default=0),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_ops_role(user=current_user, request_id=request_id)
    if role_error is not None:
        return role_error
    try:
        _enforce_limits(user=current_user, operation="list")
        data = B2BReconciliationService.list_issues(
            db,
            account_id=account_id,
            period_start=period_start,
            period_end=period_end,
            severity=severity,
            limit=limit,
            offset=offset,
        )
        _record_reconciliation_audit(
            db,
            request_id=request_id,
            user=current_user,
            action="b2b_reconciliation_list",
            status="success",
            target_id=None,
            details={
                "account_id": account_id,
                "period_start": period_start.isoformat() if period_start is not None else None,
                "period_end": period_end.isoformat() if period_end is not None else None,
                "severity": severity.value if severity is not None else None,
                "limit": limit,
                "offset": offset,
                "returned": len(data.items),
            },
        )
        db.commit()
        return {"data": data.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except RateLimitError as error:
        db.rollback()
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except B2BReconciliationServiceError as error:
        db.rollback()
        return _error_response(
            status_code=422,
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


@router.get(
    "/issues/{issue_id}",
    response_model=ReconciliationIssueDetailApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def get_reconciliation_issue_detail(
    issue_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_ops_role(user=current_user, request_id=request_id)
    if role_error is not None:
        return role_error
    try:
        _enforce_limits(user=current_user, operation="detail")
        data = B2BReconciliationService.get_issue_detail(db, issue_id=issue_id)
        _record_reconciliation_audit(
            db,
            request_id=request_id,
            user=current_user,
            action="b2b_reconciliation_detail",
            status="success",
            target_id=issue_id,
            details={},
        )
        db.commit()
        return {"data": data.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except RateLimitError as error:
        db.rollback()
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except B2BReconciliationServiceError as error:
        db.rollback()
        status_code = 404 if error.code == "reconciliation_issue_not_found" else 422
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


@router.post(
    "/issues/{issue_id}/actions",
    response_model=ReconciliationActionApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def execute_reconciliation_action(
    issue_id: str,
    request: Request,
    payload: ReconciliationActionPayload = Body(...),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_ops_role(user=current_user, request_id=request_id)
    if role_error is not None:
        return role_error
    try:
        _enforce_limits(user=current_user, operation="action")
        result = B2BReconciliationService.execute_action(db, issue_id=issue_id, payload=payload)
        _record_reconciliation_audit(
            db,
            request_id=request_id,
            user=current_user,
            action="b2b_reconciliation_action",
            status="success",
            target_id=issue_id,
            details={
                "action_code": payload.action.value,
                "note": payload.note,
                "correction_state": result.correction_state.value,
            },
        )
        db.commit()
        return {"data": result.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except RateLimitError as error:
        db.rollback()
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except B2BReconciliationServiceError as error:
        db.rollback()
        status_code = 404 if error.code == "reconciliation_issue_not_found" else 422
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
