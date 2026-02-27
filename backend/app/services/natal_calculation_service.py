"""
Service de calcul de thèmes natals.

Ce module orchestre le calcul des thèmes natals en utilisant les données
de référence et les règles de calcul astrologique.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.astrology.ephemeris_provider import SUPPORTED_AYANAMSAS, EphemerisCalcError
from app.domain.astrology.houses_provider import HousesCalcError
from app.domain.astrology.natal_calculation import (
    NatalCalculationError,
    NatalResult,
    build_natal_result,
)
from app.domain.astrology.natal_preparation import BirthInput
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
        zodiac: str,
        frame: str,
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
                if zodiac == "sidereal" or frame == "topocentric":
                    raise NatalCalculationError(
                        code="natal_engine_option_unsupported",
                        message="simplified engine does not support sidereal or topocentric",
                        details={"zodiac": zodiac, "frame": frame},
                    )
                return "simplified"
            if not settings.swisseph_enabled:
                raise NatalCalculationError(
                    code="natal_engine_unavailable",
                    message="requested natal engine is unavailable",
                    details={"engine": "swisseph"},
                )
            return "swisseph"

        # Sidereal and Topocentric require SwissEph
        requires_accurate = zodiac == "sidereal" or frame == "topocentric"
        if requires_accurate and not accurate:
            raise NatalCalculationError(
                code="accurate_mode_required",
                message="sidereal zodiac or topocentric frame requires accurate=True",
                details={"zodiac": zodiac, "frame": frame},
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
        zodiac: str,
        ayanamsa: str | None,
        frame: str,
        altitude_m: float | None,
    ) -> tuple[str, str | None, str, float | None]:
        normalized_zodiac = zodiac.strip().lower()
        if normalized_zodiac not in {"tropical", "sidereal"}:
            raise NatalCalculationError(
                code="invalid_zodiac",
                message="invalid zodiac parameter",
                details={"allowed": "tropical,sidereal", "actual": zodiac},
            )

        normalized_frame = frame.strip().lower()
        if normalized_frame not in {"geocentric", "topocentric"}:
            raise NatalCalculationError(
                code="invalid_frame",
                message="invalid frame parameter",
                details={"allowed": "geocentric,topocentric", "actual": frame},
            )

        normalized_ayanamsa: str | None = None
        if normalized_zodiac == "sidereal":
            normalized_ayanamsa = (ayanamsa or "").strip().lower() or "lahiri"
            if normalized_ayanamsa not in SUPPORTED_AYANAMSAS:
                raise NatalCalculationError(
                    code="invalid_ayanamsa",
                    message="unsupported ayanamsa for sidereal zodiac",
                    details={
                        "allowed": ",".join(sorted(SUPPORTED_AYANAMSAS)),
                        "actual": normalized_ayanamsa,
                    },
                )

        effective_altitude = None
        if normalized_frame == "topocentric":
            effective_altitude = 0.0 if altitude_m is None else altitude_m

        return normalized_zodiac, normalized_ayanamsa, normalized_frame, effective_altitude

    @staticmethod
    def calculate(
        db: Session,
        birth_input: BirthInput,
        reference_version: str | None = None,
        timeout_check: Callable[[], None] | None = None,
        accurate: bool = False,
        engine_override: str | None = None,
        internal_request: bool = False,
        zodiac: str = "tropical",
        ayanamsa: str | None = None,
        frame: str = "geocentric",
        altitude_m: float | None = None,
        request_id: str | None = None,
        tt_enabled: bool = False,
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
            resolved_altitude_m,
        ) = NatalCalculationService._resolve_calculation_options(
            zodiac=zodiac,
            ayanamsa=ayanamsa,
            frame=frame,
            altitude_m=altitude_m,
        )

        engine = NatalCalculationService._resolve_engine(
            accurate=accurate,
            engine_override=engine_override,
            internal_request=internal_request,
            zodiac=resolved_zodiac,
            frame=resolved_frame,
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
                altitude_m=resolved_altitude_m,
                ephemeris_path_version=ephemeris_path_version,
                ephemeris_path_hash=ephemeris_path_hash,
                tt_enabled=tt_enabled,
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
