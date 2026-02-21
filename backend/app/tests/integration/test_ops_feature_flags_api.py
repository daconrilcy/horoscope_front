from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.feature_flag import FeatureFlagModel
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
        db.execute(delete(FeatureFlagModel))
        db.execute(delete(UserModel))
        db.commit()


def _register_user_with_role_and_token(email: str, role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token


def test_ops_feature_flags_requires_ops_role() -> None:
    _cleanup_tables()
    user_token = _register_user_with_role_and_token("flags-user@example.com", "user")
    response = client.get(
        "/v1/ops/feature-flags",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_ops_feature_flags_list_and_update() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("flags-ops@example.com", "ops")
    headers = {"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-feature-flags-1"}

    initial = client.get("/v1/ops/feature-flags", headers=headers)
    assert initial.status_code == 200
    keys = {item["key"] for item in initial.json()["data"]["flags"]}
    assert "tarot_enabled" in keys
    assert "runes_enabled" in keys

    updated = client.put(
        "/v1/ops/feature-flags/tarot_enabled",
        headers=headers,
        json={
            "enabled": True,
            "target_roles": ["user"],
            "target_user_ids": [1, 2],
        },
    )
    assert updated.status_code == 200
    payload = updated.json()["data"]
    assert payload["enabled"] is True
    assert payload["target_roles"] == ["user"]
    assert payload["target_user_ids"] == [1, 2]

    with SessionLocal() as db:
        event = db.scalar(
            select(AuditEventModel)
            .where(AuditEventModel.request_id == "rid-feature-flags-1")
            .where(AuditEventModel.action == "ops_feature_flag_update")
            .order_by(AuditEventModel.id.desc())
            .limit(1)
        )
        assert event is not None
        assert event.status == "success"
        assert event.target_type == "feature_flag"
        assert event.target_id == "tarot_enabled"
