from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.infra.db.repositories.daily_prediction_repository import DailyPredictionRepository
from app.prediction.input_hash import compute_engine_input_hash
from app.services.daily_prediction_types import ComputeMode

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.infra.db.models.daily_prediction import DailyPredictionRunModel
    from app.services.prediction_request_resolver import ResolvedPredictionRequest

logger = logging.getLogger()


@dataclass(frozen=True)
class ReuseDecision:
    should_compute: bool
    existing_run: DailyPredictionRunModel | None = None
    input_hash: str | None = None
    reason: str | None = None


class PredictionRunReusePolicy:
    """
    Decides whether an existing prediction run can be reused or if a new calculation is needed.
    """

    def decide(
        self,
        db: Session,
        request: ResolvedPredictionRequest,
        mode: ComputeMode,
    ) -> ReuseDecision:
        repo = DailyPredictionRepository(db)

        # 1. Mode read_only
        if mode == ComputeMode.read_only:
            run = repo.get_run(
                request.user_id,
                request.resolved_date,
                request.reference_version_id,
                request.ruleset_id,
            )
            if run:
                return ReuseDecision(
                    should_compute=False,
                    existing_run=run,
                    reason="read_only_hit",
                )
            return ReuseDecision(should_compute=False, reason="read_only_miss")

        if request.engine_input is None:
            raise ValueError("engine_input is required for compute/reuse decisions")

        input_hash = compute_engine_input_hash(
            natal_chart=request.engine_input.natal_chart,
            local_date=request.engine_input.local_date,
            timezone=request.engine_input.timezone,
            latitude=request.engine_input.latitude,
            longitude=request.engine_input.longitude,
            reference_version=request.engine_input.reference_version,
            ruleset_version=request.engine_input.ruleset_version,
        )

        # 2. Mode force_recompute
        if mode == ComputeMode.force_recompute:
            # We don't delete here, the orchestrator service will handle it if needed, 
            # or we just ignore the existing one.
            return ReuseDecision(
                should_compute=True,
                input_hash=input_hash,
                reason="force_recompute",
            )

        # 3. Mode compute_if_missing
        existing_run = repo.get_run_by_hash_with_details(request.user_id, input_hash)
        if existing_run:
            if self._is_stale(existing_run):
                logger.info(
                    "prediction.stale_cached_run_recompute",
                    extra={
                        "user_id": request.user_id,
                        "run_id": existing_run.id,
                        "reason": "missing_summaries",
                    },
                )
                return ReuseDecision(
                    should_compute=True, 
                    existing_run=existing_run, 
                    input_hash=input_hash, 
                    reason="stale_run"
                )
            
            return ReuseDecision(
                should_compute=False,
                existing_run=existing_run,
                input_hash=input_hash,
                reason="cache_hit",
            )

        return ReuseDecision(should_compute=True, input_hash=input_hash, reason="cache_miss")

    def _is_stale(self, run: DailyPredictionRunModel) -> bool:
        """
        Checks if a cached run is missing critical summaries that require a recompute.
        """
        if not run.overall_summary:
            return True
        if any(b.summary is None for b in run.time_blocks):
            return True
        if any(
            tp.summary in [None, "delta_note", "top3_change", "high_priority_event"]
            for tp in run.turning_points
        ):
            return True
        return False
