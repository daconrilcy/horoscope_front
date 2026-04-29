from __future__ import annotations

from datetime import timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.entitlement_mutation.alert.handling import (
    CanonicalEntitlementMutationAlertHandlingModel,
)
from app.infra.db.models.entitlement_mutation.alert.handling_event import (
    CanonicalEntitlementMutationAlertHandlingEventModel,
)
from app.services.canonical_entitlement.alert.handling import (
    CanonicalEntitlementAlertHandlingService,
)
from app.tests.helpers.db_session import open_app_test_db_session
from app.tests.unit.canonical_entitlement_alert_helpers import (
    seed_entitlement_alert_event,
    setup_entitlement_alert_schema,
)


def _list_events(
    db: Session,
) -> list[CanonicalEntitlementMutationAlertHandlingEventModel]:
    return (
        db.execute(
            select(CanonicalEntitlementMutationAlertHandlingEventModel).order_by(
                CanonicalEntitlementMutationAlertHandlingEventModel.id.asc()
            )
        )
        .scalars()
        .all()
    )


def _as_utc_naive(value: object) -> object:
    if not hasattr(value, "tzinfo"):
        return value
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def test_append_handling_event_inserts_record() -> None:
    setup_entitlement_alert_schema()
    with open_app_test_db_session() as db:
        alert_event = seed_entitlement_alert_event(db)

        CanonicalEntitlementAlertHandlingService.append_handling_event(
            db,
            alert_event_id=alert_event.id,
            handling_status="suppressed",
            handled_by_user_id=7,
            handled_at=None,
            ops_comment="Known noise",
            suppression_key="duplicate",
            request_id="rid-append",
        )
        db.commit()

        events = _list_events(db)
        assert len(events) == 1
        assert events[0].alert_event_id == alert_event.id
        assert events[0].event_type == "updated"
        assert events[0].handling_status == "suppressed"
        assert events[0].handled_by_user_id == 7
        assert events[0].ops_comment == "Known noise"
        assert events[0].suppression_key == "duplicate"
        assert events[0].request_id == "rid-append"


def test_upsert_handling_creates_event_on_insert() -> None:
    setup_entitlement_alert_schema()
    with open_app_test_db_session() as db:
        alert_event = seed_entitlement_alert_event(db)

        CanonicalEntitlementAlertHandlingService.upsert_handling(
            db,
            alert_event_id=alert_event.id,
            handling_status="suppressed",
            handled_by_user_id=1,
            ops_comment="First triage",
            suppression_key="noise",
        )
        db.commit()

        events = _list_events(db)
        assert len(events) == 1
        assert events[0].event_type == "created"
        assert events[0].handling_status == "suppressed"


def test_upsert_handling_creates_event_on_status_change() -> None:
    setup_entitlement_alert_schema()
    with open_app_test_db_session() as db:
        alert_event = seed_entitlement_alert_event(db)
        CanonicalEntitlementAlertHandlingService.upsert_handling(
            db,
            alert_event_id=alert_event.id,
            handling_status="suppressed",
            handled_by_user_id=1,
            ops_comment="noise",
            suppression_key="dup",
        )
        CanonicalEntitlementAlertHandlingService.upsert_handling(
            db,
            alert_event_id=alert_event.id,
            handling_status="resolved",
            handled_by_user_id=2,
            ops_comment="fixed",
            suppression_key=None,
        )
        db.commit()

        events = _list_events(db)
        assert len(events) == 2
        assert [event.event_type for event in events] == ["created", "updated"]
        assert [event.handling_status for event in events] == ["suppressed", "resolved"]


def test_upsert_handling_no_event_when_no_change() -> None:
    setup_entitlement_alert_schema()
    with open_app_test_db_session() as db:
        alert_event = seed_entitlement_alert_event(db)
        first = CanonicalEntitlementAlertHandlingService.upsert_handling(
            db,
            alert_event_id=alert_event.id,
            handling_status="suppressed",
            handled_by_user_id=1,
            ops_comment="noise",
            suppression_key="dup",
        )
        first_handled_at = first.handled_at

        second = CanonicalEntitlementAlertHandlingService.upsert_handling(
            db,
            alert_event_id=alert_event.id,
            handling_status="suppressed",
            handled_by_user_id=99,
            ops_comment="noise",
            suppression_key="dup",
        )
        db.commit()

        events = _list_events(db)
        handling = db.execute(
            select(CanonicalEntitlementMutationAlertHandlingModel).where(
                CanonicalEntitlementMutationAlertHandlingModel.alert_event_id == alert_event.id
            )
        ).scalar_one()
        assert second.id == first.id
        assert len(events) == 1
        assert _as_utc_naive(handling.handled_at) == _as_utc_naive(first_handled_at)
        assert handling.handled_by_user_id == 1


def test_upsert_handling_creates_event_when_ops_comment_changes() -> None:
    setup_entitlement_alert_schema()
    with open_app_test_db_session() as db:
        alert_event = seed_entitlement_alert_event(db)
        CanonicalEntitlementAlertHandlingService.upsert_handling(
            db,
            alert_event_id=alert_event.id,
            handling_status="suppressed",
            handled_by_user_id=1,
            ops_comment="noise",
            suppression_key="dup",
        )
        CanonicalEntitlementAlertHandlingService.upsert_handling(
            db,
            alert_event_id=alert_event.id,
            handling_status="suppressed",
            handled_by_user_id=1,
            ops_comment="different comment",
            suppression_key="dup",
        )
        db.commit()

        events = _list_events(db)
        assert len(events) == 2
        assert events[-1].ops_comment == "different comment"


def test_upsert_handling_creates_event_when_suppression_key_changes() -> None:
    setup_entitlement_alert_schema()
    with open_app_test_db_session() as db:
        alert_event = seed_entitlement_alert_event(db)
        CanonicalEntitlementAlertHandlingService.upsert_handling(
            db,
            alert_event_id=alert_event.id,
            handling_status="suppressed",
            handled_by_user_id=1,
            ops_comment="noise",
            suppression_key="dup",
        )
        CanonicalEntitlementAlertHandlingService.upsert_handling(
            db,
            alert_event_id=alert_event.id,
            handling_status="suppressed",
            handled_by_user_id=1,
            ops_comment="noise",
            suppression_key="provider-incident",
        )
        db.commit()

        events = _list_events(db)
        assert len(events) == 2
        assert events[-1].suppression_key == "provider-incident"


def test_upsert_handling_stores_request_id_in_event() -> None:
    setup_entitlement_alert_schema()
    with open_app_test_db_session() as db:
        alert_event = seed_entitlement_alert_event(db)

        CanonicalEntitlementAlertHandlingService.upsert_handling(
            db,
            alert_event_id=alert_event.id,
            handling_status="resolved",
            handled_by_user_id=1,
            ops_comment="done",
            suppression_key=None,
            request_id="rid-history",
        )
        db.commit()

        events = _list_events(db)
        assert len(events) == 1
        assert events[0].request_id == "rid-history"


def test_upsert_handling_flushes_event_without_commit() -> None:
    db = MagicMock()
    db.get.return_value = SimpleNamespace()
    db.execute.return_value.scalar_one_or_none.return_value = None

    CanonicalEntitlementAlertHandlingService.upsert_handling(
        db,
        alert_event_id=1,
        handling_status="suppressed",
        handled_by_user_id=1,
        ops_comment="noise",
        suppression_key="dup",
        request_id="rid-flush",
    )

    assert db.flush.call_count >= 1
    db.commit.assert_not_called()
