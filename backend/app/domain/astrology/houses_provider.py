"""SwissEph houses provider: cuspides 1..12 + ASC/MC via swe.houses_ex.

Calcule les cuspides des 12 maisons natales (Placidus par défaut),
l'Ascendant et le Milieu-du-Ciel via pyswisseph.

Architecture strategy :
- ``_HOUSE_SYSTEM_CODES`` centralise le mapping nom public → code octet SwissEph.
- ``_SUPPORTED_HOUSE_SYSTEMS`` expose publiquement ``"placidus"``, ``"equal"``
  et ``"whole_sign"`` (story 23.2).
- ``UnsupportedHouseSystemError`` → 422 (erreur fonctionnelle).
- ``HousesCalcError`` → 503 (erreur technique runtime).

Usage::

    from app.domain.astrology.houses_provider import calculate_houses

    result = calculate_houses(jdut=2451545.0, lat=48.85, lon=2.35)
    result = calculate_houses(
        jdut=2451545.0, lat=48.85, lon=2.35,
        house_system="placidus",
        frame="topocentric",
    )
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from types import ModuleType

from app.core.ephemeris import SWISSEPH_LOCK
from app.infra.observability.metrics import increment_counter, observe_duration

logger = logging.getLogger(__name__)

METRIC_HOUSES_LATENCY = "swisseph_houses_latency_ms"
METRIC_ERRORS = "swisseph_errors_total"

# Mapping nom de système public → code octet SwissEph.
# Reference: pyswisseph houses_ex hsys parameter.
_HOUSE_SYSTEM_CODES: dict[str, bytes] = {
    "placidus": b"P",
    "equal": b"E",  # Exposé public API depuis story 23.2
    "whole_sign": b"W",  # Exposé public API depuis story 23.2
}

# Systèmes de maisons exposés en public API.
_SUPPORTED_HOUSE_SYSTEMS: frozenset[str] = frozenset({"placidus", "equal", "whole_sign"})

_DEFAULT_HOUSE_SYSTEM = "placidus"
_DEFAULT_FRAME = "geocentric"


@dataclass(frozen=True)
class HouseData:
    """Résultat du calcul des maisons natales via SwissEph."""

    cusps: tuple[float, ...]  # Cuspides maisons 1..12, normalisées [0, 360)
    ascendant_longitude: float  # Longitude ASC, normalisée [0, 360)
    mc_longitude: float  # Longitude MC, normalisée [0, 360)
    house_system: str  # Système de maisons appliqué


class HousesCalcError(Exception):
    """Levée quand swe.houses_ex échoue ou pyswisseph est indisponible."""

    code = "houses_calc_failed"

    def __init__(self, message: str = "Houses calculation failed") -> None:
        self.message = message
        super().__init__(message)


class UnsupportedHouseSystemError(Exception):
    """Levée quand le système de maisons demandé n'est pas supporté publiquement.

    Correspond à une erreur fonctionnelle 422 (le système existe en interne
    mais n'est pas exposé, ou est totalement inconnu).
    """

    code = "unsupported_house_system"

    def __init__(self, house_system: str) -> None:
        self.house_system = house_system
        self.message = f"House system not supported: {house_system!r}"
        super().__init__(self.message)


def _get_swe_module() -> ModuleType:
    """Lazy import and validation of swisseph module."""
    try:
        import swisseph as swe  # type: ignore[import-untyped]

        return swe
    except ImportError as exc:
        raise HousesCalcError("pyswisseph module is not installed") from exc


def _normalize_longitude(lon: float) -> float:
    """Normalise une longitude dans [0, 360)."""
    return lon % 360.0


def _extract_cusps(cusps_raw: tuple[object, ...]) -> tuple[float, ...]:
    """Extrait 12 cuspides à partir du format SwissEph.

    SwissEph peut retourner:
    - 13 éléments (index 0 inutilisé, 1..12 maisons)
    - 12 éléments (maisons 1..12 directement)
    """
    if len(cusps_raw) >= 13:
        source = cusps_raw[1:13]
    elif len(cusps_raw) == 12:
        source = cusps_raw
    else:
        raise HousesCalcError(f"houses_ex returned invalid cusp array length: {len(cusps_raw)}")
    return tuple(_normalize_longitude(float(value)) for value in source)


def calculate_houses(
    jdut: float,
    lat: float,
    lon: float,
    *,
    house_system: str = _DEFAULT_HOUSE_SYSTEM,
    frame: str = _DEFAULT_FRAME,
    altitude_m: float | None = None,
) -> HouseData:
    """Calcule les 12 cuspides de maisons + ASC/MC via swe.houses_ex.

    Args:
        jdut: Jour julien en Temps Universel (Julian Day UT).
        lat: Latitude géographique en degrés (−90 à +90).
        lon: Longitude géographique en degrés (−180 à +180).
        house_system: Système de maisons. Défaut ``"placidus"``.
            Valeurs supportées : ``"placidus"``, ``"equal"``, ``"whole_sign"``.
        frame: Référentiel de calcul. ``"geocentric"`` (défaut) ou
            ``"topocentric"``.
        altitude_m: Altitude en mètres pour le cadre topocentrique.
            Si ``None`` et ``frame="topocentric"``, ``0`` est utilisé
            explicitement.

    Returns:
        :class:`HouseData` avec 12 cuspides normalisées dans ``[0, 360)``
        et angles ASC/MC.

    Raises:
        UnsupportedHouseSystemError: Si ``house_system`` n'appartient pas à
            ``_SUPPORTED_HOUSE_SYSTEMS``. Code ``"unsupported_house_system"``
            → 422.
        HousesCalcError: Quand pyswisseph n'est pas installé ou que
            ``houses_ex`` échoue. Code ``"houses_calc_failed"`` → 503.
    """
    # Validation du house system avant tout appel SwissEph.
    if house_system not in _SUPPORTED_HOUSE_SYSTEMS:
        raise UnsupportedHouseSystemError(house_system)

    is_topocentric = frame == "topocentric"
    # AC3 : altitude implicite 0 si frame topocentric sans altitude fournie.
    effective_altitude = altitude_m if altitude_m is not None else 0.0
    hsys_code = _HOUSE_SYSTEM_CODES[house_system]

    topo_set = False
    start = time.monotonic()

    try:
        swe = _get_swe_module()

        with SWISSEPH_LOCK:
            try:
                if is_topocentric:
                    try:
                        swe.set_topo(lon, lat, effective_altitude)
                        topo_set = True
                    except Exception as exc:
                        raise HousesCalcError(
                            f"Failed to set topocentric position: {type(exc).__name__}"
                        ) from exc

                try:
                    cusps_raw, ascmc_raw = swe.houses_ex(jdut, lat, lon, hsys_code)
                except Exception as exc:
                    raise HousesCalcError(f"houses_ex failed: {type(exc).__name__}") from exc

            finally:
                if topo_set:
                    try:
                        swe.set_topo(0.0, 0.0, 0.0)
                    except Exception as exc:
                        # Ne pas masquer les exceptions d'origine, mais logger.
                        logger.error(
                            "failed_to_reset_topocentric_position error_type=%s",
                            type(exc).__name__,
                        )
    except HousesCalcError:
        increment_counter(f"{METRIC_ERRORS}|code=houses_calc_failed|house_system={house_system}")
        raise

    elapsed_ms = (time.monotonic() - start) * 1000.0
    observe_duration(f"{METRIC_HOUSES_LATENCY}|house_system={house_system}", elapsed_ms)

    # SwissEph peut retourner 12 ou 13 cuspides selon version/binding.
    cusps = _extract_cusps(cusps_raw)
    asc = _normalize_longitude(float(ascmc_raw[0]))
    mc = _normalize_longitude(float(ascmc_raw[1]))

    logger.debug(
        "houses_calculated jdut=%.4f house_system=%s frame=%s altitude_m=%s",
        jdut,
        house_system,
        frame,
        effective_altitude if is_topocentric else "n/a",
    )

    return HouseData(
        cusps=cusps,
        ascendant_longitude=asc,
        mc_longitude=mc,
        house_system=house_system,
    )
