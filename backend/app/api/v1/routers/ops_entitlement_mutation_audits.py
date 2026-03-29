from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, require_authenticated_user
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.core.request_id import resolve_request_id
from app.infra.db.models.canonical_entitlement_mutation_alert_delivery_attempt import (
    CanonicalEntitlementMutationAlertDeliveryAttemptModel,
)
from app.infra.db.models.canonical_entitlement_mutation_alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.canonical_entitlement_mutation_alert_event_handling import (
    CanonicalEntitlementMutationAlertEventHandlingModel,
)
from app.infra.db.models.canonical_entitlement_mutation_audit_review import (
    CanonicalEntitlementMutationAuditReviewModel,
)
from app.infra.db.session import get_db_session
from app.services.canonical_entitlement_alert_handling_service import (
    CanonicalEntitlementAlertHandlingService,
)
from app.services.canonical_entitlement_mutation_audit_query_service import (
    CanonicalEntitlementMutationAuditQueryService,
)
from app.services.canonical_entitlement_mutation_audit_review_service import (
    AuditNotFoundError,
    CanonicalEntitlementMutationAuditReviewService,
)
from app.services.canonical_entitlement_mutation_diff_service import (
    CanonicalEntitlementMutationDiffService,
)
from app.services.canonical_entitlement_review_queue_service import (
    CanonicalEntitlementReviewQueueService,
    ReviewQueueRow,
)

router = APIRouter(prefix="/v1/ops/entitlements", tags=["ops-entitlement-audits"])

WritableReviewStatusLiteral = Literal["acknowledged", "expected", "investigating", "closed"]
ReviewStatusLiteral = Literal[
    "pending_review", "acknowledged", "expected", "investigating", "closed"
]
PersistedReviewStatusLiteral = WritableReviewStatusLiteral


# ---------------------------------------------------------------------------
# Schémas Pydantic (Rest)
# ---------------------------------------------------------------------------


class ReviewState(BaseModel):
    status: ReviewStatusLiteral
    reviewed_by_user_id: int | None = None
    reviewed_at: datetime | None = None
    review_comment: str | None = None
    incident_key: str | None = None


class ReviewRequestBody(BaseModel):
    review_status: WritableReviewStatusLiteral
    review_comment: str | None = None
    incident_key: str | None = None


class ReviewResponse(BaseModel):
    audit_id: int
    review_status: WritableReviewStatusLiteral
    reviewed_by_user_id: int | None = None
    reviewed_at: datetime
    review_comment: str | None = None
    incident_key: str | None = None


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
    # Review — optionnel, omis si null via response_model_exclude_none=True
    review: ReviewState | None = None
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


class ReviewApiResponse(BaseModel):
    data: ReviewResponse
    meta: ResponseMeta


class ReviewEventItem(BaseModel):
    id: int
    audit_id: int
    previous_review_status: PersistedReviewStatusLiteral | None = None
    new_review_status: PersistedReviewStatusLiteral
    previous_review_comment: str | None = None
    new_review_comment: str | None = None
    previous_incident_key: str | None = None
    new_incident_key: str | None = None
    reviewed_by_user_id: int | None = None
    occurred_at: datetime
    request_id: str | None = None


class ReviewHistoryData(BaseModel):
    items: list[ReviewEventItem]
    total_count: int


class ReviewHistoryApiResponse(BaseModel):
    data: ReviewHistoryData
    meta: ResponseMeta


class ReviewQueueItem(MutationAuditItem):
    effective_review_status: ReviewStatusLiteral | None = None
    age_seconds: int
    age_hours: float
    is_pending: bool
    is_closed: bool
    # Nouveaux champs SLA
    sla_target_seconds: int | None = None
    due_at: datetime | None = None
    sla_status: Literal["within_sla", "due_soon", "overdue"] | None = None
    overdue_seconds: int | None = None


class ReviewQueueListData(BaseModel):
    items: list[ReviewQueueItem]
    total_count: int
    page: int
    page_size: int


class ReviewQueueApiResponse(BaseModel):
    data: ReviewQueueListData
    meta: ResponseMeta


class ReviewQueueSummaryData(BaseModel):
    pending_review_count: int
    investigating_count: int
    acknowledged_count: int
    closed_count: int
    expected_count: int
    no_review_count: int
    high_unreviewed_count: int
    total_count: int
    # Nouveaux champs SLA
    overdue_count: int
    due_soon_count: int
    oldest_pending_age_seconds: int | None = None


class ReviewQueueSummaryApiResponse(BaseModel):
    data: ReviewQueueSummaryData
    meta: ResponseMeta


class AlertAttemptItem(BaseModel):
    id: int
    alert_event_id: int
    attempt_number: int
    delivery_channel: str
    delivery_status: str
    delivery_error: str | None = None
    request_id: str | None = None
    created_at: datetime
    delivered_at: datetime | None = None


class AlertAttemptsListData(BaseModel):
    items: list[AlertAttemptItem]
    total_count: int


class AlertAttemptsApiResponse(BaseModel):
    data: AlertAttemptsListData
    meta: ResponseMeta


class AlertRetryRequestBody(BaseModel):
    dry_run: bool = False


class BatchRetryRequestBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    limit: int = Field(..., ge=1, le=100)
    dry_run: bool = False
    alert_kind: str | None = None
    audit_id: int | None = None
    feature_code: str | None = None
    plan_code: str | None = None
    actor_type: str | None = None
    request_id_filter: str | None = Field(default=None, alias="request_id")
    date_from: datetime | None = None
    date_to: datetime | None = None


class AlertRetryResponseData(BaseModel):
    alert_event_id: int
    attempted: bool
    delivery_status: str | None = None
    attempt_number: int | None = None
    request_id: str | None = None


class AlertRetryApiResponse(BaseModel):
    data: AlertRetryResponseData
    meta: ResponseMeta


class BatchRetryResultData(BaseModel):
    candidate_count: int
    retried_count: int
    sent_count: int
    failed_count: int
    skipped_count: int
    dry_run: bool
    alert_event_ids: list[int]


class BatchRetryApiResponse(BaseModel):
    data: BatchRetryResultData
    meta: ResponseMeta


class BatchHandleRequestBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    limit: int = Field(..., ge=1, le=200)
    handling_status: Literal["suppressed", "resolved"]
    dry_run: bool = False
    ops_comment: str | None = None
    suppression_key: str | None = None
    alert_kind: str | None = None
    audit_id: int | None = None
    feature_code: str | None = None
    plan_code: str | None = None
    actor_type: str | None = None
    request_id_filter: str | None = Field(default=None, alias="request_id")
    date_from: datetime | None = None
    date_to: datetime | None = None


class BatchHandleResultData(BaseModel):
    candidate_count: int
    handled_count: int
    skipped_count: int
    dry_run: bool
    alert_event_ids: list[int]


class BatchHandleApiResponse(BaseModel):
    data: BatchHandleResultData
    meta: ResponseMeta


class AlertHandlingState(BaseModel):
    handling_status: str
    handled_by_user_id: int | None = None
    handled_at: datetime | None = None
    ops_comment: str | None = None
    suppression_key: str | None = None


class AlertEventItem(BaseModel):
    id: int
    audit_id: int
    dedupe_key: str
    alert_kind: str
    delivery_status: str
    delivery_channel: str
    delivery_error: str | None = None
    created_at: datetime
    delivered_at: datetime | None = None
    feature_code_snapshot: str
    plan_id_snapshot: int
    plan_code_snapshot: str
    risk_level_snapshot: str
    effective_review_status_snapshot: str | None = None
    actor_type_snapshot: str
    actor_identifier_snapshot: str
    age_seconds_snapshot: int
    sla_target_seconds_snapshot: int | None = None
    due_at_snapshot: datetime | None = None
    request_id: str | None = None
    attempt_count: int
    last_attempt_number: int | None = None
    last_attempt_status: str | None = None
    handling: AlertHandlingState | None = None
    retryable: bool


class AlertEventListData(BaseModel):
    items: list[AlertEventItem]
    total_count: int
    page: int
    page_size: int


class AlertEventListApiResponse(BaseModel):
    data: AlertEventListData
    meta: ResponseMeta


class AlertSummaryData(BaseModel):
    total_count: int
    failed_count: int
    sent_count: int
    retryable_count: int
    webhook_failed_count: int
    log_sent_count: int
    suppressed_count: int
    resolved_count: int


class HandleAlertRequestBody(BaseModel):
    handling_status: Literal["suppressed", "resolved"]
    ops_comment: str | None = None
    suppression_key: str | None = None


class HandleAlertResponseData(BaseModel):
    alert_event_id: int
    handling_status: str
    handled_by_user_id: int | None = None
    handled_at: datetime
    ops_comment: str | None = None
    suppression_key: str | None = None


class HandleAlertApiResponse(BaseModel):
    data: HandleAlertResponseData
    meta: ResponseMeta


class AlertHandlingHistoryItem(BaseModel):
    id: int
    alert_event_id: int
    handling_status: str
    handled_by_user_id: int | None = None
    handled_at: datetime
    ops_comment: str | None = None
    suppression_key: str | None = None
    request_id: str | None = None


class AlertHandlingHistoryData(BaseModel):
    items: list[AlertHandlingHistoryItem]
    total_count: int
    limit: int
    offset: int


class AlertHandlingHistoryApiResponse(BaseModel):
    data: AlertHandlingHistoryData
    meta: ResponseMeta


class AlertSummaryApiResponse(BaseModel):
    data: AlertSummaryData
    meta: ResponseMeta


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    request_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorPayload


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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
        check_rate_limit(
            key=f"ops_entitlement_mutation_audits:global:{operation}",
            limit=60,
            window_seconds=60,
        )
        check_rate_limit(
            key=f"ops_entitlement_mutation_audits:role:{user.role}:{operation}",
            limit=30,
            window_seconds=60,
        )
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


def _load_reviews_by_audit_ids(
    db: Session, audit_ids: list[int]
) -> dict[int, CanonicalEntitlementMutationAuditReviewModel]:
    if not audit_ids:
        return {}
    result = db.execute(
        select(CanonicalEntitlementMutationAuditReviewModel).where(
            CanonicalEntitlementMutationAuditReviewModel.audit_id.in_(audit_ids)
        )
    )
    return {r.audit_id: r for r in result.scalars().all()}


def _compute_review_state(
    risk_level: str,
    review_record: CanonicalEntitlementMutationAuditReviewModel | None,
) -> ReviewState | None:
    if review_record is not None:
        return ReviewState(
            status=review_record.review_status,
            reviewed_by_user_id=review_record.reviewed_by_user_id,
            reviewed_at=review_record.reviewed_at,
            review_comment=review_record.review_comment,
            incident_key=review_record.incident_key,
        )
    if risk_level == "high":
        return ReviewState(status="pending_review")
    return None


def _load_handlings_by_event_ids(
    db: Session, event_ids: list[int]
) -> dict[int, CanonicalEntitlementMutationAlertEventHandlingModel]:
    if not event_ids:
        return {}
    result = db.execute(
        select(CanonicalEntitlementMutationAlertEventHandlingModel).where(
            CanonicalEntitlementMutationAlertEventHandlingModel.alert_event_id.in_(event_ids)
        )
    )
    return {r.alert_event_id: r for r in result.scalars().all()}


def _compute_alert_handling_state(
    delivery_status: str,
    handling_record: CanonicalEntitlementMutationAlertEventHandlingModel | None,
) -> AlertHandlingState | None:
    if handling_record is not None:
        return AlertHandlingState(
            handling_status=handling_record.handling_status,
            handled_by_user_id=handling_record.handled_by_user_id,
            handled_at=handling_record.handled_at,
            ops_comment=handling_record.ops_comment,
            suppression_key=handling_record.suppression_key,
        )
    if delivery_status == "failed":
        return AlertHandlingState(handling_status="pending_retry")
    return None


def _to_item(
    audit: Any,
    *,
    include_payloads: bool,
    review_record: CanonicalEntitlementMutationAuditReviewModel | None = None,
) -> dict[str, Any]:
    diff = CanonicalEntitlementMutationDiffService.compute_diff(
        audit.before_payload or {}, audit.after_payload or {}
    )
    return _to_item_with_diff(
        audit,
        diff=diff,
        include_payloads=include_payloads,
        review_record=review_record,
    )


def _to_item_with_diff(
    audit: Any,
    *,
    diff: Any,
    include_payloads: bool,
    review_record: CanonicalEntitlementMutationAuditReviewModel | None = None,
) -> dict[str, Any]:
    review = _compute_review_state(diff.risk_level, review_record)
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
        "review": review,
    }
    if include_payloads:
        d["before_payload"] = audit.before_payload
        d["after_payload"] = audit.after_payload
    return d


def _row_to_queue_item(row: ReviewQueueRow) -> dict[str, Any]:
    # Mapping depuis ReviewQueueRow vers le schéma Pydantic ReviewQueueItem
    base = _to_item_with_diff(
        row.audit,
        diff=row.diff,
        include_payloads=False,
        review_record=row.review_record,
    )
    return {
        **base,
        "effective_review_status": row.effective_review_status,
        "age_seconds": row.age_seconds,
        "age_hours": row.age_hours,
        "is_pending": row.effective_review_status == "pending_review",
        "is_closed": row.effective_review_status == "closed",
        "sla_target_seconds": row.sla_target_seconds,
        "due_at": row.due_at,
        "sla_status": row.sla_status,
        "overdue_seconds": row.overdue_seconds,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

_DIFF_FILTER_MAX = 10_000


@router.get(
    "/mutation-audits",
    response_model=MutationAuditListApiResponse,
    response_model_exclude_none=True,
    responses={
        400: {"model": ErrorEnvelope},
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
    # Filtres diff (61.34)
    risk_level_filter: Literal["high", "medium", "low"] | None = Query(
        default=None, alias="risk_level"
    ),
    change_kind_filter: Literal["binding_created", "binding_updated"] | None = Query(
        default=None, alias="change_kind"
    ),
    changed_field_filter: str | None = Query(default=None, alias="changed_field"),
    # Filtre review (61.35)
    review_status_filter: ReviewStatusLiteral | None = Query(default=None, alias="review_status"),
    include_payloads: bool = Query(default=False),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error

    limit_error = _enforce_limits(user=current_user, request_id=request_id, operation="list")
    if limit_error is not None:
        return limit_error

    sql_filter_kwargs: dict[str, Any] = dict(
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

    has_diff_or_review_filter = any(
        [risk_level_filter, change_kind_filter, changed_field_filter, review_status_filter]
    )

    # Chemin paginé normal : aucun filtre diff ni review
    if not has_diff_or_review_filter:
        items, total_count = CanonicalEntitlementMutationAuditQueryService.list_mutation_audits(
            db,
            page=page,
            page_size=page_size,
            **sql_filter_kwargs,
        )
        audit_ids = [a.id for a in items]
        reviews_by_id = _load_reviews_by_audit_ids(db, audit_ids)

        return {
            "data": {
                "items": [
                    _to_item(
                        item,
                        include_payloads=include_payloads,
                        review_record=reviews_by_id.get(item.id),
                    )
                    for item in items
                ],
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
            },
            "meta": {"request_id": request_id},
        }

    # Chemin avec filtre diff ou review : vérification du count SQL
    _, sql_count = CanonicalEntitlementMutationAuditQueryService.list_mutation_audits(
        db,
        page=1,
        page_size=1,
        **sql_filter_kwargs,
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
        **sql_filter_kwargs,
    )

    # Chargement des revues en une seule requête IN sur tout le batch
    all_audit_ids = [a.id for a in all_items]
    reviews_by_id = _load_reviews_by_audit_ids(db, all_audit_ids)

    filtered: list[tuple[Any, Any, CanonicalEntitlementMutationAuditReviewModel | None]] = []
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
        review_record = reviews_by_id.get(item.id)
        if review_status_filter is not None:
            effective_status = (
                review_record.review_status
                if review_record is not None
                else ("pending_review" if diff.risk_level == "high" else None)
            )
            if effective_status != review_status_filter:
                continue
        filtered.append((item, diff, review_record))

    total_count = len(filtered)
    start = (page - 1) * page_size
    page_items = filtered[start : start + page_size]

    return {
        "data": {
            "items": [
                _to_item_with_diff(
                    item,
                    diff=diff,
                    include_payloads=include_payloads,
                    review_record=review_record,
                )
                for item, diff, review_record in page_items
            ],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
        },
        "meta": {"request_id": request_id},
    }


# ── review-queue/summary ──────────────────────────────────────────────────────
@router.get(
    "/mutation-audits/review-queue/summary",
    response_model=ReviewQueueSummaryApiResponse,
    response_model_exclude_none=True,
    responses={
        400: {"model": ErrorEnvelope},
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_review_queue_summary(
    request: Request,
    risk_level_filter: Literal["high", "medium", "low"] | None = Query(
        default=None, alias="risk_level"
    ),
    effective_review_status_filter: ReviewStatusLiteral | None = Query(
        default=None, alias="effective_review_status"
    ),
    sla_status_filter: Literal["within_sla", "due_soon", "overdue"] | None = Query(
        default=None, alias="sla_status"
    ),
    feature_code: str | None = Query(default=None),
    actor_type: str | None = Query(default=None),
    actor_identifier: str | None = Query(default=None),
    incident_key_filter: str | None = Query(default=None, alias="incident_key"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    if (err := _ensure_ops_role(current_user, request_id)) is not None:
        return err
    if (
        err := _enforce_limits(
            user=current_user, request_id=request_id, operation="review_queue_summary"
        )
    ) is not None:
        return err

    # Check SQL count before building rows (to avoid large diff processing)
    _, sql_count = CanonicalEntitlementMutationAuditQueryService.list_mutation_audits(
        db,
        page=1,
        page_size=1,
        feature_code=feature_code,
        actor_type=actor_type,
        actor_identifier=actor_identifier,
        date_from=date_from,
        date_to=date_to,
    )
    if sql_count > _DIFF_FILTER_MAX:
        return _error_response(
            status_code=400,
            request_id=request_id,
            code="diff_filter_result_set_too_large",
            message=f"Too many results ({sql_count} > {_DIFF_FILTER_MAX}). Add filters to narrow.",
            details={"sql_count": sql_count, "max_allowed": _DIFF_FILTER_MAX},
        )

    now_utc = datetime.now(timezone.utc)
    rows = CanonicalEntitlementReviewQueueService.build_review_queue_rows(
        db,
        now_utc=now_utc,
        risk_level=risk_level_filter,
        effective_review_status=effective_review_status_filter,
        feature_code=feature_code,
        actor_type=actor_type,
        actor_identifier=actor_identifier,
        incident_key=incident_key_filter,
        date_from=date_from,
        date_to=date_to,
        sla_status=sla_status_filter,
        max_sql_rows=_DIFF_FILTER_MAX,
    )

    summary = CanonicalEntitlementReviewQueueService.summarize_review_queue_rows(rows)

    return {
        "data": {
            "pending_review_count": summary.pending_review_count,
            "investigating_count": summary.investigating_count,
            "acknowledged_count": summary.acknowledged_count,
            "closed_count": summary.closed_count,
            "expected_count": summary.expected_count,
            "no_review_count": summary.no_review_count,
            "high_unreviewed_count": summary.high_unreviewed_count,
            "total_count": summary.total_count,
            "overdue_count": summary.overdue_count,
            "due_soon_count": summary.due_soon_count,
            "oldest_pending_age_seconds": summary.oldest_pending_age_seconds,
        },
        "meta": {"request_id": request_id},
    }


# ── review-queue ─────────────────────────────────────────────────────────────
@router.get(
    "/mutation-audits/review-queue",
    response_model=ReviewQueueApiResponse,
    response_model_exclude_none=True,
    responses={
        400: {"model": ErrorEnvelope},
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_review_queue(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    risk_level_filter: Literal["high", "medium", "low"] | None = Query(
        default=None, alias="risk_level"
    ),
    effective_review_status_filter: ReviewStatusLiteral | None = Query(
        default=None, alias="effective_review_status"
    ),
    sla_status_filter: Literal["within_sla", "due_soon", "overdue"] | None = Query(
        default=None, alias="sla_status"
    ),
    feature_code: str | None = Query(default=None),
    actor_type: str | None = Query(default=None),
    actor_identifier: str | None = Query(default=None),
    incident_key_filter: str | None = Query(default=None, alias="incident_key"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)
    if (err := _ensure_ops_role(current_user, request_id)) is not None:
        return err
    if (
        err := _enforce_limits(user=current_user, request_id=request_id, operation="review_queue")
    ) is not None:
        return err

    # Check SQL count
    _, sql_count = CanonicalEntitlementMutationAuditQueryService.list_mutation_audits(
        db,
        page=1,
        page_size=1,
        feature_code=feature_code,
        actor_type=actor_type,
        actor_identifier=actor_identifier,
        date_from=date_from,
        date_to=date_to,
    )
    if sql_count > _DIFF_FILTER_MAX:
        return _error_response(
            status_code=400,
            request_id=request_id,
            code="diff_filter_result_set_too_large",
            message=f"Too many results ({sql_count} > {_DIFF_FILTER_MAX}). Add filters to narrow.",
            details={"sql_count": sql_count, "max_allowed": _DIFF_FILTER_MAX},
        )

    now_utc = datetime.now(timezone.utc)
    rows = CanonicalEntitlementReviewQueueService.build_review_queue_rows(
        db,
        now_utc=now_utc,
        risk_level=risk_level_filter,
        effective_review_status=effective_review_status_filter,
        feature_code=feature_code,
        actor_type=actor_type,
        actor_identifier=actor_identifier,
        incident_key=incident_key_filter,
        date_from=date_from,
        date_to=date_to,
        sla_status=sla_status_filter,
        max_sql_rows=_DIFF_FILTER_MAX,
    )

    total_count = len(rows)
    start = (page - 1) * page_size
    page_rows = rows[start : start + page_size]

    return {
        "data": {
            "items": [_row_to_queue_item(row) for row in page_rows],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
        },
        "meta": {"request_id": request_id},
    }


def _alert_event_to_item(
    row: Any,
    handling_record: CanonicalEntitlementMutationAlertEventHandlingModel | None = None,
) -> dict[str, Any]:
    event = row.event
    handling_state = _compute_alert_handling_state(event.delivery_status, handling_record)
    return {
        "id": event.id,
        "audit_id": event.audit_id,
        "dedupe_key": event.dedupe_key,
        "alert_kind": event.alert_kind,
        "delivery_status": event.delivery_status,
        "delivery_channel": event.delivery_channel,
        "delivery_error": event.delivery_error,
        "created_at": event.created_at,
        "delivered_at": event.delivered_at,
        "feature_code_snapshot": event.feature_code_snapshot,
        "plan_id_snapshot": event.plan_id_snapshot,
        "plan_code_snapshot": event.plan_code_snapshot,
        "risk_level_snapshot": event.risk_level_snapshot,
        "effective_review_status_snapshot": event.effective_review_status_snapshot,
        "actor_type_snapshot": event.actor_type_snapshot,
        "actor_identifier_snapshot": event.actor_identifier_snapshot,
        "age_seconds_snapshot": event.age_seconds_snapshot,
        "sla_target_seconds_snapshot": event.sla_target_seconds_snapshot,
        "due_at_snapshot": event.due_at_snapshot,
        "request_id": event.request_id,
        "attempt_count": row.attempt_count,
        "last_attempt_number": row.last_attempt_number,
        "last_attempt_status": row.last_attempt_status,
        "handling": handling_state,
        "retryable": (
            handling_state is not None and handling_state.handling_status == "pending_retry"
        ),
    }


@router.get(
    "/mutation-audits/alerts/summary",
    response_model=AlertSummaryApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_alert_events_summary(
    request: Request,
    alert_kind: str | None = Query(default=None),
    delivery_status: Literal["sent", "failed"] | None = Query(default=None),
    audit_id: int | None = Query(default=None),
    feature_code: str | None = Query(default=None),
    plan_code: str | None = Query(default=None),
    actor_type: str | None = Query(default=None),
    handling_status: Literal["pending_retry", "suppressed", "resolved"] | None = Query(
        default=None
    ),
    request_id_filter: str | None = Query(default=None, alias="request_id"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    from app.services.canonical_entitlement_alert_query_service import (
        CanonicalEntitlementAlertQueryService,
    )

    request_id = resolve_request_id(request)
    if (err := _ensure_ops_role(current_user, request_id)) is not None:
        return err
    if (
        err := _enforce_limits(
            user=current_user,
            request_id=request_id,
            operation="alert_events_summary",
        )
    ) is not None:
        return err

    summary = CanonicalEntitlementAlertQueryService.get_summary(
        db,
        alert_kind=alert_kind,
        delivery_status=delivery_status,
        audit_id=audit_id,
        feature_code=feature_code,
        plan_code=plan_code,
        actor_type=actor_type,
        handling_status=handling_status,
        request_id=request_id_filter,
        date_from=date_from,
        date_to=date_to,
    )
    return {
        "data": {
            "total_count": summary.total_count,
            "failed_count": summary.failed_count,
            "sent_count": summary.sent_count,
            "retryable_count": summary.retryable_count,
            "webhook_failed_count": summary.webhook_failed_count,
            "log_sent_count": summary.log_sent_count,
            "suppressed_count": summary.suppressed_count,
            "resolved_count": summary.resolved_count,
        },
        "meta": {"request_id": request_id},
    }


@router.get(
    "/mutation-audits/alerts",
    response_model=AlertEventListApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def list_alert_events(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    alert_kind: str | None = Query(default=None),
    delivery_status: Literal["sent", "failed"] | None = Query(default=None),
    audit_id: int | None = Query(default=None),
    feature_code: str | None = Query(default=None),
    plan_code: str | None = Query(default=None),
    actor_type: str | None = Query(default=None),
    handling_status: Literal["pending_retry", "suppressed", "resolved"] | None = Query(
        default=None
    ),
    request_id_filter: str | None = Query(default=None, alias="request_id"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    from app.services.canonical_entitlement_alert_query_service import (
        CanonicalEntitlementAlertQueryService,
    )

    request_id = resolve_request_id(request)
    if (err := _ensure_ops_role(current_user, request_id)) is not None:
        return err
    if (
        err := _enforce_limits(
            user=current_user,
            request_id=request_id,
            operation="list_alert_events",
        )
    ) is not None:
        return err

    rows, total_count = CanonicalEntitlementAlertQueryService.list_alert_events(
        db,
        page=page,
        page_size=page_size,
        alert_kind=alert_kind,
        delivery_status=delivery_status,
        audit_id=audit_id,
        feature_code=feature_code,
        plan_code=plan_code,
        actor_type=actor_type,
        handling_status=handling_status,
        request_id=request_id_filter,
        date_from=date_from,
        date_to=date_to,
    )
    event_ids = [row.event.id for row in rows]
    handlings = _load_handlings_by_event_ids(db, event_ids)
    return {
        "data": {
            "items": [
                _alert_event_to_item(row, handling_record=handlings.get(row.event.id))
                for row in rows
            ],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
        },
        "meta": {"request_id": request_id},
    }


@router.post(
    "/mutation-audits/alerts/retry-batch",
    response_model=BatchRetryApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"description": "Validation error"},
        429: {"model": ErrorEnvelope},
    },
)
def batch_retry_alerts(
    body: BatchRetryRequestBody,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    from app.services.canonical_entitlement_alert_batch_retry_service import (
        CanonicalEntitlementAlertBatchRetryService,
    )

    request_id = resolve_request_id(request)

    if (err := _ensure_ops_role(current_user, request_id)) is not None:
        return err
    if (
        err := _enforce_limits(
            user=current_user,
            request_id=request_id,
            operation="batch_retry_alerts",
        )
    ) is not None:
        return err

    result = CanonicalEntitlementAlertBatchRetryService.batch_retry(
        db,
        limit=body.limit,
        dry_run=body.dry_run,
        request_id=request_id,
        alert_kind=body.alert_kind,
        audit_id=body.audit_id,
        feature_code=body.feature_code,
        plan_code=body.plan_code,
        actor_type=body.actor_type,
        request_id_filter=body.request_id_filter,
        date_from=body.date_from,
        date_to=body.date_to,
    )

    if not body.dry_run:
        db.commit()

    return {
        "data": {
            "candidate_count": result.candidate_count,
            "retried_count": result.retried_count,
            "sent_count": result.sent_count,
            "failed_count": result.failed_count,
            "skipped_count": result.skipped_count,
            "dry_run": result.dry_run,
            "alert_event_ids": result.alert_event_ids,
        },
        "meta": {"request_id": request_id},
    }


@router.post(
    "/mutation-audits/alerts/handle-batch",
    response_model=BatchHandleApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        422: {"description": "Validation error"},
        429: {"model": ErrorEnvelope},
    },
)
def batch_handle_alerts(
    body: BatchHandleRequestBody,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    from app.services.canonical_entitlement_alert_batch_handling_service import (
        CanonicalEntitlementAlertBatchHandlingService,
    )

    request_id = resolve_request_id(request)

    if (err := _ensure_ops_role(current_user, request_id)) is not None:
        return err
    if (
        err := _enforce_limits(
            user=current_user,
            request_id=request_id,
            operation="batch_handle_alerts",
        )
    ) is not None:
        return err

    result = CanonicalEntitlementAlertBatchHandlingService.batch_handle(
        db,
        limit=body.limit,
        handling_status=body.handling_status,
        ops_comment=body.ops_comment,
        suppression_key=body.suppression_key,
        dry_run=body.dry_run,
        request_id=request_id,
        handled_by_user_id=current_user.id,
        alert_kind=body.alert_kind,
        audit_id=body.audit_id,
        feature_code=body.feature_code,
        plan_code=body.plan_code,
        actor_type=body.actor_type,
        request_id_filter=body.request_id_filter,
        date_from=body.date_from,
        date_to=body.date_to,
    )

    if not body.dry_run:
        db.commit()

    return {
        "data": {
            "candidate_count": result.candidate_count,
            "handled_count": result.handled_count,
            "skipped_count": result.skipped_count,
            "dry_run": result.dry_run,
            "alert_event_ids": result.alert_event_ids,
        },
        "meta": {"request_id": request_id},
    }


@router.post(
    "/mutation-audits/alerts/{alert_event_id}/handle",
    response_model=HandleAlertApiResponse,
    response_model_exclude_none=True,
    status_code=201,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        422: {"description": "Validation error"},
        429: {"model": ErrorEnvelope},
    },
)
def handle_alert_event(
    alert_event_id: int,
    body: HandleAlertRequestBody,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    if (err := _ensure_ops_role(current_user, request_id)) is not None:
        return err
    if (
        err := _enforce_limits(
            user=current_user,
            request_id=request_id,
            operation="handle_alert_event",
        )
    ) is not None:
        return err

    try:
        handling = CanonicalEntitlementAlertHandlingService.upsert_handling(
            db,
            alert_event_id=alert_event_id,
            handling_status=body.handling_status,
            handled_by_user_id=current_user.id,
            ops_comment=body.ops_comment,
            suppression_key=body.suppression_key,
            request_id=request_id,
        )
        db.commit()
    except HTTPException as exc:
        if exc.status_code == 404 and exc.detail == "alert event not found":
            return _error_response(
                status_code=404,
                request_id=request_id,
                code="alert_event_not_found",
                message=f"Alert event {alert_event_id} not found",
                details={"alert_event_id": alert_event_id},
            )
        raise

    return {
        "data": {
            "alert_event_id": handling.alert_event_id,
            "handling_status": handling.handling_status,
            "handled_by_user_id": handling.handled_by_user_id,
            "handled_at": handling.handled_at,
            "ops_comment": handling.ops_comment,
            "suppression_key": handling.suppression_key,
        },
        "meta": {"request_id": request_id},
    }


@router.get(
    "/mutation-audits/alerts/{alert_event_id}/handling-history",
    response_model=AlertHandlingHistoryApiResponse,
    response_model_exclude_none=True,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_alert_handling_history(
    alert_event_id: int,
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    if (err := _ensure_ops_role(current_user, request_id)) is not None:
        return err
    if (
        err := _enforce_limits(
            user=current_user,
            request_id=request_id,
            operation="get_alert_handling_history",
        )
    ) is not None:
        return err

    from app.infra.db.models.canonical_entitlement_mutation_alert_event_handling_event import (
        CanonicalEntitlementMutationAlertEventHandlingEventModel,
    )

    alert_event = db.get(CanonicalEntitlementMutationAlertEventModel, alert_event_id)
    if alert_event is None:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="alert_event_not_found",
            message=f"Alert event {alert_event_id} not found",
            details={"alert_event_id": alert_event_id},
        )

    total_count = db.execute(
        select(func.count())
        .select_from(CanonicalEntitlementMutationAlertEventHandlingEventModel)
        .where(
            CanonicalEntitlementMutationAlertEventHandlingEventModel.alert_event_id
            == alert_event_id
        )
    ).scalar_one()
    events = (
        db.execute(
            select(CanonicalEntitlementMutationAlertEventHandlingEventModel)
            .where(
                CanonicalEntitlementMutationAlertEventHandlingEventModel.alert_event_id
                == alert_event_id
            )
            .order_by(
                CanonicalEntitlementMutationAlertEventHandlingEventModel.handled_at.desc(),
                CanonicalEntitlementMutationAlertEventHandlingEventModel.id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )
        .scalars()
        .all()
    )

    return {
        "data": {
            "items": [
                {
                    "id": event.id,
                    "alert_event_id": event.alert_event_id,
                    "handling_status": event.handling_status,
                    "handled_by_user_id": event.handled_by_user_id,
                    "handled_at": event.handled_at,
                    "ops_comment": event.ops_comment,
                    "suppression_key": event.suppression_key,
                    "request_id": event.request_id,
                }
                for event in events
            ],
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
        },
        "meta": {"request_id": request_id},
    }


@router.get(
    "/mutation-audits/alerts/{alert_event_id}/attempts",
    response_model=AlertAttemptsApiResponse,
    response_model_exclude_none=True,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_alert_attempts(
    alert_event_id: int,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    if (err := _ensure_ops_role(current_user, request_id)) is not None:
        return err
    if (
        err := _enforce_limits(user=current_user, request_id=request_id, operation="get_attempts")
    ) is not None:
        return err

    event = db.get(CanonicalEntitlementMutationAlertEventModel, alert_event_id)
    if event is None:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="alert_event_not_found",
            message=f"Alert event {alert_event_id} not found",
            details={"alert_event_id": alert_event_id},
        )

    attempts = (
        db.execute(
            select(CanonicalEntitlementMutationAlertDeliveryAttemptModel)
            .where(
                CanonicalEntitlementMutationAlertDeliveryAttemptModel.alert_event_id
                == alert_event_id
            )
            .order_by(
                CanonicalEntitlementMutationAlertDeliveryAttemptModel.attempt_number.asc(),
                CanonicalEntitlementMutationAlertDeliveryAttemptModel.id.asc(),
            )
        )
        .scalars()
        .all()
    )
    return {
        "data": {
            "items": [
                {
                    "id": attempt.id,
                    "alert_event_id": attempt.alert_event_id,
                    "attempt_number": attempt.attempt_number,
                    "delivery_channel": attempt.delivery_channel,
                    "delivery_status": attempt.delivery_status,
                    "delivery_error": attempt.delivery_error,
                    "request_id": attempt.request_id,
                    "created_at": attempt.created_at,
                    "delivered_at": attempt.delivered_at,
                }
                for attempt in attempts
            ],
            "total_count": len(attempts),
        },
        "meta": {"request_id": request_id},
    }


@router.post(
    "/mutation-audits/alerts/{alert_event_id}/retry",
    response_model=AlertRetryApiResponse,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        409: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def retry_alert(
    alert_event_id: int,
    body: AlertRetryRequestBody,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    from app.services.canonical_entitlement_alert_retry_service import (
        AlertEventNotFoundError,
        AlertEventNotRetryableError,
        CanonicalEntitlementAlertRetryService,
    )

    request_id = resolve_request_id(request)

    if (err := _ensure_ops_role(current_user, request_id)) is not None:
        return err
    if (
        err := _enforce_limits(user=current_user, request_id=request_id, operation="retry")
    ) is not None:
        return err

    try:
        result = CanonicalEntitlementAlertRetryService.retry_failed_alerts(
            db,
            dry_run=body.dry_run,
            request_id=request_id,
            alert_event_id=alert_event_id,
        )
    except AlertEventNotFoundError:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="alert_event_not_found",
            message=f"Alert event {alert_event_id} not found",
            details={"alert_event_id": alert_event_id},
        )
    except AlertEventNotRetryableError:
        return _error_response(
            status_code=409,
            request_id=request_id,
            code="alert_event_not_retryable",
            message=f"Alert event {alert_event_id} is not in failed state",
            details={"alert_event_id": alert_event_id},
        )

    if not body.dry_run:
        db.commit()

    event = db.get(CanonicalEntitlementMutationAlertEventModel, alert_event_id)
    latest_attempt_number = None
    if not body.dry_run:
        latest_attempt_number = db.execute(
            select(
                func.max(CanonicalEntitlementMutationAlertDeliveryAttemptModel.attempt_number)
            ).where(
                CanonicalEntitlementMutationAlertDeliveryAttemptModel.alert_event_id
                == alert_event_id
            )
        ).scalar_one()

    return {
        "data": {
            "alert_event_id": alert_event_id,
            "attempted": result.retried_count > 0,
            "delivery_status": event.delivery_status if event is not None else None,
            "attempt_number": latest_attempt_number,
            "request_id": request_id,
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

    limit_error = _enforce_limits(user=current_user, request_id=request_id, operation="detail")
    if limit_error is not None:
        return limit_error

    audit = CanonicalEntitlementMutationAuditQueryService.get_mutation_audit_by_id(db, audit_id)
    if audit is None:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="audit_not_found",
            message=f"Mutation audit {audit_id} not found",
            details={"audit_id": audit_id},
        )

    reviews = _load_reviews_by_audit_ids(db, [audit_id])
    return {
        "data": _to_item(audit, include_payloads=True, review_record=reviews.get(audit_id)),
        "meta": {"request_id": request_id},
    }


@router.post(
    "/mutation-audits/{audit_id}/review",
    response_model=ReviewApiResponse,
    response_model_exclude_none=True,
    status_code=201,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def post_mutation_audit_review(
    audit_id: int,
    body: ReviewRequestBody,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db_session),
) -> Any:
    request_id = resolve_request_id(request)

    role_error = _ensure_ops_role(current_user, request_id)
    if role_error is not None:
        return role_error

    limit_error = _enforce_limits(user=current_user, request_id=request_id, operation="review")
    if limit_error is not None:
        return limit_error

    try:
        review = CanonicalEntitlementMutationAuditReviewService.upsert_review(
            db,
            audit_id=audit_id,
            review_status=body.review_status,
            reviewed_by_user_id=current_user.id,
            review_comment=body.review_comment,
            incident_key=body.incident_key,
            request_id=request_id,
        )
        db.commit()
    except AuditNotFoundError:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="audit_not_found",
            message=f"Mutation audit {audit_id} not found",
            details={"audit_id": audit_id},
        )

    return {
        "data": {
            "audit_id": review.audit_id,
            "review_status": review.review_status,
            "reviewed_by_user_id": review.reviewed_by_user_id,
            "reviewed_at": review.reviewed_at,
            "review_comment": review.review_comment,
            "incident_key": review.incident_key,
        },
        "meta": {"request_id": request_id},
    }


@router.get(
    "/mutation-audits/{audit_id}/review-history",
    response_model=ReviewHistoryApiResponse,
    response_model_exclude_none=True,
    responses={
        401: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        429: {"model": ErrorEnvelope},
    },
)
def get_review_history(
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
        user=current_user, request_id=request_id, operation="review_history"
    )
    if limit_error is not None:
        return limit_error

    # Vérification existence de l'audit
    from app.infra.db.models.canonical_entitlement_mutation_audit import (
        CanonicalEntitlementMutationAuditModel,
    )
    from app.infra.db.models.canonical_entitlement_mutation_audit_review_event import (
        CanonicalEntitlementMutationAuditReviewEventModel,
    )

    audit = db.get(CanonicalEntitlementMutationAuditModel, audit_id)
    if audit is None:
        return _error_response(
            status_code=404,
            request_id=request_id,
            code="audit_not_found",
            message=f"Audit {audit_id} not found",
            details={"audit_id": audit_id},
        )

    result = db.execute(
        select(CanonicalEntitlementMutationAuditReviewEventModel)
        .where(CanonicalEntitlementMutationAuditReviewEventModel.audit_id == audit_id)
        .order_by(
            CanonicalEntitlementMutationAuditReviewEventModel.occurred_at.asc(),
            CanonicalEntitlementMutationAuditReviewEventModel.id.asc(),
        )
    )
    events = result.scalars().all()

    return {
        "data": {
            "items": [
                {
                    "id": e.id,
                    "audit_id": e.audit_id,
                    "previous_review_status": e.previous_review_status,
                    "new_review_status": e.new_review_status,
                    "previous_review_comment": e.previous_review_comment,
                    "new_review_comment": e.new_review_comment,
                    "previous_incident_key": e.previous_incident_key,
                    "new_incident_key": e.new_incident_key,
                    "reviewed_by_user_id": e.reviewed_by_user_id,
                    "occurred_at": e.occurred_at,
                    "request_id": e.request_id,
                }
                for e in events
            ],
            "total_count": len(events),
        },
        "meta": {"request_id": request_id},
    }
