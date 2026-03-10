from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from app.infra.db.repositories.user_prediction_baseline_repository import (
    UserPredictionBaselineRepository,
)
from app.prediction.relative_scoring_calculator import RelativeScoringCalculator

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.prediction.persisted_snapshot import PersistedPredictionSnapshot


logger = logging.getLogger(__name__)


class RelativeScoringService:
    """
    Service layer for relative scoring orchestration.
    AC4 Compliance: Decouples statistical logic from daily prediction service.
    """

    def __init__(
        self,
        calculator: RelativeScoringCalculator | None = None,
    ) -> None:
        self.calculator = calculator or RelativeScoringCalculator()

    def enrich_snapshot(
        self,
        db: Session,
        snapshot: PersistedPredictionSnapshot,
    ) -> PersistedPredictionSnapshot:
        """
        Enriches a prediction snapshot with relative scores based on user's baseline.
        """
        baselines = self._get_baselines(db, snapshot)
        
        raw_scores = {s.category_code: s.raw_score for s in snapshot.category_scores}
        
        relative_scores = self.calculator.compute_all(raw_scores, baselines)
        
        # Use dataclasses.replace to return a new enriched snapshot
        from dataclasses import replace
        return replace(snapshot, relative_scores=relative_scores)

    def _get_baselines(
        self,
        db: Session,
        snapshot: PersistedPredictionSnapshot,
    ) -> dict[str, Any]:
        repo = UserPredictionBaselineRepository(db)
        
        # We look for the most recent 365-day baseline compatible with the current run.
        baselines_list = repo.get_latest_baselines_for_user(
            user_id=snapshot.user_id,
            reference_version_id=snapshot.reference_version_id,
            ruleset_id=snapshot.ruleset_id,
            house_system_effective=snapshot.house_system_effective or "placidus",
            window_days=365,
            as_of_date=snapshot.local_date,
        )
        
        return {b.category_code: b for b in baselines_list}
