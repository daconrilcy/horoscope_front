"""Bootstrap du seed QA canonique pour les environnements internes autorises."""

from __future__ import annotations

import logging

from app.core.config import settings
from app.infra.db.session import SessionLocal
from app.services.llm_generation.qa_seed_service import (
    LlmQaSeedService,
    LlmQaSeedServiceError,
)

logger = logging.getLogger(__name__)


async def seed_llm_qa_user() -> None:
    if not settings.llm_qa_seed_user_enabled:
        logger.info("llm_qa_seed_startup_disabled")
        return

    if not LlmQaSeedService.environment_allows_seed():
        logger.warning("llm_qa_seed_startup_skipped app_env=%s", settings.app_env)
        return

    with SessionLocal() as db:
        try:
            LlmQaSeedService.ensure_canonical_test_user(db)
        except LlmQaSeedServiceError as error:
            db.rollback()
            logger.warning(
                "llm_qa_seed_startup_failed code=%s message=%s",
                error.code,
                error.message,
            )
        except Exception:
            db.rollback()
            logger.exception("llm_qa_seed_startup_failed_unexpected")
