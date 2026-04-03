import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.main import app
from app.infra.db.models.user import UserModel
from app.services.email_service import EmailService

client = TestClient(app)

@pytest.fixture
def test_user(db_session: Session):
    user = UserModel(
        email="test@example.com",
        password_hash="hash",
        role="user",
        email_unsubscribed=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def test_unsubscribe_success(db_session: Session, test_user: UserModel):
    # Generate valid token
    token = EmailService.generate_unsubscribe_token(test_user.id, email_type="marketing")
    
    # Call endpoint
    response = client.get(f"/api/email/unsubscribe?token={token}")
    
    assert response.status_code == 200
    assert "Désabonnement réussi" in response.text
    
    # Check DB
    db_session.refresh(test_user)
    assert test_user.email_unsubscribed is True

def test_unsubscribe_invalid_email_type(db_session: Session, test_user: UserModel):
    # Generate token with wrong email_type
    token = EmailService.generate_unsubscribe_token(test_user.id, email_type="transactional")
    
    response = client.get(f"/api/email/unsubscribe?token={token}")
    
    assert response.status_code == 400
    assert "Lien de désabonnement non valide" in response.json()["detail"]

def test_unsubscribe_expired_token(db_session: Session, test_user: UserModel):
    import jwt
    import os
    from datetime import datetime, timedelta, timezone
    
    secret_key = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    payload = {
        "user_id": test_user.id,
        "email_type": "marketing",
        "exp": datetime.now(timezone.utc) - timedelta(days=1)
    }
    expired_token = jwt.encode(payload, secret_key, algorithm="HS256")
    
    response = client.get(f"/api/email/unsubscribe?token={expired_token}")
    
    assert response.status_code == 400
    assert "Le lien de désabonnement a expiré" in response.json()["detail"]

def test_unsubscribe_user_not_found(db_session: Session):
    # Generate token for non-existent user
    token = EmailService.generate_unsubscribe_token(9999, email_type="marketing")
    
    response = client.get(f"/api/email/unsubscribe?token={token}")
    
    assert response.status_code == 400
    assert "Utilisateur non trouvé" in response.json()["detail"]

@pytest.mark.asyncio
async def test_email_service_skips_marketing_when_unsubscribed(db_session: Session, test_user: UserModel):
    # Mark user as unsubscribed
    test_user.email_unsubscribed = True
    db_session.commit()
    
    # Try to send marketing email
    result = await EmailService._send_email(
        db=db_session,
        user_id=test_user.id,
        email=test_user.email,
        email_type="marketing",
        template_name="dummy.html", # Won't be used as it skips
        subject="Marketing",
        template_vars={}
    )
    
    assert result is True # Returns True because it's skipped intentionally
    
    # Verify no log entry marked as 'sent'
    from app.infra.db.models.email_log import EmailLogModel
    logs = db_session.execute(
        select(EmailLogModel).where(EmailLogModel.user_id == test_user.id, EmailLogModel.email_type == "marketing")
    ).scalars().all()
    
    assert len(logs) == 0

@pytest.mark.asyncio
async def test_email_service_sends_welcome_even_if_unsubscribed(db_session: Session, test_user: UserModel, monkeypatch):
    # Mark user as unsubscribed
    test_user.email_unsubscribed = True
    db_session.commit()
    
    # Mock provider to avoid actual sending
    async def mock_send(*args, **kwargs):
        return "msg-123"
    
    class MockProvider:
        async def send(self, *args, **kwargs):
            return "msg-123"
            
    monkeypatch.setattr("app.services.email_service.get_email_provider", lambda: MockProvider())
    monkeypatch.setattr("app.services.email_service.EmailService._render_template", lambda *args, **kwargs: "html")
    monkeypatch.setenv("ENABLE_EMAIL", "true")

    # Try to send welcome email (non-marketing)
    result = await EmailService.send_welcome_email(
        db=db_session,
        user_id=test_user.id,
        email=test_user.email,
        firstname="Test"
    )
    
    assert result is True
    
    # Verify log entry marked as 'sent'
    from app.infra.db.models.email_log import EmailLogModel
    log = db_session.execute(
        select(EmailLogModel).where(
            EmailLogModel.user_id == test_user.id, 
            EmailLogModel.email_type == "welcome",
            EmailLogModel.status == "sent"
        )
    ).scalars().first()
    
    assert log is not None
