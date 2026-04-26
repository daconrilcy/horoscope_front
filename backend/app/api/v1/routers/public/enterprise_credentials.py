from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.api.v1.router_logic.public.enterprise_credentials import (
    _enforce_limits,
    _ensure_enterprise_admin_role,
    _error_response,
    _record_audit_event,
)
from app.api.v1.schemas.routers.public.enterprise_credentials import (
    EnterpriseCredentialSecretApiResponse,
    EnterpriseCredentialsListApiResponse,
    ErrorEnvelope,
)
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.b2b.enterprise_credentials_service import (
    EnterpriseCredentialsService,
    EnterpriseCredentialsServiceError,
)
from app.services.ops.audit_service import AuditServiceError

router = APIRouter(prefix="/v1/b2b/credentials", tags=["b2b-credentials"])


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
