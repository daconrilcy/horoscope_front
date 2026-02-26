from fastapi.testclient import TestClient
from sqlalchemy import delete

import app.infra.db.models  # noqa: F401  # ensure all SQLAlchemy models are registered
from app.core.security import create_token
from app.infra.db.base import Base
from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.user_astro_profile_service import UserAstroProfileServiceError

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(GeoPlaceResolvedModel))
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


def test_put_and_get_birth_data_persists_city_country_and_coordinates() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    put_response = client.put(
        "/v1/users/me/birth-data",
        headers=headers,
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris, Ile-de-France, France",
            "birth_timezone": "Europe/Paris",
            "birth_city": "Paris",
            "birth_country": "France",
            "birth_lat": 48.8566,
            "birth_lon": 2.3522,
        },
    )
    get_response = client.get("/v1/users/me/birth-data", headers=headers)

    assert put_response.status_code == 200
    assert get_response.status_code == 200
    data = get_response.json()["data"]
    assert data["birth_city"] == "Paris"
    assert data["birth_country"] == "France"
    assert data["birth_lat"] == 48.8566
    assert data["birth_lon"] == 2.3522


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


def test_put_birth_data_accepts_place_resolved_id_field() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    with SessionLocal() as db:
        place = GeoPlaceResolvedModel(
            provider="nominatim",
            provider_place_id=12345,
            display_name="Paris, Ile-de-France, France",
            latitude=48.8566,
            longitude=2.3522,
            timezone_iana="Europe/Paris",
        )
        db.add(place)
        db.flush()
        place_id = place.id
        db.commit()

    response = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "place_resolved_id": place_id,
        },
    )
    assert response.status_code == 200


def test_get_birth_data_returns_birth_place_text_and_resolved_place() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    with SessionLocal() as db:
        place = GeoPlaceResolvedModel(
            provider="nominatim",
            provider_place_id=12345,
            display_name="Paris, Ile-de-France, France",
            latitude=48.8566,
            longitude=2.3522,
            timezone_iana="Europe/Paris",
        )
        db.add(place)
        db.flush()
        place_id = place.id
        db.commit()

    put_response = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "place_resolved_id": place_id,
        },
    )
    assert put_response.status_code == 200

    get_response = client.get(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert get_response.status_code == 200
    data = get_response.json()["data"]
    assert data["birth_place_text"] == "Paris"
    resolved = data["birth_place_resolved"]
    assert resolved is not None
    assert resolved["provider"] == "nominatim"
    assert resolved["provider_place_id"] == 12345
    assert resolved["display_name"] == "Paris, Ile-de-France, France"
    assert resolved["latitude"] == 48.8566
    assert resolved["longitude"] == 2.3522
    assert resolved["timezone_iana"] == "Europe/Paris"


def test_get_birth_data_legacy_profile_returns_null_resolved_place() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    put_response = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    assert put_response.status_code == 200

    get_response = client.get(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert get_response.status_code == 200
    data = get_response.json()["data"]
    assert data["birth_place_text"] == "Paris"
    assert data["birth_place_resolved"] is None


def test_put_birth_data_replaces_place_resolved_reference_on_edit() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    with SessionLocal() as db:
        first_place = GeoPlaceResolvedModel(
            provider="nominatim",
            provider_place_id=12345,
            display_name="Paris, Ile-de-France, France",
            latitude=48.8566,
            longitude=2.3522,
            timezone_iana="Europe/Paris",
        )
        second_place = GeoPlaceResolvedModel(
            provider="nominatim",
            provider_place_id=67890,
            display_name="Lyon, Auvergne-Rhone-Alpes, France",
            latitude=45.764,
            longitude=4.8357,
            timezone_iana="Europe/Paris",
        )
        db.add(first_place)
        db.add(second_place)
        db.flush()
        first_place_id = first_place.id
        second_place_id = second_place.id
        db.commit()

    first_put = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "place_resolved_id": first_place_id,
        },
    )
    assert first_put.status_code == 200

    second_put = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Lyon",
            "birth_timezone": "Europe/Paris",
            "place_resolved_id": second_place_id,
        },
    )
    assert second_put.status_code == 200

    get_response = client.get(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert get_response.status_code == 200
    data = get_response.json()["data"]
    assert data["birth_place_text"] == "Lyon"
    assert data["birth_place_resolved"]["provider_place_id"] == 67890


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


# ---------------------------------------------------------------------------
# AC3 / AC5 — birth_time null accepté + astro_profile dans GET
# ---------------------------------------------------------------------------


def test_put_birth_data_accepts_null_birth_time() -> None:
    """AC3: PUT avec birth_time=null est accepté et stocké."""
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": None,
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["birth_time"] is None


def test_put_birth_data_without_birth_time_field() -> None:
    """AC3: PUT sans le champ birth_time est accepté (défaut=null)."""
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["birth_time"] is None


def test_get_birth_data_returns_astro_profile_block() -> None:
    """AC5: GET /birth-data inclut un bloc astro_profile."""
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    response = client.get(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "astro_profile" in data


def test_get_birth_data_null_birth_time_returns_missing_flag_in_astro_profile() -> None:
    """AC3 + AC5: GET /birth-data avec birth_time=null => astro_profile.missing_birth_time=true."""
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": None,
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    response = client.get(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "astro_profile" in data
    astro = data["astro_profile"]
    if astro is not None:
        assert astro["missing_birth_time"] is True
        assert astro["ascendant_sign_code"] is None


def test_get_birth_data_non_regression_404() -> None:
    """Non-régression: GET sans profil => 404."""
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.get(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "birth_profile_not_found"


def test_get_birth_data_returns_200_when_astro_profile_service_error(
    monkeypatch: object,
) -> None:
    """Erreur métier astro_profile => réponse 200 avec astro_profile=None."""
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )

    def _raise_service_error(*args: object, **kwargs: object) -> object:
        raise UserAstroProfileServiceError(
            code="reference_version_not_found",
            message="reference version not found",
            details={},
        )

    monkeypatch.setattr(
        "app.api.v1.routers.users.UserAstroProfileService.get_for_user",
        _raise_service_error,
    )

    response = client.get(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["astro_profile"] is None


def test_get_birth_data_returns_500_on_unexpected_astro_profile_error(
    monkeypatch: object,
) -> None:
    """Erreur inattendue astro_profile => 500 avec enveloppe standard."""
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )

    def _raise_runtime_error(*args: object, **kwargs: object) -> object:
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "app.api.v1.routers.users.UserAstroProfileService.get_for_user",
        _raise_runtime_error,
    )

    response = client.get(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "astro_profile_computation_error"
