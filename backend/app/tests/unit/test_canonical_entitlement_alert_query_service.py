from __future__ import annotations

from datetime import datetime, timedelta, timezone

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
    CanonicalEntitlementMutationAlertHandlingModel,
)
from app.infra.db.models.entitlement_mutation.suppression.suppression_application import (
    CanonicalEntitlementMutationAlertSuppressionApplicationModel,
)
from app.infra.db.models.entitlement_mutation.suppression.suppression_rule import (
    CanonicalEntitlementMutationAlertSuppressionRuleModel,
)
from app.services.canonical_entitlement.alert.query import (
    CanonicalEntitlementAlertQueryService,
)


def _seed_audit(
    db: Session,
    *,
    feature_code: str = "feature-default",
) -> CanonicalEntitlementMutationAuditModel:
    audit = CanonicalEntitlementMutationAuditModel(
        operation="upsert_plan_feature_configuration",
        plan_id=1,
        plan_code_snapshot="premium",
        feature_code=feature_code,
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
    dedupe_suffix: str,
    alert_kind: str = "sla_overdue",
    delivery_status: str = "failed",
    delivery_channel: str = "webhook",
    feature_code_snapshot: str = "feature-default",
    plan_code_snapshot: str = "premium",
    actor_type_snapshot: str = "user",
    request_id: str | None = None,
    created_at: datetime | None = None,
) -> CanonicalEntitlementMutationAlertEventModel:
    event = CanonicalEntitlementMutationAlertEventModel(
        audit_id=audit_id,
        dedupe_key=f"audit:{audit_id}:{dedupe_suffix}",
        alert_kind=alert_kind,
        risk_level_snapshot="high",
        effective_review_status_snapshot="pending_review",
        feature_code_snapshot=feature_code_snapshot,
        plan_id_snapshot=1,
        plan_code_snapshot=plan_code_snapshot,
        actor_type_snapshot=actor_type_snapshot,
        actor_identifier_snapshot="user@test.com",
        sla_target_seconds_snapshot=14_400,
        due_at_snapshot=(created_at + timedelta(hours=4)) if created_at else None,
        age_seconds_snapshot=99_999,
        delivery_channel=delivery_channel,
        delivery_status=delivery_status,
        delivery_error=None if delivery_status == "sent" else "Connection refused",
        request_id=request_id,
        payload={"alert_kind": alert_kind, "audit_id": audit_id},
        created_at=created_at or datetime.now(timezone.utc),
        delivered_at=(created_at or datetime.now(timezone.utc))
        if delivery_status == "sent"
        else None,
    )
    db.add(event)
    db.flush()
    return event


def _seed_attempt(
    db: Session,
    *,
    alert_event_id: int,
    attempt_number: int,
    delivery_status: str,
) -> CanonicalEntitlementMutationAlertDeliveryAttemptModel:
    attempt = CanonicalEntitlementMutationAlertDeliveryAttemptModel(
        alert_event_id=alert_event_id,
        attempt_number=attempt_number,
        delivery_channel="webhook",
        delivery_status=delivery_status,
        delivery_error=None if delivery_status == "sent" else "Timeout",
        request_id=f"req-{attempt_number}",
        payload={"alert_event_id": alert_event_id, "attempt_number": attempt_number},
    )
    db.add(attempt)
    db.flush()
    return attempt


def _seed_rule_application(
    db: Session,
    *,
    event: CanonicalEntitlementMutationAlertEventModel,
) -> CanonicalEntitlementMutationAlertSuppressionApplicationModel:
    rule = CanonicalEntitlementMutationAlertSuppressionRuleModel(
        alert_kind=event.alert_kind,
        feature_code=event.feature_code_snapshot,
        plan_code=event.plan_code_snapshot,
        actor_type=event.actor_type_snapshot,
        is_active=True,
        suppression_key="known-noise",
        ops_comment="ignore this alert family",
    )
    db.add(rule)
    db.flush()
    application = CanonicalEntitlementMutationAlertSuppressionApplicationModel(
        alert_event_id=event.id,
        suppression_rule_id=rule.id,
        suppression_key=rule.suppression_key,
        application_mode="rule",
        application_reason=rule.ops_comment,
    )
    db.add(application)
    db.flush()
    return application


def test_list_alert_events_empty(db_session: Session) -> None:
    rows, total_count = CanonicalEntitlementAlertQueryService.list_alert_events(db_session)

    assert rows == []
    assert total_count == 0


def test_list_alert_events_returns_items_with_derived_fields(db_session: Session) -> None:
    older = datetime(2026, 3, 29, 10, 0, tzinfo=timezone.utc)
    newer = datetime(2026, 3, 29, 11, 0, tzinfo=timezone.utc)
    first_audit = _seed_audit(db_session, feature_code="feature-a")
    second_audit = _seed_audit(db_session, feature_code="feature-b")
    first_event = _seed_alert_event(
        db_session,
        audit_id=first_audit.id,
        dedupe_suffix="older",
        created_at=older,
        delivery_status="failed",
    )
    second_event = _seed_alert_event(
        db_session,
        audit_id=second_audit.id,
        dedupe_suffix="newer",
        created_at=newer,
        delivery_status="sent",
    )
    _seed_attempt(
        db_session,
        alert_event_id=first_event.id,
        attempt_number=1,
        delivery_status="failed",
    )
    _seed_attempt(
        db_session,
        alert_event_id=first_event.id,
        attempt_number=3,
        delivery_status="sent",
    )
    _seed_attempt(
        db_session,
        alert_event_id=first_event.id,
        attempt_number=2,
        delivery_status="failed",
    )

    rows, total_count = CanonicalEntitlementAlertQueryService.list_alert_events(db_session)

    assert total_count == 2
    assert [row.event.id for row in rows] == [second_event.id, first_event.id]
    assert rows[0].attempt_count == 0
    assert rows[0].last_attempt_number is None
    assert rows[0].last_attempt_status is None
    assert rows[1].attempt_count == 3
    assert rows[1].last_attempt_number == 3
    assert rows[1].last_attempt_status == "sent"


def test_list_alert_events_filter_by_delivery_status(db_session: Session) -> None:
    failed_audit = _seed_audit(db_session)
    sent_audit = _seed_audit(db_session)
    failed_event = _seed_alert_event(
        db_session,
        audit_id=failed_audit.id,
        dedupe_suffix="failed",
        delivery_status="failed",
    )
    _seed_alert_event(
        db_session,
        audit_id=sent_audit.id,
        dedupe_suffix="sent",
        delivery_status="sent",
    )

    rows, total_count = CanonicalEntitlementAlertQueryService.list_alert_events(
        db_session,
        delivery_status="failed",
    )

    assert total_count == 1
    assert [row.event.id for row in rows] == [failed_event.id]


def test_list_alert_events_filter_by_alert_kind(db_session: Session) -> None:
    first_audit = _seed_audit(db_session)
    second_audit = _seed_audit(db_session)
    _seed_alert_event(
        db_session,
        audit_id=first_audit.id,
        dedupe_suffix="due-soon",
        alert_kind="sla_due_soon",
    )
    matching_event = _seed_alert_event(
        db_session,
        audit_id=second_audit.id,
        dedupe_suffix="overdue",
        alert_kind="sla_overdue",
    )

    rows, total_count = CanonicalEntitlementAlertQueryService.list_alert_events(
        db_session,
        alert_kind="sla_overdue",
    )

    assert total_count == 1
    assert [row.event.id for row in rows] == [matching_event.id]


def test_list_alert_events_filter_by_feature_code(db_session: Session) -> None:
    first_audit = _seed_audit(db_session, feature_code="feature-a")
    second_audit = _seed_audit(db_session, feature_code="feature-b")
    matching_event = _seed_alert_event(
        db_session,
        audit_id=first_audit.id,
        dedupe_suffix="feature-a",
        feature_code_snapshot="feature-a",
    )
    _seed_alert_event(
        db_session,
        audit_id=second_audit.id,
        dedupe_suffix="feature-b",
        feature_code_snapshot="feature-b",
    )

    rows, total_count = CanonicalEntitlementAlertQueryService.list_alert_events(
        db_session,
        feature_code="feature-a",
    )

    assert total_count == 1
    assert [row.event.id for row in rows] == [matching_event.id]


def test_list_alert_events_computes_attempt_count_correctly(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    event = _seed_alert_event(db_session, audit_id=audit.id, dedupe_suffix="attempts")
    _seed_attempt(db_session, alert_event_id=event.id, attempt_number=1, delivery_status="failed")
    _seed_attempt(db_session, alert_event_id=event.id, attempt_number=2, delivery_status="failed")

    rows, _ = CanonicalEntitlementAlertQueryService.list_alert_events(db_session)

    assert rows[0].attempt_count == 2


def test_list_alert_events_computes_retryable_true_for_failed(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    event = _seed_alert_event(
        db_session,
        audit_id=audit.id,
        dedupe_suffix="retryable-failed",
        delivery_status="failed",
    )

    rows, _ = CanonicalEntitlementAlertQueryService.list_alert_events(
        db_session,
        audit_id=audit.id,
    )

    assert rows[0].event.id == event.id
    assert rows[0].event.delivery_status == "failed"


def test_list_alert_events_computes_retryable_false_for_sent(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    event = _seed_alert_event(
        db_session,
        audit_id=audit.id,
        dedupe_suffix="retryable-sent",
        delivery_status="sent",
    )

    rows, _ = CanonicalEntitlementAlertQueryService.list_alert_events(
        db_session,
        audit_id=audit.id,
    )

    assert rows[0].event.id == event.id
    assert rows[0].event.delivery_status == "sent"


def test_get_summary_counts_correctly(db_session: Session) -> None:
    audit_one = _seed_audit(db_session)
    audit_two = _seed_audit(db_session)
    audit_three = _seed_audit(db_session)
    _seed_alert_event(
        db_session,
        audit_id=audit_one.id,
        dedupe_suffix="failed-webhook",
        delivery_status="failed",
        delivery_channel="webhook",
        feature_code_snapshot="feature-a",
    )
    _seed_alert_event(
        db_session,
        audit_id=audit_two.id,
        dedupe_suffix="sent-log",
        delivery_status="sent",
        delivery_channel="log",
        feature_code_snapshot="feature-a",
    )
    _seed_alert_event(
        db_session,
        audit_id=audit_three.id,
        dedupe_suffix="sent-webhook",
        delivery_status="sent",
        delivery_channel="webhook",
        feature_code_snapshot="feature-b",
    )

    summary = CanonicalEntitlementAlertQueryService.get_summary(
        db_session,
        feature_code="feature-a",
    )

    assert summary.total_count == 2
    assert summary.failed_count == 1
    assert summary.sent_count == 1
    assert summary.retryable_count == 1
    assert summary.webhook_failed_count == 1
    assert summary.log_sent_count == 1


def test_list_alert_events_includes_rule_suppressed_handling(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    event = _seed_alert_event(
        db_session,
        audit_id=audit.id,
        dedupe_suffix="rule-suppressed",
        delivery_status="failed",
    )
    _seed_rule_application(db_session, event=event)
    db_session.commit()

    rows, total_count = CanonicalEntitlementAlertQueryService.list_alert_events(
        db_session,
        handling_status="suppressed",
    )

    assert total_count == 1
    assert [row.event.id for row in rows] == [event.id]


def test_summary_counts_rule_suppressed_alerts(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    rule_suppressed_event = _seed_alert_event(
        db_session,
        audit_id=audit.id,
        dedupe_suffix="rule-suppressed",
        delivery_status="failed",
    )
    manual_resolved_event = _seed_alert_event(
        db_session,
        audit_id=audit.id,
        dedupe_suffix="manual-resolved",
        delivery_status="failed",
        feature_code_snapshot="feature-other",
    )
    _seed_rule_application(db_session, event=rule_suppressed_event)
    db_session.add(
        CanonicalEntitlementMutationAlertHandlingModel(
            alert_event_id=manual_resolved_event.id,
            handling_status="resolved",
            handled_by_user_id=1,
        )
    )
    db_session.commit()

    summary = CanonicalEntitlementAlertQueryService.get_summary(db_session)

    assert summary.suppressed_count == 1
    assert summary.resolved_count == 1
    assert summary.retryable_count == 0


def test_pending_retry_excludes_rule_suppressed_alerts(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    matching_event = _seed_alert_event(
        db_session,
        audit_id=audit.id,
        dedupe_suffix="matching",
        delivery_status="failed",
    )
    retryable_event = _seed_alert_event(
        db_session,
        audit_id=audit.id,
        dedupe_suffix="retryable",
        delivery_status="failed",
        feature_code_snapshot="feature-retryable",
    )
    _seed_rule_application(db_session, event=matching_event)
    db_session.commit()

    rows, total_count = CanonicalEntitlementAlertQueryService.list_alert_events(
        db_session,
        handling_status="pending_retry",
    )

    assert total_count == 1
    assert [row.event.id for row in rows] == [retryable_event.id]
