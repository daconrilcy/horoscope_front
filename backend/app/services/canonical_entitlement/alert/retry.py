# Service de retry des alertes entitlement mutation.
"""Journalise les retries et réutilise les primitives canoniques de delivery."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.datetime_provider import datetime_provider
from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.entitlement_mutation.alert.delivery_attempt import (
    CanonicalEntitlementMutationAlertDeliveryAttemptModel,
)
from app.services.canonical_entitlement.shared.alert_delivery_runtime import (
    CanonicalEntitlementAlertDeliveryRuntime,
)
from app.services.canonical_entitlement.suppression.application import (
    CanonicalEntitlementAlertSuppressionApplicationService,
)


class AlertEventNotFoundError(ValueError):
    pass


class AlertEventNotRetryableError(ValueError):
    pass


@dataclass
class AlertRetryRunResult:
    candidate_count: int
    retried_count: int
    sent_count: int
    failed_count: int
    dry_run: bool


class CanonicalEntitlementAlertRetryService:
    @staticmethod
    def retry_failed_alerts(
        db: Session,
        *,
        now_utc: datetime | None = None,
        dry_run: bool = False,
        request_id: str | None = None,
        limit: int | None = None,
        alert_event_id: int | None = None,
    ) -> AlertRetryRunResult:
        effective_now = now_utc or datetime_provider.utcnow()
        candidates = CanonicalEntitlementAlertRetryService._load_candidates(
            db,
            alert_event_id=alert_event_id,
            limit=limit,
        )

        if dry_run:
            return AlertRetryRunResult(
                candidate_count=len(candidates),
                retried_count=len(candidates),
                sent_count=0,
                failed_count=0,
                dry_run=True,
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
                log_message="ops_alert_retry_log_delivery",
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
        return AlertRetryRunResult(
            candidate_count=len(candidates),
            retried_count=retried_count,
            sent_count=sent_count,
            failed_count=failed_count,
            dry_run=False,
        )

    @staticmethod
    def _load_candidates(
        db: Session,
        *,
        alert_event_id: int | None,
        limit: int | None,
    ) -> list[CanonicalEntitlementMutationAlertEventModel]:
        from app.infra.db.models.entitlement_mutation.alert.handling import (
            CanonicalEntitlementMutationAlertHandlingModel as HandlingModel,
        )
        from app.services.canonical_entitlement.suppression.rule import (
            CanonicalEntitlementAlertSuppressionRuleService,
        )

        active_rules = CanonicalEntitlementAlertSuppressionRuleService.load_active_rules(db)

        if alert_event_id is not None:
            event = db.get(CanonicalEntitlementMutationAlertEventModel, alert_event_id)
            if event is None:
                raise AlertEventNotFoundError(f"Alert event {alert_event_id} not found")
            if event.delivery_status != "failed":
                raise AlertEventNotRetryableError(f"Alert event {alert_event_id} is not retryable")

            # Check manual handling
            handling = db.scalars(
                select(HandlingModel).where(
                    HandlingModel.alert_event_id == event.id,
                    HandlingModel.handling_status.in_(["suppressed", "resolved"]),
                )
            ).first()
            if handling:
                raise AlertEventNotRetryableError(
                    f"Alert event {alert_event_id} is suppressed or resolved"
                )
            # Check rules
            suppression_service = CanonicalEntitlementAlertSuppressionApplicationService
            matcher = suppression_service.match_and_ensure_rule_application
            match = matcher(db, alert_event=event, active_rules=active_rules)
            if match is not None:
                raise AlertEventNotRetryableError(
                    f"Alert event {alert_event_id} is matched by a suppression rule"
                )
            return [event]

        query = (
            select(CanonicalEntitlementMutationAlertEventModel)
            .where(CanonicalEntitlementMutationAlertEventModel.delivery_status == "failed")
            .order_by(CanonicalEntitlementMutationAlertEventModel.id.asc())
        )
        if limit is not None:
            query = query.limit(limit)

        candidates = list(db.execute(query).scalars().all())
        if not candidates:
            return []

        event_ids = [c.id for c in candidates]

        # Pre-load manual handlings for all candidates to avoid N+1
        handlings = db.scalars(
            select(HandlingModel).where(
                HandlingModel.alert_event_id.in_(event_ids),
                HandlingModel.handling_status.in_(["suppressed", "resolved"]),
            )
        ).all()
        suppressed_event_ids = {h.alert_event_id for h in handlings}

        # Filter out suppressed ones (manual or rule)
        results = []
        for ev in candidates:
            if ev.id in suppressed_event_ids:
                continue

            suppression_service = CanonicalEntitlementAlertSuppressionApplicationService
            matcher = suppression_service.match_and_ensure_rule_application
            match = matcher(db, alert_event=ev, active_rules=active_rules)
            if match is not None:
                continue

            results.append(ev)

        return results

    @staticmethod
    def _next_attempt_number(db: Session, *, alert_event_id: int) -> int:
        max_attempt = db.execute(
            select(
                func.max(CanonicalEntitlementMutationAlertDeliveryAttemptModel.attempt_number)
            ).where(
                CanonicalEntitlementMutationAlertDeliveryAttemptModel.alert_event_id
                == alert_event_id
            )
        ).scalar_one()
        return (max_attempt or 0) + 1
