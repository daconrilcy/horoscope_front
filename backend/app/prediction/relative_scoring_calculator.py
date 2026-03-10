from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.prediction.persisted_relative_score import PersistedRelativeScore

if TYPE_CHECKING:
    from app.prediction.persisted_baseline import PersistedUserBaseline

logger = logging.getLogger(__name__)


class RelativeScoringCalculator:
    """
    Calculates relative metrics for categories against a user's baseline.
    AC2 Compliance: Explicit handling of variance null and missing baseline.
    """

    def compute_all(
        self,
        raw_scores: dict[str, float],
        baselines: dict[str, PersistedUserBaseline],
    ) -> dict[str, PersistedRelativeScore]:
        """
        Computes all relative scores and ranks them.
        AC1 Compliance: Returns a map of category code to its relative score metrics.
        """
        relative_scores: dict[str, PersistedRelativeScore] = {}

        # 1. Individual metrics calculation (z-score, percentile)
        for category_code, raw_score in raw_scores.items():
            baseline = baselines.get(category_code)
            relative_scores[category_code] = self._compute_category_relative(
                category_code, raw_score, baseline
            )

        # 2. Ranking by relative intensity, falling back to percentile when needed.
        available_scores = [
            (code, self._ranking_value(score))
            for code, score in relative_scores.items()
            if score.is_available and self._ranking_value(score) is not None
        ]

        # Stable sort: relative intensity descending, then code alphabetical.
        available_scores.sort(key=lambda item: (-item[1], item[0]))

        ranked_results: dict[str, PersistedRelativeScore] = {}
        for code, score in relative_scores.items():
            rank: int | None = None
            if score.is_available and self._ranking_value(score) is not None:
                for i, (ranked_code, _) in enumerate(available_scores):
                    if ranked_code == code:
                        rank = i + 1
                        break
            
            # Re-create with rank
            ranked_results[code] = PersistedRelativeScore(
                category_code=score.category_code,
                relative_z_score=score.relative_z_score,
                relative_percentile=score.relative_percentile,
                relative_rank=rank,
                is_available=score.is_available,
                fallback_reason=score.fallback_reason,
            )

        return ranked_results

    def _compute_category_relative(
        self,
        category_code: str,
        raw_score: float,
        baseline: PersistedUserBaseline | None,
    ) -> PersistedRelativeScore:
        if baseline is None:
            return PersistedRelativeScore(
                category_code=category_code,
                relative_z_score=None,
                relative_percentile=None,
                relative_rank=None,
                is_available=False,
                fallback_reason="baseline_missing",
            )

        if baseline.sample_size_days < 30:
            return PersistedRelativeScore(
                category_code=category_code,
                relative_z_score=None,
                relative_percentile=None,
                relative_rank=None,
                is_available=False,
                fallback_reason="sample_too_small",
            )

        # 1. Z-Score (robust proxy)
        # AC2 Compliance: Safe on null variance
        z_score: float | None = None
        fallback_reason: str | None = None
        if baseline.std_raw_score > 0:
            z_score = (raw_score - baseline.mean_raw_score) / baseline.std_raw_score
        else:
            fallback_reason = "variance_null"

        # 2. Percentile based on p10, p50, p90 (approximation)
        # AC1 Compliance: Percentile fallback when std is 0
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

        return PersistedRelativeScore(
            category_code=category_code,
            relative_z_score=z_score,
            relative_percentile=percentile,
            relative_rank=None,  # Handled in compute_all
            is_available=percentile is not None,
            fallback_reason=fallback_reason,
        )

    def _ranking_value(self, score: PersistedRelativeScore) -> float | None:
        if score.relative_z_score is not None:
            return score.relative_z_score
        return score.relative_percentile
