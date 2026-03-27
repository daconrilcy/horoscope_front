from __future__ import annotations

import logging
from typing import Any, Literal

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.b2b_entitlement_repair_service import (
    B2BEntitlementRepairService,
    RepairValidationError,
)

logger = logging.getLogger(__name__)

# --- Models ---


class ResponseMeta(BaseModel):
    request_id: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


class RepairBlockerPayload(BaseModel):
    account_id: int
    company_name: str
    reason: str
    recommended_action: str


class RepairRunData(BaseModel):
    accounts_scanned: int
    plans_created: int
    bindings_created: int
    quotas_created: int
    skipped_already_canonical: int
    remaining_blockers: list[RepairBlockerPayload]
    dry_run: bool


class RepairRunResponse(BaseModel):
    data: RepairRunData
    meta: ResponseMeta


class SetAdminUserRequest(BaseModel):
    account_id: int
    user_id: int


class SetAdminUserResponse(BaseModel):
    account_id: int
    user_id: int
    status: str


class ClassifyZeroUnitsRequest(BaseModel):
    canonical_plan_id: int
    access_mode: Literal["disabled", "unlimited", "quota"]
    quota_limit: int | None = Field(default=None, ge=1)


class ClassifyZeroUnitsResponse(BaseModel):
    canonical_plan_id: int
    access_mode: str
    quota_limit: int | None
    status: str


# --- Router ---

router = APIRouter(prefix="/v1/ops/b2b/entitlements/repair", tags=["ops-b2b-entitlements"])


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
    # AC 17: Limites plus restrictives pour le repair
    try:
        check_rate_limit(key=f"b2b_repair:global:{operation}", limit=10, window_seconds=60)
        check_rate_limit(key=f"b2b_repair:role:{user.role}:{operation}", limit=5, window_seconds=60)
        check_rate_limit(key=f"b2b_repair:user:{user.id}:{operation}", limit=3, window_seconds=60)
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
    "/run",
    response_model=RepairRunResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def run_repair(
    request: Request,
    dry_run: bool = Query(default=False),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error

    limit_error = _enforce_limits(user=current_user, request_id=request_id, operation="run")
    if limit_error is not None:
        return limit_error

    report = B2BEntitlementRepairService.run_auto_repair(db, dry_run=dry_run)

    return {
        "data": {
            "accounts_scanned": report.accounts_scanned,
            "plans_created": report.plans_created,
            "bindings_created": report.bindings_created,
            "quotas_created": report.quotas_created,
            "skipped_already_canonical": report.skipped_already_canonical,
            "remaining_blockers": [
                {
                    "account_id": b.account_id,
                    "company_name": b.company_name,
                    "reason": b.reason,
                    "recommended_action": b.recommended_action,
                }
                for b in report.remaining_blockers
            ],
            "dry_run": report.dry_run,
        },
        "meta": {"request_id": request_id},
    }


@router.post(
    "/set-admin-user",
    response_model=SetAdminUserResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def set_admin_user(
    request: Request,
    payload: SetAdminUserRequest,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error

    limit_error = _enforce_limits(
        user=current_user,
        request_id=request_id,
        operation="set_admin_user",
    )
    if limit_error is not None:
        return limit_error

    try:
        result = B2BEntitlementRepairService.set_admin_user(
            db, account_id=payload.account_id, user_id=payload.user_id
        )
        return result
    except RepairValidationError as e:
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=e.code,
            message=e.message,
            details=e.details,
        )


@router.post(
    "/classify-zero-units",
    response_model=ClassifyZeroUnitsResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def classify_zero_units(
    request: Request,
    payload: ClassifyZeroUnitsRequest,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error

    limit_error = _enforce_limits(
        user=current_user,
        request_id=request_id,
        operation="classify_zero_units",
    )
    if limit_error is not None:
        return limit_error

    try:
        result = B2BEntitlementRepairService.classify_zero_units(
            db,
            canonical_plan_id=payload.canonical_plan_id,
            access_mode=payload.access_mode,
            quota_limit=payload.quota_limit,
        )
        return result
    except RepairValidationError as e:
        return _error_response(
            status_code=422,
            request_id=request_id,
            code=e.code,
            message=e.message,
            details=e.details,
        )
