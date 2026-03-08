from __future__ import annotations

import concurrent.futures
import hashlib
import json
import logging
import time
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import select

from app.core.config import settings
from app.core.versions import LEGACY_RULESET_VERSION, get_active_ruleset_version
from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.repositories.chart_result_repository import ChartResultRepository
from app.infra.db.repositories.daily_prediction_repository import DailyPredictionRepository
from app.infra.db.repositories.prediction_ruleset_repository import PredictionRulesetRepository
from app.infra.db.repositories.user_birth_profile_repository import UserBirthProfileRepository
from app.infra.observability.metrics import increment_counter
from app.prediction.engine_orchestrator import EngineOrchestrator
from app.prediction.schemas import EngineInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.infra.db.models.daily_prediction import DailyPredictionRunModel
    from app.infra.db.models.user_birth_profile import UserBirthProfileModel
    from app.prediction.context_loader import PredictionContextLoader
    from app.prediction.persistence_service import PredictionPersistenceService
    from app.prediction.schemas import EngineOutput

logger = logging.getLogger(__name__)


class ComputeMode(Enum):
    compute_if_missing = "compute_if_missing"
    force_recompute = "force_recompute"
    read_only = "read_only"


@dataclass(frozen=True)
class ServiceResult:
    run: DailyPredictionRunModel
    engine_output: EngineOutput | None
    was_reused: bool


class DailyPredictionServiceError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class DailyPredictionService:
    def __init__(
        self,
        context_loader: PredictionContextLoader,
        persistence_service: PredictionPersistenceService,
        *,
        orchestrator: EngineOrchestrator | None = None,
    ) -> None:
        self.context_loader = context_loader
        self.persistence_service = persistence_service
        # Optional pre-built orchestrator: sub-components are reused per call
        # via with_context_loader(). If None, a fresh orchestrator is created per call.
        self._orchestrator_proto = orchestrator

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
        Orchestrates the resolution of user context, engine execution, and persistence.

        Setup errors (profile_missing, timezone_missing, etc.) propagate directly as
        DailyPredictionServiceError — no fallback is attempted for these. Only engine
        or persistence failures trigger the fallback on the latest available run (AC1).
        """
        start_time = time.perf_counter()

        # 1-6. Setup — DailyPredictionServiceError propagates directly, no fallback
        resolved_reference_version = reference_version or settings.active_reference_version
        resolved_ruleset_version = ruleset_version or settings.active_ruleset_version
        profile = self._resolve_profile(db, user_id)
        tz_str = self._resolve_timezone(profile, timezone_override)
        lat, lon = self._resolve_location(profile, location_override)
        resolved_date = self._resolve_date(date_local, tz_str)
        reference_version_id = self._resolve_reference_version_id(db, resolved_reference_version)
        ruleset_id = self._resolve_ruleset_id(db, resolved_ruleset_version, reference_version_id)

        # 2. Mode read_only : lecture seule, aucun calcul
        if mode == ComputeMode.read_only:
            run = DailyPredictionRepository(db).get_run(
                user_id, resolved_date, reference_version_id, ruleset_id
            )
            result = None
            if run is not None:
                result = ServiceResult(run=run, engine_output=None, was_reused=True)

            if result:
                self._log_and_metrics(
                    user_id, start_time, result, ruleset_version=resolved_ruleset_version
                )
            return result

        # prediction.compute is only incremented for actual compute paths (not read_only)
        increment_counter("prediction.compute")

        # 3. Resolve natal chart
        natal_chart = self._resolve_natal_chart(db, user_id)

        # 4. Build EngineInput and compute hash BEFORE engine (AC2)
        engine_input = EngineInput(
            natal_chart=natal_chart,
            local_date=resolved_date,
            timezone=tz_str,
            latitude=lat,
            longitude=lon,
            reference_version=resolved_reference_version,
            ruleset_version=resolved_ruleset_version,
            debug_mode=False,
        )
        input_hash = self._compute_input_hash(engine_input)

        # 5. Mode compute_if_missing : short-circuit if hash exists
        if mode == ComputeMode.compute_if_missing:
            existing_run = DailyPredictionRepository(db).get_run_by_hash(user_id, input_hash)
            if existing_run:
                result = ServiceResult(run=existing_run, engine_output=None, was_reused=True)
                self._log_and_metrics(
                    user_id, start_time, result, ruleset_version=resolved_ruleset_version
                )
                return result

        # 6. Mode force_recompute : remove old run if it exists
        if mode == ComputeMode.force_recompute:
            old_run = DailyPredictionRepository(db).get_run(
                user_id, resolved_date, reference_version_id, ruleset_id
            )
            if old_run:
                db.delete(old_run)
                db.flush()

        # 7-8. Engine + persistence — failures trigger fallback (AC1)
        try:
            engine_output = self._compute_with_timeout(db, engine_input)

            save_result = self.persistence_service.save(
                engine_output=engine_output,
                user_id=user_id,
                local_date=resolved_date,
                reference_version_id=reference_version_id,
                ruleset_id=ruleset_id,
                db=db,
            )

            result = ServiceResult(
                run=save_result.run,
                engine_output=engine_output,
                was_reused=False,
            )
            self._log_and_metrics(
                user_id, start_time, result, ruleset_version=resolved_ruleset_version
            )
            return result

        except Exception as e:
            # AC1 — Fallback on engine/persistence failure only
            error_str = str(e)
            logger.error(
                "prediction.compute_failed", extra={"user_id": user_id, "error": error_str}
            )

            fallback_run = self._try_read_latest_available(db, user_id, resolved_date)
            if fallback_run:
                result = ServiceResult(run=fallback_run, engine_output=None, was_reused=True)
                self._log_and_metrics(
                    user_id,
                    start_time,
                    result,
                    error=error_str,
                    ruleset_version=resolved_ruleset_version,
                )
                return result

            # No fallback available — log final failure (AC3) then re-raise as service error (AC5)
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            logger.info(
                "prediction.run",
                extra={
                    "user_id": user_id,
                    "duration_ms": duration_ms,
                    "was_reused": False,
                    "error": error_str,
                    "ruleset_version": resolved_ruleset_version,
                },
            )
            if isinstance(e, DailyPredictionServiceError):
                raise
            raise DailyPredictionServiceError(
                "compute_failed",
                f"Calcul indisponible et aucune prédiction en cache. Détail: {error_str}",
            ) from e

    def _compute_with_timeout(self, db: Session, engine_input: EngineInput) -> EngineOutput:
        """
        Timeout best-effort : lève DailyPredictionServiceError("timeout") après 30s.

        ⚠️  Limitation GIL : le thread de calcul continue en arrière-plan après timeout
        (le code CPU-bound n'est pas interruptible). Ce thread conserve une référence
        à la Session SQLAlchemy (`db` capturée dans la closure ctx_loader).
        `db.expire_all()` est appelé après timeout pour invalider le cache de session
        et limiter le risque de lectures périmées si le thread accède encore à la
        session. La session reste non thread-safe ; ne pas la réutiliser dans un autre
        thread simultanément pendant les ~30s suivant le timeout.
        """

        def ctx_loader(ref: str, rule: str, dt: date) -> object:
            return self.context_loader.load(db, ref, rule, dt)

        if self._orchestrator_proto is not None:
            orchestrator = self._orchestrator_proto.with_context_loader(ctx_loader)
        else:
            orchestrator = EngineOrchestrator(prediction_context_loader=ctx_loader)

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(orchestrator.run, engine_input)
            try:
                return future.result(timeout=30)
            except concurrent.futures.TimeoutError:
                try:
                    db.expire_all()
                except Exception:
                    pass
                raise DailyPredictionServiceError(
                    "timeout", "Calcul trop long — service temporairement dégradé"
                ) from None

    def _try_read_latest_available(
        self, db: Session, user_id: int, date_local: date
    ) -> DailyPredictionRunModel | None:
        """AC2 - Retrieves the most recent run before the requested date."""
        return DailyPredictionRepository(db).get_latest_run_before(user_id, date_local)

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
        if result.engine_output:
            has_pivots = bool(getattr(result.engine_output, "turning_points", []))
            overall_tone = getattr(result.engine_output, "run_metadata", {}).get("overall_tone")
        elif result.run:
            # Fallback for reused runs: overall_tone is usually in the model
            if hasattr(result.run, "overall_tone"):
                overall_tone = result.run.overall_tone
            if hasattr(result.run, "turning_points") and result.run.turning_points:
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
                extra={
                    "user_id": user_id,
                    "duration_ms": duration_ms,
                },
            )

    def _resolve_profile(self, db: Session, user_id: int) -> UserBirthProfileModel:
        profile = UserBirthProfileRepository(db).get_by_user_id(user_id)
        if profile is None:
            raise DailyPredictionServiceError("profile_missing", "Profil de naissance introuvable")
        return profile

    def _resolve_timezone(self, profile: UserBirthProfileModel, override: str | None) -> str:
        tz_str = override or profile.current_timezone or profile.birth_timezone
        if not tz_str:
            raise DailyPredictionServiceError("timezone_missing", "Timezone introuvable")
        try:
            ZoneInfo(tz_str)
        except (ZoneInfoNotFoundError, KeyError):
            raise DailyPredictionServiceError("timezone_invalid", f"Timezone invalide : '{tz_str}'")
        return tz_str

    def _resolve_location(
        self, profile: UserBirthProfileModel, override: tuple[float, float] | None
    ) -> tuple[float, float]:
        if override:
            return override
        if profile.current_lat is None or profile.current_lon is None:
            raise DailyPredictionServiceError("location_missing", "Localisation introuvable")
        return profile.current_lat, profile.current_lon

    def _resolve_date(self, date_local: date | None, tz_str: str) -> date:
        if date_local is not None:
            return date_local
        return datetime.now(ZoneInfo(tz_str)).date()

    def _resolve_natal_chart(self, db: Session, user_id: int) -> dict[str, Any]:
        chart = ChartResultRepository(db).get_latest_by_user_id(user_id)
        if chart is None:
            raise DailyPredictionServiceError("natal_missing", "Aucun thème natal trouvé")
        return chart.result_payload

    def _resolve_reference_version_id(self, db: Session, version: str) -> int:
        rv_id = db.scalar(
            select(ReferenceVersionModel.id).where(ReferenceVersionModel.version == version)
        )
        if rv_id is None:
            raise DailyPredictionServiceError(
                "version_missing", f"Référence version '{version}' introuvable"
            )
        return rv_id

    def _resolve_ruleset_id(
        self, db: Session, version: str, expected_reference_version_id: int | None = None
    ) -> int:
        ruleset = PredictionRulesetRepository(db).get_ruleset(version)
        if ruleset is None:
            raise DailyPredictionServiceError(
                "ruleset_missing", f"Ruleset version '{version}' introuvable"
            )

        if (
            expected_reference_version_id is not None
            and ruleset.reference_version_id != expected_reference_version_id
        ):
            raise DailyPredictionServiceError(
                "ruleset_inconsistent",
                f"Le ruleset '{version}' est rattaché à la référence ID "
                f"{ruleset.reference_version_id}, "
                f"mais la référence active demandée est ID {expected_reference_version_id}. "
                "Vérifiez la cohérence de la configuration runtime.",
            )

        if version == LEGACY_RULESET_VERSION:
            canonical_ruleset_version = get_active_ruleset_version()
            logger.warning(
                "DEPRECATION: Legacy ruleset '%s' is being used. "
                "Please migrate to canonical version '%s'.",
                version,
                canonical_ruleset_version,
                extra={"ruleset_version": version, "legacy": True},
            )

        return ruleset.id

    def _compute_input_hash(self, engine_input: EngineInput) -> str:
        """Reproduces the hash used by EngineOrchestrator for consistency."""
        canonical = {
            "natal": engine_input.natal_chart,
            "local_date": engine_input.local_date.isoformat(),
            "timezone": engine_input.timezone,
            "latitude": engine_input.latitude,
            "longitude": engine_input.longitude,
            "reference_version": engine_input.reference_version,
            "ruleset_version": engine_input.ruleset_version,
        }
        serialized = json.dumps(canonical, sort_keys=True, ensure_ascii=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()
