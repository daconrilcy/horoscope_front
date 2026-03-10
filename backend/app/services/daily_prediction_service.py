from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Any

from app.infra.db.repositories.daily_prediction_repository import DailyPredictionRepository
from app.infra.observability.metrics import increment_counter
from app.prediction.exceptions import PredictionContextError
from app.services.daily_prediction_types import ComputeMode, DailyPredictionServiceError
from app.services.prediction_compute_runner import PredictionComputeRunner
from app.services.prediction_context_repair_service import PredictionContextRepairService
from app.services.prediction_fallback_policy import PredictionFallbackPolicy
from app.services.prediction_request_resolver import PredictionRequestResolver
from app.services.prediction_run_reuse_policy import PredictionRunReusePolicy

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.prediction.context_loader import PredictionContextLoader
    from app.prediction.engine_orchestrator import EngineOrchestrator
    from app.prediction.persisted_snapshot import PersistedPredictionSnapshot
    from app.prediction.persistence_service import PredictionPersistenceService
    from app.prediction.schemas import PersistablePredictionBundle
    from app.services.prediction_request_resolver import ResolvedPredictionRequest

logger = logging.getLogger()


@dataclass(frozen=True)
class ServiceResult:
    run: PersistedPredictionSnapshot
    bundle: PersistablePredictionBundle | None
    was_reused: bool


class DailyPredictionService:
    def __init__(
        self,
        context_loader: PredictionContextLoader,
        persistence_service: PredictionPersistenceService,
        *,
        orchestrator: EngineOrchestrator | None = None,
        resolver: PredictionRequestResolver | None = None,
        reuse_policy: PredictionRunReusePolicy | None = None,
        compute_runner: PredictionComputeRunner | None = None,
        fallback_policy: PredictionFallbackPolicy | None = None,
        repair_service: PredictionContextRepairService | None = None,
    ) -> None:
        self.context_loader = context_loader
        self.persistence_service = persistence_service
        self.repair_service = repair_service or PredictionContextRepairService()
        self.resolver = resolver or PredictionRequestResolver(self.repair_service)
        self.reuse_policy = reuse_policy or PredictionRunReusePolicy()
        self.compute_runner = compute_runner or PredictionComputeRunner(
            context_loader, orchestrator
        )
        self.fallback_policy = fallback_policy or PredictionFallbackPolicy()

    def get_or_compute(
        self,
        *,
        user_id: int,
        db: Session,
        date_local: date | None = None,
        location_override: tuple[float, float] | None = None,
        timezone_override: str | None = None,
        mode: ComputeMode = ComputeMode.compute_if_missing,
        reference_version: str | None = None,
        ruleset_version: str | None = None,
    ) -> ServiceResult | None:
        """
        Orchestrates user context resolution, reuse decision, engine execution and fallback.
        """
        start_time = time.perf_counter()

        # 1. Resolve Request
        resolved_request = self.resolver.resolve(
            db=db,
            user_id=user_id,
            date_local=date_local,
            location_override=location_override,
            timezone_override=timezone_override,
            reference_version=reference_version,
            ruleset_version=ruleset_version,
            include_engine_input=mode != ComputeMode.read_only,
        )

        if mode != ComputeMode.read_only:
            increment_counter("prediction.compute")

        # 2. Reuse Decision
        reuse_decision = self.reuse_policy.decide(db, resolved_request, mode)
        
        if not reuse_decision.should_compute:
            if reuse_decision.existing_run:
                result = ServiceResult(
                    run=reuse_decision.existing_run,
                    bundle=None,
                    was_reused=True,
                )
                self._log_and_metrics(
                    user_id,
                    start_time,
                    result,
                    ruleset_version=resolved_request.ruleset_version,
                )
                return result
            
            # read_only miss
            return None

        # 3. Mode force_recompute : cleanup if needed
        if mode == ComputeMode.force_recompute:
            old_run = DailyPredictionRepository(db).get_run(
                user_id, 
                resolved_request.resolved_date, 
                resolved_request.reference_version_id, 
                resolved_request.ruleset_id
            )
            if old_run:
                db.delete(old_run)
                db.flush()

        # 4. Compute and Save
        try:
            if reuse_decision.should_compute and reuse_decision.existing_run:
                from app.infra.db.models.daily_prediction import DailyPredictionRunModel

                run_model = db.get(
                    DailyPredictionRunModel,
                    reuse_decision.existing_run.run_id,
                )
                if run_model is not None:
                    db.delete(run_model)
                db.flush()

            result = self._execute_and_persist(db, resolved_request)
            self._log_and_metrics(
                user_id,
                start_time,
                result,
                ruleset_version=resolved_request.ruleset_version,
            )
            return result

        except Exception as e:
            # AC3 Compliance: Context Repair Attempt via specialized service
            if self._try_repair_context(db, e, resolved_request):
                try:
                    result = self._execute_and_persist(db, resolved_request)
                    self._log_and_metrics(
                        user_id,
                        start_time,
                        result,
                        ruleset_version=resolved_request.ruleset_version,
                    )
                    return result
                except Exception as retry_error:
                    e = retry_error

            # AC1 - Fallback on engine/persistence failure
            error_str = str(e)
            logger.error(
                "prediction.compute_failed",
                extra={"user_id": user_id, "error": error_str},
            )

            fallback = self.fallback_policy.try_fallback(
                db,
                user_id,
                resolved_request.resolved_date,
            )
            if fallback.success:
                result = ServiceResult(
                    run=fallback.fallback_run,
                    bundle=None,
                    was_reused=True,
                )
                self._log_and_metrics(
                    user_id,
                    start_time,
                    result,
                    error=error_str,
                    ruleset_version=resolved_request.ruleset_version,
                )
                return result

            # No fallback available
            self._log_failure(
                user_id,
                start_time,
                error_str,
                resolved_request.ruleset_version,
            )
            if isinstance(e, DailyPredictionServiceError):
                raise
            raise DailyPredictionServiceError(
                "compute_failed",
                f"Calcul indisponible et aucune prédiction en cache. Détail: {error_str}",
            ) from e

    def _execute_and_persist(
        self,
        db: Session,
        request: "ResolvedPredictionRequest",
    ) -> ServiceResult:
        if request.engine_input is None:
            raise ValueError("engine_input is required for execution")
        compute_result = self.compute_runner.run_with_timeout(db, request.engine_input)
        
        save_result = self.persistence_service.save(
            bundle=compute_result.bundle,
            user_id=request.user_id,
            local_date=request.resolved_date,
            reference_version_id=request.reference_version_id,
            ruleset_id=request.ruleset_id,
            db=db,
        )

        return ServiceResult(
            run=save_result.run,
            bundle=compute_result.bundle,
            was_reused=False,
        )

    def _try_repair_context(
        self,
        db: Session,
        error: Exception,
        request: "ResolvedPredictionRequest",
    ) -> bool:
        # AC3 Compliance: Delegates to PredictionContextRepairService
        error_text = str(error)
        if isinstance(error, PredictionContextError):
            needs_repair = (
                "Prediction context has no planet profiles" in error_text
                or "Prediction context has no house profiles" in error_text
                or "Prediction context has no enabled categories" in error_text
            )
            if needs_repair:
                return self.repair_service.try_repair(
                    db,
                    reference_version=request.reference_version,
                    ruleset_version=request.ruleset_version,
                    reference_version_id=request.reference_version_id,
                )
        return False

    def _log_and_metrics(
        self,
        user_id: int,
        start_time: float,
        result: ServiceResult,
        *,
        error: str | None = None,
        ruleset_version: str | None = None,
    ) -> None:
        duration_ms = int((time.perf_counter() - start_time) * 1000)

        if result.was_reused:
            increment_counter("prediction.reused")

        has_pivots = False
        overall_tone = None
        
        # Use typed snapshot fields (AC1)
        if result.bundle:
            has_pivots = len(result.bundle.core.turning_points) > 0
            if result.bundle.editorial:
                overall_tone = result.bundle.editorial.data.overall_tone
            else:
                overall_tone = result.bundle.core.run_metadata.get("overall_tone")
        elif result.run:
            overall_tone = result.run.overall_tone
            has_pivots = len(result.run.turning_points) > 0

        log_extra: dict[str, Any] = {
            "user_id": user_id,
            "duration_ms": duration_ms,
            "was_reused": result.was_reused,
            "has_pivots": has_pivots,
            "overall_tone": overall_tone,
        }
        if ruleset_version:
            log_extra["ruleset_version"] = ruleset_version
        if error is not None:
            log_extra["error"] = error

        logger.info("prediction.run", extra=log_extra)

        if duration_ms > 25000:
            logger.warning(
                "prediction.slow_run",
                extra={"user_id": user_id, "duration_ms": duration_ms},
            )

    def _log_failure(
        self,
        user_id: int,
        start_time: float,
        error_str: str,
        ruleset_version: str,
    ) -> None:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        logger.info(
            "prediction.run",
            extra={
                "user_id": user_id,
                "duration_ms": duration_ms,
                "was_reused": False,
                "error": error_str,
                "ruleset_version": ruleset_version,
            },
        )
