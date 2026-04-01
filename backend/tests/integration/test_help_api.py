from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.support_incident import SupportIncidentModel
from app.infra.db.models.support_ticket_category import SupportTicketCategoryModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.main import app

client = TestClient(app)

def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(SupportIncidentModel))
        db.execute(delete(SupportTicketCategoryModel))
        db.execute(delete(UserModel))
        db.commit()

def _register_and_get_access_token(email: str = "user@example.com") -> str:
    register = client.post(
        "/v1/auth/register",
        json={"email": email, "password": "strong-pass-123"},
    )
    assert register.status_code == 200
    return register.json()["data"]["tokens"]["access_token"]

def _seed_categories():
    with SessionLocal() as db:
        cat1 = SupportTicketCategoryModel(
            code="bug", label_fr="Bug", label_en="Bug", label_es="Error", display_order=1
        )
        cat2 = SupportTicketCategoryModel(
            code="other", label_fr="Autre", label_en="Other", label_es="Otro", display_order=2
        )
        db.add_all([cat1, cat2])
        db.commit()

def test_get_help_categories_success() -> None:
    _cleanup_tables()
    _seed_categories()
    token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/v1/help/categories?lang=fr", headers=headers)
    assert response.status_code == 200
    categories = response.json()["data"]["categories"]
    assert len(categories) == 2
    assert categories[0]["code"] == "bug"
    assert categories[0]["label"] == "Bug"

def test_create_help_ticket_success() -> None:
    _cleanup_tables()
    _seed_categories()
    token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "category_code": "bug",
        "subject": "Test Subject",
        "description": "This is a test description with at least 20 characters."
    }
    response = client.post("/v1/help/tickets", headers=headers, json=payload)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["status"] == "pending"
    assert data["category_code"] == "bug"
    assert data["subject"] == "Test Subject"

def test_create_help_ticket_invalid_category() -> None:
    _cleanup_tables()
    token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "category_code": "non_existent",
        "subject": "Test Subject",
        "description": "This is a test description."
    }
    response = client.post("/v1/help/tickets", headers=headers, json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "ticket_invalid_category"

def test_list_help_tickets_success() -> None:
    _cleanup_tables()
    _seed_categories()
    token = _register_and_get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a ticket
    create_resp = client.post("/v1/help/tickets", headers=headers, json={
        "category_code": "bug",
        "subject": "Ticket 1",
        "description": "Description for ticket 1"
    })
    assert create_resp.status_code == 201
    
    response = client.get("/v1/help/tickets", headers=headers)
    assert response.status_code == 200
    tickets = response.json()["data"]["tickets"]
    assert len(tickets) == 1
    assert tickets[0]["subject"] == "Ticket 1"

def test_list_help_tickets_only_own_tickets() -> None:
    _cleanup_tables()
    _seed_categories()
    token1 = _register_and_get_access_token("user1@example.com")
    token2 = _register_and_get_access_token("user2@example.com")
    
    # User 1 creates a ticket
    client.post("/v1/help/tickets", headers={"Authorization": f"Bearer {token1}"}, json={
        "category_code": "bug",
        "subject": "User 1 Ticket",
        "description": "Description for user 1"
    })
    
    # User 2 lists tickets
    response = client.get("/v1/help/tickets", headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 200
    assert len(response.json()["data"]["tickets"]) == 0
