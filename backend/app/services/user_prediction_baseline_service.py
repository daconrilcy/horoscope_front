from __future__ import annotations

import logging
import statistics
import time
from dataclasses import replace
from datetime import date, timedelta
from typing import TYPE_CHECKING, Any

from app.infra.db.repositories.prediction_reference_repository import (
    PredictionReferenceRepository,
)
from app.infra.db.repositories.user_prediction_baseline_repository import (
    UserPredictionBaselineRepository,
)
from app.prediction.engine_orchestrator import EngineOrchestrator
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
        Generates a 12-month baseline for a user by simulating N days of predictions.
        AC3 Compliance: Reuses existing engine without coupling API.
        """
        start_time = time.perf_counter()
        logger.info(
            "baseline.start_generation user_id=%s window_days=%s", user_id, window_days
        )

        # 1. Resolve initial request to get versions and base info
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

        # 2. Setup simulation period
        end_date = resolved.resolved_date
        start_date = end_date - timedelta(days=window_days - 1)

        # 3. Prepare orchestrator with context loader
        def ctx_loader(ref: str, rule: str, dt: date) -> Any:
            return self.context_loader.load(db, ref, rule, dt)

        orch = self.orchestrator.with_context_loader(ctx_loader)

        ref_repo = PredictionReferenceRepository(db)
        categories = ref_repo.get_categories(resolved.reference_version_id)
        category_raw_scores: dict[str, list[float]] = {category.code: [] for category in categories}
        category_notes: dict[str, list[int]] = {category.code: [] for category in categories}
        cat_map = {category.code: category.id for category in categories}

        current_date = start_date
        days_processed = 0
        house_system_effective: str | None = None

        while current_date <= end_date:
            # Clone engine input for current date
            engine_input = replace(resolved.engine_input, local_date=current_date)

            # Run engine - only core computation, no editorial text (AC3)
            # We don't need complex outputs, just category scores
            bundle = orch.run(engine_input, include_editorial=False)
            current_house_system = (
                bundle.core.effective_context.house_system_effective or "placidus"
            )
            if house_system_effective is None:
                house_system_effective = current_house_system
            elif current_house_system != house_system_effective:
                raise ValueError(
                    "Inconsistent effective house system while generating baseline: "
                    f"{house_system_effective!r} != {current_house_system!r}"
                )

            # Extract scores
            for cat_code, scores in bundle.core.category_scores.items():
                if cat_code not in category_raw_scores:
                    logger.warning(
                        "baseline.category_missing_in_db code=%s ref_version_id=%s",
                        cat_code,
                        resolved.reference_version_id,
                    )
                    continue

                category_raw_scores[cat_code].append(float(scores["raw_score"]))
                category_notes[cat_code].append(int(scores["note_20"]))

            current_date += timedelta(days=1)
            days_processed += 1

        # 5. Compute statistics and upsert
        repo = UserPredictionBaselineRepository(db)

        results: dict[str, PersistedUserBaseline] = {}
        expected_sample_size = window_days

        for cat_code, raw_scores in category_raw_scores.items():
            cat_id = cat_map.get(cat_code)
            if not cat_id:
                continue

            notes = category_notes[cat_code]

            if not raw_scores:
                logger.warning(
                    "baseline.category_absent user_id=%s category=%s window_start=%s window_end=%s",
                    user_id,
                    cat_code,
                    start_date,
                    end_date,
                )
                continue

            sample_size = len(raw_scores)
            if sample_size < expected_sample_size:
                logger.warning(
                    (
                        "baseline.incomplete_history user_id=%s category=%s "
                        "expected_days=%s actual_days=%s"
                    ),
                    user_id,
                    cat_code,
                    expected_sample_size,
                    sample_size,
                )
                continue

            mean_raw = sum(raw_scores) / sample_size
            mean_note = sum(notes) / sample_size

            # Variance null check (AC4)
            if sample_size > 1:
                try:
                    std_raw = statistics.stdev(raw_scores)
                    std_note = statistics.stdev(notes)
                except statistics.StatisticsError:
                    std_raw = 0.0
                    std_note = 0.0
            else:
                std_raw = 0.0
                std_note = 0.0

            # Percentiles (AC1)
            sorted_raw = sorted(raw_scores)
            p10 = self._percentile(sorted_raw, 0.1)
            p50 = self._percentile(sorted_raw, 0.5)
            p90 = self._percentile(sorted_raw, 0.9)

            stats = {
                "mean_raw_score": mean_raw,
                "std_raw_score": std_raw,
                "mean_note_20": mean_note,
                "std_note_20": std_note,
                "p10": p10,
                "p50": p50,
                "p90": p90,
                "sample_size_days": sample_size,
            }

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
            )
            results[cat_code] = baseline

        duration_ms = int((time.perf_counter() - start_time) * 1000)
        logger.info(
            "baseline.generated user_id=%s categories=%s days=%s duration_ms=%s",
            user_id,
            len(results),
            days_processed,
            duration_ms,
        )

        return results

    def _percentile(self, sorted_data: list[float], percentile: float) -> float:
        """Linear interpolation between closest ranks."""
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
