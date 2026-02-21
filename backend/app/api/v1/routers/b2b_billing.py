from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.dependencies.b2b_auth import (
    AuthenticatedEnterpriseClient,
    require_authenticated_b2b_client,
)
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.audit_service import AuditEventCreatePayload, AuditService, AuditServiceError
from app.services.b2b_billing_service import (
    B2BBillingClosePayload,
    B2BBillingCycleData,
    B2BBillingCycleListData,
    B2BBillingService,
    B2BBillingServiceError,
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


class B2BBillingCycleApiResponse(BaseModel):
    data: B2BBillingCycleData | None
    meta: ResponseMeta


class B2BBillingCycleListApiResponse(BaseModel):
    data: B2BBillingCycleListData
    meta: ResponseMeta


router = APIRouter(prefix="/v1/b2b/billing", tags=["b2b-billing"])


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


def _enforce_enterprise_limits(*, client: AuthenticatedEnterpriseClient, operation: str) -> None:
    check_rate_limit(key=f"b2b_billing:global:{operation}", limit=180, window_seconds=60)
    check_rate_limit(
        key=f"b2b_billing:account:{client.account_id}:{operation}",
        limit=90,
        window_seconds=60,
    )
    check_rate_limit(
        key=f"b2b_billing:credential:{client.credential_id}:{operation}",
        limit=45,
        window_seconds=60,
    )


def _enforce_ops_limits(*, user: AuthenticatedUser, operation: str) -> None:
    check_rate_limit(key=f"b2b_billing_ops:global:{operation}", limit=120, window_seconds=60)
    check_rate_limit(
        key=f"b2b_billing_ops:role:{user.role}:{operation}", limit=60, window_seconds=60
    )
    check_rate_limit(key=f"b2b_billing_ops:user:{user.id}:{operation}", limit=30, window_seconds=60)


def _record_billing_audit(
    db: Session,
    *,
    request_id: str,
    actor_user_id: int | None,
    actor_role: str,
    action: str,
    target_id: str | None,
    status: str,
    details: dict[str, object],
) -> None:
    AuditService.record_event(
        db,
        payload=AuditEventCreatePayload(
            request_id=request_id,
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            action=action,
            target_type="enterprise_billing_cycle",
            target_id=target_id,
            status=status,
            details=details,
        ),
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


@router.get(
    "/cycles/latest",
    response_model=B2BBillingCycleApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_latest_b2b_billing_cycle(
    request: Request,
    client: AuthenticatedEnterpriseClient = Depends(require_authenticated_b2b_client),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    try:
        _enforce_enterprise_limits(client=client, operation="latest")
        data = B2BBillingService.get_latest_cycle(db, account_id=client.account_id)
        _record_billing_audit(
            db,
            request_id=request_id,
            actor_user_id=None,
            actor_role="enterprise_client",
            action="b2b_billing_cycle_read_latest",
            target_id=str(data.cycle_id) if data is not None else None,
            status="success",
            details={"account_id": client.account_id},
        )
        db.commit()
        return {
            "data": data.model_dump(mode="json") if data is not None else None,
            "meta": {"request_id": request_id},
        }
    except RateLimitError as error:
        db.rollback()
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except B2BBillingServiceError as error:
        db.rollback()
        try:
            _record_billing_audit(
                db,
                request_id=request_id,
                actor_user_id=None,
                actor_role="enterprise_client",
                action="b2b_billing_cycle_read_latest",
                target_id=None,
                status="failed",
                details={"account_id": client.account_id, "error_code": error.code},
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
        status_code = (
            404
            if error.code in {"enterprise_account_not_found", "b2b_billing_plan_not_found"}
            else 422
        )
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


@router.get(
    "/cycles",
    response_model=B2BBillingCycleListApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def list_b2b_billing_cycles(
    request: Request,
    limit: int = Query(default=20),
    offset: int = Query(default=0),
    client: AuthenticatedEnterpriseClient = Depends(require_authenticated_b2b_client),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    try:
        _enforce_enterprise_limits(client=client, operation="list")
        data = B2BBillingService.list_cycles(
            db,
            account_id=client.account_id,
            limit=limit,
            offset=offset,
        )
        _record_billing_audit(
            db,
            request_id=request_id,
            actor_user_id=None,
            actor_role="enterprise_client",
            action="b2b_billing_cycle_read_list",
            target_id=None,
            status="success",
            details={
                "account_id": client.account_id,
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
    except B2BBillingServiceError as error:
        db.rollback()
        try:
            _record_billing_audit(
                db,
                request_id=request_id,
                actor_user_id=None,
                actor_role="enterprise_client",
                action="b2b_billing_cycle_read_list",
                target_id=None,
                status="failed",
                details={
                    "account_id": client.account_id,
                    "limit": limit,
                    "offset": offset,
                    "error_code": error.code,
                },
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


@router.post(
    "/cycles/close",
    response_model=B2BBillingCycleApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def close_b2b_billing_cycle(
    request: Request,
    payload: B2BBillingClosePayload = Body(...),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_ops_role(user=current_user, request_id=request_id)
    if role_error is not None:
        return role_error
    try:
        _enforce_ops_limits(user=current_user, operation="close_cycle")
        closed = B2BBillingService.close_cycle(
            db,
            account_id=payload.account_id,
            period_start=payload.period_start,
            period_end=payload.period_end,
            closed_by_user_id=current_user.id,
        )
        _record_billing_audit(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="b2b_billing_cycle_close",
            target_id=str(closed.cycle_id),
            status="success",
            details={
                "account_id": payload.account_id,
                "period_start": payload.period_start.isoformat(),
                "period_end": payload.period_end.isoformat(),
                "total_amount_cents": closed.total_amount_cents,
            },
        )
        db.commit()
        return {"data": closed.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except RateLimitError as error:
        db.rollback()
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except B2BBillingServiceError as error:
        db.rollback()
        try:
            _record_billing_audit(
                db,
                request_id=request_id,
                actor_user_id=current_user.id,
                actor_role=current_user.role,
                action="b2b_billing_cycle_close",
                target_id=None,
                status="failed",
                details={
                    "error_code": error.code,
                    "account_id": payload.account_id,
                    "period_start": payload.period_start.isoformat(),
                    "period_end": payload.period_end.isoformat(),
                },
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
        status_code = (
            404
            if error.code in {"enterprise_account_not_found", "b2b_billing_plan_not_found"}
            else 422
        )
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


@router.get(
    "/ops/cycles/latest",
    response_model=B2BBillingCycleApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def get_latest_b2b_billing_cycle_ops(
    request: Request,
    account_id: int = Query(...),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_ops_role(user=current_user, request_id=request_id)
    if role_error is not None:
        return role_error
    try:
        _enforce_ops_limits(user=current_user, operation="read_latest")
        data = B2BBillingService.get_latest_cycle(db, account_id=account_id)
        _record_billing_audit(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="b2b_billing_cycle_read_latest",
            target_id=str(data.cycle_id) if data is not None else None,
            status="success",
            details={"account_id": account_id},
        )
        db.commit()
        return {
            "data": data.model_dump(mode="json") if data is not None else None,
            "meta": {"request_id": request_id},
        }
    except RateLimitError as error:
        db.rollback()
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except B2BBillingServiceError as error:
        db.rollback()
        try:
            _record_billing_audit(
                db,
                request_id=request_id,
                actor_user_id=current_user.id,
                actor_role=current_user.role,
                action="b2b_billing_cycle_read_latest",
                target_id=None,
                status="failed",
                details={"account_id": account_id, "error_code": error.code},
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
        status_code = (
            404
            if error.code in {"enterprise_account_not_found", "b2b_billing_plan_not_found"}
            else 422
        )
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


@router.get(
    "/ops/cycles",
    response_model=B2BBillingCycleListApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def list_b2b_billing_cycles_ops(
    request: Request,
    account_id: int = Query(...),
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
        _enforce_ops_limits(user=current_user, operation="read_list")
        data = B2BBillingService.list_cycles(
            db,
            account_id=account_id,
            limit=limit,
            offset=offset,
        )
        _record_billing_audit(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="b2b_billing_cycle_read_list",
            target_id=None,
            status="success",
            details={
                "account_id": account_id,
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
    except B2BBillingServiceError as error:
        db.rollback()
        try:
            _record_billing_audit(
                db,
                request_id=request_id,
                actor_user_id=current_user.id,
                actor_role=current_user.role,
                action="b2b_billing_cycle_read_list",
                target_id=None,
                status="failed",
                details={
                    "account_id": account_id,
                    "limit": limit,
                    "offset": offset,
                    "error_code": error.code,
                },
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
