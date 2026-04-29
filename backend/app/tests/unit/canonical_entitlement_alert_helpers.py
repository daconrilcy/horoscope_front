# Helpers partages pour les tests unitaires de handling des alertes entitlement.
from __future__ import annotations

from datetime import datetime, timezone

from app.infra.db.base import Base
from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)
from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.tests.helpers.db_session import app_test_engine


def setup_entitlement_alert_schema() -> None:
    """Recree le schema utilise par les tests unitaires de handling."""
    engine = app_test_engine()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed_entitlement_alert_audit(db) -> CanonicalEntitlementMutationAuditModel:
    """Insere l'audit canonique minimal requis par les evenements d'alerte."""
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


def seed_entitlement_alert_event(db) -> CanonicalEntitlementMutationAlertEventModel:
    """Insere un evenement d'alerte utilisable par le service de handling."""
    audit = seed_entitlement_alert_audit(db)
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
