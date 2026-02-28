"""
Service de calcul de thèmes natals.

Ce module orchestre le calcul des thèmes natals en utilisant les données
de référence et les règles de calcul astrologique.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from sqlalchemy.orm import Session

from app.core.config import FrameType, HouseSystemType, ZodiacType, settings
from app.domain.astrology.ephemeris_provider import SUPPORTED_AYANAMSAS, EphemerisCalcError
from app.domain.astrology.houses_provider import HousesCalcError
from app.domain.astrology.natal_calculation import (
    NatalCalculationError,
    NatalResult,
    build_natal_result,
)
from app.domain.astrology.natal_preparation import BirthInput
from app.infra.observability.metrics import increment_counter
from app.services.reference_data_service import ReferenceDataService

logger = logging.getLogger(__name__)


class NatalCalculationService:
    """
    Service de calcul de thèmes natals.

    Coordonne le chargement des données de référence et l'exécution
    des calculs astrologiques.
    """

    @staticmethod
    def _is_swisseph_provider_error(error: Exception) -> bool:
        """Return True for SwissEph provider errors, even if class identity drifted.

        In large test suites some modules can be reloaded, creating a new exception
        class object with the same name. `isinstance()` may then fail across modules.
        """
        if isinstance(error, (EphemerisCalcError, HousesCalcError)):
            return True
        return error.__class__.__name__ in {"EphemerisCalcError", "HousesCalcError"}

    @staticmethod
    def _resolve_engine(
        *,
        accurate: bool,
        engine_override: str | None,
        internal_request: bool,
        zodiac: ZodiacType,
        frame: FrameType,
        house_system: HouseSystemType,
    ) -> str:
        override = (engine_override or "").strip().lower() or None

        if override is not None:
            if override not in {"swisseph", "simplified"}:
                raise NatalCalculationError(
                    code="invalid_natal_engine_override",
                    message="invalid natal engine override",
                    details={"allowed": "swisseph,simplified", "actual": override},
                )
            if override == "simplified":
                if (
                    not internal_request
                    or settings.app_env == "production"
                    or not settings.natal_engine_simplified_enabled
                ):
                    raise NatalCalculationError(
                        code="natal_engine_override_forbidden",
                        message="natal engine override is forbidden",
                        details={"engine": "simplified"},
                    )
                if (
                    zodiac != ZodiacType.TROPICAL
                    or frame != FrameType.GEOCENTRIC
                    or house_system != HouseSystemType.EQUAL
                ):
                    increment_counter(
                        "natal_ruleset_invalid_total|code=natal_engine_option_unsupported"
                    )
                    raise NatalCalculationError(
                        code="natal_engine_option_unsupported",
                        message="simplified engine only supports tropical/geocentric/equal",
                        details={"zodiac": zodiac, "frame": frame, "house_system": house_system},
                    )
                return "simplified"
            if not settings.swisseph_enabled:
                raise NatalCalculationError(
                    code="natal_engine_unavailable",
                    message="requested natal engine is unavailable",
                    details={"engine": "swisseph"},
                )
            return "swisseph"

        # Sidereal, Topocentric, or non-Equal house system require SwissEph
        requires_accurate = (
            zodiac == ZodiacType.SIDEREAL
            or frame == FrameType.TOPOCENTRIC
            or house_system != HouseSystemType.EQUAL
        )
        if requires_accurate and not accurate:
            increment_counter("natal_ruleset_invalid_total|code=accurate_mode_required")
            raise NatalCalculationError(
                code="accurate_mode_required",
                message="sidereal, topocentric or non-equal house system requires accurate=True",
                details={"zodiac": zodiac, "frame": frame, "house_system": house_system},
            )

        if (accurate or requires_accurate) and not settings.swisseph_enabled:
            raise NatalCalculationError(
                code="natal_engine_unavailable",
                message="accurate mode requires SwissEph which is disabled",
                details={"engine": "swisseph"},
            )

        preferred = "swisseph" if (accurate or requires_accurate) else settings.natal_engine_default
        if preferred == "swisseph" and settings.swisseph_enabled:
            return "swisseph"
        return "simplified"

    @staticmethod
    def _resolve_calculation_options(
        *,
        zodiac: str | None,
        ayanamsa: str | None,
        frame: str | None,
        house_system: str | None,
        altitude_m: float | None,
        prefer_simplified_defaults: bool = False,
    ) -> tuple[ZodiacType, str | None, FrameType, HouseSystemType, float | None]:
        zodiac_str = (zodiac or "").strip().lower()
        if not zodiac_str:
            resolved_zodiac = settings.natal_ruleset_default_zodiac
        else:
            try:
                resolved_zodiac = ZodiacType(zodiac_str)
            except ValueError:
                increment_counter("natal_ruleset_invalid_total|code=invalid_zodiac")
                raise NatalCalculationError(
                    code="invalid_zodiac",
                    message="invalid zodiac parameter",
                    details={
                        "allowed": ",".join(z.value for z in ZodiacType),
                        "actual": zodiac or "",
                    },
                )

        frame_str = (frame or "").strip().lower()
        if not frame_str:
            resolved_frame = settings.natal_ruleset_default_frame
        else:
            try:
                resolved_frame = FrameType(frame_str)
            except ValueError:
                increment_counter("natal_ruleset_invalid_total|code=invalid_frame")
                raise NatalCalculationError(
                    code="invalid_frame",
                    message="invalid frame parameter",
                    details={
                        "allowed": ",".join(f.value for f in FrameType),
                        "actual": frame or "",
                    },
                )

        hs_str = (house_system or "").strip().lower()
        if not hs_str:
            # Runtime compatibility: when caller indicates simplified defaults are preferred
            # and no explicit house_system is provided, default to EQUAL for non-accurate
            # tropical/geocentric requests.
            zodiac_str = (zodiac or "").strip().lower()
            frame_str = (frame or "").strip().lower()
            requires_accurate = zodiac_str == "sidereal" or frame_str == "topocentric"
            if prefer_simplified_defaults and not requires_accurate:
                resolved_house_system = HouseSystemType.EQUAL
            else:
                resolved_house_system = settings.natal_ruleset_default_house_system
        else:
            try:
                resolved_house_system = HouseSystemType(hs_str)
            except ValueError:
                increment_counter("natal_ruleset_invalid_total|code=invalid_house_system")
                raise NatalCalculationError(
                    code="invalid_house_system",
                    message="invalid house_system parameter",
                    details={
                        "allowed": ",".join(h.value for h in HouseSystemType),
                        "actual": house_system or "",
                    },
                )

        resolved_ayanamsa: str | None = None
        if resolved_zodiac == ZodiacType.SIDEREAL:
            # AC 2: sidereal WITHOUT ayanamsa must return 422 if explicitly requested.
            # If zodiac was None, it took default. If default is sidereal, it might also need ayanamsa.
            resolved_ayanamsa = (ayanamsa or "").strip().lower() or None
            if resolved_ayanamsa and resolved_ayanamsa not in SUPPORTED_AYANAMSAS:
                increment_counter("natal_ruleset_invalid_total|code=invalid_ayanamsa")
                raise NatalCalculationError(
                    code="invalid_ayanamsa",
                    message="unsupported ayanamsa for sidereal zodiac",
                    details={
                        "allowed": ",".join(sorted(SUPPORTED_AYANAMSAS)),
                        "actual": resolved_ayanamsa,
                    },
                )

        effective_altitude = None
        if resolved_frame == FrameType.TOPOCENTRIC:
            effective_altitude = 0.0 if altitude_m is None else altitude_m

        return (
            resolved_zodiac,
            resolved_ayanamsa,
            resolved_frame,
            resolved_house_system,
            effective_altitude,
        )

    @staticmethod
    def calculate(
        db: Session,
        birth_input: BirthInput,
        reference_version: str | None = None,
        timeout_check: Callable[[], None] | None = None,
        accurate: bool = False,
        engine_override: str | None = None,
        internal_request: bool = False,
        zodiac: str | None = None,
        ayanamsa: str | None = None,
        frame: str | None = None,
        house_system: str | None = None,
        altitude_m: float | None = None,
        request_id: str | None = None,
        tt_enabled: bool = False,
        aspect_school: str | None = None,
    ) -> NatalResult:
        """
        Calcule un thème natal complet.

        Args:
            db: Session de base de données.
            birth_input: Données de naissance.
            reference_version: Version des données de référence (optionnel).
            timeout_check: Callback de vérification de timeout (optionnel).
            accurate: Si True, utilise le moteur SwissEph si disponible.
            engine_override: Override interne d'engine (``"swisseph"`` ou ``"simplified"``).
            internal_request: Indique qu'il s'agit d'un appel interne autorisé.
            zodiac: Zodiaque à utiliser (``"tropical"`` ou ``"sidereal"``).
            ayanamsa: Ayanamsa pour zodiaque sidéral (défaut ``"lahiri"``).
            frame: Référentiel de calcul (``"geocentric"`` ou ``"topocentric"``).
            altitude_m: Altitude en mètres pour le cadre topocentrique.
            tt_enabled: Si True, calcule ΔT et JD TT pour la traçabilité audit (story 22.2).

        Returns:
            Résultat du calcul natal.

        Raises:
            NatalCalculationError: Si la version de référence n'existe pas.
            EphemerisDataMissingError: Si les données SwissEph sont manquantes (accurate=True).
            SwissEphInitError: Si SwissEph n'est pas initialisé (accurate=True).
        """
        resolved_version = reference_version or settings.active_reference_version

        if timeout_check is not None:
            timeout_check()
        reference_data = ReferenceDataService.get_active_reference_data(
            db,
            version=resolved_version,
        )
        if timeout_check is not None:
            timeout_check()

        if not reference_data:
            raise NatalCalculationError(
                code="reference_version_not_found",
                message="reference version not found",
                details={"version": resolved_version},
            )

        (
            resolved_zodiac,
            resolved_ayanamsa,
            resolved_frame,
            resolved_house_system,
            resolved_altitude_m,
        ) = NatalCalculationService._resolve_calculation_options(
            zodiac=zodiac,
            ayanamsa=ayanamsa,
            frame=frame,
            house_system=house_system,
            altitude_m=altitude_m,
            prefer_simplified_defaults=not accurate and not engine_override,
        )

        # AC 2: Given zodiac=sidereal sans ayanamsa -> 422 missing_ayanamsa
        # This applies when zodiac is explicitly requested as sidereal.
        if (zodiac or "").strip().lower() == "sidereal" and not (ayanamsa or "").strip():
            increment_counter("natal_ruleset_invalid_total|code=missing_ayanamsa")
            raise NatalCalculationError(
                code="missing_ayanamsa",
                message="ayanamsa is required when sidereal zodiac is explicitly requested",
                details={"zodiac": "sidereal"},
            )

        # Fallback to default ayanamsa if still missing (e.g. zodiac came from defaults)
        if resolved_zodiac == ZodiacType.SIDEREAL and not resolved_ayanamsa:
            resolved_ayanamsa = settings.natal_ruleset_default_ayanamsa
            if not resolved_ayanamsa:
                increment_counter("natal_ruleset_invalid_total|code=missing_ayanamsa")
                raise NatalCalculationError(
                    code="missing_ayanamsa",
                    message="ayanamsa is required for sidereal zodiac",
                    details={"zodiac": "sidereal"},
                )

        engine = NatalCalculationService._resolve_engine(
            accurate=accurate,
            engine_override=engine_override,
            internal_request=internal_request,
            zodiac=resolved_zodiac,
            frame=resolved_frame,
            house_system=resolved_house_system,
        )

        # Story 23-3: topocentric frame requires lat/lon to avoid provider-level 503
        if resolved_frame == FrameType.TOPOCENTRIC:
            if birth_input.birth_lat is None or birth_input.birth_lon is None:
                increment_counter(
                    "natal_ruleset_invalid_total|code=missing_topocentric_coordinates"
                )
                raise NatalCalculationError(
                    code="missing_topocentric_coordinates",
                    message="lat/lon are required for topocentric frame",
                    details={"frame": "topocentric"},
                )

        ephemeris_path_version: str | None = None
        ephemeris_path_hash: str | None = None
        if engine == "swisseph":
            from app.core.ephemeris import (
                SwissEphInitError,
                get_bootstrap_result,
            )

            bootstrap = get_bootstrap_result()
            if bootstrap is None:
                raise SwissEphInitError("SwissEph bootstrap was not called at startup")
            if not bootstrap.success:
                # Re-raise the stored bootstrap error
                if bootstrap.error is not None:
                    raise bootstrap.error
                raise SwissEphInitError("SwissEph bootstrap failed with unknown error")
            engine = "swisseph"
            ephemeris_path_version = bootstrap.path_version
            ephemeris_path_hash = getattr(bootstrap, "path_hash", "") or None

        # Story 24-1: aspect school and versioned rules identifier.
        from app.core.config import AspectSchoolType

        aspect_school_str = (aspect_school or "").strip().lower()
        if not aspect_school_str:
            resolved_aspect_school = settings.natal_ruleset_default_aspect_school
        else:
            try:
                resolved_aspect_school = AspectSchoolType(aspect_school_str)
            except ValueError:
                increment_counter("natal_ruleset_invalid_total|code=invalid_aspect_school")
                raise NatalCalculationError(
                    code="invalid_aspect_school",
                    message="invalid aspect_school parameter",
                    details={
                        "allowed": ",".join(s.value for s in AspectSchoolType),
                        "actual": aspect_school or "",
                    },
                )

        aspect_rules_version = f"{resolved_aspect_school.value}-{settings.ruleset_version}"

        try:
            return build_natal_result(
                birth_input=birth_input,
                reference_data=reference_data,
                ruleset_version=settings.ruleset_version,
                timeout_check=timeout_check,
                engine=engine,
                birth_lat=birth_input.birth_lat,
                birth_lon=birth_input.birth_lon,
                zodiac=resolved_zodiac,
                ayanamsa=resolved_ayanamsa,
                frame=resolved_frame,
                house_system=resolved_house_system,
                altitude_m=resolved_altitude_m,
                ephemeris_path_version=ephemeris_path_version,
                ephemeris_path_hash=ephemeris_path_hash,
                tt_enabled=tt_enabled,
                aspect_school=resolved_aspect_school,
                aspect_rules_version=aspect_rules_version,
            )
        except Exception as error:
            if not NatalCalculationService._is_swisseph_provider_error(error):
                raise
            logger.error(
                "swisseph_calc_error request_id=%s engine=%s ephe_version=%s ephe_hash=%s code=%s",
                request_id or "unknown",
                engine,
                ephemeris_path_version or "n/a",
                ephemeris_path_hash or "n/a",
                getattr(error, "code", "swisseph_calc_failed"),
            )
            raise NatalCalculationError(
                code=getattr(error, "code", "swisseph_calc_failed"),
                message=getattr(error, "message", str(error)),
                details={"engine": engine},
            ) from error
