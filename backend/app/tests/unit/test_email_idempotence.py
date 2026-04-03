import pytest
from sqlalchemy.orm import Session
from app.services.email_service import EmailService
from app.infra.db.models.email_log import EmailLogModel
from sqlalchemy import select

@pytest.mark.asyncio
async def test_email_idempotence(db_session: Session):
    user_id = 1
    email = "test@example.com"
    
    # First call
    success1 = await EmailService.send_welcome_email(db_session, user_id, email)
    assert success1 is True
    
    # Check log entry
    logs = db_session.execute(
        select(EmailLogModel).where(EmailLogModel.user_id == user_id, EmailLogModel.email_type == "welcome")
    ).scalars().all()
    assert len(logs) == 1
    assert logs[0].status == "skipped" # Because ENABLE_EMAIL is false by default in tests
    
    # Force status to 'sent' to test idempotence skip
    logs[0].status = "sent"
    db_session.commit()
    
    # Second call
    success2 = await EmailService.send_welcome_email(db_session, user_id, email)
    assert success2 is True
    
    # Check that no new log entry was created
    logs_after = db_session.execute(
        select(EmailLogModel).where(EmailLogModel.user_id == user_id, EmailLogModel.email_type == "welcome")
    ).scalars().all()
    assert len(logs_after) == 1
