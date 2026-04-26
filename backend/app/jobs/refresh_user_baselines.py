from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from app.infra.db.repositories.user_prediction_baseline_repository import (
    UserPredictionBaselineRepository,
)
from app.infra.db.session import SessionLocal
from app.prediction.context_loader import PredictionContextLoader
from app.services.user_profile.prediction_baseline_service import UserPredictionBaselineService

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

NON_BLOCKING_REFRESH_ERROR_CODES = frozenset(
    {
        "version_missing",
        "ruleset_missing",
        "ruleset_inconsistent",
        "natal_missing",
        "profile_missing",
        "location_missing",
        "timezone_missing",
        "timezone_invalid",
    }
)


def refresh_user_baseline(db: Session, user_id: int) -> None:
    """Refreshes baseline for a specific user using current canonical versions."""
    from app.core.config import settings

    service = UserPredictionBaselineService(context_loader=PredictionContextLoader())
    service.generate_baseline(
        db=db,
        user_id=user_id,
        window_days=365,
        reference_version=settings.active_reference_version,
        ruleset_version=settings.ruleset_version,
    )


def safe_refresh_user_baseline(db: Session, user_id: int) -> None:
    """Runs refresh on the provided session and never breaks the caller flow."""
    from app.services.prediction.types import DailyPredictionServiceError

    try:
        refresh_user_baseline(db, user_id)
        db.commit()
    except DailyPredictionServiceError as exc:
        db.rollback()
        if exc.code in NON_BLOCKING_REFRESH_ERROR_CODES:
            logger.warning(
                "baseline_refresh_skipped user_id=%d code=%s error=%s",
                user_id,
                exc.code,
                exc.message,
            )
            return
        logger.exception(
            "baseline_refresh_failed user_id=%d code=%s error=%s",
            user_id,
            exc.code,
            exc.message,
        )
    except Exception:
        db.rollback()
        logger.exception("baseline_refresh_failed user_id=%d", user_id)


def run_job() -> None:
    """
    Job to refresh user baselines that are missing or obsolete.
    AC1, AC2, AC3 Compliance.
    """
    start_time_global = time.time()
    logger.info("Starting user baseline refresh job")

    with SessionLocal() as db:
        # Resolve global active versions
        from app.core.config import settings
        from app.infra.db.repositories.prediction_ruleset_repository import (
            PredictionRulesetRepository,
        )
        from app.infra.db.repositories.reference_repository import ReferenceRepository

        ref_repo = ReferenceRepository(db)
        ruleset_repo = PredictionRulesetRepository(db)

        ref_v = ref_repo.get_version(settings.active_reference_version)
        if not ref_v:
            logger.error("Active reference version %s not found", settings.active_reference_version)
            return

        ruleset_data = ruleset_repo.get_ruleset(settings.ruleset_version)
        if not ruleset_data:
            logger.error("Active ruleset version %s not found", settings.ruleset_version)
            return

        repo = UserPredictionBaselineRepository(db)
        user_ids = repo.get_users_needing_baseline(
            reference_version_id=ref_v.id,
            ruleset_id=ruleset_data.id,
            house_system_effective=ruleset_data.house_system,
            window_days=365,
        )

        if not user_ids:
            logger.info("No users need baseline refresh. Job completed.")
            return

        logger.info("Found %d users needing baseline refresh", len(user_ids))

        success_count = 0
        failed_count = 0

        for user_id in user_ids:
            try:
                # AC3: Structured logs
                logger.info("refreshing_baseline user_id=%d", user_id)

                refresh_user_baseline(db, user_id)

                db.commit()
                success_count += 1
                logger.info("baseline_refreshed user_id=%d status=success", user_id)

            except Exception as e:
                logger.error(
                    "baseline_refreshed user_id=%d status=failed error=%s", user_id, str(e)
                )
                db.rollback()
                failed_count += 1

    duration_global = time.time() - start_time_global
    logger.info(
        "Job completed. success=%d failed=%d duration=%.2fs",
        success_count,
        failed_count,
        duration_global,
    )


if __name__ == "__main__":
    run_job()
