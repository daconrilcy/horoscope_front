from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.session import get_db_session
from app.services.canonical_entitlement_mutation_audit_query_service import (
    CanonicalEntitlementMutationAuditQueryService,
)
from app.services.canonical_entitlement_mutation_diff_service import (
    CanonicalEntitlementMutationDiffService,
)

router = APIRouter(prefix="/v1/ops/entitlements", tags=["ops-entitlement-audits"])


class QuotaChangeSummarySchema(BaseModel):
    added: list[dict]
    removed: list[dict]
    updated: list[dict]


class MutationAuditItem(BaseModel):
    id: int
    occurred_at: datetime
    operation: str
    plan_id: int
    plan_code_snapshot: str
    feature_code: str
    actor_type: str
    actor_identifier: str
    request_id: str | None
    source_origin: str
    # Diff champs dérivés — TOUJOURS présents, non-optionnels
    change_kind: str
    changed_fields: list[str]
    risk_level: str
    quota_changes: QuotaChangeSummarySchema
    # Payloads bruts — conditionnels (include_payloads), omis par exclude_none
    before_payload: dict | None = None
    after_payload: dict | None = None


class MutationAuditListData(BaseModel):
    items: list[MutationAuditItem]
    total_count: int
    page: int
    page_size: int


class ResponseMeta(BaseModel):
    request_id: str


class MutationAuditListApiResponse(BaseModel):
    data: MutationAuditListData
    meta: ResponseMeta


class MutationAuditDetailApiResponse(BaseModel):
    data: MutationAuditItem
    meta: ResponseMeta


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


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
        # key: f"ops_entitlement_mutation_audits:global:{operation}", limit=60, window_seconds=60
        check_rate_limit(
            key=f"ops_entitlement_mutation_audits:global:{operation}",
            limit=60,
            window_seconds=60,
        )
        # key: f"ops_entitlement_mutation_audits:role:{user.role}:{operation}"
        # limit=30, window_seconds=60
        check_rate_limit(
            key=f"ops_entitlement_mutation_audits:role:{user.role}:{operation}",
            limit=30,
            window_seconds=60,
        )
        # key: f"ops_entitlement_mutation_audits:user:{user.id}:{operation}"
        # limit=15, window_seconds=60
        check_rate_limit(
            key=f"ops_entitlement_mutation_audits:user:{user.id}:{operation}",
            limit=15,
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


def _to_item(audit: Any, *, include_payloads: bool) -> dict[str, Any]:
    diff = CanonicalEntitlementMutationDiffService.compute_diff(
        audit.before_payload or {}, audit.after_payload or {}
    )
    d: dict[str, Any] = {
        "id": audit.id,
        "occurred_at": audit.occurred_at,
        "operation": audit.operation,
        "plan_id": audit.plan_id,
        "plan_code_snapshot": audit.plan_code_snapshot,
        "feature_code": audit.feature_code,
        "actor_type": audit.actor_type,
        "actor_identifier": audit.actor_identifier,
        "request_id": audit.request_id,
        "source_origin": audit.source_origin,
        "change_kind": diff.change_kind,
        "changed_fields": diff.changed_fields,
        "risk_level": diff.risk_level,
        "quota_changes": {
            "added": diff.quota_changes.added,
            "removed": diff.quota_changes.removed,
            "updated": diff.quota_changes.updated,
        },
    }
    if include_payloads:
        d["before_payload"] = audit.before_payload
        d["after_payload"] = audit.after_payload
    return d


@router.get(
    "/mutation-audits",
    response_model=MutationAuditListApiResponse,
    response_model_exclude_none=True,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def list_mutation_audits(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    plan_id: int | None = Query(default=None),
    plan_code: str | None = Query(default=None),
    feature_code: str | None = Query(default=None),
    actor_type: str | None = Query(default=None),
    actor_identifier: str | None = Query(default=None),
    source_origin: str | None = Query(default=None),
    request_id_filter: str | None = Query(default=None, alias="request_id"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    # Nouveaux filtres diff
    risk_level_filter: Literal["high", "medium", "low"] | None = Query(
        default=None, alias="risk_level"
    ),
    change_kind_filter: Literal["binding_created", "binding_updated"] | None = Query(
        default=None, alias="change_kind"
    ),
    changed_field_filter: str | None = Query(default=None, alias="changed_field"),
    include_payloads: bool = Query(default=False),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error

    limit_error = _enforce_limits(
        user=current_user, request_id=request_id, operation="list"
    )
    if limit_error is not None:
        return limit_error

    _DIFF_FILTER_MAX = 10_000

    # Si aucun filtre diff : comportement inchangé (SQL paginé)
    if not any([risk_level_filter, change_kind_filter, changed_field_filter]):
        items, total_count = CanonicalEntitlementMutationAuditQueryService.list_mutation_audits(
            db,
            page=page,
            page_size=page_size,
            plan_id=plan_id,
            plan_code=plan_code,
            feature_code=feature_code,
            actor_type=actor_type,
            actor_identifier=actor_identifier,
            source_origin=source_origin,
            request_id=request_id_filter,
            date_from=date_from,
            date_to=date_to,
        )

        return {
            "data": {
                "items": [
                    _to_item(item, include_payloads=include_payloads) for item in items
                ],
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
            },
            "meta": {"request_id": request_id},
        }

    # Avec filtre diff : vérifier le count SQL avant de tout charger
    _, sql_count = CanonicalEntitlementMutationAuditQueryService.list_mutation_audits(
        db,
        page=1,
        page_size=1,
        plan_id=plan_id,
        plan_code=plan_code,
        feature_code=feature_code,
        actor_type=actor_type,
        actor_identifier=actor_identifier,
        source_origin=source_origin,
        request_id=request_id_filter,
        date_from=date_from,
        date_to=date_to,
    )

    if sql_count > _DIFF_FILTER_MAX:
        return _error_response(
            status_code=400,
            request_id=request_id,
            code="diff_filter_result_set_too_large",
            message=(
                f"Too many results to apply diff filter ({sql_count} > {_DIFF_FILTER_MAX}). "
                "Add SQL filters to narrow the result set."
            ),
            details={"sql_count": sql_count, "max_allowed": _DIFF_FILTER_MAX},
        )

    all_items, _ = CanonicalEntitlementMutationAuditQueryService.list_mutation_audits(
        db,
        page=1,
        page_size=_DIFF_FILTER_MAX,
        plan_id=plan_id,
        plan_code=plan_code,
        feature_code=feature_code,
        actor_type=actor_type,
        actor_identifier=actor_identifier,
        source_origin=source_origin,
        request_id=request_id_filter,
        date_from=date_from,
        date_to=date_to,
    )

    filtered = []
    for item in all_items:
        diff = CanonicalEntitlementMutationDiffService.compute_diff(
            item.before_payload or {}, item.after_payload or {}
        )
        if risk_level_filter and diff.risk_level != risk_level_filter:
            continue
        if change_kind_filter and diff.change_kind != change_kind_filter:
            continue
        if changed_field_filter and changed_field_filter not in diff.changed_fields:
            continue
        filtered.append(item)

    total_count = len(filtered)
    start = (page - 1) * page_size
    page_items = filtered[start : start + page_size]

    return {
        "data": {
            "items": [
                _to_item(item, include_payloads=include_payloads) for item in page_items
            ],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
        },
        "meta": {"request_id": request_id},
    }


@router.get(
    "/mutation-audits/{audit_id}",
    response_model=MutationAuditDetailApiResponse,
    response_model_exclude_none=True,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_mutation_audit(
    audit_id: int,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error

    limit_error = _enforce_limits(
        user=current_user, request_id=request_id, operation="detail"
    )
    if limit_error is not None:
        return limit_error

    audit = CanonicalEntitlementMutationAuditQueryService.get_mutation_audit_by_id(
        db, audit_id
    )
    if audit is None:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="audit_not_found",
            message=f"Mutation audit {audit_id} not found",
            details={"audit_id": audit_id},
        )

    return {
        "data": _to_item(audit, include_payloads=True),
        "meta": {"request_id": request_id},
    }
