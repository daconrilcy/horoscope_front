from __future__ import annotations

import logging
import statistics
import time
from collections import defaultdict
from dataclasses import replace
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Any

from app.infra.db.repositories.prediction_reference_repository import (
    PredictionReferenceRepository,
)
from app.infra.db.repositories.user_prediction_baseline_repository import (
    UserPredictionBaselineRepository,
)
from app.prediction.engine_orchestrator import EngineOrchestrator
from app.prediction.persisted_baseline import V3Granularity
from app.services.prediction_request_resolver import PredictionRequestResolver

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.prediction.context_loader import PredictionContextLoader
    from app.prediction.persisted_baseline import PersistedUserBaseline

logger = logging.getLogger(__name__)


class UserPredictionBaselineService:
    def __init__(
        self,
        context_loader: PredictionContextLoader,
        *,
        orchestrator: EngineOrchestrator | None = None,
        resolver: PredictionRequestResolver | None = None,
    ) -> None:
        self.context_loader = context_loader
        self.orchestrator = orchestrator or EngineOrchestrator()
        self.resolver = resolver or PredictionRequestResolver()

    def generate_baseline(
        self,
        db: Session,
        user_id: int,
        window_days: int = 365,
        reference_version: str | None = None,
        ruleset_version: str | None = None,
        end_date: date | None = None,
    ) -> dict[str, PersistedUserBaseline]:
        """
        Generates extended baselines (day, slot, season) for a user.
        AC1, AC2 Story 42.12.
        """
        start_time_perf = time.perf_counter()

        resolved = self.resolver.resolve(
            db=db,
            user_id=user_id,
            date_local=end_date,
            reference_version=reference_version,
            ruleset_version=ruleset_version,
            include_engine_input=True,
        )

        if not resolved.engine_input:
            raise ValueError(f"Could not resolve engine input for user {user_id}")

        end_date = resolved.resolved_date
        start_date = end_date - timedelta(days=window_days - 1)

        def ctx_loader(ref: str, rule: str, dt: date) -> Any:
            return self.context_loader.load(db, ref, rule, dt)

        orch = self.orchestrator.with_context_loader(ctx_loader)

        ref_repo = PredictionReferenceRepository(db)
        categories = ref_repo.get_categories(resolved.reference_version_id)
        cat_map = {category.code: category.id for category in categories}

        # Accumulators: (granularity_type, granularity_value, cat_code) -> list[raw_scores]
        # For simplicity in 42.12, we collect everything in one pass
        accumulators: dict[tuple[str, str, str], list[float]] = defaultdict(list)
        accumulators_notes: dict[tuple[str, str, str], list[int]] = defaultdict(list)

        current_date = start_date
        house_system_effective: str | None = None

        while current_date <= end_date:
            engine_input = replace(resolved.engine_input, local_date=current_date)
            # Run engine V3 to get rich metrics if available
            bundle = orch.run(engine_input, include_editorial=False, engine_mode="v3")

            if house_system_effective is None:
                house_system_effective = (
                    bundle.core.effective_context.house_system_effective or "placidus"
                )

            # 1. Day level accumulation
            for cat_code, scores in bundle.core.category_scores.items():
                accumulators[(V3Granularity.DAY, "all", cat_code)].append(
                    float(scores["raw_score"])
                )
                accumulators_notes[(V3Granularity.DAY, "all", cat_code)].append(
                    int(scores["note_20"])
                )

            # 2. Season/Month level accumulation
            season = self._get_season(current_date)
            month = f"month_{current_date.month}"
            for cat_code, scores in bundle.core.category_scores.items():
                accumulators[(V3Granularity.SEASON, season, cat_code)].append(
                    float(scores["raw_score"])
                )
                accumulators_notes[(V3Granularity.SEASON, season, cat_code)].append(
                    int(scores["note_20"])
                )
                accumulators[(V3Granularity.MONTH, month, cat_code)].append(
                    float(scores["raw_score"])
                )
                accumulators_notes[(V3Granularity.MONTH, month, cat_code)].append(
                    int(scores["note_20"])
                )

            # 3. Slot level accumulation (from V3 time blocks if available)
            if bundle.v3_core and bundle.v3_core.time_blocks:
                for block in bundle.v3_core.time_blocks:
                    slot = self._get_time_slot(block.start_local)
                    # We approximate block impact for the baseline
                    # In V3, blocks have dominant themes.
                    for cat_code in block.dominant_themes:
                        accumulators[(V3Granularity.SLOT, slot, cat_code)].append(block.intensity)
                        # Confidence as a proxy for note? Or just skip note for slots
                        accumulators_notes[(V3Granularity.SLOT, slot, cat_code)].append(
                            int(block.intensity)
                        )

            current_date += timedelta(days=1)

        # 5. Compute statistics and upsert
        repo = UserPredictionBaselineRepository(db)
        results: dict[str, PersistedUserBaseline] = {}
        complete_day_categories = {
            cat_code
            for (g_type, g_val, cat_code), raw_scores in accumulators.items()
            if g_type == V3Granularity.DAY and g_val == "all" and len(raw_scores) == window_days
        }

        for (g_type, g_val, cat_code), raw_scores in accumulators.items():
            if cat_code not in complete_day_categories:
                continue
            cat_id = cat_map.get(cat_code)
            if not cat_id or not raw_scores:
                continue

            notes = accumulators_notes[(g_type, g_val, cat_code)]
            stats = self._compute_stats(raw_scores, notes)

            baseline = repo.upsert_baseline(
                user_id=user_id,
                category_id=cat_id,
                reference_version_id=resolved.reference_version_id,
                ruleset_id=resolved.ruleset_id,
                house_system_effective=house_system_effective or "placidus",
                window_days=window_days,
                window_start_date=start_date,
                window_end_date=end_date,
                stats=stats,
                granularity_type=g_type,
                granularity_value=g_val,
            )

            # For backward compatibility, return DAY level in the dict
            if g_type == V3Granularity.DAY:
                results[cat_code] = baseline

        duration_ms = int((time.perf_counter() - start_time_perf) * 1000)
        logger.info("baseline.generated user_id=%s duration_ms=%s", user_id, duration_ms)
        return results

    def _compute_stats(self, raw_scores: list[float], notes: list[int]) -> dict[str, Any]:
        sample_size = len(raw_scores)
        mean_raw = sum(raw_scores) / sample_size
        mean_note = sum(notes) / sample_size if notes else 10.0

        if sample_size > 1:
            try:
                std_raw = statistics.stdev(raw_scores)
                std_note = statistics.stdev(notes) if notes else 0.0
            except statistics.StatisticsError:
                std_raw = 0.0
                std_note = 0.0
        else:
            std_raw = 0.0
            std_note = 0.0

        sorted_raw = sorted(raw_scores)
        return {
            "mean_raw_score": mean_raw,
            "std_raw_score": std_raw,
            "mean_note_20": mean_note,
            "std_note_20": std_note,
            "p10": self._percentile(sorted_raw, 0.1),
            "p50": self._percentile(sorted_raw, 0.5),
            "p90": self._percentile(sorted_raw, 0.9),
            "sample_size_days": sample_size,
        }

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

    def _percentile(self, sorted_data: list[float], percentile: float) -> float:
        if not sorted_data:
            return 0.0
        n = len(sorted_data)
        if n == 1:
            return sorted_data[0]
        idx = (n - 1) * percentile
        low = int(idx)
        high = min(low + 1, n - 1)
        if low == high:
            return sorted_data[low]
        weight = idx - low
        return sorted_data[low] * (1.0 - weight) + sorted_data[high] * weight
