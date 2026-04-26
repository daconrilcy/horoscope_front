"""Service canonique de scoring relatif des predictions quotidiennes."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
from datetime import date, datetime
from typing import TYPE_CHECKING

from app.core.datetime_provider import datetime_provider
from app.infra.db.repositories.user_prediction_baseline_repository import (
    UserPredictionBaselineRepository,
)
from app.prediction.persisted_baseline import V3Granularity
from app.prediction.relative_scoring_calculator import RelativeScoringCalculator

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.prediction.persisted_baseline import PersistedUserBaseline
    from app.prediction.persisted_snapshot import PersistedPredictionSnapshot


class RelativeScoringService:
    """Orchestre l enrichissement relatif d un snapshot de prediction."""

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
        """Enrichit un snapshot avec les scores relatifs V3 disponibles."""
        grouped_baselines = self._get_grouped_baselines(db, snapshot)
        raw_scores = {score.category_code: score.raw_score for score in snapshot.category_scores}
        relative_scores = self.calculator.compute_all(raw_scores, grouped_baselines)
        return replace(snapshot, relative_scores=relative_scores)

    def _get_grouped_baselines(
        self,
        db: Session,
        snapshot: PersistedPredictionSnapshot,
    ) -> dict[str, dict[str, PersistedUserBaseline]]:
        """Recupere les baselines compatibles par categorie et granularite."""
        repo = UserPredictionBaselineRepository(db)
        results: dict[str, dict[str, PersistedUserBaseline]] = defaultdict(dict)

        day_baselines = repo.get_latest_baselines_for_user(
            user_id=snapshot.user_id,
            reference_version_id=snapshot.reference_version_id,
            ruleset_id=snapshot.ruleset_id,
            house_system_effective=snapshot.house_system_effective or "placidus",
            window_days=365,
            as_of_date=snapshot.local_date,
            granularity_type=V3Granularity.DAY,
        )
        for baseline in day_baselines:
            results[baseline.category_code][V3Granularity.DAY.value] = baseline

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
        for baseline in season_baselines:
            if baseline.granularity_value == season:
                results[baseline.category_code][V3Granularity.SEASON.value] = baseline

        current_slot = self._get_time_slot(datetime_provider.now())
        slot_baselines = repo.get_latest_baselines_for_user(
            user_id=snapshot.user_id,
            reference_version_id=snapshot.reference_version_id,
            ruleset_id=snapshot.ruleset_id,
            house_system_effective=snapshot.house_system_effective or "placidus",
            window_days=365,
            as_of_date=snapshot.local_date,
            granularity_type=V3Granularity.SLOT,
        )
        for baseline in slot_baselines:
            if baseline.granularity_value == current_slot:
                results[baseline.category_code][V3Granularity.SLOT.value] = baseline

        return results

    def _get_season(self, dt: date) -> str:
        """Derive la saison metier a partir d une date locale."""
        month = dt.month
        if month in (12, 1, 2):
            return "winter"
        if month in (3, 4, 5):
            return "spring"
        if month in (6, 7, 8):
            return "summer"
        return "autumn"

    def _get_time_slot(self, dt: datetime) -> str:
        """Derive le slot horaire metier utilise par les baselines."""
        hour = dt.hour
        if 5 <= hour < 12:
            return "morning"
        if 12 <= hour < 18:
            return "afternoon"
        if 18 <= hour < 22:
            return "evening"
        return "night"
