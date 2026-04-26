"""Service canonique d orchestration des predictions quotidiennes."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import date
from threading import Condition, Lock
from typing import TYPE_CHECKING, Any

from app.core.config import settings
from app.infra.db.repositories.daily_prediction_repository import DailyPredictionRepository
from app.infra.observability.metrics import increment_counter
from app.prediction.exceptions import PredictionContextError
from app.services.prediction.compute_runner import PredictionComputeRunner
from app.services.prediction.context_repair_service import PredictionContextRepairService
from app.services.prediction.fallback_policy import PredictionFallbackPolicy
from app.services.prediction.relative_scoring_service import RelativeScoringService
from app.services.prediction.request_resolver import PredictionRequestResolver
from app.services.prediction.run_reuse_policy import PredictionRunReusePolicy
from app.services.prediction.types import ComputeMode, DailyPredictionServiceError

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.prediction.context_loader import PredictionContextLoader
    from app.prediction.engine_orchestrator import EngineOrchestrator
    from app.prediction.persisted_snapshot import PersistedPredictionSnapshot
    from app.prediction.persistence_service import PredictionPersistenceService
    from app.prediction.schemas import PersistablePredictionBundle
    from app.services.prediction.request_resolver import ResolvedPredictionRequest


logger = logging.getLogger(__name__)


class _PredictionSingleFlight:
    """Evite les recalculs concurrents pour une meme cle de prediction."""

    def __init__(self) -> None:
        self._mutex = Lock()
        self._condition = Condition(self._mutex)
        self._inflight_keys: set[tuple[object, ...]] = set()

    def acquire(self, key: tuple[object, ...]) -> bool:
        """Retourne `True` pour le leader qui doit calculer effectivement."""
        with self._condition:
            if key not in self._inflight_keys:
                self._inflight_keys.add(key)
                return True

            while key in self._inflight_keys:
                self._condition.wait()
            return False

    def release(self, key: tuple[object, ...]) -> None:
        """Libere la cle en vol et reveille les appels suiveurs."""
        with self._condition:
            self._inflight_keys.discard(key)
            self._condition.notify_all()


_prediction_single_flight = _PredictionSingleFlight()


@dataclass(frozen=True)
class ServiceResult:
    """Resultat unifie renvoye par le service de prediction quotidienne."""

    run: PersistedPredictionSnapshot
    bundle: PersistablePredictionBundle | None
    was_reused: bool


class DailyPredictionService:
    """Orchestre resolution, calcul, fallback et enrichissement des predictions."""

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
        relative_scoring_service: RelativeScoringService | None = None,
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
        self.relative_scoring_service = relative_scoring_service or RelativeScoringService()

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
        """Resout le contexte, calcule si necessaire puis retourne le snapshot utile."""
        start_time = time.perf_counter()
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

        reuse_decision = self.reuse_policy.decide(db, resolved_request, mode)
        if not reuse_decision.should_compute:
            return self._build_reused_result(
                db,
                reuse_decision.existing_run,
                user_id=user_id,
                start_time=start_time,
                ruleset_version=resolved_request.ruleset_version,
            )

        single_flight_key = (
            user_id,
            resolved_request.resolved_date,
            resolved_request.reference_version_id,
            resolved_request.ruleset_id,
            settings.daily_engine_mode.value,
        )
        single_flight_leader = _prediction_single_flight.acquire(single_flight_key)
        if not single_flight_leader:
            logger.info(
                "prediction.compute_wait_reuse user_id=%s date=%s",
                user_id,
                resolved_request.resolved_date.isoformat(),
            )
            reuse_decision = self.reuse_policy.decide(db, resolved_request, mode)
            reused_result = self._build_reused_result(
                db,
                reuse_decision.existing_run if not reuse_decision.should_compute else None,
                user_id=user_id,
                start_time=start_time,
                ruleset_version=resolved_request.ruleset_version,
            )
            if reused_result is not None:
                return reused_result

            logger.info(
                "prediction.compute_wait_miss user_id=%s date=%s",
                user_id,
                resolved_request.resolved_date.isoformat(),
            )

        try:
            self._cleanup_recompute_run_if_needed(db, resolved_request, mode)
            return self._compute_with_repair_and_fallback(
                db=db,
                request=resolved_request,
                reuse_decision=reuse_decision,
                user_id=user_id,
                start_time=start_time,
            )
        finally:
            if single_flight_leader:
                _prediction_single_flight.release(single_flight_key)

    def _cleanup_recompute_run_if_needed(
        self,
        db: Session,
        request: "ResolvedPredictionRequest",
        mode: ComputeMode,
    ) -> None:
        """Supprime l execution precedente si le mode force un recalcul."""
        if mode != ComputeMode.force_recompute:
            return

        old_run = DailyPredictionRepository(db).get_run(
            request.user_id,
            request.resolved_date,
            request.reference_version_id,
            request.ruleset_id,
            engine_mode=settings.daily_engine_mode.value,
        )
        if old_run:
            db.delete(old_run)
            db.flush()

    def _compute_with_repair_and_fallback(
        self,
        *,
        db: Session,
        request: "ResolvedPredictionRequest",
        reuse_decision: Any,
        user_id: int,
        start_time: float,
    ) -> ServiceResult:
        """Execute le calcul canonique, avec tentative de repair puis fallback."""
        try:
            self._delete_existing_run_if_needed(db, reuse_decision)
            result = self._execute_and_persist(db, request)
            result = self._enrich_result(db, result)
            self._log_and_metrics(
                user_id,
                start_time,
                result,
                ruleset_version=request.ruleset_version,
            )
            return result
        except Exception as error:
            repaired_result = self._retry_after_repair(
                db=db,
                error=error,
                request=request,
                user_id=user_id,
                start_time=start_time,
            )
            if repaired_result is not None:
                return repaired_result

            return self._fallback_or_raise(
                db=db,
                error=error,
                request=request,
                user_id=user_id,
                start_time=start_time,
            )

    def _delete_existing_run_if_needed(self, db: Session, reuse_decision: Any) -> None:
        """Supprime l ancien run a remplacer avant persistance du nouveau."""
        if not reuse_decision.should_compute or not reuse_decision.existing_run:
            return

        from app.infra.db.models.daily_prediction import DailyPredictionRunModel

        run_model = db.get(
            DailyPredictionRunModel,
            reuse_decision.existing_run.run_id,
        )
        if run_model is not None:
            db.delete(run_model)
        db.flush()

    def _retry_after_repair(
        self,
        *,
        db: Session,
        error: Exception,
        request: "ResolvedPredictionRequest",
        user_id: int,
        start_time: float,
    ) -> ServiceResult | None:
        """Rejoue une execution si le contexte prediction peut etre repare."""
        if not self._try_repair_context(db, error, request):
            return None

        retry_result = self._execute_and_persist(db, request)
        retry_result = self._enrich_result(db, retry_result)
        self._log_and_metrics(
            user_id,
            start_time,
            retry_result,
            ruleset_version=request.ruleset_version,
        )
        return retry_result

    def _fallback_or_raise(
        self,
        *,
        db: Session,
        error: Exception,
        request: "ResolvedPredictionRequest",
        user_id: int,
        start_time: float,
    ) -> ServiceResult:
        """Applique le fallback canonique ou remonte une erreur explicite."""
        error_str = str(error)
        logger.error(
            "prediction.compute_failed error=%s",
            error_str,
            extra={"user_id": user_id, "error": error_str},
            exc_info=True,
        )

        try:
            db.rollback()
        except Exception:
            pass

        fallback = self.fallback_policy.try_fallback(
            db,
            user_id,
            request.resolved_date,
        )
        if fallback.success:
            run = self._enrich_run_safely(db, fallback.fallback_run)
            result = ServiceResult(
                run=run,
                bundle=None,
                was_reused=True,
            )
            self._log_and_metrics(
                user_id,
                start_time,
                result,
                error=error_str,
                ruleset_version=request.ruleset_version,
            )
            return result

        self._log_failure(
            user_id,
            start_time,
            error_str,
            request.ruleset_version,
        )
        if isinstance(error, DailyPredictionServiceError):
            raise
        raise DailyPredictionServiceError(
            "compute_failed",
            f"Calcul indisponible et aucune prédiction en cache. Détail: {error_str}",
        ) from error

    def _build_reused_result(
        self,
        db: Session,
        run: PersistedPredictionSnapshot | None,
        *,
        user_id: int,
        start_time: float,
        ruleset_version: str | None,
    ) -> ServiceResult | None:
        """Construit un resultat reutilise si un run compatible existe deja."""
        if run is None:
            return None

        enriched_run = self._enrich_run_safely(db, run)
        result = ServiceResult(
            run=enriched_run,
            bundle=None,
            was_reused=True,
        )
        self._log_and_metrics(
            user_id,
            start_time,
            result,
            ruleset_version=ruleset_version,
        )
        return result

    def _enrich_result(self, db: Session, result: ServiceResult) -> ServiceResult:
        """Enrichit le resultat avec les scores relatifs quand ils sont disponibles."""
        enriched_run = self._enrich_run_safely(db, result.run)
        return ServiceResult(
            run=enriched_run,
            bundle=result.bundle,
            was_reused=result.was_reused,
        )

    def _enrich_run_safely(
        self,
        db: Session,
        run: PersistedPredictionSnapshot,
    ) -> PersistedPredictionSnapshot:
        """Applique l enrichissement relatif sans casser le flux nominal."""
        try:
            return self.relative_scoring_service.enrich_snapshot(db, run)
        except Exception as error:
            logger.warning("prediction.enrich_failed error=%s", str(error))
            return run

    def _execute_and_persist(
        self,
        db: Session,
        request: "ResolvedPredictionRequest",
    ) -> ServiceResult:
        """Execute le moteur puis persiste le bundle calcule."""
        if request.engine_input is None:
            raise ValueError("engine_input is required for execution")

        compute_result = self.compute_runner.run_with_timeout(
            db, request.engine_input, engine_mode=settings.daily_engine_mode
        )
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
        """Declenche un repair du contexte prediction si l erreur le justifie."""
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
        """Emet les metriques et logs normalises du flux prediction."""
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        if result.was_reused:
            increment_counter("prediction.reused")

        has_pivots = False
        overall_tone = None
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
        """Journalise un echec sans fallback exploitable."""
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
