# Tests ciblés du refactor entitlement mutation de la story 70-19.
"""Vérifie la structure canonique, le versioning et la traçabilité du sous-domaine.

Entitlement mutation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

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
from app.infra.db.models.entitlement_mutation.audit.review import (
    CanonicalEntitlementMutationAuditReviewModel,
)
from app.infra.db.models.entitlement_mutation.suppression.suppression_application import (
    CanonicalEntitlementMutationAlertSuppressionApplicationModel,
)
from app.infra.db.session import SessionLocal, engine
from app.services.canonical_entitlement.alert.handling import (
    CanonicalEntitlementAlertHandlingService,
)
from app.services.canonical_entitlement.audit.audit_review import (
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
        plan_code_snapshot="premium",
        feature_code="feature-a",
        actor_type="script",
        actor_identifier="seed.py",
        source_origin="manual",
        before_payload={},
        after_payload={"is_enabled": True},
    )
    db.add(audit)
    db.flush()
    return audit


def _seed_alert_event(db, *, audit_id: int) -> CanonicalEntitlementMutationAlertEventModel:
    event = CanonicalEntitlementMutationAlertEventModel(
        audit_id=audit_id,
        dedupe_key=f"audit:{audit_id}:seed",
        alert_kind="sla_overdue",
        alert_status="open",
        risk_level_snapshot="high",
        review_status_snapshot="pending_review",
        feature_code_snapshot="feature-a",
        plan_id_snapshot=1,
        plan_code_snapshot="premium",
        actor_type_snapshot="script",
        actor_identifier_snapshot="seed.py",
        sla_target_seconds_snapshot=3600,
        age_seconds_snapshot=7200,
        delivery_channel="webhook",
        last_delivery_status="failed",
        last_delivery_error="timeout",
        payload={"audit_id": audit_id},
        delivery_attempt_count=1,
    )
    db.add(event)
    db.flush()
    return event


def test_canonical_package_exposes_expected_models() -> None:
    from app.infra.db.models.entitlement_mutation import (
        CanonicalEntitlementMutationAlertDeliveryAttemptModel,
        CanonicalEntitlementMutationAlertHandlingEventModel,
        CanonicalEntitlementMutationAuditReviewEventModel,
    )
    from app.infra.db.models.entitlement_mutation import (
        CanonicalEntitlementMutationAlertEventModel as EventModel,
    )
    from app.infra.db.models.entitlement_mutation import (
        CanonicalEntitlementMutationAlertHandlingModel as HandlingModel,
    )
    from app.infra.db.models.entitlement_mutation import (
        CanonicalEntitlementMutationAlertSuppressionApplicationModel as ApplicationModel,
    )
    from app.infra.db.models.entitlement_mutation import (
        CanonicalEntitlementMutationAuditReviewModel as ReviewModel,
    )

    assert EventModel.__tablename__ == "canonical_entitlement_mutation_alert_events"
    assert HandlingModel.__tablename__ == "canonical_entitlement_mutation_alert_event_handlings"
    assert (
        CanonicalEntitlementMutationAlertHandlingEventModel.__tablename__
        == "canonical_entitlement_mutation_alert_event_handling_events"
    )
    assert (
        CanonicalEntitlementMutationAlertDeliveryAttemptModel.__tablename__
        == "canonical_entitlement_mutation_alert_delivery_attempts"
    )
    assert ReviewModel.__tablename__ == "canonical_entitlement_mutation_audit_reviews"
    assert (
        CanonicalEntitlementMutationAuditReviewEventModel.__tablename__
        == "canonical_entitlement_mutation_audit_review_events"
    )
    assert (
        ApplicationModel.__tablename__
        == "canonical_entitlement_mutation_alert_suppression_applications"
    )


def test_audit_review_is_versioned_and_event_is_typed() -> None:
    _setup()
    with SessionLocal() as db:
        audit = _seed_audit(db)

        review = CanonicalEntitlementMutationAuditReviewService.upsert_review(
            db,
            audit_id=audit.id,
            review_status="acknowledged",
            reviewed_by_user_id=10,
            review_comment="initial",
            incident_key="INC-1",
            request_id="req-1",
        )
        db.flush()

        assert review.review_version == 1
        assert review.request_id == "req-1"

        review = CanonicalEntitlementMutationAuditReviewService.upsert_review(
            db,
            audit_id=audit.id,
            review_status="closed",
            reviewed_by_user_id=11,
            review_comment="done",
            incident_key="INC-2",
            request_id="req-2",
        )
        db.commit()

        assert review.review_version == 2
        assert review.request_id == "req-2"

        events = db.execute(
            select(
                CanonicalEntitlementMutationAuditReviewModel,
            ).where(CanonicalEntitlementMutationAuditReviewModel.audit_id == audit.id)
        )
        assert events is not None


def test_handling_creates_suppression_application_and_updates_alert_state() -> None:
    _setup()
    with SessionLocal() as db:
        audit = _seed_audit(db)
        event = _seed_alert_event(db, audit_id=audit.id)

        handling = CanonicalEntitlementAlertHandlingService.upsert_handling(
            db,
            alert_event_id=event.id,
            handling_status="suppressed",
            handled_by_user_id=7,
            ops_comment="known-noise",
            suppression_key="rule-duplicate",
            request_id="req-suppress",
        )
        db.commit()

        assert handling.handling_version == 1
        assert handling.request_id == "req-suppress"
        assert handling.suppression_application_id is not None

        refreshed_event = db.get(CanonicalEntitlementMutationAlertEventModel, event.id)
        assert refreshed_event is not None
        assert refreshed_event.alert_status == "suppressed"
        assert refreshed_event.is_suppressed is True
        assert refreshed_event.suppression_reason == "known-noise"

        application = db.execute(
            select(CanonicalEntitlementMutationAlertSuppressionApplicationModel).where(
                CanonicalEntitlementMutationAlertSuppressionApplicationModel.alert_event_id
                == event.id
            )
        ).scalar_one()
        assert application.application_mode == "manual"
        assert application.request_id == "req-suppress"
        assert application.suppression_key == "rule-duplicate"


def test_alert_event_contains_new_current_state_fields() -> None:
    columns = CanonicalEntitlementMutationAlertEventModel.__table__.columns.keys()

    assert "alert_status" in columns
    assert "effective_review_status_snapshot" in columns
    assert "delivery_attempt_count" in columns
    assert "first_delivered_at" in columns
    assert "delivery_status" in columns
    assert "delivery_error" in columns
    assert "updated_at" in columns
    assert "closed_at" in columns
    assert "is_suppressed" in columns


def test_current_handling_contains_hardening_fields() -> None:
    columns = CanonicalEntitlementMutationAlertHandlingModel.__table__.columns.keys()

    assert "resolution_code" in columns
    assert "incident_key" in columns
    assert "requires_followup" in columns
    assert "followup_due_at" in columns
    assert "handling_version" in columns
    assert "request_id" in columns
    assert "created_at" in columns
    assert "updated_at" in columns


def test_history_tables_expose_typed_event_log_fields() -> None:
    from app.infra.db.models.entitlement_mutation.alert.handling_event import (
        CanonicalEntitlementMutationAlertHandlingEventModel,
    )
    from app.infra.db.models.entitlement_mutation.audit.review_event import (
        CanonicalEntitlementMutationAuditReviewEventModel,
    )

    review_columns = CanonicalEntitlementMutationAuditReviewEventModel.__table__.columns.keys()
    handling_columns = CanonicalEntitlementMutationAlertHandlingEventModel.__table__.columns.keys()

    assert "event_type" in review_columns
    assert "event_type" in handling_columns
    assert "resolution_code" in handling_columns
    assert "incident_key" in handling_columns
    assert "requires_followup" in handling_columns
    assert "followup_due_at" in handling_columns


def test_legacy_root_model_shims_are_removed() -> None:
    legacy_files = [
        "canonical_entitlement_mutation_alert_delivery_attempt.py",
        "canonical_entitlement_mutation_alert_event.py",
        "canonical_entitlement_mutation_alert_event_handling.py",
        "canonical_entitlement_mutation_alert_event_handling_event.py",
        "canonical_entitlement_mutation_alert_suppression_rule.py",
        "canonical_entitlement_mutation_audit_review.py",
        "canonical_entitlement_mutation_audit_review_event.py",
    ]
    models_root = Path(__file__).resolve().parents[2] / "infra" / "db" / "models"

    assert all(not (models_root / name).exists() for name in legacy_files)


def test_canonical_entitlement_services_live_only_in_dedicated_subdomain() -> None:
    legacy_service_files = [
        "canonical_entitlement_alert_batch_handling_service.py",
        "canonical_entitlement_alert_batch_retry_service.py",
        "canonical_entitlement_alert_handling_service.py",
        "canonical_entitlement_alert_query_service.py",
        "canonical_entitlement_alert_retry_service.py",
        "canonical_entitlement_alert_service.py",
        "canonical_entitlement_alert_suppression_application_service.py",
        "canonical_entitlement_alert_suppression_rule_service.py",
        "canonical_entitlement_db_consistency_validator.py",
        "canonical_entitlement_mutation_audit_query_service.py",
        "canonical_entitlement_mutation_audit_review_service.py",
        "canonical_entitlement_mutation_diff_service.py",
        "canonical_entitlement_mutation_service.py",
        "canonical_entitlement_review_queue_service.py",
    ]
    expected_service_files = [
        "alert/__init__.py",
        "alert/batch_handling.py",
        "alert/batch_retry.py",
        "alert/handling.py",
        "alert/query.py",
        "alert/retry.py",
        "alert/service.py",
        "audit/__init__.py",
        "audit/audit_query.py",
        "audit/audit_review.py",
        "audit/diff_service.py",
        "audit/mutation_service.py",
        "audit/review_queue.py",
        "shared/__init__.py",
        "shared/alert_delivery_runtime.py",
        "shared/db_consistency_validator.py",
        "suppression/__init__.py",
        "suppression/application.py",
        "suppression/rule.py",
    ]
    services_root = Path(__file__).resolve().parents[2] / "services"
    canonical_root = services_root / "canonical_entitlement"

    assert canonical_root.exists()
    assert all((canonical_root / name).exists() for name in expected_service_files)
    assert all(not (services_root / name).exists() for name in legacy_service_files)
