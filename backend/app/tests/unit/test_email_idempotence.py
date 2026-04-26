from unittest.mock import patch

import pytest
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.infra.db.models.email_log import EmailLogModel
from app.infra.db.models.user import UserModel
from app.services.email.service import EmailService


@pytest.mark.asyncio
async def test_email_idempotence_granular_types(db_session: Session):
    # Mock SessionLocal to return our test session
    with patch("app.infra.db.session.SessionLocal", return_value=db_session):
        # Setup: Create a real user in the test DB
        user = UserModel(email="granular@example.com", password_hash="hash", role="user")
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        email = user.email

        # 1. Send welcome email
        await EmailService.send_welcome_email(db_session, user_id, email)

        # 2. Mock it as 'sent'
        db_session.execute(
            update(EmailLogModel)
            .where(EmailLogModel.user_id == user_id, EmailLogModel.email_type == "welcome")
            .values(status="sent")
        )
        db_session.commit()

        # 3. Sending welcome again should be skipped
        success_repeat = await EmailService.send_welcome_email(db_session, user_id, email)
        assert success_repeat is True

        # 4. Sending a DIFFERENT type should NOT be skipped
        await EmailService.send_education_email_task(user_id, email, "Granular")

        # Verify we have logs for both types
        logs = (
            db_session.execute(select(EmailLogModel).where(EmailLogModel.user_id == user_id))
            .scalars()
            .all()
        )

        types = [log.email_type for log in logs]
        assert "welcome" in types
        assert "onboarding_j1_education" in types
