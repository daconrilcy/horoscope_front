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
from app.infra.db.models.entitlement_mutation.alert.handling import (
    CanonicalEntitlementMutationAlertHandlingModel,
)
from app.services.canonical_entitlement_alert_batch_handling_service import (
    CanonicalEntitlementAlertBatchHandlingService,
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
    effective_created_at = created_at or datetime.now(timezone.utc)
    event = CanonicalEntitlementMutationAlertEventModel(
        audit_id=audit_id,
        dedupe_key=(
            f"audit:{audit_id}:{alert_kind}:{feature_code}:{delivery_status}:"
            f"{effective_created_at.isoformat()}"
        ),
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
        created_at=effective_created_at,
    )
    db.add(event)
    db.flush()
    return event


def _seed_handling(
    db: Session,
    *,
    alert_event_id: int,
    handling_status: str,
    ops_comment: str | None = None,
    suppression_key: str | None = None,
) -> CanonicalEntitlementMutationAlertHandlingModel:
    handling = CanonicalEntitlementMutationAlertHandlingModel(
        alert_event_id=alert_event_id,
        handling_status=handling_status,
        handled_by_user_id=42,
        handled_at=datetime(2026, 3, 29, 10, 0, tzinfo=timezone.utc),
        ops_comment=ops_comment,
        suppression_key=suppression_key,
    )
    db.add(handling)
    db.flush()
    return handling


def test_batch_handle_returns_correct_candidate_count(db_session: Session) -> None:
    first_audit = _seed_audit(db_session)
    second_audit = _seed_audit(db_session)
    first = _seed_alert_event(db_session, audit_id=first_audit.id, delivery_status="failed")
    second = _seed_alert_event(db_session, audit_id=second_audit.id, delivery_status="sent")

    result = CanonicalEntitlementAlertBatchHandlingService.batch_handle(
        db_session,
        limit=10,
        handling_status="suppressed",
        dry_run=True,
    )

    assert result.candidate_count == 2
    assert result.handled_count == 2
    assert result.skipped_count == 0
    assert result.alert_event_ids == [first.id, second.id]


def test_batch_handle_dry_run_does_not_call_upsert(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    first = _seed_alert_event(db_session, audit_id=audit.id)
    second = _seed_alert_event(db_session, audit_id=audit.id)
    _seed_handling(
        db_session,
        alert_event_id=first.id,
        handling_status="suppressed",
        ops_comment="known-noise",
        suppression_key="incident-1",
    )

    with patch(
        "app.services.canonical_entitlement_alert_batch_handling_service."
        "CanonicalEntitlementAlertHandlingService.upsert_handling"
    ) as upsert_mock:
        result = CanonicalEntitlementAlertBatchHandlingService.batch_handle(
            db_session,
            limit=10,
            handling_status="suppressed",
            ops_comment="known-noise",
            suppression_key="incident-1",
            dry_run=True,
        )

    upsert_mock.assert_not_called()
    assert result.handled_count == 1
    assert result.skipped_count == 1
    assert result.alert_event_ids == [first.id, second.id]


def test_batch_handle_calls_upsert_for_each_candidate(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    first = _seed_alert_event(db_session, audit_id=audit.id)
    second = _seed_alert_event(db_session, audit_id=audit.id)

    with patch(
        "app.services.canonical_entitlement_alert_batch_handling_service."
        "CanonicalEntitlementAlertHandlingService.upsert_handling"
    ) as upsert_mock:
        result = CanonicalEntitlementAlertBatchHandlingService.batch_handle(
            db_session,
            limit=10,
            handling_status="resolved",
            dry_run=False,
        )

    assert upsert_mock.call_count == 2
    assert result.handled_count == 2
    assert result.skipped_count == 0
    assert result.alert_event_ids == [first.id, second.id]


def test_batch_handle_skips_already_handled_with_same_state(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    event = _seed_alert_event(db_session, audit_id=audit.id)
    _seed_handling(
        db_session,
        alert_event_id=event.id,
        handling_status="suppressed",
        ops_comment="known-noise",
        suppression_key="incident-1",
    )

    with patch(
        "app.services.canonical_entitlement_alert_batch_handling_service."
        "CanonicalEntitlementAlertHandlingService.upsert_handling"
    ) as upsert_mock:
        result = CanonicalEntitlementAlertBatchHandlingService.batch_handle(
            db_session,
            limit=10,
            handling_status="suppressed",
            ops_comment="known-noise",
            suppression_key="incident-1",
        )

    upsert_mock.assert_not_called()
    assert result.handled_count == 0
    assert result.skipped_count == 1


def test_batch_handle_processes_when_status_differs(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    event = _seed_alert_event(db_session, audit_id=audit.id)
    _seed_handling(
        db_session,
        alert_event_id=event.id,
        handling_status="suppressed",
        ops_comment="known-noise",
        suppression_key="incident-1",
    )

    with patch(
        "app.services.canonical_entitlement_alert_batch_handling_service."
        "CanonicalEntitlementAlertHandlingService.upsert_handling"
    ) as upsert_mock:
        result = CanonicalEntitlementAlertBatchHandlingService.batch_handle(
            db_session,
            limit=10,
            handling_status="resolved",
            ops_comment="known-noise",
            suppression_key="incident-1",
        )

    upsert_mock.assert_called_once()
    assert result.handled_count == 1
    assert result.skipped_count == 0


def test_batch_handle_processes_when_comment_differs(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    event = _seed_alert_event(db_session, audit_id=audit.id)
    _seed_handling(
        db_session,
        alert_event_id=event.id,
        handling_status="suppressed",
        ops_comment="old-comment",
        suppression_key="incident-1",
    )

    with patch(
        "app.services.canonical_entitlement_alert_batch_handling_service."
        "CanonicalEntitlementAlertHandlingService.upsert_handling"
    ) as upsert_mock:
        result = CanonicalEntitlementAlertBatchHandlingService.batch_handle(
            db_session,
            limit=10,
            handling_status="suppressed",
            ops_comment="new-comment",
            suppression_key="incident-1",
        )

    upsert_mock.assert_called_once()
    assert result.handled_count == 1
    assert result.skipped_count == 0


def test_batch_handle_passes_request_id_to_upsert(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    _seed_alert_event(db_session, audit_id=audit.id)
    _seed_alert_event(db_session, audit_id=audit.id)

    with patch(
        "app.services.canonical_entitlement_alert_batch_handling_service."
        "CanonicalEntitlementAlertHandlingService.upsert_handling"
    ) as upsert_mock:
        CanonicalEntitlementAlertBatchHandlingService.batch_handle(
            db_session,
            limit=10,
            handling_status="resolved",
            request_id="rid-batch-handle",
        )

    assert upsert_mock.call_count == 2
    for call in upsert_mock.call_args_list:
        assert call.kwargs["request_id"] == "rid-batch-handle"


def test_batch_handle_passes_handled_by_user_id(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    _seed_alert_event(db_session, audit_id=audit.id)

    with patch(
        "app.services.canonical_entitlement_alert_batch_handling_service."
        "CanonicalEntitlementAlertHandlingService.upsert_handling"
    ) as upsert_mock:
        CanonicalEntitlementAlertBatchHandlingService.batch_handle(
            db_session,
            limit=10,
            handling_status="suppressed",
            handled_by_user_id=77,
        )

    upsert_mock.assert_called_once()
    assert upsert_mock.call_args.kwargs["handled_by_user_id"] == 77


def test_batch_handle_limit_is_respected(db_session: Session) -> None:
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
        "app.services.canonical_entitlement_alert_batch_handling_service."
        "CanonicalEntitlementAlertHandlingService.upsert_handling"
    ) as upsert_mock:
        result = CanonicalEntitlementAlertBatchHandlingService.batch_handle(
            db_session,
            limit=2,
            handling_status="suppressed",
        )

    assert upsert_mock.call_count == 2
    assert result.candidate_count == 2
    assert result.alert_event_ids == [first.id, second.id]


def test_batch_handle_does_not_commit(db_session: Session) -> None:
    audit = _seed_audit(db_session)
    _seed_alert_event(db_session, audit_id=audit.id)

    with patch.object(db_session, "commit") as commit_mock:
        CanonicalEntitlementAlertBatchHandlingService.batch_handle(
            db_session,
            limit=10,
            handling_status="resolved",
            dry_run=True,
        )

    commit_mock.assert_not_called()
