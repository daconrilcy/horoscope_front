# Service de batch retry des alertes entitlement mutation.
"""Applique les retries de masse en réutilisant les primitives canoniques de delivery."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.datetime_provider import datetime_provider
from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.entitlement_mutation.alert.handling import (
    CanonicalEntitlementMutationAlertHandlingModel,
)
from app.services.canonical_entitlement.alert.retry import (
    CanonicalEntitlementAlertRetryService,
)
from app.services.canonical_entitlement.shared.alert_delivery_runtime import (
    CanonicalEntitlementAlertDeliveryRuntime,
)
from app.services.canonical_entitlement.suppression.application import (
    CanonicalEntitlementAlertSuppressionApplicationService,
)


@dataclass
class BatchRetryResult:
    candidate_count: int
    retried_count: int
    sent_count: int
    failed_count: int
    skipped_count: int
    dry_run: bool
    alert_event_ids: list[int] = field(default_factory=list)


class CanonicalEntitlementAlertBatchRetryService:
    @staticmethod
    def batch_retry(
        db: Session,
        *,
        limit: int,
        dry_run: bool = False,
        request_id: str | None = None,
        alert_kind: str | None = None,
        audit_id: int | None = None,
        feature_code: str | None = None,
        plan_code: str | None = None,
        actor_type: str | None = None,
        request_id_filter: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> BatchRetryResult:
        effective_now = datetime_provider.utcnow()
        candidates = CanonicalEntitlementAlertBatchRetryService._load_batch_candidates(
            db,
            limit=limit,
            alert_kind=alert_kind,
            audit_id=audit_id,
            feature_code=feature_code,
            plan_code=plan_code,
            actor_type=actor_type,
            request_id_filter=request_id_filter,
            date_from=date_from,
            date_to=date_to,
        )
        alert_event_ids = [event.id for event in candidates]
        candidate_count = len(candidates)

        if dry_run:
            return BatchRetryResult(
                candidate_count=candidate_count,
                retried_count=candidate_count,
                sent_count=0,
                failed_count=0,
                skipped_count=0,
                dry_run=True,
                alert_event_ids=alert_event_ids,
            )

        retried_count = 0
        sent_count = 0
        failed_count = 0

        for event in candidates:
            attempt_number = CanonicalEntitlementAlertRetryService._next_attempt_number(
                db, alert_event_id=event.id
            )
            outcome = CanonicalEntitlementAlertDeliveryRuntime.deliver_payload(
                event.payload,
                log_message="ops_alert_batch_retry_log_delivery",
                delivered_at=effective_now,
            )
            if outcome.status == "sent":
                sent_count += 1
            else:
                failed_count += 1

            CanonicalEntitlementAlertDeliveryRuntime.add_delivery_attempt(
                db=db,
                alert_event=event,
                attempt_number=attempt_number,
                request_id=request_id,
                payload=event.payload,
                outcome=outcome,
            )
            CanonicalEntitlementAlertDeliveryRuntime.apply_delivery_state(
                alert_event=event,
                outcome=outcome,
                attempt_number=attempt_number,
                updated_at=effective_now,
            )
            retried_count += 1

        db.flush()
        return BatchRetryResult(
            candidate_count=candidate_count,
            retried_count=retried_count,
            sent_count=sent_count,
            failed_count=failed_count,
            skipped_count=candidate_count - retried_count,
            dry_run=False,
            alert_event_ids=alert_event_ids,
        )

    @staticmethod
    def _load_batch_candidates(
        db: Session,
        *,
        limit: int,
        alert_kind: str | None,
        audit_id: int | None,
        feature_code: str | None,
        plan_code: str | None,
        actor_type: str | None,
        request_id_filter: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> list[CanonicalEntitlementMutationAlertEventModel]:
        model = CanonicalEntitlementMutationAlertEventModel
        handling_model = CanonicalEntitlementMutationAlertHandlingModel
        query = select(model).where(model.delivery_status == "failed")
        excluded_subquery = select(handling_model.alert_event_id).where(
            handling_model.handling_status.in_(["suppressed", "resolved"])
        )
        query = query.where(model.id.notin_(excluded_subquery))
        query = query.where(
            model.id.notin_(
                CanonicalEntitlementAlertSuppressionApplicationService.active_rule_application_event_ids_subquery()
            )
        )

        if alert_kind is not None:
            query = query.where(model.alert_kind == alert_kind)
        if audit_id is not None:
            query = query.where(model.audit_id == audit_id)
        if feature_code is not None:
            query = query.where(model.feature_code_snapshot == feature_code)
        if plan_code is not None:
            query = query.where(model.plan_code_snapshot == plan_code)
        if actor_type is not None:
            query = query.where(model.actor_type_snapshot == actor_type)
        if request_id_filter is not None:
            query = query.where(model.request_id == request_id_filter)
        if date_from is not None:
            query = query.where(model.created_at >= date_from)
        if date_to is not None:
            query = query.where(model.created_at <= date_to)
        query = query.order_by(model.id.asc()).limit(limit)
        return list(db.scalars(query).all())
