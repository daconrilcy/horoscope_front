from __future__ import annotations

import logging
import math
from typing import TYPE_CHECKING

from app.prediction.persisted_relative_score import PersistedRelativeScore

if TYPE_CHECKING:
    from app.prediction.persisted_baseline import PersistedUserBaseline

logger = logging.getLogger(__name__)


class RelativeScoringCalculator:
    """
    Calculates relative metrics for categories against a user's baseline.
    AC2 Compliance: Explicit handling of variance null and missing baseline.
    V3 Compliance: Support for granular baselines (day, slot, season).
    """

    def compute_all(
        self,
        raw_scores: dict[str, float],
        granular_baselines: dict[str, dict[str, PersistedUserBaseline] | PersistedUserBaseline],
    ) -> dict[str, PersistedRelativeScore]:
        """
        Computes all relative scores and ranks them.
        AC1 Compliance: Returns a map of category code to its relative score metrics.
        granular_baselines: category_code -> {granularity_type: baseline}
        """
        relative_scores: dict[str, PersistedRelativeScore] = {}

        # 1. Individual metrics calculation
        for category_code, raw_score in raw_scores.items():
            category_baselines = self._coerce_baselines(granular_baselines.get(category_code))
            relative_scores[category_code] = self._compute_category_relative(
                category_code, raw_score, category_baselines
            )

        # 2. Ranking by ABSOLUTE relative intensity (z_abs)
        # AC: high relief (positive or negative) should be ranked high.
        available_scores = [
            (code, self._ranking_value(score))
            for code, score in relative_scores.items()
            if score.is_available and self._ranking_value(score) is not None
        ]

        # Stable sort: absolute intensity descending
        available_scores.sort(key=lambda item: (-item[1], item[0]))

        ranked_results: dict[str, PersistedRelativeScore] = {}
        for code, score in relative_scores.items():
            rank: int | None = None
            if score.is_available and self._ranking_value(score) is not None:
                for i, (ranked_code, _) in enumerate(available_scores):
                    if ranked_code == code:
                        rank = i + 1
                        break
            
            from dataclasses import replace
            ranked_results[code] = replace(score, relative_rank=rank)

        return ranked_results

    def _compute_category_relative(
        self,
        category_code: str,
        raw_score: float,
        baselines: dict[str, PersistedUserBaseline],
    ) -> PersistedRelativeScore:
        day_baseline = baselines.get("day")
        slot_baseline = baselines.get("slot")
        season_baseline = baselines.get("season")
        
        # 1. Day metrics (z_abs, pct_abs)
        z_abs, pct_abs, fallback_day = self._calculate_stats(raw_score, day_baseline)
        
        # 2. Slot metrics (z_slot, pct_rel)
        z_slot, pct_rel, _ = self._calculate_stats(raw_score, slot_baseline)
        
        # 3. Season metrics (z_season, pct_season)
        z_season, pct_season, _ = self._calculate_stats(raw_score, season_baseline)
        
        # 4. Rarity derivation (AC1)
        # Fallback to percentile if z is missing
        rarity: float | None = None
        if z_abs is not None:
            # 0.0 to 1.0 index of how unusual this is. 
            # 2.0 sigma -> ~0.74, 3.0 sigma -> ~0.86
            rarity = 1.0 - math.exp(-abs(z_abs) / 1.5)
        elif pct_abs is not None:
            # Distance from median
            rarity = abs(pct_abs - 0.5) * 2.0

        return PersistedRelativeScore(
            category_code=category_code,
            relative_z_score=z_abs,  
            relative_percentile=pct_abs,
            relative_rank=None,
            z_abs=z_abs,
            z_slot=z_slot,
            z_season=z_season,
            pct_abs=pct_abs,
            pct_rel=pct_rel,
            pct_season=pct_season,
            rarity=rarity,
            is_available=any(
                metric is not None
                for metric in (z_abs, z_slot, z_season, pct_abs, pct_rel, pct_season)
            ),
            fallback_reason=fallback_day,
        )

    def _calculate_stats(
        self, raw_score: float, baseline: PersistedUserBaseline | None
    ) -> tuple[float | None, float | None, str | None]:
        if baseline is None:
            return None, None, "baseline_missing"

        if baseline.sample_size_days < 30:
            return None, None, "sample_too_small"

        # Z-Score
        z_score: float | None = None
        fallback_reason: str | None = None
        if baseline.std_raw_score > 1e-6:
            z_score = (raw_score - baseline.mean_raw_score) / baseline.std_raw_score
        else:
            fallback_reason = "variance_null"

        # Percentile approximation
        percentile: float | None = None
        if raw_score >= baseline.p90:
            diff = min(raw_score, baseline.p90 * 2) - baseline.p90
            percentile = 0.9 + (diff / max(baseline.p90, 1.0)) * 0.1
            percentile = min(percentile, 0.99)
        elif raw_score >= baseline.p50:
            denom = max(baseline.p90 - baseline.p50, 0.001)
            percentile = 0.5 + (raw_score - baseline.p50) / denom * 0.4
        elif raw_score >= baseline.p10:
            denom = max(baseline.p50 - baseline.p10, 0.001)
            percentile = 0.1 + (raw_score - baseline.p10) / denom * 0.4
        else:
            percentile = 0.05

        return z_score, percentile, fallback_reason

    def _ranking_value(self, score: PersistedRelativeScore) -> float | None:
        if score.z_abs is not None:
            return abs(score.z_abs)  # AC: Rank by intensity (abs)
        return score.pct_abs

    def _coerce_baselines(
        self,
        baselines: dict[str, PersistedUserBaseline] | PersistedUserBaseline | None,
    ) -> dict[str, PersistedUserBaseline]:
        if baselines is None:
            return {}
        if isinstance(baselines, dict):
            return baselines
        return {"day": baselines}
