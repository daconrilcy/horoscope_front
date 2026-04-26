"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser
from app.core.rate_limit import RateLimitError, check_rate_limit
from app.infra.db.models.entitlement_mutation.alert.handling import (
    CanonicalEntitlementMutationAlertHandlingModel,
)
from app.infra.db.models.entitlement_mutation.audit.review import (
    CanonicalEntitlementMutationAuditReviewModel,
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

router = APIRouter(prefix="/v1/ops/entitlements", tags=["ops-entitlement-audits"])
WritableReviewStatusLiteral = Literal["acknowledged", "expected", "investigating", "closed"]
ReviewStatusLiteral = Literal[
    "pending_review", "acknowledged", "expected", "investigating", "closed"
]
PersistedReviewStatusLiteral = WritableReviewStatusLiteral
_DIFF_FILTER_MAX = 10_000
from app.api.v1.schemas.routers.ops.entitlement_mutation_audits import *


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
