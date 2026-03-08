from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import select

from app.core.config import settings
from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.repositories.chart_result_repository import ChartResultRepository
from app.infra.db.repositories.daily_prediction_repository import DailyPredictionRepository
from app.infra.db.repositories.prediction_ruleset_repository import PredictionRulesetRepository
from app.infra.db.repositories.user_birth_profile_repository import UserBirthProfileRepository
from app.prediction.engine_orchestrator import EngineOrchestrator
from app.prediction.exceptions import PredictionContextError
from app.prediction.schemas import EngineInput

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.infra.db.models.daily_prediction import DailyPredictionRunModel
    from app.infra.db.models.user_birth_profile import UserBirthProfileModel
    from app.prediction.context_loader import PredictionContextLoader
    from app.prediction.persistence_service import PredictionPersistenceService
    from app.prediction.schemas import EngineOutput


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
        reference_version: str = settings.active_reference_version,
        ruleset_version: str,
    ) -> ServiceResult | None:
        """
        Orchestrates the resolution of user context, engine execution, and persistence.
        """
        # 1. Resolve dependencies
        profile = self._resolve_profile(db, user_id)
        tz_str = self._resolve_timezone(profile, timezone_override)
        lat, lon = self._resolve_location(profile, location_override)
        resolved_date = self._resolve_date(date_local, tz_str)
        reference_version_id = self._resolve_reference_version_id(db, reference_version)
        ruleset_id = self._resolve_ruleset_id(db, ruleset_version)

        # 2. Mode read_only : lecture seule, aucun calcul
        if mode == ComputeMode.read_only:
            run = DailyPredictionRepository(db).get_run(
                user_id, resolved_date, reference_version_id, ruleset_id
            )
            if run is None:
                return None
            return ServiceResult(run=run, engine_output=None, was_reused=True)

        # 3. Resolve natal chart
        natal_chart = self._resolve_natal_chart(db, user_id)

        # 4. Build EngineInput and compute hash BEFORE engine (AC2)
        engine_input = EngineInput(
            natal_chart=natal_chart,
            local_date=resolved_date,
            timezone=tz_str,
            latitude=lat,
            longitude=lon,
            reference_version=reference_version,
            ruleset_version=ruleset_version,
            debug_mode=False,
        )
        input_hash = self._compute_input_hash(engine_input)

        # 5. Mode compute_if_missing : short-circuit if hash exists
        if mode == ComputeMode.compute_if_missing:
            existing_run = DailyPredictionRepository(db).get_run_by_hash(user_id, input_hash)
            if existing_run:
                return ServiceResult(run=existing_run, engine_output=None, was_reused=True)

        # 6. Mode force_recompute : remove old run if it exists
        if mode == ComputeMode.force_recompute:
            old_run = DailyPredictionRepository(db).get_run(
                user_id, resolved_date, reference_version_id, ruleset_id
            )
            if old_run:
                db.delete(old_run)
                db.flush()

        # 7. Engine calculation
        def ctx_loader(ref: str, rule: str, dt: date) -> object:
            return self.context_loader.load(db, ref, rule, dt)

        if self._orchestrator_proto is not None:
            orchestrator = self._orchestrator_proto.with_context_loader(ctx_loader)
        else:
            orchestrator = EngineOrchestrator(prediction_context_loader=ctx_loader)
        try:
            engine_output = orchestrator.run(engine_input)
        except PredictionContextError as exc:
            raise DailyPredictionServiceError("context_error", str(exc)) from exc

        # 8. Persistence
        save_result = self.persistence_service.save(
            engine_output=engine_output,
            user_id=user_id,
            local_date=resolved_date,
            reference_version_id=reference_version_id,
            ruleset_id=ruleset_id,
            db=db,
        )

        return ServiceResult(
            run=save_result.run,
            engine_output=engine_output,
            was_reused=False,
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

    def _resolve_ruleset_id(self, db: Session, version: str) -> int:
        ruleset = PredictionRulesetRepository(db).get_ruleset(version)
        if ruleset is None:
            raise DailyPredictionServiceError(
                "ruleset_missing", f"Ruleset version '{version}' introuvable"
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
