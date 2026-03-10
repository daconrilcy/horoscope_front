from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.infra.db.repositories.daily_prediction_repository import DailyPredictionRepository

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from datetime import date
    from app.infra.db.models.daily_prediction import DailyPredictionRunModel

logger = logging.getLogger()


@dataclass(frozen=True)
class FallbackDecision:
    success: bool
    fallback_run: DailyPredictionRunModel | None = None
    reason: str | None = None


class PredictionFallbackPolicy:
    """
    Handles the fallback logic when a prediction calculation fails.
    """

    def try_fallback(
        self,
        db: Session,
        user_id: int,
        requested_date: date,
    ) -> FallbackDecision:
        """
        Retrieves the most recent run before the requested date.
        """
        repo = DailyPredictionRepository(db)
        fallback_run = repo.get_latest_run_before(user_id, requested_date)
        
        if fallback_run:
            return FallbackDecision(success=True, fallback_run=fallback_run, reason="latest_available")
        
        return FallbackDecision(success=False, reason="no_historical_data")
