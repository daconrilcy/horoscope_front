from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

from sqlalchemy.orm import Session

from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)
from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.entitlement_mutation.alert.delivery_attempt import (
    CanonicalEntitlementMutationAlertDeliveryAttemptModel,
)
from app.infra.db.models.entitlement_mutation.alert.handling import (
    CanonicalEntitlementMutationAlertEventHandlingModel,
)
from app.infra.db.models.entitlement_mutation.suppression.suppression_rule import (
    CanonicalEntitlementMutationAlertSuppressionRuleModel,
)
from app.services.canonical_entitlement_alert_batch_retry_service import (
    CanonicalEntitlementAlertBatchRetryService,
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
    alert_kind: str = "sla_overdue",
    feature_code: str = "test_feature",
    plan_code: str = "premium",
    actor_type: str = "user",
    request_id: str | None = None,
    created_at: datetime | None = None,
) -> CanonicalEntitlementMutationAlertEventModel:
    event = CanonicalEntitlementMutationAlertEventModel(
        audit_id=audit_id,
        dedupe_key=f"audit:{audit_id}:{alert_kind}:{feature_code}:{delivery_status}:{created_at}",
        alert_kind=alert_kind,
        risk_level_snapshot="high",
        effective_review_status_snapshot="pending_review",
        feature_code_snapshot=feature_code,
        plan_id_snapshot=1,
        plan_code_snapshot=plan_code,
        actor_type_snapshot=actor_type,
        actor_identifier_snapshot="user@test.com",
        sla_target_seconds_snapshot=14_400,
        age_seconds_snapshot=99_999,
        delivery_channel="webhook",
        delivery_status=delivery_status,
        delivery_error=None if delivery_status == "sent" else "Connection refused",
        request_id=request_id,
        payload={"alert_kind": alert_kind, "audit_id": audit_id, "feature_code": feature_code},
        created_at=created_at or datetime.now(timezone.utc),
    )
    db.add(event)
    db.flush()
    return event


def _attempt_count(db: Session) -> int:
    return db.query(CanonicalEntitlementMutationAlertDeliveryAttemptModel).count()


def test_batch_retry_dry_run_returns_candidate_count_without_writes(
    db_session: Session,
) -> None:
    first_audit = _seed_audit(db_session)
    second_audit = _seed_audit(db_session)
    first = _seed_alert_event(db_session, audit_id=first_audit.id)
    second = _seed_alert_event(db_session, audit_id=second_audit.id)

    result = CanonicalEntitlementAlertBatchRetryService.batch_retry(
        db_session,
        limit=10,
        dry_run=True,
    )

    assert result.candidate_count == 2
    assert result.retried_count == 2
    assert result.sent_count == 0
    assert result.failed_count == 0
    assert result.skipped_count == 0
    assert result.dry_run is True
    assert result.alert_event_ids == [first.id, second.id]
    assert _attempt_count(db_session) == 0


def test_batch_retry_dry_run_no_db_add(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    _seed_alert_event(db_session, audit_id=audit.id)

    original_add = db_session.add
    add_calls: list[object] = []

    def _tracking_add(instance: object) -> None:
        add_calls.append(instance)
        original_add(instance)

    with patch.object(db_session, "add", side_effect=_tracking_add):
        CanonicalEntitlementAlertBatchRetryService.batch_retry(
            db_session,
            limit=10,
            dry_run=True,
        )

    assert all(
        not isinstance(instance, CanonicalEntitlementMutationAlertDeliveryAttemptModel)
        for instance in add_calls
    )
    assert _attempt_count(db_session) == 0


def test_batch_retry_real_retries_all_failed_candidates(db_session: Session) -> None:
    first_audit = _seed_audit(db_session)
    second_audit = _seed_audit(db_session)
    first = _seed_alert_event(db_session, audit_id=first_audit.id)
    second = _seed_alert_event(db_session, audit_id=second_audit.id)

    with patch(
        "app.services.canonical_entitlement_alert_batch_retry_service."
        "CanonicalEntitlementAlertService._deliver_webhook",
        return_value=(True, None),
    ):
        result = CanonicalEntitlementAlertBatchRetryService.batch_retry(
            db_session,
            limit=10,
            request_id="req-batch",
        )

    assert result.candidate_count == 2
    assert result.retried_count == 2
    assert result.sent_count == 2
    assert result.failed_count == 0
    assert result.skipped_count == 0
    assert result.alert_event_ids == [first.id, second.id]
    assert _attempt_count(db_session) == 2


def test_batch_retry_respects_limit(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    first = _seed_alert_event(
        db_session,
        audit_id=audit.id,
        created_at=datetime(2026, 3, 29, 8, 0, tzinfo=timezone.utc),
    )
    second = _seed_alert_event(
        db_session,
        audit_id=audit.id,
        created_at=datetime(2026, 3, 29, 9, 0, tzinfo=timezone.utc),
    )
    _seed_alert_event(
        db_session,
        audit_id=audit.id,
        created_at=datetime(2026, 3, 29, 10, 0, tzinfo=timezone.utc),
    )

    with patch(
        "app.services.canonical_entitlement_alert_batch_retry_service."
        "CanonicalEntitlementAlertService._deliver_webhook",
        return_value=(True, None),
    ):
        result = CanonicalEntitlementAlertBatchRetryService.batch_retry(
            db_session,
            limit=2,
        )

    assert result.candidate_count == 2
    assert result.alert_event_ids == [first.id, second.id]


def test_batch_retry_filter_by_alert_kind(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    matching = _seed_alert_event(db_session, audit_id=audit.id, alert_kind="sla_overdue")
    _seed_alert_event(db_session, audit_id=audit.id, alert_kind="sla_due_soon")

    result = CanonicalEntitlementAlertBatchRetryService.batch_retry(
        db_session,
        limit=10,
        dry_run=True,
        alert_kind="sla_overdue",
    )

    assert result.candidate_count == 1
    assert result.alert_event_ids == [matching.id]


def test_batch_retry_filter_by_feature_code(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    matching = _seed_alert_event(db_session, audit_id=audit.id, feature_code="feature-a")
    _seed_alert_event(db_session, audit_id=audit.id, feature_code="feature-b")

    result = CanonicalEntitlementAlertBatchRetryService.batch_retry(
        db_session,
        limit=10,
        dry_run=True,
        feature_code="feature-a",
    )

    assert result.candidate_count == 1
    assert result.alert_event_ids == [matching.id]


def test_batch_retry_filter_by_audit_id(db_session: Session) -> None:
    matching_audit = _seed_audit(db_session)
    other_audit = _seed_audit(db_session)
    matching = _seed_alert_event(db_session, audit_id=matching_audit.id)
    _seed_alert_event(db_session, audit_id=other_audit.id)

    result = CanonicalEntitlementAlertBatchRetryService.batch_retry(
        db_session,
        limit=10,
        dry_run=True,
        audit_id=matching_audit.id,
    )

    assert result.candidate_count == 1
    assert result.alert_event_ids == [matching.id]


def test_batch_retry_filter_by_request_id(db_session: Session) -> None:
    matching_audit = _seed_audit(db_session)
    other_audit = _seed_audit(db_session)
    matching = _seed_alert_event(db_session, audit_id=matching_audit.id, request_id="req-1")
    _seed_alert_event(db_session, audit_id=other_audit.id, request_id="req-2")

    result = CanonicalEntitlementAlertBatchRetryService.batch_retry(
        db_session,
        limit=10,
        dry_run=True,
        request_id_filter="req-1",
    )

    assert result.candidate_count == 1
    assert result.alert_event_ids == [matching.id]


def test_batch_retry_returns_correct_alert_event_ids(db_session: Session) -> None:
    first_audit = _seed_audit(db_session)
    second_audit = _seed_audit(db_session)
    first = _seed_alert_event(db_session, audit_id=first_audit.id)
    second = _seed_alert_event(db_session, audit_id=second_audit.id)

    result = CanonicalEntitlementAlertBatchRetryService.batch_retry(
        db_session,
        limit=10,
        dry_run=True,
    )

    assert result.alert_event_ids == [first.id, second.id]


def test_batch_retry_skipped_count_is_zero_when_all_retried(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    _seed_alert_event(db_session, audit_id=audit.id)

    with patch(
        "app.services.canonical_entitlement_alert_batch_retry_service."
        "CanonicalEntitlementAlertService._deliver_webhook",
        return_value=(True, None),
    ):
        result = CanonicalEntitlementAlertBatchRetryService.batch_retry(
            db_session,
            limit=10,
        )

    assert result.candidate_count == 1
    assert result.retried_count == 1
    assert result.skipped_count == 0


def test_batch_retry_empty_when_no_failed(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    _seed_alert_event(db_session, audit_id=audit.id, delivery_status="sent")

    result = CanonicalEntitlementAlertBatchRetryService.batch_retry(
        db_session,
        limit=10,
        dry_run=False,
    )

    assert result.candidate_count == 0
    assert result.retried_count == 0
    assert result.sent_count == 0
    assert result.failed_count == 0
    assert result.skipped_count == 0
    assert result.alert_event_ids == []
    assert _attempt_count(db_session) == 0


def test_batch_retry_excludes_rule_suppressed_alerts(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    matching = _seed_alert_event(db_session, audit_id=audit.id, feature_code="feature-rule")
    retryable = _seed_alert_event(db_session, audit_id=audit.id, feature_code="feature-open")
    db_session.add(
        CanonicalEntitlementMutationAlertSuppressionRuleModel(
            alert_kind=matching.alert_kind,
            feature_code=matching.feature_code_snapshot,
            plan_code=matching.plan_code_snapshot,
            actor_type=matching.actor_type_snapshot,
            is_active=True,
        )
    )
    db_session.add(
        CanonicalEntitlementMutationAlertEventHandlingModel(
            alert_event_id=retryable.id,
            handling_status="resolved",
            handled_by_user_id=1,
        )
    )
    db_session.commit()

    third_retryable = _seed_alert_event(db_session, audit_id=audit.id, feature_code="feature-final")
    db_session.commit()

    result = CanonicalEntitlementAlertBatchRetryService.batch_retry(
        db_session,
        limit=10,
        dry_run=True,
    )

    assert result.candidate_count == 1
    assert result.alert_event_ids == [third_retryable.id]


def test_batch_retry_dry_run_excludes_rule_suppressed_alerts(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    matching = _seed_alert_event(db_session, audit_id=audit.id, feature_code="feature-rule")
    open_event = _seed_alert_event(db_session, audit_id=audit.id, feature_code="feature-open")
    db_session.add(
        CanonicalEntitlementMutationAlertSuppressionRuleModel(
            alert_kind=matching.alert_kind,
            feature_code=matching.feature_code_snapshot,
            plan_code=matching.plan_code_snapshot,
            actor_type=matching.actor_type_snapshot,
            is_active=True,
        )
    )
    db_session.commit()

    result = CanonicalEntitlementAlertBatchRetryService.batch_retry(
        db_session,
        limit=10,
        dry_run=True,
    )

    assert result.candidate_count == 1
    assert result.retried_count == 1
    assert result.alert_event_ids == [open_event.id]
