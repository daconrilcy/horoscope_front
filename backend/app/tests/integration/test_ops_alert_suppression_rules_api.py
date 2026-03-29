from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.canonical_entitlement_mutation_alert_suppression_rule import (
    CanonicalEntitlementMutationAlertSuppressionRuleModel,
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
        db.execute(delete(CanonicalEntitlementMutationAlertSuppressionRuleModel))
        db.commit()

def _register_user_with_role_and_token(email: str, role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token

def test_crud_ops_alert_suppression_rules() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    headers = {"Authorization": f"Bearer {ops_token}"}

    # 1. List empty
    response = client.get("/v1/ops/entitlements/mutation-audits/alerts/suppression-rules", headers=headers)
    assert response.status_code == 200
    assert response.json()["data"] == []

    # 2. Create rule
    payload = {
        "alert_kind": "audit_failed",
        "feature_code": "feat1",
        "ops_comment": "Test suppression"
    }
    response = client.post("/v1/ops/entitlements/mutation-audits/alerts/suppression-rules", headers=headers, json=payload)
    assert response.status_code == 201
    rule_id = response.json()["data"]["id"]
    assert response.json()["data"]["alert_kind"] == "audit_failed"
    assert response.json()["data"]["is_active"] is True

    # 3. Get rule
    response = client.get(f"/v1/ops/entitlements/mutation-audits/alerts/suppression-rules/{rule_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["data"]["id"] == rule_id

    # 4. Patch rule
    response = client.patch(f"/v1/ops/entitlements/mutation-audits/alerts/suppression-rules/{rule_id}", headers=headers, json={"ops_comment": "Updated"})
    assert response.status_code == 200
    assert response.json()["data"]["ops_comment"] == "Updated"

    # 5. Delete rule (logical)
    response = client.delete(f"/v1/ops/entitlements/mutation-audits/alerts/suppression-rules/{rule_id}", headers=headers)
    assert response.status_code == 204

    # 6. Verify logical delete
    response = client.get(f"/v1/ops/entitlements/mutation-audits/alerts/suppression-rules/{rule_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["data"]["is_active"] is False

    response = client.get("/v1/ops/entitlements/mutation-audits/alerts/suppression-rules", headers=headers)
    assert response.status_code == 200
    # Should be empty because is_active defaults to True
    assert len(response.json()["data"]) == 0

    response = client.get("/v1/ops/entitlements/mutation-audits/alerts/suppression-rules?is_active=false", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1

def test_create_duplicate_rule_returns_409() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    headers = {"Authorization": f"Bearer {ops_token}"}

    payload = {
        "alert_kind": "audit_failed",
        "feature_code": "feat1",
        "ops_comment": "Original"
    }
    response = client.post("/v1/ops/entitlements/mutation-audits/alerts/suppression-rules", headers=headers, json=payload)
    assert response.status_code == 201

    # Same criteria, DIFFERENT comment -> 409
    payload["ops_comment"] = "Different"
    response = client.post("/v1/ops/entitlements/mutation-audits/alerts/suppression-rules", headers=headers, json=payload)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "suppression_rule_conflict"

def test_role_restriction() -> None:
    _cleanup_tables()
    user_token = _register_user_with_role_and_token("user@example.com", "user")
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get("/v1/ops/entitlements/mutation-audits/alerts/suppression-rules", headers=headers)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"
