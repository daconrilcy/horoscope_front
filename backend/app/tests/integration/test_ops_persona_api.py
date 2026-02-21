from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.persona_config import PersonaConfigModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(AuditEventModel))
        db.execute(delete(PersonaConfigModel))
        db.execute(delete(UserModel))
        db.commit()


def _register_user_with_role_and_token(email: str, role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token


def test_ops_persona_requires_token() -> None:
    _cleanup_tables()
    response = client.get("/v1/ops/persona/config")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_access_token"


def test_ops_persona_forbidden_for_non_ops_role() -> None:
    _cleanup_tables()
    user_token = _register_user_with_role_and_token("persona-user@example.com", "user")
    response = client.get(
        "/v1/ops/persona/config",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_ops_persona_get_default_then_update_and_rollback() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("persona-ops@example.com", "ops")

    get_default = client.get(
        "/v1/ops/persona/config",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert get_default.status_code == 200
    assert get_default.json()["data"]["is_default"] is True
    assert get_default.json()["data"]["profile_code"] == "legacy-default"

    update = client.put(
        "/v1/ops/persona/config",
        headers={"Authorization": f"Bearer {ops_token}"},
        json={
            "tone": "direct",
            "prudence_level": "high",
            "scope_policy": "balanced",
            "response_style": "detailed",
            "fallback_policy": "safe_fallback",
        },
    )
    assert update.status_code == 200
    assert update.json()["data"]["status"] == "active"
    assert update.json()["data"]["version"] == 1

    second_update = client.put(
        "/v1/ops/persona/config",
        headers={"Authorization": f"Bearer {ops_token}"},
        json={
            "tone": "empathetic",
            "prudence_level": "standard",
            "scope_policy": "strict",
            "response_style": "concise",
            "fallback_policy": "retry_once_then_safe",
        },
    )
    assert second_update.status_code == 200
    assert second_update.json()["data"]["version"] == 2

    rollback = client.post(
        "/v1/ops/persona/rollback",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert rollback.status_code == 200
    data = rollback.json()["data"]
    assert data["rolled_back_version"] == 2
    assert data["active"]["version"] == 1


def test_ops_persona_update_invalid_payload_returns_422() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("persona-ops-invalid@example.com", "ops")
    response = client.put(
        "/v1/ops/persona/config",
        headers={"Authorization": f"Bearer {ops_token}"},
        json={
            "tone": "invalid",
            "prudence_level": "high",
            "scope_policy": "strict",
            "response_style": "concise",
            "fallback_policy": "safe_fallback",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_persona_config"


def test_ops_persona_put_config_is_idempotent_for_identical_payload() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("persona-ops-idempotent@example.com", "ops")
    headers = {"Authorization": f"Bearer {ops_token}"}
    payload = {
        "tone": "direct",
        "prudence_level": "high",
        "scope_policy": "balanced",
        "response_style": "detailed",
        "fallback_policy": "safe_fallback",
    }

    first = client.put("/v1/ops/persona/config", headers=headers, json=payload)
    assert first.status_code == 200
    second = client.put("/v1/ops/persona/config", headers=headers, json=payload)
    assert second.status_code == 200

    first_data = first.json()["data"]
    second_data = second.json()["data"]
    assert second_data["id"] == first_data["id"]
    assert second_data["version"] == first_data["version"]

    with SessionLocal() as db:
        rows = list(db.scalars(select(PersonaConfigModel)))
        assert len(rows) == 1


def test_ops_persona_rollback_records_audit_with_request_id() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("persona-ops-audit@example.com", "ops")

    first_update = client.put(
        "/v1/ops/persona/config",
        headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-persona-update-1"},
        json={
            "tone": "direct",
            "prudence_level": "high",
            "scope_policy": "balanced",
            "response_style": "detailed",
            "fallback_policy": "safe_fallback",
        },
    )
    assert first_update.status_code == 200

    second_update = client.put(
        "/v1/ops/persona/config",
        headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-persona-update-2"},
        json={
            "tone": "empathetic",
            "prudence_level": "standard",
            "scope_policy": "strict",
            "response_style": "concise",
            "fallback_policy": "retry_once_then_safe",
        },
    )
    assert second_update.status_code == 200

    rollback = client.post(
        "/v1/ops/persona/rollback",
        headers={"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-persona-rollback"},
    )
    assert rollback.status_code == 200

    with SessionLocal() as db:
        event = db.scalar(
            select(AuditEventModel)
            .where(AuditEventModel.request_id == "rid-persona-rollback")
            .where(AuditEventModel.action == "ops_persona_rollback")
            .limit(1)
        )
        assert event is not None
        assert event.actor_role == "ops"
        assert event.status == "success"
        assert event.target_type == "persona_config"
        assert event.target_id is not None


def test_ops_persona_returns_429_when_rate_limited(monkeypatch: object) -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("persona-ops-429@example.com", "ops")
    headers = {"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-persona-429"}

    def _always_rate_limited(*args: object, **kwargs: object) -> None:
        from app.core.rate_limit import RateLimitError

        raise RateLimitError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            details={"retry_after": "4"},
            status_code=429,
        )

    monkeypatch.setattr("app.api.v1.routers.ops_persona.check_rate_limit", _always_rate_limited)

    response = client.get("/v1/ops/persona/config", headers=headers)
    assert response.status_code == 429
    payload = response.json()["error"]
    assert payload["code"] == "rate_limit_exceeded"
    assert payload["request_id"] == "rid-persona-429"


def test_ops_persona_profiles_lifecycle_endpoints() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("persona-ops-lifecycle@example.com", "ops")
    headers = {"Authorization": f"Bearer {ops_token}"}

    created = client.post(
        "/v1/ops/persona/profiles",
        headers=headers,
        json={
            "profile_code": "sage-astro",
            "display_name": "Sage Astrologue",
            "tone": "empathetic",
            "prudence_level": "high",
            "scope_policy": "strict",
            "response_style": "detailed",
            "fallback_policy": "safe_fallback",
            "activate": False,
        },
    )
    assert created.status_code == 200
    profile_id = created.json()["data"]["id"]

    profiles = client.get("/v1/ops/persona/profiles", headers=headers)
    assert profiles.status_code == 200
    assert profiles.json()["data"]["total"] >= 1

    activated = client.post(f"/v1/ops/persona/profiles/{profile_id}/activate", headers=headers)
    assert activated.status_code == 200
    assert activated.json()["data"]["status"] == "active"

    archive_active = client.post(f"/v1/ops/persona/profiles/{profile_id}/archive", headers=headers)
    assert archive_active.status_code == 422
    assert archive_active.json()["error"]["code"] == "persona_profile_archive_forbidden"

    switch_back = client.put(
        "/v1/ops/persona/config",
        headers=headers,
        json={
            "tone": "direct",
            "prudence_level": "high",
            "scope_policy": "balanced",
            "response_style": "detailed",
            "fallback_policy": "safe_fallback",
        },
    )
    assert switch_back.status_code == 200

    archived = client.post(f"/v1/ops/persona/profiles/{profile_id}/archive", headers=headers)
    assert archived.status_code == 200
    assert archived.json()["data"]["status"] == "archived"

    restored = client.post(f"/v1/ops/persona/profiles/{profile_id}/restore", headers=headers)
    assert restored.status_code == 200
    assert restored.json()["data"]["status"] == "inactive"
