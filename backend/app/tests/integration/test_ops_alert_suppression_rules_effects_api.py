from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from datetime import datetime, timezone

from app.infra.db.base import Base
from app.infra.db.models.canonical_entitlement_mutation_alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.canonical_entitlement_mutation_alert_suppression_rule import (
    CanonicalEntitlementMutationAlertSuppressionRuleModel,
)
from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService

client = TestClient(app)

def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(UserModel))
        db.execute(delete(CanonicalEntitlementMutationAuditModel))
        db.execute(delete(CanonicalEntitlementMutationAlertEventModel))
        db.execute(delete(CanonicalEntitlementMutationAlertSuppressionRuleModel))
        db.commit()

def _register_user_with_role_and_token(email: str, role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token

def _seed_audit(db):
    audit = CanonicalEntitlementMutationAuditModel(
        occurred_at=datetime.now(timezone.utc),
        operation="upsert_plan_feature_configuration",
        plan_id=1,
        plan_code_snapshot="plan1",
        feature_code="feat1",
        actor_type="script",
        actor_identifier="test.py",
        source_origin="manual",
        before_payload={},
        after_payload={"is_enabled": True},
    )
    db.add(audit)
    db.flush()
    return audit

def _seed_alert(db, audit_id, alert_kind="audit_failed", feature="feat1", status="failed"):
    event = CanonicalEntitlementMutationAlertEventModel(
        audit_id=audit_id,
        dedupe_key=f"key-{alert_kind}-{feature}-{status}",
        alert_kind=alert_kind,
        delivery_status=status,
        delivery_channel="webhook",
        payload={},
        feature_code_snapshot=feature,
        plan_id_snapshot=1,
        plan_code_snapshot="plan1",
        risk_level_snapshot="high",
        actor_type_snapshot="user",
        actor_identifier_snapshot="u1",
        age_seconds_snapshot=100,
        created_at=datetime.now(timezone.utc)
    )
    db.add(event)
    db.flush()
    return event

def test_alert_suppression_by_rule_effects() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    headers = {"Authorization": f"Bearer {ops_token}"}

    with SessionLocal() as db:
        audit = _seed_audit(db)
        # 1. Seed two failed alerts
        _seed_alert(db, audit.id, alert_kind="audit_failed", feature="feat1")
        _seed_alert(db, audit.id, alert_kind="audit_failed", feature="feat2")
        
        # 2. Create suppression rule for feat1
        rule = CanonicalEntitlementMutationAlertSuppressionRuleModel(
            alert_kind="audit_failed",
            feature_code="feat1",
            is_active=True
        )
        db.add(rule)
        db.commit()

    # 3. Check summary
    response = client.get("/v1/ops/entitlements/mutation-audits/alerts/summary", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    # Total failed = 2. 1 suppressed by rule, 1 retryable.
    assert data["total_count"] == 2
    assert data["failed_count"] == 2
    assert data["suppressed_count"] == 1
    assert data["retryable_count"] == 1

    # 4. Check list with handling_status=suppressed
    response = client.get("/v1/ops/entitlements/mutation-audits/alerts?handling_status=suppressed", headers=headers)
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["feature_code_snapshot"] == "feat1"
    assert items[0]["handling"]["source"] == "rule"

    # 5. Check list with handling_status=pending_retry
    response = client.get("/v1/ops/entitlements/mutation-audits/alerts?handling_status=pending_retry", headers=headers)
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["feature_code_snapshot"] == "feat2"
    assert items[0]["handling"]["source"] == "virtual"
    assert items[0]["handling"]["handling_status"] == "pending_retry"
