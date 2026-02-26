"""
Service de calcul de thèmes natals.

Ce module orchestre le calcul des thèmes natals en utilisant les données
de référence et les règles de calcul astrologique.
"""

from __future__ import annotations

from collections.abc import Callable

from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.astrology.natal_calculation import (
    NatalCalculationError,
    NatalResult,
    build_natal_result,
)
from app.domain.astrology.natal_preparation import BirthInput
from app.services.reference_data_service import ReferenceDataService


class NatalCalculationService:
    """
    Service de calcul de thèmes natals.

    Coordonne le chargement des données de référence et l'exécution
    des calculs astrologiques.
    """

    @staticmethod
    def _resolve_engine(
        *,
        accurate: bool,
        engine_override: str | None,
        internal_request: bool,
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
                return "simplified"
            if not settings.swisseph_enabled:
                raise NatalCalculationError(
                    code="natal_engine_unavailable",
                    message="requested natal engine is unavailable",
                    details={"engine": "swisseph"},
                )
            return "swisseph"

        if accurate and not settings.swisseph_enabled:
            raise NatalCalculationError(
                code="natal_engine_unavailable",
                message="accurate mode requires SwissEph which is disabled",
                details={"engine": "swisseph"},
            )

        preferred = "swisseph" if accurate else settings.natal_engine_default
        if preferred == "swisseph" and settings.swisseph_enabled:
            return "swisseph"
        return "simplified"

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

        engine = NatalCalculationService._resolve_engine(
            accurate=accurate,
            engine_override=engine_override,
            internal_request=internal_request,
        )
        ephemeris_path_version: str | None = None
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

        return build_natal_result(
            birth_input=birth_input,
            reference_data=reference_data,
            ruleset_version=settings.ruleset_version,
            timeout_check=timeout_check,
            engine=engine,
            birth_lat=birth_input.birth_lat,
            birth_lon=birth_input.birth_lon,
            zodiac=zodiac,
            ayanamsa=ayanamsa,
            frame=frame,
            altitude_m=altitude_m,
            ephemeris_path_version=ephemeris_path_version,
        )
