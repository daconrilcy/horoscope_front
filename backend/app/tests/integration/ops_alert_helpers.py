# Helpers partages pour les tests d'integration des alertes ops.
from __future__ import annotations

from sqlalchemy import delete

from app.core.security import create_access_token
from app.infra.db.base import Base
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
from app.infra.db.models.entitlement_mutation.alert.handling_event import (
    CanonicalEntitlementMutationAlertHandlingEventModel,
)
from app.infra.db.models.user import UserModel
from app.services.auth_service import AuthService
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session


def cleanup_ops_alert_tables() -> None:
    """Reinitialise les tables utilisees par les tests d'alertes ops."""
    engine = app_test_engine()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with open_app_test_db_session() as db:
        db.execute(delete(UserModel))
        db.execute(delete(CanonicalEntitlementMutationAlertDeliveryAttemptModel))
        db.execute(delete(CanonicalEntitlementMutationAlertHandlingEventModel))
        db.execute(delete(CanonicalEntitlementMutationAlertHandlingModel))
        db.execute(delete(CanonicalEntitlementMutationAlertEventModel))
        db.execute(delete(CanonicalEntitlementMutationAuditModel))
        db.commit()


def register_user_with_role_and_token(email: str, role: str) -> str:
    """Cree un utilisateur de test et retourne un jeton portant son role stocke."""
    with open_app_test_db_session() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token


def register_user_and_issue_token_with_role_claim(email: str, role: str, claim_role: str) -> str:
    """Cree un utilisateur et emet un jeton dont le claim role peut diverger."""
    with open_app_test_db_session() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return create_access_token(subject=str(auth.user.id), role=claim_role)


def seed_ops_alert_audit(db) -> CanonicalEntitlementMutationAuditModel:
    """Insere un audit canonique minimal pour construire les alertes ops."""
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


def seed_ops_alert_event(
    db,
    *,
    audit_id: int,
    delivery_status: str = "failed",
) -> CanonicalEntitlementMutationAlertEventModel:
    """Insere un evenement d'alerte ops coherent avec l'audit fourni."""
    event = CanonicalEntitlementMutationAlertEventModel(
        audit_id=audit_id,
        dedupe_key=f"audit:{audit_id}:review:pending_review:sla:overdue:{delivery_status}",
        alert_kind="sla_overdue",
        risk_level_snapshot="high",
        effective_review_status_snapshot="pending_review",
        feature_code_snapshot="test_feature",
        plan_id_snapshot=1,
        plan_code_snapshot="premium",
        actor_type_snapshot="user",
        actor_identifier_snapshot="user@test.com",
        sla_target_seconds_snapshot=14_400,
        age_seconds_snapshot=99_999,
        delivery_channel="webhook",
        delivery_status=delivery_status,
        delivery_error=None if delivery_status == "sent" else "Connection refused",
        payload={"alert_kind": "sla_overdue", "audit_id": audit_id},
    )
    db.add(event)
    db.flush()
    return event


def seed_ops_alert_attempt(
    db,
    *,
    alert_event_id: int,
    attempt_number: int,
    delivery_status: str,
    request_id: str | None = None,
) -> CanonicalEntitlementMutationAlertDeliveryAttemptModel:
    """Insere une tentative de livraison rattachee a une alerte ops."""
    attempt = CanonicalEntitlementMutationAlertDeliveryAttemptModel(
        alert_event_id=alert_event_id,
        attempt_number=attempt_number,
        delivery_channel="webhook",
        delivery_status=delivery_status,
        delivery_error=None if delivery_status == "sent" else "Timeout",
        request_id=request_id,
        payload={"alert_event_id": alert_event_id, "attempt_number": attempt_number},
    )
    db.add(attempt)
    db.flush()
    return attempt
