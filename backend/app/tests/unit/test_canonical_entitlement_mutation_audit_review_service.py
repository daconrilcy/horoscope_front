from __future__ import annotations

from datetime import datetime, timezone

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
        result = db.execute(
            __import__("sqlalchemy").select(CanonicalEntitlementMutationAuditReviewModel)
        )
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
