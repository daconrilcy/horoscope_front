from __future__ import annotations

import asyncio
import logging

from app.core.config import settings
from app.core.security import hash_password
from app.infra.db.models.user import UserModel

logger = logging.getLogger(__name__)


def _seed_dev_admin_sync() -> None:
    """
    Seed a default admin user if in development environment and no admin exists.
    """
    from app.infra.db.session import SessionLocal

    # Guard strict: check APP_ENV or SEED_ADMIN
    is_allowed_env = settings.app_env in {"development", "dev", "local", "test", "testing"}
    if not is_allowed_env and not settings.seed_admin:
        return

    admin_email = "admin@test.com"
    admin_password = "admin123"
    admin_role = "admin"

    try:
        with SessionLocal() as db:
            # Check for existing user with role 'admin'
            existing_admin = db.query(UserModel).filter(UserModel.role == admin_role).first()
            if existing_admin:
                return

            # Also check if the specific email is already taken
            existing_user = db.query(UserModel).filter(UserModel.email == admin_email).first()
            if existing_user:
                logger.warning(
                    "dev_seed_admin_skip: user with email %s already exists but is not an admin",
                    admin_email,
                )
                return

            logger.info("dev_seed_admin_creating email=%s", admin_email)
            admin_user = UserModel(
                email=admin_email,
                password_hash=hash_password(admin_password),
                role=admin_role,
                astrologer_profile="standard",
                email_unsubscribed=False,
            )
            db.add(admin_user)
            db.commit()
            logger.info("dev_seed_admin_success email=%s", admin_email)

    except Exception as e:
        logger.error("dev_seed_admin_failed error=%s", e)


async def seed_dev_admin() -> None:
    await asyncio.to_thread(_seed_dev_admin_sync)
