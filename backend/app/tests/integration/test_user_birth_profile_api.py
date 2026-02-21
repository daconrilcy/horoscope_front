from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.security import create_token
from app.infra.db.base import Base
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.session import SessionLocal, engine
from app.main import app

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(UserBirthProfileModel))
        db.execute(delete(UserModel))
        db.commit()


def _register_and_get_access_token() -> str:
    register = client.post(
        "/v1/auth/register",
        json={"email": "user@example.com", "password": "strong-pass-123"},
    )
    assert register.status_code == 200
    return register.json()["data"]["tokens"]["access_token"]


def test_put_birth_data_requires_token() -> None:
    _cleanup_tables()
    response = client.put(
        "/v1/users/me/birth-data",
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_access_token"


def test_put_and_get_birth_data_success() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    put_response = client.put(
        "/v1/users/me/birth-data",
        headers=headers,
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    get_response = client.get("/v1/users/me/birth-data", headers=headers)

    assert put_response.status_code == 200
    assert put_response.json()["data"]["birth_place"] == "Paris"
    assert get_response.status_code == 200
    assert get_response.json()["data"]["birth_timezone"] == "Europe/Paris"


def test_put_birth_data_invalid_timezone_returns_explicit_error() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Mars/Olympus",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_timezone"


def test_put_birth_data_rejects_unknown_fields() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "unknown_field": "unexpected",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_birth_input"
    assert any(
        error.get("type") == "extra_forbidden"
        for error in response.json()["error"]["details"].get("errors", [])
    )


def test_put_birth_data_rejects_overlong_place() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "P" * 256,
            "birth_timezone": "Europe/Paris",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_birth_input"
    assert any(
        error.get("type") == "string_too_long"
        for error in response.json()["error"]["details"].get("errors", [])
    )


def test_put_birth_data_malformed_json_returns_error_envelope() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.put(
        "/v1/users/me/birth-data",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        content='{"birth_date":"1990-06-15","birth_time":',
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request_payload"
    assert "request_id" in response.json()["error"]


def test_get_birth_data_not_found() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.get(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "birth_profile_not_found"


def test_put_birth_data_invalid_token() -> None:
    _cleanup_tables()
    response = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": "Bearer not-a-token"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_token"


def test_put_birth_data_expired_token() -> None:
    _cleanup_tables()
    expired_access = create_token(
        subject="1",
        role="user",
        token_type="access",
        expires_minutes=-1,
    )
    response = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {expired_access}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "token_expired"


def test_put_birth_data_refresh_token_rejected() -> None:
    _cleanup_tables()
    register = client.post(
        "/v1/auth/register",
        json={"email": "user@example.com", "password": "strong-pass-123"},
    )
    refresh_token = register.json()["data"]["tokens"]["refresh_token"]
    response = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {refresh_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_token_type"


def test_put_birth_data_insufficient_role() -> None:
    _cleanup_tables()
    token = create_token(
        subject="1",
        role="unknown-role",
        token_type="access",
        expires_minutes=15,
    )
    response = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"
