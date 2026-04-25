from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.b2b.audit_service import B2BAuditService


class ResponseMeta(BaseModel):
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class B2BAuditEntryPayload(BaseModel):
    account_id: int
    company_name: str
    enterprise_plan_id: int | None
    enterprise_plan_code: str | None
    canonical_plan_id: int | None
    canonical_plan_code: str | None
    feature_code: str
    resolution_source: str
    reason: str
    binding_status: str | None
    quota_limit: int | None
    remaining: int | None
    window_end: datetime | None
    admin_user_id_present: bool
    manual_review_required: bool


class B2BAuditListData(BaseModel):
    items: list[B2BAuditEntryPayload]
    total_count: int
    page: int
    page_size: int


class B2BAuditListApiResponse(BaseModel):
    data: B2BAuditListData
    meta: ResponseMeta


router = APIRouter(prefix="/v1/ops/b2b/entitlements", tags=["ops-b2b-entitlements"])
VALID_RESOLUTION_SOURCES = {
    "canonical_quota",
    "canonical_unlimited",
    "canonical_disabled",
    "settings_fallback",
}


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


def _ensure_ops_role(user: AuthenticatedUser, request_id: str) -> JSONResponse | None:
    if user.role not in ["ops", "admin"]:
        return _error_response(
            status_code=403,
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "ops, admin", "actual_role": user.role},
        )
    return None


def _enforce_limits(
    *, user: AuthenticatedUser, request_id: str, operation: str
) -> JSONResponse | None:
    try:
        check_rate_limit(key=f"b2b_audit:global:{operation}", limit=60, window_seconds=60)
        check_rate_limit(key=f"b2b_audit:role:{user.role}:{operation}", limit=30, window_seconds=60)
        check_rate_limit(key=f"b2b_audit:user:{user.id}:{operation}", limit=15, window_seconds=60)
    except RateLimitError as error:
        return _error_response(
            status_code=error.status_code,
            request_id=request_id,
            code=error.code,
            message=error.message,
            details=error.details,
        )
    return None


@router.get(
    "/audit",
    response_model=B2BAuditListApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_b2b_entitlements_audit(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    resolution_source: str | None = Query(default=None),
    blocker_only: bool = Query(default=False),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error

    limit_error = _enforce_limits(
        user=current_user, request_id=request_id, operation="entitlements_audit"
    )
    if limit_error is not None:
        return limit_error

    if resolution_source is not None and resolution_source not in VALID_RESOLUTION_SOURCES:
        return _error_response(
            status_code=422,
            request_id=request_id,
            code="invalid_resolution_source",
            message="Invalid resolution_source filter value",
            details={"allowed": sorted(VALID_RESOLUTION_SOURCES), "received": resolution_source},
        )

    items, total_count = B2BAuditService.list_b2b_entitlement_audit(
        db,
        page=page,
        page_size=page_size,
        resolution_source_filter=resolution_source,
        blocker_only=blocker_only,
    )

    return {
        "data": {
            "items": [B2BAuditEntryPayload(**vars(item)).model_dump(mode="json") for item in items],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
        },
        "meta": {"request_id": request_id},
    }
