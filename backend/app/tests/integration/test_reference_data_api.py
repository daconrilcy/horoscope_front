from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.reference import (
    AspectModel,
    AstroCharacteristicModel,
    HouseModel,
    PlanetModel,
    ReferenceVersionModel,
    SignModel,
)
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService

client = TestClient(app)


def _cleanup_reference_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            AuditEventModel,
            AstroCharacteristicModel,
            AspectModel,
            HouseModel,
            SignModel,
            PlanetModel,
            ReferenceVersionModel,
        ):
            db.execute(delete(model))
        db.commit()


def _register_user(email: str, role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token


def test_reference_seed_then_read_active() -> None:
    _cleanup_reference_tables()
    ops_token = _register_user("reference-seed-active-ops@example.com", "ops")

    seed_response = client.post(
        "/v1/reference-data/seed?version=1.0.0",
        headers={
            "authorization": f"Bearer {ops_token}",
            "x-request-id": "rid-reference-seed",
        },
    )
    assert seed_response.status_code == 200
    seed_payload = seed_response.json()
    assert seed_payload["data"]["seeded_version"] == "1.0.0"
    assert seed_payload["meta"]["request_id"] == "rid-reference-seed"

    read_response = client.get(
        "/v1/reference-data/active?version=1.0.0",
        headers={"x-request-id": "rid-reference-read"},
    )
    assert read_response.status_code == 200
    read_payload = read_response.json()
    assert read_payload["meta"]["request_id"] == "rid-reference-read"
    assert read_payload["data"]["version"] == "1.0.0"
    assert len(read_payload["data"]["planets"]) > 0
    aspects = read_payload["data"]["aspects"]
    assert {item["code"] for item in aspects} == {
        "conjunction",
        "sextile",
        "square",
        "trine",
        "opposition",
    }
    assert all("default_orb_deg" in item for item in aspects)


def test_reference_read_missing_version_returns_404() -> None:
    _cleanup_reference_tables()
    response = client.get(
        "/v1/reference-data/active?version=9.9.9",
        headers={"x-request-id": "rid-reference-missing"},
    )
    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "reference_version_not_found"
    assert payload["error"]["request_id"] == "rid-reference-missing"


def test_reference_seed_requires_admin_token() -> None:
    _cleanup_reference_tables()
    response = client.post(
        "/v1/reference-data/seed?version=1.0.0",
        headers={"x-request-id": "rid-reference-unauthorized"},
    )
    assert response.status_code == 401
    payload = response.json()
    assert payload["error"]["code"] == "unauthorized_seed_access"
    assert payload["error"]["request_id"] == "rid-reference-unauthorized"


def test_reference_clone_creates_new_version_and_writes_audit() -> None:
    _cleanup_reference_tables()
    ops_token = _register_user("reference-clone-ops@example.com", "ops")
    seed_response = client.post(
        "/v1/reference-data/seed?version=1.0.0",
        headers={"authorization": f"Bearer {ops_token}"},
    )
    assert seed_response.status_code == 200

    clone_response = client.post(
        "/v1/reference-data/versions/clone",
        headers={
            "authorization": f"Bearer {ops_token}",
            "x-request-id": "rid-reference-clone",
        },
        json={"source_version": "1.0.0", "new_version": "1.1.0"},
    )
    assert clone_response.status_code == 200
    clone_payload = clone_response.json()
    assert clone_payload["data"]["cloned_version"] == "1.1.0"
    assert clone_payload["meta"]["request_id"] == "rid-reference-clone"

    with SessionLocal() as db:
        event = db.scalar(
            select(AuditEventModel)
            .where(AuditEventModel.request_id == "rid-reference-clone")
            .where(AuditEventModel.action == "reference_clone")
            .limit(1)
        )
        assert event is not None
        assert event.status == "success"


def test_reference_seed_allows_ops_bearer_auth_without_admin_token() -> None:
    _cleanup_reference_tables()
    ops_token = _register_user("reference-ops@example.com", "ops")

    response = client.post(
        "/v1/reference-data/seed?version=1.0.0",
        headers={
            "authorization": f"Bearer {ops_token}",
            "x-request-id": "rid-reference-seed-ops",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["seeded_version"] == "1.0.0"


def test_reference_seed_rejects_non_ops_bearer_auth() -> None:
    _cleanup_reference_tables()
    user_token = _register_user("reference-user@example.com", "user")

    response = client.post(
        "/v1/reference-data/seed?version=1.0.0",
        headers={
            "authorization": f"Bearer {user_token}",
            "x-request-id": "rid-reference-seed-non-ops",
        },
    )
    assert response.status_code == 403
    payload = response.json()
    assert payload["error"]["code"] == "insufficient_role"


def test_reference_seed_rejects_admin_token_fallback_by_default() -> None:
    _cleanup_reference_tables()

    response = client.post(
        "/v1/reference-data/seed?version=1.0.0",
        headers={
            "x-admin-token": "dev-seed-anything",
            "x-request-id": "rid-reference-seed-fallback-off",
        },
    )
    assert response.status_code == 401
    payload = response.json()
    assert payload["error"]["code"] == "unauthorized_seed_access"
