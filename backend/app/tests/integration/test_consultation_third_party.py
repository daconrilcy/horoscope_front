from fastapi.testclient import TestClient
from sqlalchemy import delete

import app.infra.db.models  # noqa: F401
from app.infra.db.base import Base
from app.infra.db.models.user import UserModel
from app.infra.db.models.consultation_third_party import ConsultationThirdPartyProfileModel
from app.infra.db.session import SessionLocal, engine
from app.main import app

client = TestClient(app)

def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(ConsultationThirdPartyProfileModel))
        db.execute(delete(UserModel))
        db.commit()

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
        "birth_country": "France"
    }
    response = client.post("/v1/consultations/third-parties", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["nickname"] == "Partner"
    assert data["external_id"] is not None

def test_list_third_parties_with_data():
    _cleanup_tables()
    headers = _get_auth_headers(email="user_tp_list@example.com")
    # Create one
    client.post("/v1/consultations/third-parties", json={
        "nickname": "Friend",
        "birth_date": "1985-10-10",
        "birth_place": "Paris",
        "birth_city": "Paris",
        "birth_country": "France"
    }, headers=headers)
    
    response = client.get("/v1/consultations/third-parties", headers=headers)
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["nickname"] == "Friend"
