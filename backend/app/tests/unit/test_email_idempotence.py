"""Tests unitaires de l'idempotence des emails applicatifs."""

from unittest.mock import patch

import pytest
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.infra.db.models.email_log import EmailLogModel
from app.infra.db.models.user import UserModel
from app.services.email import service as email_service_module
from app.services.email.service import EmailService


@pytest.mark.asyncio
async def test_email_idempotence_granular_types(db_session: Session):
    with patch.object(email_service_module, "SessionLocal", return_value=db_session):
        # Le test utilise un vrai utilisateur dans la DB de test canonique.
        user = UserModel(email="granular@example.com", password_hash="hash", role="user")
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        email = user.email

        await EmailService.send_welcome_email(db_session, user_id, email)

        # Force l'etat envoye pour verifier l'idempotence par type.
        db_session.execute(
            update(EmailLogModel)
            .where(EmailLogModel.user_id == user_id, EmailLogModel.email_type == "welcome")
            .values(status="sent")
        )
        db_session.commit()

        success_repeat = await EmailService.send_welcome_email(db_session, user_id, email)
        assert success_repeat is True

        await EmailService.send_education_email_task(user_id, email, "Granular")

        logs = (
            db_session.execute(select(EmailLogModel).where(EmailLogModel.user_id == user_id))
            .scalars()
            .all()
        )

        types = [log.email_type for log in logs]
        assert "welcome" in types
        assert "onboarding_j1_education" in types
