from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.audit_service import AuditEventCreatePayload, AuditService
from app.services.billing_service import BillingService
from app.services.privacy_service import (
    PrivacyComplianceEvidenceData,
    PrivacyRequestData,
    PrivacyService,
    PrivacyServiceError,
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


class PrivacyApiResponse(BaseModel):
    data: PrivacyRequestData
    meta: ResponseMeta


class PrivacyEvidenceApiResponse(BaseModel):
    data: PrivacyComplianceEvidenceData
    meta: ResponseMeta


class DeleteRequestPayload(BaseModel):
    confirmation: str


router = APIRouter(prefix="/v1/privacy", tags=["privacy"])
logger = logging.getLogger(__name__)


class AuditWriteError(Exception):
    pass


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


def _ensure_user_role(current_user: AuthenticatedUser, request_id: str) -> JSONResponse | None:
    if current_user.role != "user":
        return _error_response(
            status_code=403,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed for privacy requests",
            details={"required_role": "user", "actual_role": current_user.role},
        )
    return None


def _ensure_support_or_ops_role(
    current_user: AuthenticatedUser, request_id: str
) -> JSONResponse | None:
    if current_user.role not in {"support", "ops"}:
        return _error_response(
            status_code=403,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed for privacy evidence",
            details={"required_roles": "support,ops", "actual_role": current_user.role},
        )
    return None


def _record_audit_event(
    db: Session,
    *,
    request_id: str,
    actor_user_id: int | None,
    actor_role: str,
    action: str,
    target_type: str,
    target_id: str | None,
    status: str,
    details: dict[str, object] | None = None,
) -> None:
    try:
        AuditService.record_event(
            db,
            payload=AuditEventCreatePayload(
                request_id=request_id,
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                action=action,
                target_type=target_type,
                target_id=target_id,
                status=status,
                details=details or {},
            ),
        )
    except Exception as error:
        logger.exception("audit_event_write_failed action=%s request_id=%s", action, request_id)
        raise AuditWriteError("audit event write failed") from error


def _record_failed_audit_or_503(
    db: Session,
    *,
    request_id: str,
    actor_user_id: int | None,
    actor_role: str,
    action: str,
    target_type: str,
    target_id: str | None,
    error_code: str,
) -> JSONResponse | None:
    try:
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            action=action,
            target_type=target_type,
            target_id=target_id,
            status="failed",
            details={"error_code": error_code},
        )
        db.commit()
    except AuditWriteError:
        db.rollback()
        return _error_response(
            status_code=503,
            request_id=request_id,
            code="audit_unavailable",
            message="audit persistence is unavailable",
            details={},
        )
    return None


def _enforce_privacy_limits(
    *,
    user_id: int,
    plan_code: str | None,
    operation: str,
    request_id: str,
) -> JSONResponse | None:
    try:
        check_rate_limit(key=f"privacy:global:{operation}", limit=120, window_seconds=60)
        check_rate_limit(key=f"privacy:user:{user_id}:{operation}", limit=20, window_seconds=60)
        if plan_code is not None:
            check_rate_limit(
                key=f"privacy:user_plan:{user_id}:{plan_code}:{operation}",
                limit=10,
                window_seconds=60,
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


@router.post(
    "/export",
    response_model=PrivacyApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        409: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def request_export(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_user_role(current_user, request_id)
    if role_error is not None:
        return role_error
    subscription = BillingService.get_subscription_status(db, user_id=current_user.id)
    plan_code = subscription.plan.code if subscription.plan is not None else "no-plan"
    rate_error = _enforce_privacy_limits(
        user_id=current_user.id,
        plan_code=plan_code,
        operation="request_export",
        request_id=request_id,
    )
    if rate_error is not None:
        return rate_error
    try:
        response = PrivacyService.request_export(db, user_id=current_user.id, request_id=request_id)
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="privacy_export",
            target_type="user",
            target_id=str(current_user.id),
            status="success",
        )
        db.commit()
        return {"data": response.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except PrivacyServiceError as error:
        db.rollback()
        audit_error = _record_failed_audit_or_503(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="privacy_export",
            target_type="user",
            target_id=str(current_user.id),
            error_code=error.code,
        )
        if audit_error is not None:
            return audit_error
        status_code = 409 if error.code == "privacy_request_conflict" else 422
        return _error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except AuditWriteError:
        db.rollback()
        return _error_response(
            status_code=503,
            request_id=request_id,
            code="audit_unavailable",
            message="audit persistence is unavailable",
            details={},
        )


@router.get(
    "/export",
    response_model=PrivacyApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_export_status(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_user_role(current_user, request_id)
    if role_error is not None:
        return role_error
    subscription = BillingService.get_subscription_status(db, user_id=current_user.id)
    plan_code = subscription.plan.code if subscription.plan is not None else "no-plan"
    rate_error = _enforce_privacy_limits(
        user_id=current_user.id,
        plan_code=plan_code,
        operation="get_export",
        request_id=request_id,
    )
    if rate_error is not None:
        return rate_error
    try:
        response = PrivacyService.get_latest_export_status(db, user_id=current_user.id)
        return {"data": response.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except PrivacyServiceError as error:
        status_code = 404 if error.code == "privacy_not_found" else 422
        return _error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )


@router.post(
    "/delete",
    response_model=PrivacyApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        409: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def request_delete(
    request: Request,
    payload: Any = Body(...),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_user_role(current_user, request_id)
    if role_error is not None:
        return role_error
    subscription = BillingService.get_subscription_status(db, user_id=current_user.id)
    plan_code = subscription.plan.code if subscription.plan is not None else "no-plan"
    rate_error = _enforce_privacy_limits(
        user_id=current_user.id,
        plan_code=plan_code,
        operation="request_delete",
        request_id=request_id,
    )
    if rate_error is not None:
        return rate_error
    try:
        parsed = DeleteRequestPayload.model_validate(payload)
        if parsed.confirmation != "DELETE":
            audit_error = _record_failed_audit_or_503(
                db,
                request_id=request_id,
                actor_user_id=current_user.id,
                actor_role=current_user.role,
                action="privacy_delete",
                target_type="user",
                target_id=str(current_user.id),
                error_code="privacy_request_invalid",
            )
            if audit_error is not None:
                return audit_error
            return _error_response(
                status_code=422,
                request_id=request_id,
                code="privacy_request_invalid",
                message="delete confirmation is invalid",
                details={"expected_confirmation": "DELETE"},
            )
        response = PrivacyService.request_delete(db, user_id=current_user.id, request_id=request_id)
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="privacy_delete",
            target_type="user",
            target_id=str(current_user.id),
            status="success",
        )
        db.commit()
        return {"data": response.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except ValidationError as error:
        db.rollback()
        audit_error = _record_failed_audit_or_503(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="privacy_delete",
            target_type="user",
            target_id=str(current_user.id),
            error_code="privacy_request_invalid",
        )
        if audit_error is not None:
            return audit_error
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="privacy_request_invalid",
            message="privacy delete request validation failed",
            details={"errors": error.errors()},
        )
    except PrivacyServiceError as error:
        db.rollback()
        audit_error = _record_failed_audit_or_503(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="privacy_delete",
            target_type="user",
            target_id=str(current_user.id),
            error_code=error.code,
        )
        if audit_error is not None:
            return audit_error
        status_code = 409 if error.code == "privacy_request_conflict" else 422
        return _error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except AuditWriteError:
        db.rollback()
        return _error_response(
            status_code=503,
            request_id=request_id,
            code="audit_unavailable",
            message="audit persistence is unavailable",
            details={},
        )


@router.get(
    "/delete",
    response_model=PrivacyApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_delete_status(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_user_role(current_user, request_id)
    if role_error is not None:
        return role_error
    subscription = BillingService.get_subscription_status(db, user_id=current_user.id)
    plan_code = subscription.plan.code if subscription.plan is not None else "no-plan"
    rate_error = _enforce_privacy_limits(
        user_id=current_user.id,
        plan_code=plan_code,
        operation="get_delete",
        request_id=request_id,
    )
    if rate_error is not None:
        return rate_error
    try:
        response = PrivacyService.get_latest_delete_status(db, user_id=current_user.id)
        return {"data": response.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except PrivacyServiceError as error:
        status_code = 404 if error.code == "privacy_not_found" else 422
        return _error_response(
            status_code=status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )


@router.get(
    "/evidence/{target_user_id}",
    response_model=PrivacyEvidenceApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_privacy_evidence(
    target_user_id: int,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    role_error = _ensure_support_or_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error
    rate_error = _enforce_privacy_limits(
        user_id=current_user.id,
        plan_code=None,
        operation="get_evidence",
        request_id=request_id,
    )
    if rate_error is not None:
        return rate_error
    try:
        evidence = PrivacyService.get_compliance_evidence(db, user_id=target_user_id)
        _record_audit_event(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="privacy_evidence_export",
            target_type="user",
            target_id=str(target_user_id),
            status="success",
        )
        db.commit()
        return {"data": evidence.model_dump(mode="json"), "meta": {"request_id": request_id}}
    except PrivacyServiceError as error:
        db.rollback()
        audit_error = _record_failed_audit_or_503(
            db,
            request_id=request_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            action="privacy_evidence_export",
            target_type="user",
            target_id=str(target_user_id),
            error_code=error.code,
        )
        if audit_error is not None:
            return audit_error
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    except AuditWriteError:
        db.rollback()
        return _error_response(
            status_code=503,
            request_id=request_id,
            code="audit_unavailable",
            message="audit persistence is unavailable",
            details={},
        )
