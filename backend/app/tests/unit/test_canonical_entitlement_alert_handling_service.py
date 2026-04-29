from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy import select

from app.infra.db.models.entitlement_mutation.alert.handling import (
    CanonicalEntitlementMutationAlertHandlingModel,
)
from app.services.canonical_entitlement.alert.handling import (
    AlertEventNotFoundError,
    CanonicalEntitlementAlertHandlingService,
)
from app.tests.helpers.db_session import open_app_test_db_session
from app.tests.unit.canonical_entitlement_alert_helpers import (
    seed_entitlement_alert_event,
    setup_entitlement_alert_schema,
)


def test_upsert_handling_creates_new_record_when_none_exists() -> None:
    setup_entitlement_alert_schema()
    with open_app_test_db_session() as db:
        event = seed_entitlement_alert_event(db)

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
    setup_entitlement_alert_schema()
    with open_app_test_db_session() as db:
        event = seed_entitlement_alert_event(db)
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

    with open_app_test_db_session() as db:
        rows = db.execute(select(CanonicalEntitlementMutationAlertHandlingModel)).scalars().all()
        assert len(rows) == 1
        assert rows[0].handling_status == "resolved"


def test_upsert_handling_raises_404_when_alert_event_not_found() -> None:
    setup_entitlement_alert_schema()
    with open_app_test_db_session() as db:
        with pytest.raises(AlertEventNotFoundError) as exc_info:
            CanonicalEntitlementAlertHandlingService.upsert_handling(
                db,
                alert_event_id=99999,
                handling_status="suppressed",
                handled_by_user_id=1,
                ops_comment=None,
                suppression_key=None,
            )

        assert str(exc_info.value) == "alert event not found"


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
    setup_entitlement_alert_schema()
    with open_app_test_db_session() as db:
        event = seed_entitlement_alert_event(db)

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
    setup_entitlement_alert_schema()
    with open_app_test_db_session() as db:
        event = seed_entitlement_alert_event(db)

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
    setup_entitlement_alert_schema()
    with open_app_test_db_session() as db:
        event = seed_entitlement_alert_event(db)

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
