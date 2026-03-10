from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import select

from app.core.config import settings
from app.core.versions import LEGACY_RULESET_VERSION, get_active_ruleset_version
from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.repositories.chart_result_repository import ChartResultRepository
from app.infra.db.repositories.prediction_ruleset_repository import PredictionRulesetRepository
from app.infra.db.repositories.user_birth_profile_repository import UserBirthProfileRepository
from app.prediction.schemas import EngineInput
from app.services.user_birth_profile_service import UserBirthProfileService

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.infra.db.models.user_birth_profile import UserBirthProfileModel

logger = logging.getLogger()


@dataclass(frozen=True)
class ResolvedPredictionRequest:
    user_id: int
    engine_input: EngineInput | None
    resolved_date: date
    reference_version_id: int
    ruleset_id: int
    timezone: str
    reference_version: str
    ruleset_version: str


class PredictionRequestResolver:
    """
    Handles the resolution of all inputs required for a daily prediction run.
    """

    def resolve(
        self,
        db: Session,
        user_id: int,
        date_local: date | None = None,
        location_override: tuple[float, float] | None = None,
        timezone_override: str | None = None,
        reference_version: str | None = None,
        ruleset_version: str | None = None,
        include_engine_input: bool = True,
    ) -> ResolvedPredictionRequest:
        resolved_reference_version = reference_version or settings.active_reference_version
        resolved_ruleset_version = ruleset_version or settings.active_ruleset_version
        
        profile = self._resolve_profile(db, user_id)
        tz_str = self._resolve_timezone(profile, timezone_override)
        lat, lon = self._resolve_location(db, profile, location_override)
        resolved_date = self._resolve_date(date_local, tz_str)
        
        reference_version_id = self._resolve_reference_version_id(db, resolved_reference_version)
        ruleset_id = self._resolve_ruleset_id(db, resolved_ruleset_version, reference_version_id)
        
        engine_input: EngineInput | None = None
        if include_engine_input:
            natal_chart = self._resolve_natal_chart(db, user_id)
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

        return ResolvedPredictionRequest(
            user_id=user_id,
            engine_input=engine_input,
            resolved_date=resolved_date,
            reference_version_id=reference_version_id,
            ruleset_id=ruleset_id,
            timezone=tz_str,
            reference_version=resolved_reference_version,
            ruleset_version=resolved_ruleset_version,
        )

    def _resolve_profile(self, db: Session, user_id: int) -> UserBirthProfileModel:
        from app.services.daily_prediction_types import DailyPredictionServiceError
        profile = UserBirthProfileRepository(db).get_by_user_id(user_id)
        if profile is None:
            raise DailyPredictionServiceError("profile_missing", "Profil de naissance introuvable")
        return profile

    def _resolve_timezone(self, profile: UserBirthProfileModel, override: str | None) -> str:
        from app.services.daily_prediction_types import DailyPredictionServiceError
        tz_str = override or profile.current_timezone or profile.birth_timezone
        if not tz_str:
            raise DailyPredictionServiceError("timezone_missing", "Timezone introuvable")
        try:
            ZoneInfo(tz_str)
        except (ZoneInfoNotFoundError, KeyError):
            raise DailyPredictionServiceError("timezone_invalid", f"Timezone invalide : '{tz_str}'")
        return tz_str

    def _resolve_location(
        self,
        db: Session,
        profile: UserBirthProfileModel,
        override: tuple[float, float] | None,
    ) -> tuple[float, float]:
        from app.services.daily_prediction_types import DailyPredictionServiceError
        if override:
            return override
        if profile.current_lat is not None and profile.current_lon is not None:
            return profile.current_lat, profile.current_lon

        resolved = UserBirthProfileService.resolve_coordinates(db, profile)
        if resolved.birth_lat is None or resolved.birth_lon is None:
            raise DailyPredictionServiceError("location_missing", "Localisation introuvable")
        return resolved.birth_lat, resolved.birth_lon

    def _resolve_date(self, date_local: date | None, tz_str: str) -> date:
        if date_local is not None:
            return date_local
        return datetime.now(ZoneInfo(tz_str)).date()

    def _resolve_natal_chart(self, db: Session, user_id: int) -> dict[str, Any]:
        from app.services.daily_prediction_types import DailyPredictionServiceError
        chart = ChartResultRepository(db).get_latest_by_user_id(user_id)
        if chart is None:
            raise DailyPredictionServiceError("natal_missing", "Aucun thème natal trouvé")
        return self._normalize_natal_chart_payload(chart.result_payload)

    def _normalize_natal_chart_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(payload)
        if "planets" in normalized:
            return normalized

        planet_positions = normalized.get("planet_positions")
        if not isinstance(planet_positions, list):
            return normalized

        planets: list[dict[str, Any]] = []
        for position in planet_positions:
            if not isinstance(position, dict):
                continue
            code = position.get("code") or position.get("planet_code")
            longitude = position.get("longitude")
            if code is None or longitude is None:
                continue
            planets.append({"code": code, "longitude": longitude})

        if planets:
            normalized["planets"] = planets
        return normalized

    def _resolve_reference_version_id(self, db: Session, version: str) -> int:
        from app.services.daily_prediction_types import DailyPredictionServiceError
        rv_id = db.scalar(
            select(ReferenceVersionModel.id).where(ReferenceVersionModel.version == version)
        )
        if rv_id is None and self._should_auto_seed_reference_version(version):
            self._auto_seed_reference_version(db, version=version)
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
        from app.services.daily_prediction_types import DailyPredictionServiceError
        repo = PredictionRulesetRepository(db)
        ruleset = repo.get_ruleset(version)
        if ruleset is None and self._should_auto_seed_prediction_ruleset(version):
            self._auto_seed_prediction_ruleset(
                db,
                ruleset_version=version,
                expected_reference_version_id=expected_reference_version_id,
            )
            ruleset = repo.get_ruleset(version)

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

    def _should_auto_seed_prediction_ruleset(self, version: str) -> bool:
        if settings.app_env in {"production", "prod"}:
            return False
        return version in {settings.active_ruleset_version, LEGACY_RULESET_VERSION}

    def _should_auto_seed_reference_version(self, version: str) -> bool:
        if settings.app_env in {"production", "prod"}:
            return False
        return version in {settings.active_reference_version, LEGACY_RULESET_VERSION}

    def _auto_seed_reference_version(self, db: Session, *, version: str) -> None:
        from app.services.reference_data_service import ReferenceDataService

        if version != LEGACY_RULESET_VERSION:
            ReferenceDataService.seed_reference_version(db, LEGACY_RULESET_VERSION)
        ReferenceDataService.seed_reference_version(db, version)

    def _auto_seed_prediction_ruleset(
        self,
        db: Session,
        *,
        ruleset_version: str,
        expected_reference_version_id: int | None,
    ) -> None:
        from app.services.daily_prediction_types import DailyPredictionServiceError
        from scripts.seed_31_prediction_reference_v2 import SeedAbortError, run_seed

        try:
            run_seed(db)
            db.commit()
            return
        except SeedAbortError as exc:
            db.rollback()
            if not self._repair_locked_incomplete_reference_version(
                db,
                expected_reference_version_id=expected_reference_version_id,
                error_text=str(exc),
            ):
                raise DailyPredictionServiceError(
                    "ruleset_seed_failed",
                    f"Seed automatique impossible pour le ruleset '{ruleset_version}': {exc}",
                ) from exc

        try:
            run_seed(db)
            db.commit()
        except SeedAbortError as exc:
            db.rollback()
            raise DailyPredictionServiceError(
                "ruleset_seed_failed",
                f"Seed automatique impossible pour le ruleset '{ruleset_version}': {exc}",
            ) from exc

    def _repair_locked_incomplete_reference_version(
        self,
        db: Session,
        *,
        expected_reference_version_id: int | None,
        error_text: str,
    ) -> bool:
        if "LOCKED but is incomplete" not in error_text:
            return False

        version_model = None
        if expected_reference_version_id is not None:
            version_model = db.get(ReferenceVersionModel, expected_reference_version_id)
        if version_model is None:
            version_model = db.scalar(
                select(ReferenceVersionModel).where(
                    ReferenceVersionModel.version == settings.active_reference_version
                )
            )
        if version_model is None or not version_model.is_locked:
            return False

        logger.warning(
            "prediction.ruleset_autoseed_repair",
            extra={
                "reference_version": version_model.version,
                "reference_version_id": version_model.id,
            },
        )
        version_model.is_locked = False
        db.commit()
        return True
