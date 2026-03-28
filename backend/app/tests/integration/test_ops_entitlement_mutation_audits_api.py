from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
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
        db.commit()


def _register_user_with_role_and_token(email: str, role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token


def _seed_audit(
    db,
    *,
    occurred_at=None,
    operation="upsert_plan_feature_configuration",
    plan_id=1,
    plan_code="basic-entry",
    feature_code="astrologer_chat",
    actor_type="script",
    actor_identifier="test.py",
    source_origin="manual",
    request_id=None,
    before_payload=None,
    after_payload=None,
):
    audit = CanonicalEntitlementMutationAuditModel(
        occurred_at=occurred_at or datetime.now(timezone.utc),
        operation=operation,
        plan_id=plan_id,
        plan_code_snapshot=plan_code,
        feature_code=feature_code,
        actor_type=actor_type,
        actor_identifier=actor_identifier,
        source_origin=source_origin,
        request_id=request_id,
        before_payload=before_payload or {},
        after_payload=after_payload or {"is_enabled": True},
    )
    db.add(audit)
    db.flush()
    return audit


def test_list_returns_empty_when_no_audits() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["items"] == []
    assert payload["data"]["total_count"] == 0
    assert payload["data"]["page"] == 1
    assert payload["data"]["page_size"] == 20


def test_list_returns_audits_sorted_desc() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with SessionLocal() as db:
        _seed_audit(db, occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc), feature_code="f1")
        _seed_audit(db, occurred_at=datetime(2026, 1, 3, tzinfo=timezone.utc), feature_code="f3")
        _seed_audit(db, occurred_at=datetime(2026, 1, 2, tzinfo=timezone.utc), feature_code="f2")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 3
    assert items[0]["feature_code"] == "f3"
    assert items[1]["feature_code"] == "f2"
    assert items[2]["feature_code"] == "f1"


def test_list_filter_by_feature_code() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with SessionLocal() as db:
        _seed_audit(db, feature_code="chat")
        _seed_audit(db, feature_code="daily")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"feature_code": "chat"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["feature_code"] == "chat"


def test_list_filter_by_actor_type() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with SessionLocal() as db:
        _seed_audit(db, actor_type="script")
        _seed_audit(db, actor_type="admin")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"actor_type": "script"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["actor_type"] == "script"


def test_list_filter_by_plan_code() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with SessionLocal() as db:
        _seed_audit(db, plan_code="basic")
        _seed_audit(db, plan_code="premium")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"plan_code": "basic"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["plan_code_snapshot"] == "basic"


def test_list_filter_by_request_id() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with SessionLocal() as db:
        _seed_audit(db, request_id="rid-1")
        _seed_audit(db, request_id="rid-2")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"request_id": "rid-1"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["request_id"] == "rid-1"


def test_list_filter_by_date_range() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with SessionLocal() as db:
        _seed_audit(db, occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc), feature_code="f1")
        _seed_audit(db, occurred_at=datetime(2026, 1, 10, tzinfo=timezone.utc), feature_code="f10")
        _seed_audit(db, occurred_at=datetime(2026, 1, 20, tzinfo=timezone.utc), feature_code="f20")
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={
            "date_from": "2026-01-05T00:00:00Z",
            "date_to": "2026-01-15T00:00:00Z",
        },
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["feature_code"] == "f10"


def test_list_pagination() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with SessionLocal() as db:
        for i in range(1, 6):
            _seed_audit(
                db,
                occurred_at=datetime(2026, 1, i, tzinfo=timezone.utc),
                feature_code=f"f{i}",
            )
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"page": 2, "page_size": 2},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    items = payload["data"]["items"]
    assert len(items) == 2
    assert payload["data"]["total_count"] == 5
    assert payload["data"]["page"] == 2
    assert payload["data"]["page_size"] == 2
    # Sorted desc: f5, f4, f3, f2, f1. Page 2 of size 2: f3, f2.
    assert items[0]["feature_code"] == "f3"
    assert items[1]["feature_code"] == "f2"


def test_list_include_payloads_false() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with SessionLocal() as db:
        _seed_audit(db, before_payload={"old": 1}, after_payload={"new": 2})
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"include_payloads": "false"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert "before_payload" not in item
    assert "after_payload" not in item


def test_list_include_payloads_true() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with SessionLocal() as db:
        _seed_audit(db, before_payload={"old": 1}, after_payload={"new": 2})
        db.commit()

    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        params={"include_payloads": "true"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    item = response.json()["data"]["items"][0]
    assert item["before_payload"] == {"old": 1}
    assert item["after_payload"] == {"new": 2}


def test_detail_returns_audit_with_payloads() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    with SessionLocal() as db:
        audit = _seed_audit(db, before_payload={"old": 1}, after_payload={"new": 2})
        db.commit()
        audit_id = audit.id

    response = client.get(
        f"/v1/ops/entitlements/mutation-audits/{audit_id}",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 200
    item = response.json()["data"]
    assert item["id"] == audit_id
    assert item["before_payload"] == {"old": 1}
    assert item["after_payload"] == {"new": 2}


def test_detail_returns_404_on_unknown_id() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    response = client.get(
        "/v1/ops/entitlements/mutation-audits/9999",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "audit_not_found"


def test_detail_returns_403_for_non_ops_role() -> None:
    _cleanup_tables()
    user_token = _register_user_with_role_and_token("user@example.com", "user")
    response = client.get(
        "/v1/ops/entitlements/mutation-audits/1",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_detail_returns_401_when_unauthenticated() -> None:
    _cleanup_tables()
    response = client.get("/v1/ops/entitlements/mutation-audits/1")
    assert response.status_code == 401


def test_list_returns_403_for_non_ops_role() -> None:
    _cleanup_tables()
    user_token = _register_user_with_role_and_token("user@example.com", "user")
    response = client.get(
        "/v1/ops/entitlements/mutation-audits",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_list_returns_401_when_unauthenticated() -> None:
    _cleanup_tables()
    response = client.get("/v1/ops/entitlements/mutation-audits")
    assert response.status_code == 401
