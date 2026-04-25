from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.infra.db.base import Base
from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)
from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.entitlement_mutation.alert.handling import (
    CanonicalEntitlementMutationAlertHandlingModel,
)
from app.infra.db.session import SessionLocal, engine
from app.services.canonical_entitlement.alert.handling import (
    CanonicalEntitlementAlertHandlingService,
)


def _setup() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _seed_audit(db) -> CanonicalEntitlementMutationAuditModel:
    audit = CanonicalEntitlementMutationAuditModel(
        occurred_at=datetime.now(timezone.utc),
        operation="upsert_plan_feature_configuration",
        plan_id=1,
        plan_code_snapshot="basic",
        feature_code="astrologer_chat",
        actor_type="script",
        actor_identifier="test.py",
        source_origin="manual",
        before_payload={},
        after_payload={"is_enabled": True, "access_mode": "quota", "quotas": []},
    )
    db.add(audit)
    db.flush()
    return audit


def _seed_alert_event(db) -> CanonicalEntitlementMutationAlertEventModel:
    audit = _seed_audit(db)
    event = CanonicalEntitlementMutationAlertEventModel(
        audit_id=audit.id,
        dedupe_key=f"audit:{audit.id}:review:pending_review:sla:overdue:failed",
        alert_kind="sla_overdue",
        risk_level_snapshot="high",
        effective_review_status_snapshot="pending_review",
        feature_code_snapshot="astrologer_chat",
        plan_id_snapshot=1,
        plan_code_snapshot="basic",
        actor_type_snapshot="script",
        actor_identifier_snapshot="test.py",
        age_seconds_snapshot=3600,
        sla_target_seconds_snapshot=14400,
        delivery_channel="webhook",
        delivery_status="failed",
        delivery_error="timeout",
        payload={"audit_id": audit.id},
    )
    db.add(event)
    db.flush()
    return event


def test_upsert_handling_creates_new_record_when_none_exists() -> None:
    _setup()
    with SessionLocal() as db:
        event = _seed_alert_event(db)

        handling = CanonicalEntitlementAlertHandlingService.upsert_handling(
            db,
            alert_event_id=event.id,
            handling_status="suppressed",
            handled_by_user_id=42,
            ops_comment="Known noise",
            suppression_key="duplicate",
        )
        db.commit()

        assert handling.alert_event_id == event.id
        assert handling.handling_status == "suppressed"
        assert handling.handled_by_user_id == 42
        assert handling.ops_comment == "Known noise"
        assert handling.suppression_key == "duplicate"


def test_upsert_handling_updates_existing_record() -> None:
    _setup()
    with SessionLocal() as db:
        event = _seed_alert_event(db)
        CanonicalEntitlementAlertHandlingService.upsert_handling(
            db,
            alert_event_id=event.id,
            handling_status="suppressed",
            handled_by_user_id=1,
            ops_comment="noise",
            suppression_key="dup",
        )
        db.commit()

        updated = CanonicalEntitlementAlertHandlingService.upsert_handling(
            db,
            alert_event_id=event.id,
            handling_status="resolved",
            handled_by_user_id=99,
            ops_comment="fixed",
            suppression_key=None,
        )
        db.commit()

        assert updated.handling_status == "resolved"
        assert updated.handled_by_user_id == 99
        assert updated.ops_comment == "fixed"
        assert updated.suppression_key is None

    with SessionLocal() as db:
        rows = db.execute(select(CanonicalEntitlementMutationAlertHandlingModel)).scalars().all()
        assert len(rows) == 1
        assert rows[0].handling_status == "resolved"


def test_upsert_handling_raises_404_when_alert_event_not_found() -> None:
    _setup()
    with SessionLocal() as db:
        with pytest.raises(HTTPException) as exc_info:
            CanonicalEntitlementAlertHandlingService.upsert_handling(
                db,
                alert_event_id=99999,
                handling_status="suppressed",
                handled_by_user_id=1,
                ops_comment=None,
                suppression_key=None,
            )

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "alert event not found"


def test_upsert_handling_does_not_commit() -> None:
    db = MagicMock()
    db.get.return_value = SimpleNamespace()
    db.execute.return_value.scalar_one_or_none.return_value = None

    CanonicalEntitlementAlertHandlingService.upsert_handling(
        db,
        alert_event_id=1,
        handling_status="suppressed",
        handled_by_user_id=1,
        ops_comment=None,
        suppression_key=None,
    )

    db.commit.assert_not_called()


def test_upsert_handling_flushes_session() -> None:
    db = MagicMock()
    db.get.return_value = SimpleNamespace()
    db.execute.return_value.scalar_one_or_none.return_value = None

    CanonicalEntitlementAlertHandlingService.upsert_handling(
        db,
        alert_event_id=1,
        handling_status="suppressed",
        handled_by_user_id=1,
        ops_comment=None,
        suppression_key=None,
    )

    assert db.flush.call_count >= 1


def test_upsert_handling_suppressed_sets_correct_status() -> None:
    _setup()
    with SessionLocal() as db:
        event = _seed_alert_event(db)

        handling = CanonicalEntitlementAlertHandlingService.upsert_handling(
            db,
            alert_event_id=event.id,
            handling_status="suppressed",
            handled_by_user_id=None,
            ops_comment=None,
            suppression_key="known",
        )

        assert handling.handling_status == "suppressed"


def test_upsert_handling_resolved_sets_correct_status() -> None:
    _setup()
    with SessionLocal() as db:
        event = _seed_alert_event(db)

        handling = CanonicalEntitlementAlertHandlingService.upsert_handling(
            db,
            alert_event_id=event.id,
            handling_status="resolved",
            handled_by_user_id=None,
            ops_comment=None,
            suppression_key=None,
        )

        assert handling.handling_status == "resolved"


def test_upsert_handling_stores_ops_comment_and_suppression_key() -> None:
    _setup()
    with SessionLocal() as db:
        event = _seed_alert_event(db)

        handling = CanonicalEntitlementAlertHandlingService.upsert_handling(
            db,
            alert_event_id=event.id,
            handling_status="suppressed",
            handled_by_user_id=7,
            ops_comment="Escalated to provider",
            suppression_key="provider-incident",
        )

        assert handling.ops_comment == "Escalated to provider"
        assert handling.suppression_key == "provider-incident"
