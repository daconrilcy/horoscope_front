from pathlib import Path
from datetime import UTC, datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db import session as db_session_module
from app.infra.db.base import Base
from app.infra.db.models.user import UserModel
from app.infra.db.models.support_incident import SupportIncidentModel
from app.infra.db.models.flagged_content import FlaggedContentModel
from app.infra.db.models.audit_event import AuditEventModel
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def _isolated_database(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'test-admin-support.db').as_posix()}"
    test_engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        future=True,
    )
    test_session_local = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )
    monkeypatch.setattr(db_session_module, "engine", test_engine)
    monkeypatch.setattr(db_session_module, "SessionLocal", test_session_local)
    Base.metadata.create_all(bind=test_engine)
    try:
        yield
    finally:
        test_engine.dispose()

@pytest.fixture
def admin_token():
    with db_session_module.SessionLocal() as db:
        from app.core.security import hash_password
        admin = UserModel(
            email="admin-support@example.com",
            password_hash=hash_password("admin123"),
            role="admin",
            astrologer_profile="standard"
        )
        db.add(admin)
        db.commit()
    
    response = client.post("/v1/auth/login", json={
        "email": "admin-support@example.com",
        "password": "admin123"
    })
    return response.json()["data"]["tokens"]["access_token"]

def test_list_tickets_and_flagged_content(admin_token):
    with db_session_module.SessionLocal() as db:
        user = UserModel(email="user-support@test.com", password_hash="x", role="user")
        db.add(user)
        db.flush()
        
        ticket = SupportIncidentModel(
            user_id=user.id,
            category="billing",
            title="Billing issue",
            description="I was double charged",
            status="open",
            priority="high"
        )
        db.add(ticket)
        
        flagged = FlaggedContentModel(
            user_id=user.id,
            content_type="chat_message",
            content_ref_id="msg_1",
            excerpt="Offensive content",
            status="pending"
        )
        db.add(flagged)
        db.commit()
        ticket_id = ticket.id
        flagged_id = flagged.id

    # 1. List Tickets
    response = client.get("/v1/admin/support/tickets", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    
    # 2. Update Ticket Status
    response = client.patch(
        f"/v1/admin/support/tickets/{ticket_id}", 
        json={"status": "resolved"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    # 3. List Flagged Content
    response = client.get("/v1/admin/support/flagged-content", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    
    # 4. Review Flagged Content
    response = client.patch(
        f"/v1/admin/support/flagged-content/{flagged_id}", 
        json={"status": "resolved"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    with db_session_module.SessionLocal() as db:
        # Check audit logs
        audit_ticket = db.scalar(select(AuditEventModel).where(AuditEventModel.action == "support_ticket_action"))
        assert audit_ticket is not None
        audit_flagged = db.scalar(select(AuditEventModel).where(AuditEventModel.action == "flagged_content_reviewed"))
        assert audit_flagged is not None
