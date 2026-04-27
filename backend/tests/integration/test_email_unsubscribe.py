import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.user import UserModel
from app.infra.db.session import get_db_session
from app.main import app
from app.services.email.service import EmailService
from tests.integration.app_db import open_app_db_session

client = TestClient(app)


@pytest.fixture
def db() -> Session:
    """Même base que l’app FastAPI (pas le SQLite :memory: du conftest générique)."""
    session = open_app_db_session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def _override_get_db_session(db: Session):
    app.dependency_overrides[get_db_session] = lambda: db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db: Session):
    user = UserModel(
        email=f"unsub-test-{uuid.uuid4().hex}@example.com",
        password_hash="hash",
        role="user",
        email_unsubscribed=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_unsubscribe_success(db: Session, test_user: UserModel):
    # Generate valid token
    token = EmailService.generate_unsubscribe_token(test_user.id, email_type="marketing")

    # Call endpoint
    response = client.get(f"/api/email/unsubscribe?token={token}")

    assert response.status_code == 200
    assert "Désabonnement réussi" in response.text

    # Check DB
    db.refresh(test_user)
    assert test_user.email_unsubscribed is True


def test_unsubscribe_invalid_email_type(db: Session, test_user: UserModel):
    # Generate token with wrong email_type
    token = EmailService.generate_unsubscribe_token(test_user.id, email_type="transactional")

    response = client.get(f"/api/email/unsubscribe?token={token}")

    assert response.status_code == 400
    assert "Lien de désabonnement non valide" in response.json()["error"]["message"]


def test_unsubscribe_expired_token(db: Session, test_user: UserModel):
    from datetime import datetime, timedelta, timezone

    import jwt

    from app.core.config import settings

    secret_key = settings.jwt_secret_key
    payload = {
        "user_id": test_user.id,
        "email_type": "marketing",
        "exp": datetime.now(timezone.utc) - timedelta(days=1),
    }
    expired_token = jwt.encode(payload, secret_key, algorithm="HS256")

    response = client.get(f"/api/email/unsubscribe?token={expired_token}")

    assert response.status_code == 400
    assert "Le lien de désabonnement a expiré" in response.json()["error"]["message"]


def test_unsubscribe_user_not_found(db: Session):
    # Generate token for non-existent user
    token = EmailService.generate_unsubscribe_token(9999, email_type="marketing")

    response = client.get(f"/api/email/unsubscribe?token={token}")

    assert response.status_code == 400
    assert "Utilisateur non trouvé" in response.json()["error"]["message"]


@pytest.mark.asyncio
async def test_email_service_skips_marketing_when_unsubscribed(db: Session, test_user: UserModel):
    # Mark user as unsubscribed
    test_user.email_unsubscribed = True
    db.commit()

    # Try to send marketing email
    result = await EmailService._send_email(
        db=db,
        user_id=test_user.id,
        email=test_user.email,
        email_type="marketing",
        template_name="dummy.html",  # Won't be used as it skips
        subject="Marketing",
        template_vars={},
    )

    assert result is True  # Returns True because it's skipped intentionally

    # Verify no log entry marked as 'sent'
    from app.infra.db.models.email_log import EmailLogModel

    logs = (
        db.execute(
            select(EmailLogModel).where(
                EmailLogModel.user_id == test_user.id, EmailLogModel.email_type == "marketing"
            )
        )
        .scalars()
        .all()
    )

    assert len(logs) == 0


@pytest.mark.asyncio
async def test_email_service_sends_welcome_even_if_unsubscribed(
    db: Session, test_user: UserModel, monkeypatch
):
    # Mark user as unsubscribed
    test_user.email_unsubscribed = True
    db.commit()

    # Mock provider to avoid actual sending
    async def mock_send(*args, **kwargs):
        return "msg-123"

    class MockProvider:
        async def send(self, *args, **kwargs):
            return "msg-123"

    monkeypatch.setattr("app.services.email.service.get_email_provider", lambda: MockProvider())
    monkeypatch.setattr(
        "app.services.email.service.EmailService._render_template", lambda *args, **kwargs: "html"
    )
    monkeypatch.setenv("ENABLE_EMAIL", "true")

    # Try to send welcome email (non-marketing)
    result = await EmailService.send_welcome_email(
        db=db, user_id=test_user.id, email=test_user.email, firstname="Test"
    )

    assert result is True

    # Verify log entry marked as 'sent'
    from app.infra.db.models.email_log import EmailLogModel

    log = (
        db.execute(
            select(EmailLogModel).where(
                EmailLogModel.user_id == test_user.id,
                EmailLogModel.email_type == "welcome",
                EmailLogModel.status == "sent",
            )
        )
        .scalars()
        .first()
    )

    assert log is not None
