from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.entitlement_mutation.suppression.suppression_rule import (
    CanonicalEntitlementMutationAlertSuppressionRuleModel,
)
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService

client = TestClient(app)

RULES_PATH = "/v1/ops/entitlements/mutation-audits/alerts/suppression-rules"


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


def test_list_suppression_rules_returns_empty_state() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")

    response = client.get(RULES_PATH, headers={"Authorization": f"Bearer {ops_token}"})

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["items"] == []
    assert payload["total_count"] == 0
    assert payload["page"] == 1
    assert payload["page_size"] == 20


def test_create_suppression_rule_returns_201() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-create@example.com", "ops")

    response = client.post(
        RULES_PATH,
        headers={"Authorization": f"Bearer {ops_token}"},
        json={
            "alert_kind": "sla_overdue",
            "feature_code": "feature-a",
            "ops_comment": "Known noise",
            "suppression_key": "noise",
        },
    )

    assert response.status_code == 201
    payload = response.json()["data"]
    assert payload["alert_kind"] == "sla_overdue"
    assert payload["feature_code"] == "feature-a"
    assert payload["ops_comment"] == "Known noise"
    assert payload["suppression_key"] == "noise"
    assert payload["is_active"] is True


def test_create_suppression_rule_is_idempotent_on_same_body() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-idempotent@example.com", "ops")
    body = {
        "alert_kind": "sla_overdue",
        "feature_code": "feature-a",
        "ops_comment": "Known noise",
        "suppression_key": "noise",
    }

    first = client.post(RULES_PATH, headers={"Authorization": f"Bearer {ops_token}"}, json=body)
    second = client.post(RULES_PATH, headers={"Authorization": f"Bearer {ops_token}"}, json=body)

    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json()["data"]["id"] == first.json()["data"]["id"]


def test_create_suppression_rule_returns_409_on_conflicting_same_criteria() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-conflict@example.com", "ops")

    first = client.post(
        RULES_PATH,
        headers={"Authorization": f"Bearer {ops_token}"},
        json={"alert_kind": "sla_overdue", "feature_code": "feature-a", "ops_comment": "First"},
    )
    second = client.post(
        RULES_PATH,
        headers={"Authorization": f"Bearer {ops_token}"},
        json={"alert_kind": "sla_overdue", "feature_code": "feature-a", "ops_comment": "Second"},
    )

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "suppression_rule_conflict"


def test_patch_suppression_rule_can_deactivate_rule() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-patch@example.com", "ops")
    created = client.post(
        RULES_PATH,
        headers={"Authorization": f"Bearer {ops_token}"},
        json={"alert_kind": "sla_overdue", "feature_code": "feature-a"},
    )

    response = client.patch(
        f"{RULES_PATH}/{created.json()['data']['id']}",
        headers={"Authorization": f"Bearer {ops_token}"},
        json={"is_active": False},
    )

    assert response.status_code == 200
    assert response.json()["data"]["is_active"] is False


def test_patch_suppression_rule_updates_comment_and_key() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-patch2@example.com", "ops")
    created = client.post(
        RULES_PATH,
        headers={"Authorization": f"Bearer {ops_token}"},
        json={"alert_kind": "sla_overdue", "feature_code": "feature-a"},
    )

    response = client.patch(
        f"{RULES_PATH}/{created.json()['data']['id']}",
        headers={"Authorization": f"Bearer {ops_token}"},
        json={"ops_comment": "Updated comment", "suppression_key": "updated-key"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["ops_comment"] == "Updated comment"
    assert payload["suppression_key"] == "updated-key"


def test_rules_api_requires_ops_role() -> None:
    _cleanup_tables()
    user_token = _register_user_with_role_and_token("user@example.com", "user")

    response = client.get(RULES_PATH, headers={"Authorization": f"Bearer {user_token}"})

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_rules_api_requires_authentication() -> None:
    _cleanup_tables()

    response = client.get(RULES_PATH)

    assert response.status_code == 401


def test_rules_api_returns_429_when_rate_limited(monkeypatch: object) -> None:
    from app.core.rate_limit import RateLimitError

    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops-429@example.com", "ops")

    def _always_rate_limited(*args: object, **kwargs: object) -> None:
        raise RateLimitError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            details={"retry_after": "7"},
            status_code=429,
        )

    monkeypatch.setattr(
        "app.services.canonical_entitlement.audit.api_mutation_audits.check_rate_limit",
        _always_rate_limited,
    )

    response = client.get(
        RULES_PATH,
        headers={
            "Authorization": f"Bearer {ops_token}",
            "X-Request-Id": "rid-alert-rules-429",
        },
    )

    assert response.status_code == 429
    assert response.json()["error"]["request_id"] == "rid-alert-rules-429"
