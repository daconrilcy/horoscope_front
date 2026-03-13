from fastapi.testclient import TestClient
from sqlalchemy import delete

import app.infra.db.models  # noqa: F401
from app.infra.db.base import Base
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from datetime import date

client = TestClient(app)

def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(UserBirthProfileModel))
        db.execute(delete(UserModel))
        db.commit()

def _register_and_get_access_token(email="user@example.com") -> str:
    register = client.post(
        "/v1/auth/register",
        json={"email": email, "password": "strong-pass-123"},
    )
    assert register.status_code == 200
    return register.json()["data"]["tokens"]["access_token"]

def test_precheck_unauthenticated():
    _cleanup_tables()
    response = client.post("/v1/consultations/precheck", json={"consultation_type": "period"})
    assert response.status_code == 401

def test_precheck_authenticated_no_profile():
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = client.post("/v1/consultations/precheck", json={"consultation_type": "period"}, headers=headers)
    
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["user_profile_quality"] == "missing"
    assert json_data["data"]["status"] == "blocked"

def test_precheck_authenticated_nominal():
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Create birth profile
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
    
    response = client.post("/v1/consultations/precheck", json={"consultation_type": "period"}, headers=headers)
    
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["consultation_type"] == "period"
    assert json_data["data"]["status"] == "nominal"
    assert json_data["data"]["user_profile_quality"] == "complete"
