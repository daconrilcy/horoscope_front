from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from app.infra.db.base import Base
from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)
from app.infra.db.models.canonical_entitlement_mutation_audit_review import (
    CanonicalEntitlementMutationAuditReviewModel,
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
        plan_code_snapshot="basic-entry",
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
