"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser
from app.core.exceptions import ApplicationError
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.infra.db.models.entitlement_mutation.alert.handling import (
    CanonicalEntitlementMutationAlertHandlingModel,
)
from app.infra.db.models.entitlement_mutation.audit.review import (
    CanonicalEntitlementMutationAuditReviewModel,
)
from app.services.canonical_entitlement.audit.audit_query import (
    CanonicalEntitlementMutationAuditQueryService,
)
from app.services.canonical_entitlement.audit.diff_service import (
    CanonicalEntitlementMutationDiffService,
)
from app.services.canonical_entitlement.audit.review_queue import (
    ReviewQueueRow,
)
from app.services.canonical_entitlement.suppression.application import (
    CanonicalEntitlementAlertSuppressionApplicationService,
)

WritableReviewStatusLiteral = Literal["acknowledged", "expected", "investigating", "closed"]
ReviewStatusLiteral = Literal[
    "pending_review", "acknowledged", "expected", "investigating", "closed"
]
PersistedReviewStatusLiteral = WritableReviewStatusLiteral
_DIFF_FILTER_MAX = 10_000
from app.api.v1.schemas.routers.ops.entitlement_mutation_audits import (
    AlertHandlingState,
    ReviewState,
)


def build_mutation_audit_list_response(
    *,
    db: Session,
    current_user: AuthenticatedUser,
    request_id: str,
    page: int,
    page_size: int,
    plan_id: int | None,
    plan_code: str | None,
    feature_code: str | None,
    actor_type: str | None,
    actor_identifier: str | None,
    source_origin: str | None,
    request_id_filter: str | None,
    date_from: datetime | None,
    date_to: datetime | None,
    risk_level_filter: Literal["high", "medium", "low"] | None,
    change_kind_filter: Literal["binding_created", "binding_updated"] | None,
    changed_field_filter: str | None,
    review_status_filter: ReviewStatusLiteral | None,
    include_payloads: bool,
) -> Any:
    """Construit la réponse de liste des mutations en dehors du routeur HTTP."""
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

    if not has_diff_or_review_filter:
        items, total_count = CanonicalEntitlementMutationAuditQueryService.list_mutation_audits(
            db,
            page=page,
            page_size=page_size,
            **sql_filter_kwargs,
        )
        audit_ids = [audit.id for audit in items]
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

    _, sql_count = CanonicalEntitlementMutationAuditQueryService.list_mutation_audits(
        db,
        page=1,
        page_size=1,
        **sql_filter_kwargs,
    )

    if sql_count > _DIFF_FILTER_MAX:
        return _raise_error(
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

    all_audit_ids = [audit.id for audit in all_items]
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


def _raise_error(
    *,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any],
    **_: Any,
) -> Any:
    raise ApplicationError(
        request_id=request_id,
        code=code,
        message=message,
        details=details,
    )


def _ensure_ops_role(user: AuthenticatedUser, request_id: str) -> Any | None:
    if user.role not in ["ops", "admin"]:
        return _raise_error(
            request_id=request_id,
            code="insufficient_role",
            message="role is not allowed",
            details={"required_roles": "ops, admin", "actual_role": user.role},
        )
    return None


def _enforce_limits(*, user: AuthenticatedUser, request_id: str, operation: str) -> Any | None:
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
        return _raise_error(
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
) -> dict[int, CanonicalEntitlementMutationAlertHandlingModel]:
    if not event_ids:
        return {}
    result = db.execute(
        select(CanonicalEntitlementMutationAlertHandlingModel).where(
            CanonicalEntitlementMutationAlertHandlingModel.alert_event_id.in_(event_ids)
        )
    )
    return {r.alert_event_id: r for r in result.scalars().all()}


def _load_active_rule_applications_by_event_ids(
    db: Session, event_ids: list[int]
) -> dict[int, Any]:
    if not event_ids:
        return {}
    suppression_service = CanonicalEntitlementAlertSuppressionApplicationService
    loader = suppression_service.load_active_rule_applications_by_event_ids
    return loader(
        db,
        event_ids=event_ids,
    )


def _normalize_optional_rule_field(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _compute_alert_handling_state(
    delivery_status: str,
    handling_record: CanonicalEntitlementMutationAlertHandlingModel | None,
    rule_application: Any | None = None,
) -> AlertHandlingState | None:
    if handling_record is not None:
        return AlertHandlingState(
            handling_status=handling_record.handling_status,
            source="manual",
            handled_by_user_id=handling_record.handled_by_user_id,
            handled_at=handling_record.handled_at,
            ops_comment=handling_record.ops_comment,
            suppression_key=handling_record.suppression_key,
        )
    if rule_application is not None:
        return AlertHandlingState(
            handling_status="suppressed",
            source="rule",
            suppression_rule_id=rule_application.suppression_rule_id,
            ops_comment=rule_application.application_reason,
            suppression_key=rule_application.suppression_key,
        )
    if delivery_status == "failed":
        return AlertHandlingState(
            handling_status="pending_retry",
            source="virtual",
        )
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


def _alert_event_to_item(
    row: Any,
    handling_record: CanonicalEntitlementMutationAlertHandlingModel | None = None,
    rule_application: Any | None = None,
) -> dict[str, Any]:
    event = row.event
    handling_state = _compute_alert_handling_state(
        event.delivery_status, handling_record, rule_application
    )
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
