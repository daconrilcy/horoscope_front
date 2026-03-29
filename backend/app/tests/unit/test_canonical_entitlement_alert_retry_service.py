from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session

from app.infra.db.models.canonical_entitlement_mutation_alert_delivery_attempt import (
    CanonicalEntitlementMutationAlertDeliveryAttemptModel,
)
from app.infra.db.models.canonical_entitlement_mutation_alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)
from app.services.canonical_entitlement_alert_retry_service import (
    AlertEventNotFoundError,
    AlertEventNotRetryableError,
    CanonicalEntitlementAlertRetryService,
)


def _seed_audit(db: Session) -> CanonicalEntitlementMutationAuditModel:
    audit = CanonicalEntitlementMutationAuditModel(
        operation="upsert_plan_feature_configuration",
        plan_id=1,
        plan_code_snapshot="premium",
        feature_code="test_feature",
        actor_type="user",
        actor_identifier="user@test.com",
        source_origin="manual",
        before_payload={"is_enabled": True},
        after_payload={"is_enabled": False},
    )
    db.add(audit)
    db.flush()
    return audit


def _seed_alert_event(
    db: Session,
    *,
    audit_id: int,
    delivery_status: str = "failed",
    delivery_error: str | None = "Connection refused",
    payload: dict | None = None,
) -> CanonicalEntitlementMutationAlertEventModel:
    event = CanonicalEntitlementMutationAlertEventModel(
        audit_id=audit_id,
        dedupe_key=f"audit:{audit_id}:review:pending_review:sla:overdue",
        alert_kind="sla_overdue",
        risk_level_snapshot="high",
        effective_review_status_snapshot="pending_review",
        feature_code_snapshot="test_feature",
        plan_id_snapshot=1,
        plan_code_snapshot="premium",
        actor_type_snapshot="user",
        actor_identifier_snapshot="user@test.com",
        sla_target_seconds_snapshot=14_400,
        age_seconds_snapshot=99_999,
        delivery_channel="webhook",
        delivery_status=delivery_status,
        delivery_error=delivery_error,
        payload=payload or {"alert_kind": "sla_overdue", "audit_id": audit_id},
    )
    db.add(event)
    db.flush()
    return event


def _get_attempts(db: Session) -> list[CanonicalEntitlementMutationAlertDeliveryAttemptModel]:
    return (
        db.query(CanonicalEntitlementMutationAlertDeliveryAttemptModel)
        .order_by(
            CanonicalEntitlementMutationAlertDeliveryAttemptModel.attempt_number.asc(),
            CanonicalEntitlementMutationAlertDeliveryAttemptModel.id.asc(),
        )
        .all()
    )


def test_retry_failed_alert_creates_attempt(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    event = _seed_alert_event(db_session, audit_id=audit.id)

    with patch(
        "app.services.canonical_entitlement_alert_retry_service."
        "CanonicalEntitlementAlertService._deliver_webhook",
        return_value=(True, None),
    ):
        result = CanonicalEntitlementAlertRetryService.retry_failed_alerts(
            db_session,
            alert_event_id=event.id,
            request_id="req-retry",
        )

    attempts = _get_attempts(db_session)
    assert result.candidate_count == 1
    assert result.retried_count == 1
    assert result.sent_count == 1
    assert result.failed_count == 0
    assert len(attempts) == 1
    assert attempts[0].alert_event_id == event.id
    assert attempts[0].attempt_number == 1
    assert attempts[0].request_id == "req-retry"
    assert attempts[0].payload == event.payload


def test_retry_failed_alert_updates_parent_status_on_success(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    event = _seed_alert_event(db_session, audit_id=audit.id)
    now_utc = datetime(2026, 3, 29, 12, 0, tzinfo=timezone.utc)

    with patch(
        "app.services.canonical_entitlement_alert_retry_service."
        "CanonicalEntitlementAlertService._deliver_webhook",
        return_value=(True, None),
    ):
        with patch(
            "app.services.canonical_entitlement_alert_retry_service."
            "settings.ops_review_queue_alert_webhook_url",
            "https://example.test/webhook",
        ):
            CanonicalEntitlementAlertRetryService.retry_failed_alerts(
                db_session,
                now_utc=now_utc,
                alert_event_id=event.id,
            )

    db_session.refresh(event)
    assert event.delivery_status == "sent"
    assert event.delivery_error is None
    assert event.delivered_at == now_utc.replace(tzinfo=None)


def test_retry_failed_alert_keeps_failed_on_delivery_failure(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    event = _seed_alert_event(db_session, audit_id=audit.id)

    with patch(
        "app.services.canonical_entitlement_alert_retry_service."
        "CanonicalEntitlementAlertService._deliver_webhook",
        return_value=(False, "Timeout"),
    ):
        with patch(
            "app.services.canonical_entitlement_alert_retry_service."
            "settings.ops_review_queue_alert_webhook_url",
            "https://example.test/webhook",
        ):
            result = CanonicalEntitlementAlertRetryService.retry_failed_alerts(
                db_session,
                alert_event_id=event.id,
            )

    db_session.refresh(event)
    attempts = _get_attempts(db_session)
    assert result.sent_count == 0
    assert result.failed_count == 1
    assert event.delivery_status == "failed"
    assert event.delivery_error == "Timeout"
    assert attempts[0].delivery_status == "failed"
    assert attempts[0].delivery_error == "Timeout"


def test_retry_dry_run_persists_nothing(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    event = _seed_alert_event(db_session, audit_id=audit.id)
    original_status = event.delivery_status
    original_error = event.delivery_error

    with patch(
        "app.services.canonical_entitlement_alert_retry_service."
        "CanonicalEntitlementAlertService._deliver_webhook",
        side_effect=AssertionError("webhook should not be called in dry-run"),
    ):
        result = CanonicalEntitlementAlertRetryService.retry_failed_alerts(
            db_session,
            alert_event_id=event.id,
            dry_run=True,
        )

    db_session.refresh(event)
    assert result.candidate_count == 1
    assert result.retried_count == 1
    assert result.sent_count == 0
    assert result.failed_count == 0
    assert result.dry_run is True
    assert _get_attempts(db_session) == []
    assert event.delivery_status == original_status
    assert event.delivery_error == original_error


def test_retry_targeted_unknown_alert_raises_not_found(db_session: Session) -> None:
    with pytest.raises(AlertEventNotFoundError):
        CanonicalEntitlementAlertRetryService.retry_failed_alerts(
            db_session,
            alert_event_id=9999,
        )


def test_retry_targeted_non_failed_alert_raises_not_retryable(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    event = _seed_alert_event(
        db_session,
        audit_id=audit.id,
        delivery_status="sent",
        delivery_error=None,
    )

    with pytest.raises(AlertEventNotRetryableError):
        CanonicalEntitlementAlertRetryService.retry_failed_alerts(
            db_session,
            alert_event_id=event.id,
        )


def test_retry_attempt_number_increments(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    event = _seed_alert_event(db_session, audit_id=audit.id)
    existing_attempt = CanonicalEntitlementMutationAlertDeliveryAttemptModel(
        alert_event_id=event.id,
        attempt_number=1,
        delivery_channel="webhook",
        delivery_status="failed",
        delivery_error="Timeout",
        request_id="req-1",
        payload=event.payload,
    )
    db_session.add(existing_attempt)
    db_session.flush()

    with patch(
        "app.services.canonical_entitlement_alert_retry_service."
        "CanonicalEntitlementAlertService._deliver_webhook",
        return_value=(True, None),
    ):
        CanonicalEntitlementAlertRetryService.retry_failed_alerts(
            db_session,
            alert_event_id=event.id,
        )

    attempts = _get_attempts(db_session)
    assert [attempt.attempt_number for attempt in attempts] == [1, 2]


def test_retry_ignores_non_failed_events_in_batch_mode(db_session: Session) -> None:
    first_audit = _seed_audit(db_session)
    second_audit = _seed_audit(db_session)
    failed_event = _seed_alert_event(db_session, audit_id=first_audit.id)
    _seed_alert_event(
        db_session,
        audit_id=second_audit.id,
        delivery_status="sent",
        delivery_error=None,
    )

    with patch(
        "app.services.canonical_entitlement_alert_retry_service."
        "CanonicalEntitlementAlertService._deliver_webhook",
        return_value=(True, None),
    ):
        result = CanonicalEntitlementAlertRetryService.retry_failed_alerts(db_session)

    attempts = _get_attempts(db_session)
    assert result.candidate_count == 1
    assert result.retried_count == 1
    assert len(attempts) == 1
    assert attempts[0].alert_event_id == failed_event.id
