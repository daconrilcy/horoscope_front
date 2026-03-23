import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.infra.db.models.consultation_template import ConsultationTemplateModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.api.dependencies.auth import AuthenticatedUser

client = TestClient(app)

def _cleanup_catalogue():
    with SessionLocal() as db:
        db.query(ConsultationTemplateModel).delete()
        db.commit()

def _get_auth_headers(email="test-catalogue@example.com"):
    # Registration might fail if already exists, but we cleanup in some tests
    # For integration tests we usually use a dedicated test DB
    register = client.post(
        "/v1/auth/register",
        json={"email": email, "password": "strong-pass-123"},
    )
    if register.status_code == 200:
        token = register.json()["data"]["tokens"]["access_token"]
    else:
        # Try login
        login = client.post(
            "/v1/auth/login",
            json={"email": email, "password": "strong-pass-123"},
        )
        token = login.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_catalogue_empty():
    _cleanup_catalogue()
    headers = _get_auth_headers()
    response = client.get("/v1/consultations/catalogue", headers=headers)
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["meta"]["total"] == 0

def test_get_catalogue_with_items():
    _cleanup_catalogue()
    with SessionLocal() as db:
        db.add(ConsultationTemplateModel(
            id=uuid.uuid4(),
            key="test-1",
            icon_ref="🚀",
            title="Test Title",
            subtitle="Test Subtitle",
            description="Test Description",
            prompt_content="Test Prompt",
            metadata_config={"tags": ["Test"]},
            sort_order=10
        ))
        db.add(ConsultationTemplateModel(
            id=uuid.uuid4(),
            key="test-2",
            icon_ref="🌟",
            title="Test Title 2",
            subtitle="Test Subtitle 2",
            description="Test Description 2",
            prompt_content="Test Prompt 2",
            metadata_config={"tags": ["Test 2"]},
            sort_order=5
        ))
        db.commit()

    headers = _get_auth_headers()
    response = client.get("/v1/consultations/catalogue", headers=headers)
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 2
    # Check order (sort_order 5 before 10)
    assert items[0]["key"] == "test-2"
    assert items[1]["key"] == "test-1"

def test_legacy_mapping_precheck():
    headers = _get_auth_headers()
    # Mocking precheck response indirectly via router
    # We check if it accepts 'work' and returns something valid
    response = client.post(
        "/v1/consultations/precheck",
        json={"consultation_type": "work"},
        headers=headers
    )
    assert response.status_code == 200
    # Service should have mapped 'work' to 'career'
    assert response.json()["data"]["consultation_type"] == "career"

def test_legacy_mapping_generate():
    headers = _get_auth_headers()
    # Need birth data for generate
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
            "question": "Test legacy",
        },
        headers=headers
    )
    assert response.status_code == 200
    # Should be mapped to 'relationship'
    assert response.json()["data"]["consultation_type"] == "relationship"
