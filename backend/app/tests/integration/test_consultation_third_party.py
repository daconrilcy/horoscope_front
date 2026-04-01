from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import app.infra.db.models  # noqa: F401
from app.infra.db.base import Base
from app.infra.db.repositories.consultation_third_party_repository import (
    ConsultationThirdPartyRepository,
)
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.thematic_consultation_entitlement_gate import ConsultationEntitlementResult

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_consultation_gate():
    with patch(
        "app.api.v1.routers.consultations.ThematicConsultationEntitlementGate.check_access"
    ) as mock:
        mock.return_value = ConsultationEntitlementResult(
            path="canonical_unlimited", usage_states=[]
        )
        yield mock



def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _get_auth_headers(email="user_tp@example.com"):
    register = client.post(
        "/v1/auth/register",
        json={"email": email, "password": "strong-pass-123"},
    )
    assert register.status_code == 200
    token = register.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_list_third_parties_empty():
    _cleanup_tables()
    headers = _get_auth_headers()
    response = client.get("/v1/consultations/third-parties", headers=headers)
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_create_third_party():
    _cleanup_tables()
    headers = _get_auth_headers(email="user_tp_create@example.com")
    payload = {
        "nickname": "Partner",
        "birth_date": "1992-05-15",
        "birth_place": "Lyon, France",
        "birth_city": "Lyon",
        "birth_country": "France",
    }
    response = client.post("/v1/consultations/third-parties", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["nickname"] == "Partner"
    assert data["external_id"] is not None


def test_list_third_parties_with_data():
    _cleanup_tables()
    headers = _get_auth_headers(email="user_tp_list@example.com")
    client.post(
        "/v1/consultations/third-parties",
        json={
            "nickname": "Friend",
            "birth_date": "1985-10-10",
            "birth_place": "Paris",
            "birth_city": "Paris",
            "birth_country": "France",
        },
        headers=headers,
    )

    response = client.get("/v1/consultations/third-parties", headers=headers)
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["nickname"] == "Friend"


def test_usage_recorded_and_returned():
    """AC8: la mise à jour de l'usage est tracée et retournée dans le listing."""
    _cleanup_tables()
    headers = _get_auth_headers(email="user_tp_usage@example.com")
    create_resp = client.post(
        "/v1/consultations/third-parties",
        json={
            "nickname": "Colleague",
            "birth_date": "1988-03-22",
            "birth_place": "Lyon, France",
            "birth_city": "Lyon",
            "birth_country": "France",
        },
        headers=headers,
    )
    assert create_resp.status_code == 200
    external_id = create_resp.json()["external_id"]

    with SessionLocal() as db:
        repo = ConsultationThirdPartyRepository(db)
        profile = repo.get_by_external_id(external_id)
        assert profile is not None
        repo.record_usage(
            third_party_profile_id=profile.id,
            consultation_id="consult_test_001",
            consultation_type="work",
            context_summary="Entretien avec un recruteur",
        )
        db.commit()

    list_resp = client.get("/v1/consultations/third-parties", headers=headers)
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    assert len(items) == 1
    assert len(items[0]["usage_history"]) == 1
    usage = items[0]["usage_history"][0]
    assert usage["consultation_id"] == "consult_test_001"
    assert usage["consultation_type"] == "work"
    assert usage["context_summary"] == "Entretien avec un recruteur"


def test_updated_at_refreshed_on_usage():
    """AC5: updated_at du profil est mis à jour lors d'un enregistrement d'usage."""
    _cleanup_tables()
    headers = _get_auth_headers(email="user_tp_updated@example.com")
    create_resp = client.post(
        "/v1/consultations/third-parties",
        json={
            "nickname": "OldContact",
            "birth_date": "1975-07-14",
            "birth_place": "Bordeaux",
            "birth_city": "Bordeaux",
            "birth_country": "France",
        },
        headers=headers,
    )
    assert create_resp.status_code == 200
    external_id = create_resp.json()["external_id"]

    with SessionLocal() as db:
        repo = ConsultationThirdPartyRepository(db)
        profile = repo.get_by_external_id(external_id)
        assert profile is not None
        created_updated_at = profile.updated_at
        repo.record_usage(
            third_party_profile_id=profile.id,
            consultation_id="consult_test_002",
            consultation_type="relation",
            context_summary="Synastrie",
        )
        db.commit()
        db.expire(profile)
        profile = repo.get_by_external_id(external_id)
        assert profile is not None
        assert profile.updated_at >= created_updated_at


def test_generate_records_usage_for_existing_third_party():
    _cleanup_tables()
    headers = _get_auth_headers(email="user_tp_generate@example.com")

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

    create_resp = client.post(
        "/v1/consultations/third-parties",
        json={
            "nickname": "Wife",
            "birth_date": "1988-03-22",
            "birth_time": "08:30",
            "birth_time_known": True,
            "birth_place": "Lyon, France",
            "birth_city": "Lyon",
            "birth_country": "France",
        },
        headers=headers,
    )
    assert create_resp.status_code == 200
    external_id = create_resp.json()["external_id"]

    response = client.post(
        "/v1/consultations/generate",
        json={
            "consultation_type": "relation",
            "question": "Comment evolue notre relation ?",
            "third_party_external_id": external_id,
            "other_person": {
                "birth_date": "1988-03-22",
                "birth_time": "08:30",
                "birth_time_known": True,
                "birth_place": "Lyon, France",
                "birth_city": "Lyon",
                "birth_country": "France",
            },
        },
        headers=headers,
    )

    assert response.status_code == 200

    list_resp = client.get("/v1/consultations/third-parties", headers=headers)
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    assert len(items) == 1
    assert len(items[0]["usage_history"]) == 1
    assert items[0]["usage_history"][0]["consultation_type"] == "relationship"


def test_generate_can_save_new_third_party_for_later_reuse():
    _cleanup_tables()
    headers = _get_auth_headers(email="user_tp_save@example.com")

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
            "question": "Que comprendre de cette relation ?",
            "save_third_party": True,
            "third_party_nickname": "Partenaire",
            "other_person": {
                "birth_date": "1988-03-22",
                "birth_time": "08:30",
                "birth_time_known": True,
                "birth_place": "Arras, France",
                "birth_city": "Arras",
                "birth_country": "France",
                "birth_lat": 50.291,
                "birth_lon": 2.777,
            },
        },
        headers=headers,
    )

    assert response.status_code == 200

    list_resp = client.get("/v1/consultations/third-parties", headers=headers)
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    assert len(items) == 1
    assert items[0]["nickname"] == "Partenaire"
    assert items[0]["birth_date"] == "1988-03-22"
    assert items[0]["birth_city"] == "Arras"
    assert len(items[0]["usage_history"]) == 1
