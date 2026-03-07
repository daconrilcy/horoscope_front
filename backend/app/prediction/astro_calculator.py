from __future__ import annotations

import logging
import math

import swisseph as swe

from app.core.ephemeris import SWISSEPH_LOCK
from app.prediction.exceptions import PredictionEngineError
from app.prediction.schemas import PlanetState, StepAstroState

logger = logging.getLogger(__name__)

HOUSE_SYSTEM_PLACIDUS = "placidus"
HOUSE_SYSTEM_PORPHYRE = "porphyre"
_EXPECTED_CUSP_COUNT = 12
_FLG_SWIEPH_SPEED = swe.FLG_SWIEPH | swe.FLG_SPEED

V1_PLANETS: dict[str, int] = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}


class AstroCalculator:
    """Service to calculate astrological states for prediction engine steps."""

    def __init__(
        self,
        natal_cusps: list[float],
        latitude: float,
        longitude: float,
    ) -> None:
        """Initialize the calculator.

        Args:
            natal_cusps: List of 12 natal house cusps (1-based index 0..11).
            latitude: Latitude of the location.
            longitude: Longitude of the location.
        """
        if len(natal_cusps) != _EXPECTED_CUSP_COUNT:
            raise PredictionEngineError(
                f"Expected {_EXPECTED_CUSP_COUNT} natal cusps, got {len(natal_cusps)}"
            )
        if not all(math.isfinite(cusp) for cusp in natal_cusps):
            raise PredictionEngineError("Natal cusps must be finite numbers")

        self.natal_cusps = [c % 360.0 for c in natal_cusps]
        self.latitude = latitude
        self.longitude = longitude

    def compute_step(self, ut_jd: float, local_time: datetime) -> StepAstroState:
        """Compute the full astrological state for a given Julian Day UT.

        Args:
            ut_jd: Julian Day UT.
            local_time: Local time corresponding to ut_jd.

        Returns:
            StepAstroState containing all calculated values.

        Raises:
            PredictionEngineError: If calculation fails.
        """
        try:
            with SWISSEPH_LOCK:
                cusps, asc, mc, effective_system = self._compute_houses(ut_jd)

                planets_state: dict[str, PlanetState] = {}
                for name in V1_PLANETS:
                    planets_state[name] = self._compute_planet(ut_jd, name)

                return StepAstroState(
                    ut_jd=ut_jd,
                    local_time=local_time,
                    ascendant_deg=asc,
                    mc_deg=mc,
                    house_cusps=list(cusps),
                    house_system_effective=effective_system,
                    planets=planets_state,
                )

        except Exception as exc:
            if isinstance(exc, PredictionEngineError):
                raise
            logger.error("astro_calculation_failed ut_jd=%.4f error=%s", ut_jd, str(exc))
            raise PredictionEngineError(f"Astrological calculation failed: {str(exc)}") from exc

    def _compute_planet(self, ut_jd: float, name: str) -> PlanetState:
        """Compute state for a specific planet."""
        if name not in V1_PLANETS:
            raise PredictionEngineError(f"Body '{name}' is not in V1_PLANETS scope (AC7)")

        swe_id = V1_PLANETS[name]
        xx, retflag = swe.calc_ut(ut_jd, swe_id, _FLG_SWIEPH_SPEED)
        if retflag < 0:
            raise PredictionEngineError(f"calc_ut failed for planet {name}")

        lon = xx[0] % 360.0
        speed_lon = xx[3]
        is_retrograde = speed_lon < 0.0
        sign_code = int(math.floor(lon / 30.0))
        natal_house = self._natal_house_for_longitude(lon)

        return PlanetState(
            code=name,
            longitude=lon,
            speed_lon=speed_lon,
            is_retrograde=is_retrograde,
            sign_code=sign_code,
            natal_house_transited=natal_house,
        )

    def _compute_houses(self, ut_jd: float) -> tuple[list[float], float, float, str]:
        """Compute houses with Placidus (P) and fallback to Porphyre (O) if needed."""
        try:
            return self._run_house_calculation(ut_jd, b"P", HOUSE_SYSTEM_PLACIDUS)
        except PredictionEngineError as exc:
            logger.warning(
                "placidus_failed_trying_porphyre lat=%.2f lon=%.2f error=%s",
                self.latitude,
                self.longitude,
                str(exc),
            )

        try:
            return self._run_house_calculation(ut_jd, b"O", HOUSE_SYSTEM_PORPHYRE)
        except PredictionEngineError as exc:
            msg = f"House calculation failed even with Porphyre: {str(exc)}"
            raise PredictionEngineError(msg) from exc

    def _run_house_calculation(
        self,
        ut_jd: float,
        house_code: bytes,
        effective_system: str,
    ) -> tuple[list[float], float, float, str]:
        try:
            cusps_raw, ascmc_raw = swe.houses(ut_jd, self.latitude, self.longitude, house_code)
        except Exception as exc:
            raise PredictionEngineError(
                f"houses failed for system {effective_system}: {type(exc).__name__}"
            ) from exc

        cusps = self._extract_house_cusps(cusps_raw)
        asc, mc = self._extract_angles(ascmc_raw)
        self._validate_house_cusps(cusps)
        return cusps, asc, mc, effective_system

    def _extract_house_cusps(self, cusps_raw: tuple[object, ...]) -> list[float]:
        if len(cusps_raw) >= 13:
            source = cusps_raw[1:13]
        elif len(cusps_raw) == _EXPECTED_CUSP_COUNT:
            source = cusps_raw
        else:
            raise PredictionEngineError(
                f"houses returned invalid cusp array length: {len(cusps_raw)}"
            )

        cusps = [float(value) % 360.0 for value in source]
        if not all(math.isfinite(cusp) for cusp in cusps):
            raise PredictionEngineError("houses returned non-finite cusp values")
        return cusps

    def _extract_angles(self, ascmc_raw: tuple[object, ...]) -> tuple[float, float]:
        if len(ascmc_raw) < 2:
            raise PredictionEngineError("houses returned an incomplete ASC/MC array")

        asc = float(ascmc_raw[0]) % 360.0
        mc = float(ascmc_raw[1]) % 360.0
        if not math.isfinite(asc) or not math.isfinite(mc):
            raise PredictionEngineError("houses returned non-finite ASC/MC values")
        return asc, mc

    def _validate_house_cusps(self, cusps: list[float]) -> None:
        if len(cusps) != _EXPECTED_CUSP_COUNT:
            raise PredictionEngineError(
                f"Expected {_EXPECTED_CUSP_COUNT} house cusps, got {len(cusps)}"
            )

        arc_sum = 0.0
        for index, cusp_start in enumerate(cusps):
            cusp_end = cusps[(index + 1) % _EXPECTED_CUSP_COUNT]
            arc = (cusp_end - cusp_start) % 360.0
            if arc <= 0.0:
                raise PredictionEngineError("houses returned overlapping or duplicate cusps")
            arc_sum += arc

        if not math.isclose(arc_sum, 360.0, rel_tol=0.0, abs_tol=1e-6):
            raise PredictionEngineError(
                f"houses returned inconsistent cusp coverage: total_arc={arc_sum:.6f}"
            )

    def _natal_house_for_longitude(self, lon: float) -> int:
        """Determine which natal house a given longitude falls into."""
        lon = lon % 360.0
        # Iterate through houses
        for i in range(12):
            cusp_start = self.natal_cusps[i]
            cusp_end = self.natal_cusps[(i + 1) % 12]

            if cusp_start < cusp_end:
                # Normal case: house doesn't cross 0°
                if cusp_start <= lon < cusp_end:
                    return i + 1
            else:
                # Wrap-around case: house crosses 0°
                if lon >= cusp_start or lon < cusp_end:
                    return i + 1

        # Fallback (should not happen with 12 cusps covering 360°)
        return 1
