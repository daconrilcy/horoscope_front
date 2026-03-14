from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import replace
from datetime import date, datetime
from typing import TYPE_CHECKING

from app.infra.db.repositories.user_prediction_baseline_repository import (
    UserPredictionBaselineRepository,
)
from app.prediction.persisted_baseline import V3Granularity
from app.prediction.relative_scoring_calculator import RelativeScoringCalculator

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.prediction.persisted_baseline import PersistedUserBaseline
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
        Enriches a prediction snapshot with V3 relative scores.
        """
        # Map of category_code -> {granularity_type: baseline}
        grouped_baselines = self._get_grouped_baselines(db, snapshot)

        raw_scores = {s.category_code: s.raw_score for s in snapshot.category_scores}

        relative_scores = self.calculator.compute_all(raw_scores, grouped_baselines)

        return replace(snapshot, relative_scores=relative_scores)

    def _get_grouped_baselines(
        self,
        db: Session,
        snapshot: PersistedPredictionSnapshot,
    ) -> dict[str, dict[str, PersistedUserBaseline]]:
        repo = UserPredictionBaselineRepository(db)
        results: dict[str, dict[str, PersistedUserBaseline]] = defaultdict(dict)

        # 1. DAY level
        day_baselines = repo.get_latest_baselines_for_user(
            user_id=snapshot.user_id,
            reference_version_id=snapshot.reference_version_id,
            ruleset_id=snapshot.ruleset_id,
            house_system_effective=snapshot.house_system_effective or "placidus",
            window_days=365,
            as_of_date=snapshot.local_date,
            granularity_type=V3Granularity.DAY,
        )
        for b in day_baselines:
            results[b.category_code][V3Granularity.DAY.value] = b

        # 2. SEASON level
        season = self._get_season(snapshot.local_date)
        season_baselines = repo.get_latest_baselines_for_user(
            user_id=snapshot.user_id,
            reference_version_id=snapshot.reference_version_id,
            ruleset_id=snapshot.ruleset_id,
            house_system_effective=snapshot.house_system_effective or "placidus",
            window_days=365,
            as_of_date=snapshot.local_date,
            granularity_type=V3Granularity.SEASON,
        )
        for b in season_baselines:
            if b.granularity_value == season:
                results[b.category_code][V3Granularity.SEASON.value] = b

        # 3. SLOT level (We use current time to find the active slot)
        now_local = datetime.now()  # This is a bit weak, should ideally use request context
        # But for snapshots, we might look for common slots
        current_slot = self._get_time_slot(now_local)
        slot_baselines = repo.get_latest_baselines_for_user(
            user_id=snapshot.user_id,
            reference_version_id=snapshot.reference_version_id,
            ruleset_id=snapshot.ruleset_id,
            house_system_effective=snapshot.house_system_effective or "placidus",
            window_days=365,
            as_of_date=snapshot.local_date,
            granularity_type=V3Granularity.SLOT,
        )
        for b in slot_baselines:
            if b.granularity_value == current_slot:
                results[b.category_code][V3Granularity.SLOT.value] = b

        return results

    def _get_season(self, dt: date) -> str:
        month = dt.month
        if month in (12, 1, 2):
            return "winter"
        if month in (3, 4, 5):
            return "spring"
        if month in (6, 7, 8):
            return "summer"
        return "autumn"

    def _get_time_slot(self, dt: datetime) -> str:
        hour = dt.hour
        if 5 <= hour < 12:
            return "morning"
        if 12 <= hour < 18:
            return "afternoon"
        if 18 <= hour < 22:
            return "evening"
        return "night"
