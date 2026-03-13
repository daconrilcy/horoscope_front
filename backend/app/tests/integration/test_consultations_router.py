from fastapi.testclient import TestClient
from sqlalchemy import delete

import app.infra.db.models  # noqa: F401
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


def _get_auth_headers(email="user@example.com"):
    register = client.post(
        "/v1/auth/register",
        json={"email": email, "password": "strong-pass-123"},
    )
    assert register.status_code == 200
    token = register.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_precheck_unauthenticated():
    _cleanup_tables()
    response = client.post("/v1/consultations/precheck", json={"consultation_type": "period"})
    assert response.status_code == 401


def test_precheck_authenticated_no_profile():
    _cleanup_tables()
    headers = _get_auth_headers()
    response = client.post(
        "/v1/consultations/precheck",
        json={"consultation_type": "period"},
        headers=headers,
    )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["user_profile_quality"] == "missing"
    assert json_data["data"]["status"] == "blocked"


def test_precheck_authenticated_nominal():
    _cleanup_tables()
    headers = _get_auth_headers()

    client.put(
        "/v1/users/me/birth-data",
        headers=headers,
        json={
            "birth_date": "1990-01-01",
            "birth_time": "12:00",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )

    response = client.post(
        "/v1/consultations/precheck",
        json={"consultation_type": "period"},
        headers=headers,
    )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["consultation_type"] == "period"
    assert json_data["data"]["status"] == "nominal"
    assert json_data["data"]["user_profile_quality"] == "complete"


def test_generate_authenticated_nominal():
    _cleanup_tables()
    headers = _get_auth_headers()

    client.put(
        "/v1/users/me/birth-data",
        headers=headers,
        json={
            "birth_date": "1990-01-01",
            "birth_time": "12:00",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )

    response = client.post(
        "/v1/consultations/generate",
        json={
            "consultation_type": "period",
            "question": "Comment va se passer mon mois ?",
        },
        headers=headers,
    )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["consultation_type"] == "period"
    assert json_data["data"]["status"] == "nominal"
    assert json_data["data"]["route_key"] == "period_full"
    assert len(json_data["data"]["sections"]) > 0


def test_precheck_accepts_enriched_other_person_payload():
    _cleanup_tables()
    headers = _get_auth_headers()

    client.put(
        "/v1/users/me/birth-data",
        headers=headers,
        json={
            "birth_date": "1990-01-01",
            "birth_time": "12:00",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )

    response = client.post(
        "/v1/consultations/precheck",
        json={
            "consultation_type": "relation",
            "question": "Que comprendre de cette rencontre ?",
            "other_person": {
                "birth_date": "1992-05-04",
                "birth_time": "08:15",
                "birth_time_known": True,
                "birth_place": "Paris, Ile-de-France, France",
                "birth_city": "Paris",
                "birth_country": "France",
                "place_resolved_id": 777,
                "birth_lat": 48.8566,
                "birth_lon": 2.3522,
            },
        },
        headers=headers,
    )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["consultation_type"] == "relation"
    assert json_data["data"]["status"] == "nominal"


def test_generate_accepts_enriched_other_person_payload():
    _cleanup_tables()
    headers = _get_auth_headers(email="other@example.com")

    client.put(
        "/v1/users/me/birth-data",
        headers=headers,
        json={
            "birth_date": "1990-01-01",
            "birth_time": "12:00",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )

    response = client.post(
        "/v1/consultations/generate",
        json={
            "consultation_type": "relation",
            "question": "Quel est le climat de cette relation ?",
            "other_person": {
                "birth_date": "1992-05-04",
                "birth_time": "08:15",
                "birth_time_known": True,
                "birth_place": "Paris, Ile-de-France, France",
                "birth_city": "Paris",
                "birth_country": "France",
                "place_resolved_id": 777,
                "birth_lat": 48.8566,
                "birth_lon": 2.3522,
            },
        },
        headers=headers,
    )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["consultation_type"] == "relation"
    assert json_data["data"]["status"] == "nominal"
    assert json_data["data"]["route_key"] == "relation_full_full"
