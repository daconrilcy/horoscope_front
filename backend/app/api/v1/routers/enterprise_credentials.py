from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.audit_service import AuditEventCreatePayload, AuditService, AuditServiceError
from app.services.enterprise_credentials_service import (
    EnterpriseCredentialListData,
    EnterpriseCredentialSecretData,
    EnterpriseCredentialsService,
    EnterpriseCredentialsServiceError,
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


class EnterpriseCredentialsListApiResponse(BaseModel):
    data: EnterpriseCredentialListData
    meta: ResponseMeta


class EnterpriseCredentialSecretApiResponse(BaseModel):
    data: EnterpriseCredentialSecretData
    meta: ResponseMeta


router = APIRouter(prefix="/v1/b2b/credentials", tags=["b2b-credentials"])


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


def _ensure_enterprise_admin_role(user: AuthenticatedUser, request_id: str) -> JSONResponse | None:
    if user.role != "enterprise_admin":
        return _error_response(
            status_code=403,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "enterprise_admin", "actual_role": user.role},
        )
    return None


def _enforce_limits(
    *, user: AuthenticatedUser, request_id: str, operation: str
) -> JSONResponse | None:
    try:
        check_rate_limit(key=f"b2b_credentials:global:{operation}", limit=120, window_seconds=60)
        check_rate_limit(
            key=f"b2b_credentials:role:{user.role}:{operation}", limit=60, window_seconds=60
        )
        check_rate_limit(
            key=f"b2b_credentials:user:{user.id}:{operation}", limit=30, window_seconds=60
        )
    except RateLimitError as error:
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    return None


def _record_audit_event(
    db: Session,
    *,
    request_id: str,
    actor_user_id: int,
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
            target_type="enterprise_api_credential",
            target_id=target_id,
            status=status,
            details=details,
        ),
    )


@router.get(
    "",
    response_model=EnterpriseCredentialsListApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def list_enterprise_credentials(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_enterprise_admin_role(current_user, request_id)
    if role_error is not None:
        return role_error
    limit_error = _enforce_limits(user=current_user, request_id=request_id, operation="list")
    if limit_error is not None:
        return limit_error

    try:
        data = EnterpriseCredentialsService.list_credentials(db, admin_user_id=current_user.id)
        return {"data": data.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except EnterpriseCredentialsServiceError as error:
        status_code = (
            404 if error.code in {"enterprise_account_not_found", "credential_not_found"} else 422
        )
        return _error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )


@router.post(
    "/generate",
    response_model=EnterpriseCredentialSecretApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def generate_enterprise_credential(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_enterprise_admin_role(current_user, request_id)
    if role_error is not None:
        return role_error
    limit_error = _enforce_limits(user=current_user, request_id=request_id, operation="generate")
    if limit_error is not None:
        return limit_error

    try:
        data = EnterpriseCredentialsService.create_credential(db, admin_user_id=current_user.id)
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="b2b_api_key_create",
            target_id=str(data.credential_id),
            status="success",
            details={"key_prefix": data.key_prefix},
        )
        db.commit()
        return {"data": data.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except EnterpriseCredentialsServiceError as error:
        db.rollback()
        try:
            _record_audit_event(
                db,
                request_id=request_id,
                actor_user_id=current_user.id,
                actor_role=current_user.role,
                action="b2b_api_key_create",
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
        status_code = (
            404 if error.code in {"enterprise_account_not_found", "credential_not_found"} else 422
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


@router.post(
    "/rotate",
    response_model=EnterpriseCredentialSecretApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def rotate_enterprise_credential(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_enterprise_admin_role(current_user, request_id)
    if role_error is not None:
        return role_error
    limit_error = _enforce_limits(user=current_user, request_id=request_id, operation="rotate")
    if limit_error is not None:
        return limit_error

    try:
        data = EnterpriseCredentialsService.rotate_credential(db, admin_user_id=current_user.id)
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="b2b_api_key_rotate",
            target_id=str(data.credential_id),
            status="success",
            details={"key_prefix": data.key_prefix},
        )
        db.commit()
        return {"data": data.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except EnterpriseCredentialsServiceError as error:
        db.rollback()
        try:
            _record_audit_event(
                db,
                request_id=request_id,
                actor_user_id=current_user.id,
                actor_role=current_user.role,
                action="b2b_api_key_rotate",
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
        status_code = (
            404 if error.code in {"enterprise_account_not_found", "credential_not_found"} else 422
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
