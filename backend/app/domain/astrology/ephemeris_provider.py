"""SwissEph ephemeris provider: positions planétaires via swe.calc_ut.

Calcule la longitude écliptique, latitude, vitesse longitudinale et indicateur
de rétrograde pour les 10 corps majeurs (Sun..Pluto) via pyswisseph.

Le mode sidéral (``zodiac="sidereal"``) est encapsulé par appel : l'état global
``swe.set_sid_mode`` est réinitialisé à zéro après chaque calcul pour éviter
tout effet de bord permanent.

Usage::

    from app.domain.astrology.ephemeris_provider import calculate_planets

    planets = calculate_planets(jdut=2451545.0)          # tropical
    planets = calculate_planets(jdut=2451545.0, zodiac="sidereal")  # sidéral Lahiri
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from types import ModuleType
from typing import TYPE_CHECKING

from app.core.ephemeris import SWISSEPH_LOCK

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Mapping stable : id planète interne → constante entière SwissEph.
# swe.SUN=0, swe.MOON=1, swe.MERCURY=2, swe.VENUS=3, swe.MARS=4,
# swe.JUPITER=5, swe.SATURN=6, swe.URANUS=7, swe.NEPTUNE=8, swe.PLUTO=9
_PLANET_IDS: dict[str, int] = {
    "sun": 0,
    "moon": 1,
    "mercury": 2,
    "venus": 3,
    "mars": 4,
    "jupiter": 5,
    "saturn": 6,
    "uranus": 7,
    "neptune": 8,
    "pluto": 9,
}

# Ayanamsa name → constante SwissEph SIDM.
_AYANAMSA_IDS: dict[str, int] = {
    "lahiri": 1,  # swe.SIDM_LAHIRI
    "fagan_bradley": 0,  # swe.SIDM_FAGAN_BRADLEY
}

SUPPORTED_AYANAMSAS = frozenset(_AYANAMSA_IDS.keys())

# Constantes de flags SwissEph (stables entre versions).
_FLG_SWIEPH: int = 2  # swe.FLG_SWIEPH
_FLG_SPEED: int = 256  # swe.FLG_SPEED
_FLG_SIDEREAL: int = 65536  # swe.FLG_SIDEREAL
SIDM_RESET: int = 0  # reset après mode sidéral (SIDM_FAGAN_BRADLEY)


@dataclass(frozen=True)
class PlanetData:
    """Coordonnées écliptiques et indicateur rétrograde pour une planète."""

    planet_id: str
    longitude: float  # longitude écliptique, 0 <= lon < 360 degrés
    latitude: float  # latitude écliptique, degrés
    speed_longitude: float  # vitesse longitudinale, degrés/jour
    is_retrograde: bool  # True quand speed_longitude < 0


class EphemerisCalcError(Exception):
    """Levée quand swe.calc_ut échoue ou pyswisseph est indisponible."""

    code = "ephemeris_calc_failed"

    def __init__(self, message: str = "Ephemeris calculation failed") -> None:
        self.message = message
        super().__init__(message)


def _get_swe_module() -> ModuleType:
    """Lazy import and validation of swisseph module."""
    try:
        import swisseph as swe

        return swe
    except ImportError as exc:
        raise EphemerisCalcError("pyswisseph module is not installed") from exc


def _normalize_longitude(lon: float) -> float:
    """Normalise une longitude écliptique dans [0, 360)."""
    return lon % 360.0


def calculate_planets(
    jdut: float,
    lat: float | None = None,
    lon: float | None = None,
    *,
    zodiac: str = "tropical",
    ayanamsa: str | None = None,
    frame: str = "geocentric",
    altitude_m: float | None = None,
) -> list[PlanetData]:
    """Calcule les positions de Sun..Pluto via swe.calc_ut.

    Args:
        jdut: Jour julien en Temps Universel (Julian Day UT).
        lat: Latitude (requis si ``frame="topocentric"``).
        lon: Longitude (requis si ``frame="topocentric"``).
        zodiac: ``"tropical"`` (défaut) ou ``"sidereal"``.
        ayanamsa: Uniquement pour ``zodiac="sidereal"``.
            Défaut ``"lahiri"`` quand ``None``.
        frame: ``"geocentric"`` (défaut) ou ``"topocentric"``.
        altitude_m: Altitude en mètres. Défaut ``0.0`` si topocentrique.

    Returns:
        Liste de :class:`PlanetData` dans l'ordre de définition.

    Raises:
        EphemerisCalcError: Si pyswisseph est absent, si ``calc_ut`` échoue,
            ou si lat/lon manquent pour le mode topocentrique.
    """
    swe = _get_swe_module()

    is_sidereal = zodiac == "sidereal"
    effective_ayanamsa = (ayanamsa or "lahiri") if is_sidereal else None
    is_topocentric = frame == "topocentric"

    # Resolve flags from module if possible, otherwise use hardcoded stable defaults
    flg_swieph = getattr(swe, "FLG_SWIEPH", _FLG_SWIEPH)
    flg_speed = getattr(swe, "FLG_SPEED", _FLG_SPEED)
    flg_sidereal = getattr(swe, "FLG_SIDEREAL", _FLG_SIDEREAL)
    flg_topocentric = getattr(swe, "FLG_TOPOCENTRIC", 32768)  # swe.FLG_TOPOCENTRIC
    sidm_reset = getattr(swe, "SIDM_FAGAN_BRADLEY", SIDM_RESET)

    flags = flg_swieph | flg_speed
    topo_set = False

    results: list[PlanetData] = []

    with SWISSEPH_LOCK:
        if is_sidereal:
            flags |= flg_sidereal
            ayanamsa_id = _AYANAMSA_IDS.get(effective_ayanamsa or "lahiri")
            if ayanamsa_id is None:
                raise EphemerisCalcError(f"Unknown ayanamsa: {effective_ayanamsa}")
            try:
                swe.set_sid_mode(ayanamsa_id)
            except Exception as exc:
                raise EphemerisCalcError(
                    f"Failed to set sidereal mode: {type(exc).__name__}"
                ) from exc

        if is_topocentric:
            if lat is None or lon is None:
                raise EphemerisCalcError("lat/lon are required for topocentric frame")
            flags |= flg_topocentric
            try:
                swe.set_topo(lon, lat, altitude_m or 0.0)
                topo_set = True
            except Exception as exc:
                raise EphemerisCalcError(
                    f"Failed to set topocentric position: {type(exc).__name__}"
                ) from exc

        try:
            for planet_id, swe_id in _PLANET_IDS.items():
                try:
                    xx, retflag = swe.calc_ut(jdut, swe_id, flags)
                except Exception as exc:
                    raise EphemerisCalcError(
                        f"calc_ut failed for {planet_id}: {type(exc).__name__}"
                    ) from exc

                if retflag < 0:
                    raise EphemerisCalcError(f"calc_ut returned error flag for planet {planet_id}")

                speed_lon = float(xx[3])
                results.append(
                    PlanetData(
                        planet_id=planet_id,
                        longitude=_normalize_longitude(float(xx[0])),
                        latitude=float(xx[1]),
                        speed_longitude=speed_lon,
                        is_retrograde=speed_lon < 0.0,
                    )
                )
        finally:
            if is_sidereal:
                # Réinitialise le mode sidéral pour éviter un état global permanent.
                try:
                    swe.set_sid_mode(sidm_reset)
                except Exception as exc:
                    # Ne pas masquer les exceptions d'origine, mais logger.
                    logger.error(
                        "failed_to_reset_sidereal_mode error_type=%s",
                        type(exc).__name__,
                    )
            if topo_set:
                try:
                    swe.set_topo(0.0, 0.0, 0.0)
                except Exception as exc:
                    logger.error(
                        "failed_to_reset_topocentric_position error_type=%s",
                        type(exc).__name__,
                    )

    logger.debug(
        "ephemeris_planets_calculated jdut=%.4f zodiac=%s ayanamsa=%s frame=%s planet_count=%d",
        jdut,
        zodiac,
        effective_ayanamsa or "n/a",
        frame,
        len(results),
    )
    return results
