from __future__ import annotations

from fastapi import APIRouter, Body, Depends, Header, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, get_optional_authenticated_user
from app.api.v1.schemas.common import ErrorEnvelope
from app.api.v1.schemas.routers.public.reference_data import (
    CloneReferenceVersionPayload,
)
from app.core.config import settings
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.ops.audit_service import AuditServiceError
from app.services.reference_data.public_support import (
    _error_response,
    _record_reference_audit,
    _validate_seed_access,
)
from app.services.reference_data_service import ReferenceDataService, ReferenceDataServiceError

router = APIRouter(prefix="/v1/reference-data", tags=["reference-data"])


@router.post(
    "/seed",
    response_model=None,
    responses={
        200: {"model": dict[str, object]},
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def seed_reference_data(
    request: Request,
    version: str | None = Query(default=None),
    x_admin_token: str | None = Header(default=None),
    current_user: AuthenticatedUser | None = Depends(get_optional_authenticated_user),
    db: Session = Depends(get_db_session),
) -> dict[str, object] | JSONResponse:
    request_id = resolve_request_id(request)
    auth_error = _validate_seed_access(x_admin_token, current_user)
    if auth_error is not None:
        return _error_response(
            status_code=(
                status.HTTP_403_FORBIDDEN
                if auth_error.code == "insufficient_role"
                else status.HTTP_401_UNAUTHORIZED
            ),
            request_id=request_id,
            code=auth_error.code,
            message=auth_error.message,
            details=auth_error.details,
        )
    try:
        seeded_version = ReferenceDataService.seed_reference_version(db, version=version)
        _record_reference_audit(
            db,
            request_id=request_id,
            action="reference_seed",
            target_id=seeded_version,
            status_value="success",
            details={"version": seeded_version},
        )
        db.commit()
    except ReferenceDataServiceError as error:
        db.rollback()
        try:
            _record_reference_audit(
                db,
                request_id=request_id,
                action="reference_seed",
                target_id=version,
                status_value="failed",
                details={
                    "version": version or settings.active_reference_version,
                    "error_code": error.code,
                },
            )
            db.commit()
        except AuditServiceError:
            db.rollback()
            return _error_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                request_id=request_id,
                code="audit_unavailable",
                message="audit service is unavailable",
                details={},
            )
        status_code = (
            status.HTTP_401_UNAUTHORIZED
            if error.code == "unauthorized_seed_access"
            else status.HTTP_422_UNPROCESSABLE_CONTENT
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
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            request_id=request_id,
            code="audit_unavailable",
            message="audit service is unavailable",
            details={},
        )
    return {
        "data": {"seeded_version": seeded_version},
        "meta": {"request_id": request_id},
    }


@router.get(
    "/active",
    response_model=None,
    responses={404: {"model": ErrorEnvelope}},
)
def get_active_reference_data(
    request: Request,
    version: str | None = Query(default=None),
    db: Session = Depends(get_db_session),
) -> dict[str, object] | JSONResponse:
    request_id = resolve_request_id(request)
    data = ReferenceDataService.get_active_reference_data(db, version=version)
    if not data:
        return _error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            request_id=request_id,
            code="reference_version_not_found",
            message="reference version not found",
            details={"version": version or "active"},
        )

    return {
        "data": data,
        "meta": {"request_id": request_id},
    }


@router.post(
    "/versions/clone",
    response_model=None,
    responses={
        200: {"model": dict[str, object]},
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
def clone_reference_version(
    request: Request,
    payload: CloneReferenceVersionPayload = Body(...),
    x_admin_token: str | None = Header(default=None),
    current_user: AuthenticatedUser | None = Depends(get_optional_authenticated_user),
    db: Session = Depends(get_db_session),
) -> dict[str, object] | JSONResponse:
    request_id = resolve_request_id(request)
    auth_error = _validate_seed_access(x_admin_token, current_user)
    if auth_error is not None:
        return _error_response(
            status_code=(
                status.HTTP_403_FORBIDDEN
                if auth_error.code == "insufficient_role"
                else status.HTTP_401_UNAUTHORIZED
            ),
            request_id=request_id,
            code=auth_error.code,
            message=auth_error.message,
            details=auth_error.details,
        )
    try:
        cloned_version = ReferenceDataService.clone_reference_version(
            db,
            source_version=payload.source_version,
            new_version=payload.new_version,
        )
        _record_reference_audit(
            db,
            request_id=request_id,
            action="reference_clone",
            target_id=cloned_version,
            status_value="success",
            details={
                "source_version": payload.source_version,
                "new_version": payload.new_version,
            },
        )
        db.commit()
        return {
            "data": {"cloned_version": cloned_version},
            "meta": {"request_id": request_id},
        }
    except ReferenceDataServiceError as error:
        db.rollback()
        try:
            _record_reference_audit(
                db,
                request_id=request_id,
                action="reference_clone",
                target_id=payload.new_version,
                status_value="failed",
                details={
                    "source_version": payload.source_version,
                    "new_version": payload.new_version,
                    "error_code": error.code,
                },
            )
            db.commit()
        except AuditServiceError:
            db.rollback()
            return _error_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                request_id=request_id,
                code="audit_unavailable",
                message="audit service is unavailable",
                details={},
            )
        status_code = (
            status.HTTP_401_UNAUTHORIZED
            if error.code == "unauthorized_seed_access"
            else status.HTTP_422_UNPROCESSABLE_CONTENT
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
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            request_id=request_id,
            code="audit_unavailable",
            message="audit service is unavailable",
            details={},
        )
