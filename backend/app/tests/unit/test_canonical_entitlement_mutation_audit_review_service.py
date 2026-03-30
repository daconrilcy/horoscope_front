from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from sqlalchemy import select

from app.infra.db.base import Base
from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)
from app.infra.db.models.canonical_entitlement_mutation_audit_review import (
    CanonicalEntitlementMutationAuditReviewModel,
)
from app.infra.db.models.canonical_entitlement_mutation_audit_review_event import (
    CanonicalEntitlementMutationAuditReviewEventModel,
)
from app.infra.db.session import SessionLocal, engine
from app.services.canonical_entitlement_mutation_audit_review_service import (
    AuditNotFoundError,
    CanonicalEntitlementMutationAuditReviewService,
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


def test_upsert_creates_review_when_none_exists() -> None:
    _setup()
    with SessionLocal() as db:
        audit = _seed_audit(db)
        db.flush()

        review = CanonicalEntitlementMutationAuditReviewService.upsert_review(
            db,
            audit_id=audit.id,
            review_status="acknowledged",
            reviewed_by_user_id=42,
            review_comment="Changement attendu",
            incident_key="INC-001",
        )
        db.commit()

        assert review.audit_id == audit.id
        assert review.review_status == "acknowledged"
        assert review.reviewed_by_user_id == 42
        assert review.review_comment == "Changement attendu"
        assert review.incident_key == "INC-001"
        assert isinstance(review.reviewed_at, datetime)


def test_upsert_updates_review_when_already_exists() -> None:
    _setup()
    with SessionLocal() as db:
        audit = _seed_audit(db)

        # Première revue
        CanonicalEntitlementMutationAuditReviewService.upsert_review(
            db,
            audit_id=audit.id,
            review_status="acknowledged",
            reviewed_by_user_id=42,
            review_comment="Premier commentaire",
            incident_key=None,
        )
        db.commit()

        # Mise à jour
        review = CanonicalEntitlementMutationAuditReviewService.upsert_review(
            db,
            audit_id=audit.id,
            review_status="closed",
            reviewed_by_user_id=99,
            review_comment="Clôturé",
            incident_key="INC-002",
        )
        db.commit()

        assert review.review_status == "closed"
        assert review.reviewed_by_user_id == 99
        assert review.review_comment == "Clôturé"
        assert review.incident_key == "INC-002"

    # Vérifier qu'il n'y a qu'une seule ligne en DB
    with SessionLocal() as db:
        result = db.execute(select(CanonicalEntitlementMutationAuditReviewModel))
        rows = result.scalars().all()
        assert len(rows) == 1
        assert rows[0].review_status == "closed"


def test_upsert_updates_reviewed_at_on_update() -> None:
    _setup()
    with SessionLocal() as db:
        audit = _seed_audit(db)

        r1 = CanonicalEntitlementMutationAuditReviewService.upsert_review(
            db,
            audit_id=audit.id,
            review_status="acknowledged",
            reviewed_by_user_id=1,
            review_comment=None,
            incident_key=None,
        )
        db.commit()
        first_reviewed_at = r1.reviewed_at

        # Petite pause pour s'assurer que le timestamp change
        import time

        time.sleep(0.01)

        r2 = CanonicalEntitlementMutationAuditReviewService.upsert_review(
            db,
            audit_id=audit.id,
            review_status="closed",
            reviewed_by_user_id=1,
            review_comment=None,
            incident_key=None,
        )
        db.commit()

        assert r2.reviewed_at >= first_reviewed_at


def test_upsert_raises_404_when_audit_not_found() -> None:
    _setup()
    with SessionLocal() as db:
        try:
            CanonicalEntitlementMutationAuditReviewService.upsert_review(
                db,
                audit_id=99999,
                review_status="acknowledged",
                reviewed_by_user_id=1,
                review_comment=None,
                incident_key=None,
            )
            assert False, "Expected AuditNotFoundError"
        except AuditNotFoundError as e:
            assert e.audit_id == 99999


def test_upsert_recovers_from_concurrent_insert_race() -> None:
    _setup()
    with SessionLocal() as db:
        audit = _seed_audit(db)
        db.commit()
        audit_id = audit.id

    with SessionLocal() as db:
        original_execute = db.execute
        injected_competing_review = False

        def execute_with_concurrent_insert(statement, *args, **kwargs):
            nonlocal injected_competing_review
            result = original_execute(statement, *args, **kwargs)
            statement_text = str(statement)
            should_inject_race = (
                not injected_competing_review
                and "canonical_entitlement_mutation_audit_reviews" in statement_text
            )
            if should_inject_race:
                with SessionLocal() as competing_db:
                    competing_db.add(
                        CanonicalEntitlementMutationAuditReviewModel(
                            audit_id=audit_id,
                            review_status="expected",
                            reviewed_by_user_id=5,
                            reviewed_at=datetime.now(timezone.utc),
                            review_comment="Competing write",
                            incident_key="INC-RACE",
                        )
                    )
                    competing_db.commit()
                injected_competing_review = True
            return result

        db.execute = execute_with_concurrent_insert  # type: ignore[method-assign]

        review = CanonicalEntitlementMutationAuditReviewService.upsert_review(
            db,
            audit_id=audit_id,
            review_status="closed",
            reviewed_by_user_id=99,
            review_comment="Resolved after race",
            incident_key="INC-RESOLVED",
        )
        db.commit()

        assert review.review_status == "closed"
        assert review.reviewed_by_user_id == 99
        assert review.review_comment == "Resolved after race"
        assert review.incident_key == "INC-RESOLVED"

    with SessionLocal() as db:
        rows = db.execute(select(CanonicalEntitlementMutationAuditReviewModel)).scalars().all()
        assert len(rows) == 1
        assert rows[0].review_status == "closed"
        assert rows[0].review_comment == "Resolved after race"


def test_upsert_concurrent_first_review_noop_creates_no_event() -> None:
    _setup()
    with SessionLocal() as db:
        audit = _seed_audit(db)
        db.commit()
        audit_id = audit.id

    with SessionLocal() as db:
        original_execute = db.execute
        injected_competing_review = False

        def execute_with_concurrent_insert(statement, *args, **kwargs):
            nonlocal injected_competing_review
            result = original_execute(statement, *args, **kwargs)
            statement_text = str(statement)
            should_inject_race = (
                not injected_competing_review
                and "canonical_entitlement_mutation_audit_reviews" in statement_text
            )
            if should_inject_race:
                with SessionLocal() as competing_db:
                    competing_db.add(
                        CanonicalEntitlementMutationAuditReviewModel(
                            audit_id=audit_id,
                            review_status="acknowledged",
                            reviewed_by_user_id=7,
                            reviewed_at=datetime.now(timezone.utc),
                            review_comment="Same values",
                            incident_key="INC-SAME",
                        )
                    )
                    competing_db.commit()
                injected_competing_review = True
            return result

        db.execute = execute_with_concurrent_insert  # type: ignore[method-assign]

        review = CanonicalEntitlementMutationAuditReviewService.upsert_review(
            db,
            audit_id=audit_id,
            review_status="acknowledged",
            reviewed_by_user_id=99,
            review_comment="Same values",
            incident_key="INC-SAME",
        )
        db.commit()

        assert review.reviewed_by_user_id == 7
        assert review.review_comment == "Same values"
        assert review.incident_key == "INC-SAME"

    with SessionLocal() as db:
        reviews = db.execute(select(CanonicalEntitlementMutationAuditReviewModel)).scalars().all()
        events = (
            db.execute(select(CanonicalEntitlementMutationAuditReviewEventModel)).scalars().all()
        )
        assert len(reviews) == 1
        assert len(events) == 0


def test_upsert_creates_event_on_first_review() -> None:
    _setup()
    with SessionLocal() as db:
        audit = _seed_audit(db)
        db.flush()
        audit_id = audit.id

        CanonicalEntitlementMutationAuditReviewService.upsert_review(
            db,
            audit_id=audit_id,
            review_status="acknowledged",
            reviewed_by_user_id=42,
            review_comment="First review",
            incident_key="INC-001",
            request_id="req-123",
        )
        db.commit()

    with SessionLocal() as db:
        events = (
            db.execute(select(CanonicalEntitlementMutationAuditReviewEventModel)).scalars().all()
        )
        assert len(events) == 1
        assert events[0].audit_id == audit_id
        assert events[0].previous_review_status is None
        assert events[0].new_review_status == "acknowledged"
        assert events[0].new_review_comment == "First review"
        assert events[0].new_incident_key == "INC-001"
        assert events[0].request_id == "req-123"


def test_upsert_creates_event_on_status_change() -> None:
    _setup()
    with SessionLocal() as db:
        audit = _seed_audit(db)
        db.flush()
        audit_id = audit.id

        # First review
        CanonicalEntitlementMutationAuditReviewService.upsert_review(
            db,
            audit_id=audit_id,
            review_status="investigating",
            reviewed_by_user_id=1,
            review_comment="Investigating...",
            incident_key=None,
        )
        db.commit()

        # Second review (change)
        CanonicalEntitlementMutationAuditReviewService.upsert_review(
            db,
            audit_id=audit_id,
            review_status="closed",
            reviewed_by_user_id=2,
            review_comment="Closed finally",
            incident_key="INC-999",
        )
        db.commit()

    with SessionLocal() as db:
        events = (
            db.execute(
                select(CanonicalEntitlementMutationAuditReviewEventModel).order_by(
                    CanonicalEntitlementMutationAuditReviewEventModel.occurred_at.asc()
                )
            )
            .scalars()
            .all()
        )
        assert len(events) == 2
        assert events[1].previous_review_status == "investigating"
        assert events[1].new_review_status == "closed"
        assert events[1].previous_review_comment == "Investigating..."
        assert events[1].new_review_comment == "Closed finally"
        assert events[1].previous_incident_key is None
        assert events[1].new_incident_key == "INC-999"


def test_upsert_no_event_on_noop() -> None:
    _setup()
    with SessionLocal() as db:
        audit = _seed_audit(db)
        db.flush()
        audit_id = audit.id

        # First review
        r1 = CanonicalEntitlementMutationAuditReviewService.upsert_review(
            db,
            audit_id=audit_id,
            review_status="acknowledged",
            reviewed_by_user_id=1,
            review_comment="Comment",
            incident_key="INC",
        )
        db.commit()
        first_reviewed_at = r1.reviewed_at

        # No-op review
        r2 = CanonicalEntitlementMutationAuditReviewService.upsert_review(
            db,
            audit_id=audit_id,
            review_status="acknowledged",
            reviewed_by_user_id=99,  # User change but fields same -> NO-OP
            review_comment="Comment",
            incident_key="INC",
        )
        db.commit()

        assert r2.reviewed_at == first_reviewed_at

    with SessionLocal() as db:
        events = (
            db.execute(select(CanonicalEntitlementMutationAuditReviewEventModel)).scalars().all()
        )
        assert len(events) == 1


def test_upsert_event_carries_request_id() -> None:
    _setup()
    with SessionLocal() as db:
        audit = _seed_audit(db)
        db.flush()
        audit_id = audit.id

        CanonicalEntitlementMutationAuditReviewService.upsert_review(
            db,
            audit_id=audit_id,
            review_status="closed",
            reviewed_by_user_id=1,
            review_comment=None,
            incident_key=None,
            request_id="trace-abc-123",
        )
        db.commit()

    with SessionLocal() as db:
        event = db.execute(select(CanonicalEntitlementMutationAuditReviewEventModel)).scalar_one()
        assert event.request_id == "trace-abc-123"


def test_upsert_transactional_rollback() -> None:
    """Si db.flush() sur l'event lève une exception, la session peut rollback."""
    db = MagicMock()
    audit = MagicMock()
    audit.id = 1
    db.get.return_value = audit

    # Pas de revue existante
    db.execute.return_value.scalar_one_or_none.return_value = None

    # Simuler un flush qui échoue sur le 2ème appel (après l'insertion de l'événement)
    flush_call_count = {"n": 0}

    def flush_side_effect():
        flush_call_count["n"] += 1
        if flush_call_count["n"] == 2:
            raise Exception("DB error on event insert")

    db.flush.side_effect = flush_side_effect

    with pytest.raises(Exception, match="DB error on event insert"):
        CanonicalEntitlementMutationAuditReviewService.upsert_review(
            db,
            audit_id=1,
            review_status="closed",
            reviewed_by_user_id=1,
            review_comment=None,
            incident_key=None,
        )

    # db.add() a été appelé 2 fois (1x projection, 1x événement)
    # Mais comme le 2ème flush a échoué, l'appelant (router) peut rollback.
    assert db.add.call_count == 2
