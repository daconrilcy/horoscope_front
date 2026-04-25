from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.core.config import DailyEngineMode, settings
from app.infra.db.repositories.daily_prediction_repository import DailyPredictionRepository
from app.prediction.input_hash import compute_engine_input_hash
from app.services.daily_prediction_types import ComputeMode

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.prediction.persisted_snapshot import PersistedPredictionSnapshot
    from app.services.prediction.request_resolver import ResolvedPredictionRequest

logger = logging.getLogger()


def _current_v3_versions() -> tuple[str | None, str | None, str | None]:
    if settings.daily_engine_mode == DailyEngineMode.V2:
        return (None, None, None)
    return (
        settings.v3_engine_version,
        settings.v3_snapshot_version,
        settings.v3_evidence_pack_version,
    )


@dataclass(frozen=True)
class ReuseDecision:
    should_compute: bool
    existing_run: PersistedPredictionSnapshot | None = None
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
            run_model = repo.get_run(
                request.user_id,
                request.resolved_date,
                request.reference_version_id,
                request.ruleset_id,
                engine_mode=settings.daily_engine_mode.value,
            )
            if run_model:
                snapshot = repo.get_snapshot(run_model)
                return ReuseDecision(
                    should_compute=False,
                    existing_run=snapshot,
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
            engine_mode=settings.daily_engine_mode.value,
            engine_version=_current_v3_versions()[0],
            snapshot_version=_current_v3_versions()[1],
            evidence_pack_version=_current_v3_versions()[2],
        )
        engine_version, snapshot_version, evidence_pack_version = _current_v3_versions()

        # 2. Mode force_recompute
        if mode == ComputeMode.force_recompute:
            # We don't delete here, the orchestrator service will handle it if needed
            return ReuseDecision(
                should_compute=True,
                input_hash=input_hash,
                reason="force_recompute",
            )

        # 3. Mode compute_if_missing
        # AC2 Compliance: Explicit naming for technical reuse
        existing_run = repo.get_run_for_reuse(
            request.user_id,
            input_hash,
            engine_mode=settings.daily_engine_mode.value,
            engine_version=engine_version,
            snapshot_version=snapshot_version,
            evidence_pack_version=evidence_pack_version,
        )
        if existing_run:
            if self._is_stale(existing_run):
                logger.info(
                    "prediction.stale_cached_run_recompute",
                    extra={
                        "user_id": request.user_id,
                        "run_id": existing_run.run_id,
                        "reason": "missing_summaries",
                    },
                )
                return ReuseDecision(
                    should_compute=True,
                    existing_run=existing_run,
                    input_hash=input_hash,
                    reason="stale_run",
                )

            return ReuseDecision(
                should_compute=False,
                existing_run=existing_run,
                input_hash=input_hash,
                reason="cache_hit",
            )

        return ReuseDecision(should_compute=True, input_hash=input_hash, reason="cache_miss")

    def _is_stale(self, run: PersistedPredictionSnapshot) -> bool:
        """
        Checks if a cached run is missing critical summaries that require a recompute.
        AC1 Compliance: Works on typed snapshot.
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
