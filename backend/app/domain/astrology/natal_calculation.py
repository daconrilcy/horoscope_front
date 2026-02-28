from __future__ import annotations

import math
from collections.abc import Callable
from math import isfinite

from pydantic import BaseModel

from app.core.config import AspectSchoolType, FrameType, HouseSystemType, ZodiacType
from app.core.constants import MAJOR_ASPECT_CODES, MAX_ORB_DEG, MIN_ORB_DEG
from app.domain.astrology.angle_utils import contains_angle
from app.domain.astrology.calculators import (
    calculate_houses,
    calculate_major_aspects,
    calculate_planet_positions,
)
from app.domain.astrology.calculators.houses import HOUSE_SYSTEM_CODE, assign_house_number
from app.domain.astrology.natal_preparation import BirthInput, BirthPreparedData, prepare_birth_data
from app.infra.observability.metrics import increment_counter


class PlanetPosition(BaseModel):
    planet_code: str
    longitude: float
    sign_code: str
    house_number: int
    speed_longitude: float | None = None
    is_retrograde: bool | None = None


class HouseResult(BaseModel):
    number: int
    cusp_longitude: float


class AspectResult(BaseModel):
    aspect_code: str
    planet_a: str
    planet_b: str
    angle: float
    orb: float                    # actual angular deviation (backward compat)
    orb_used: float               # actual angular deviation, story 24-2 (same as orb)
    orb_max: float                # resolved max threshold by priority chain, story 24-2


class NatalResult(BaseModel):
    reference_version: str
    ruleset_version: str
    house_system: HouseSystemType
    engine: str = "simplified"
    zodiac: ZodiacType = ZodiacType.TROPICAL
    frame: FrameType = FrameType.GEOCENTRIC
    ayanamsa: str | None = None
    altitude_m: float | None = None
    ephemeris_path_version: str | None = None
    ephemeris_path_hash: str | None = None
    # time_scale: "TT" when Terrestrial Time fields are present, "UT" otherwise (story 22.2).
    time_scale: str = "UT"
    # aspect school and versioned rules identifier (story 24-1).
    aspect_school: AspectSchoolType = AspectSchoolType.MODERN
    aspect_rules_version: str = "1.0.0"
    prepared_input: BirthPreparedData
    planet_positions: list[PlanetPosition]
    houses: list[HouseResult]
    aspects: list[AspectResult]


class NatalCalculationError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


ZODIAC_SIGNS = (
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
)


def _normalize_360(value: float) -> float:
    normalized = value % 360.0
    return normalized if normalized >= 0 else normalized + 360.0


def _sign_from_longitude(longitude: float) -> str:
    normalized = _normalize_360(longitude)
    index = int(normalized // 30.0) % 12
    return ZODIAC_SIGNS[index]


def _raise_invalid_reference(version: str, field: str, reason: str) -> None:
    raise NatalCalculationError(
        code="invalid_reference_data",
        message=f"{field} reference data is invalid",
        details={"reference_version": version, "field": field, "reason": reason},
    )


def _validate_house_cusps(version: str, houses_raw: list[dict[str, object]]) -> None:
    if len(houses_raw) != 12:
        _raise_invalid_reference(version, "houses", "expected_12_cusps")

    longitudes: list[float] = []
    for house in houses_raw:
        value = house.get("cusp_longitude")
        if value is None:
            _raise_invalid_reference(version, "houses", "missing_cusp_longitude")
        try:
            longitude = float(value)
        except (TypeError, ValueError):
            _raise_invalid_reference(version, "houses", "invalid_cusp_longitude")
        if not isfinite(longitude):
            _raise_invalid_reference(version, "houses", "non_finite_cusp_longitude")
        normalized = _normalize_360(longitude)
        if normalized != longitude:
            _raise_invalid_reference(version, "houses", "non_normalized_cusp_longitude")
        longitudes.append(normalized)

    if len(set(longitudes)) != len(longitudes):
        _raise_invalid_reference(version, "houses", "duplicate_cusp_longitude")


def _build_swisseph_positions(
    jdut: float,
    planet_codes: list[str],
    zodiac: ZodiacType = ZodiacType.TROPICAL,
    ayanamsa: str | None = None,
    frame: FrameType = FrameType.GEOCENTRIC,
    lat: float | None = None,
    lon: float | None = None,
    altitude_m: float | None = None,
) -> list[dict[str, object]]:
    """Build positions_raw list from SwissEph ephemeris provider."""
    from app.domain.astrology.ephemeris_provider import calculate_planets

    ephem_result = calculate_planets(
        jdut,
        lat=lat,
        lon=lon,
        zodiac=zodiac,
        ayanamsa=ayanamsa,
        frame=frame,
        altitude_m=altitude_m,
    )
    planet_data_by_id = {pd.planet_id: pd for pd in ephem_result.planets}

    positions_raw: list[dict[str, object]] = []
    for code in planet_codes:
        pd = planet_data_by_id.get(code)
        if pd is None:
            continue
        longitude = pd.longitude  # already normalized [0, 360) by ephemeris_provider
        positions_raw.append(
            {
                "planet_code": code,
                "longitude": longitude,
                "sign_code": _sign_from_longitude(longitude),
                "speed_longitude": pd.speed_longitude,
                "is_retrograde": pd.is_retrograde,
            }
        )
    return positions_raw


def _build_swisseph_houses(
    jdut: float,
    lat: float,
    lon: float,
    house_numbers: list[int],
    house_system: HouseSystemType = HouseSystemType.PLACIDUS,
    frame: FrameType = FrameType.GEOCENTRIC,
    altitude_m: float | None = None,
) -> tuple[list[dict[str, object]], str]:
    """Build houses_raw list from SwissEph houses provider.

    Returns:
        Tuple of (houses_raw, house_system_name).
    """
    from app.domain.astrology.houses_provider import calculate_houses as calc_sw_houses

    house_data = calc_sw_houses(
        jdut,
        lat,
        lon,
        house_system=house_system,
        frame=frame,
        altitude_m=altitude_m,
    )
    houses_raw: list[dict[str, object]] = [
        {"number": number, "cusp_longitude": house_data.cusps[number - 1]}
        for number in house_numbers
        if 1 <= number <= 12
    ]
    return houses_raw, house_data.house_system


def build_natal_result(
    birth_input: BirthInput,
    reference_data: dict[str, object],
    ruleset_version: str,
    timeout_check: Callable[[], None] | None = None,
    engine: str = "simplified",
    birth_lat: float | None = None,
    birth_lon: float | None = None,
    zodiac: ZodiacType = ZodiacType.TROPICAL,
    ayanamsa: str | None = None,
    frame: FrameType = FrameType.GEOCENTRIC,
    house_system: HouseSystemType = HouseSystemType.PLACIDUS,
    altitude_m: float | None = None,
    ephemeris_path_version: str | None = None,
    ephemeris_path_hash: str | None = None,
    tt_enabled: bool = False,
    aspect_school: str = "modern",
    aspect_rules_version: str = "1.0.0",
) -> NatalResult:
    if timeout_check is not None:
        timeout_check()

    version = reference_data.get("version")
    if not isinstance(version, str) or not version:
        raise NatalCalculationError(
            code="reference_version_not_found",
            message="reference version not found",
            details={"version": "unknown"},
        )

    planets_data = reference_data.get("planets")
    signs_data = reference_data.get("signs")
    houses_data = reference_data.get("houses")
    aspects_data = reference_data.get("aspects")

    if not isinstance(planets_data, list) or not planets_data:
        _raise_invalid_reference(version, "planets", "missing_or_empty")
    if not isinstance(signs_data, list) or not signs_data:
        _raise_invalid_reference(version, "signs", "missing_or_empty")
    if not isinstance(houses_data, list) or not houses_data:
        _raise_invalid_reference(version, "houses", "missing_or_empty")
    if not isinstance(aspects_data, list) or not aspects_data:
        _raise_invalid_reference(version, "aspects", "missing_or_empty")

    prepared = prepare_birth_data(birth_input, tt_enabled=tt_enabled)
    if timeout_check is not None:
        timeout_check()
    planet_codes = [
        str(item["code"])
        for item in planets_data
        if isinstance(item, dict) and isinstance(item.get("code"), str)
    ]
    if not planet_codes:
        _raise_invalid_reference(version, "planets", "missing_code")

    sign_codes = [
        str(item["code"])
        for item in signs_data
        if isinstance(item, dict) and isinstance(item.get("code"), str)
    ]
    if not sign_codes:
        _raise_invalid_reference(version, "signs", "missing_code")

    house_numbers: list[int] = []
    for item in houses_data:
        if not isinstance(item, dict) or "number" not in item:
            _raise_invalid_reference(version, "houses", "missing_number")
        number_value = item["number"]
        if isinstance(number_value, bool):
            _raise_invalid_reference(version, "houses", "invalid_number")
        try:
            number = int(number_value)
        except (TypeError, ValueError):
            _raise_invalid_reference(version, "houses", "invalid_number")
        house_numbers.append(number)
    if not house_numbers:
        _raise_invalid_reference(version, "houses", "missing_number")

    # Engine-specific calculation
    if engine == "swisseph":
        if birth_lat is None or birth_lon is None:
            raise NatalCalculationError(
                code="missing_birth_coordinates",
                message="birth_lat and birth_lon are required for swisseph engine",
                details={"engine": engine},
            )
        positions_raw = _build_swisseph_positions(
            prepared.julian_day,
            planet_codes,
            zodiac=zodiac,
            ayanamsa=ayanamsa,
            frame=frame,
            lat=birth_lat,
            lon=birth_lon,
            altitude_m=altitude_m,
        )
        if timeout_check is not None:
            timeout_check()
        houses_raw, effective_house_system = _build_swisseph_houses(
            prepared.julian_day,
            birth_lat,
            birth_lon,
            house_numbers,
            house_system=house_system,
            frame=frame,
            altitude_m=altitude_m,
        )
    else:
        positions_raw = calculate_planet_positions(prepared.julian_day, planet_codes, sign_codes)
        if timeout_check is not None:
            timeout_check()
        houses_raw = calculate_houses(prepared.julian_day, house_numbers)
        effective_house_system = HOUSE_SYSTEM_CODE

    _validate_house_cusps(version, houses_raw)
    if timeout_check is not None:
        timeout_check()

    # Coherence invariant: house assignment must use the same cusp list we return.
    for position in positions_raw:
        longitude = float(position["longitude"])
        position["house_number"] = assign_house_number(longitude, houses_raw)
        expected_sign = _sign_from_longitude(longitude)
        if str(position.get("sign_code")) != expected_sign:
            raise NatalCalculationError(
                code="inconsistent_natal_result",
                message="planet sign does not match longitude",
                details={
                    "planet_code": str(position.get("planet_code", "")),
                    "longitude": str(longitude),
                    "expected_sign_code": expected_sign,
                    "actual_sign_code": str(position.get("sign_code", "")),
                    "reference_version": version,
                    "house_system": effective_house_system,
                },
            )
        house_number = int(position["house_number"])
        current_cusp = next(
            (
                float(house["cusp_longitude"])
                for house in houses_raw
                if int(house["number"]) == house_number
            ),
            None,
        )
        next_house_number = 1 if house_number == 12 else house_number + 1
        next_cusp = next(
            (
                float(house["cusp_longitude"])
                for house in houses_raw
                if int(house["number"]) == next_house_number
            ),
            None,
        )
        if current_cusp is None or next_cusp is None:
            raise NatalCalculationError(
                code="inconsistent_natal_result",
                message="house cusp interval is missing for assigned house",
                details={
                    "planet_code": str(position.get("planet_code", "")),
                    "house_number": str(house_number),
                    "reference_version": version,
                    "house_system": effective_house_system,
                },
            )
        if not contains_angle(longitude, current_cusp, next_cusp):
            raise NatalCalculationError(
                code="inconsistent_natal_result",
                message="planet house does not match cusp interval",
                details={
                    "planet_code": str(position.get("planet_code", "")),
                    "longitude": str(longitude),
                    "house_number": str(house_number),
                    "interval_start": str(current_cusp),
                    "interval_end": str(next_cusp),
                    "reference_version": version,
                    "house_system": effective_house_system,
                },
            )

    aspect_definitions: list[dict[str, object]] = []
    for item in aspects_data:
        if not isinstance(item, dict):
            _raise_invalid_reference(version, "aspects", "invalid_entry")
        if "code" not in item or "angle" not in item:
            _raise_invalid_reference(version, "aspects", "missing_code_or_angle")
        code_value = item["code"]
        if not isinstance(code_value, str) or not code_value.strip():
            _raise_invalid_reference(version, "aspects", "invalid_code")
        try:
            angle_value = float(item["angle"])
        except (TypeError, ValueError):
            _raise_invalid_reference(version, "aspects", "invalid_angle")

        # AC1 story 24-1: default_orb_deg is required and must be within strict bounds.
        if "default_orb_deg" not in item:
            _raise_invalid_reference(version, "aspects", "missing_default_orb_deg")
        try:
            default_orb_value = float(item["default_orb_deg"])
        except (TypeError, ValueError):
            _raise_invalid_reference(version, "aspects", "invalid_default_orb_deg")
        # Fix: Allow 0.0 for exact aspects (MIN_ORB_DEG is 0.0).
        orb_in_bounds = (
            isfinite(default_orb_value) and MIN_ORB_DEG <= default_orb_value <= MAX_ORB_DEG
        )
        if not orb_in_bounds:
            _raise_invalid_reference(version, "aspects", "invalid_default_orb_deg")

        aspect_definition: dict[str, object] = {
            "code": code_value.strip(),
            "angle": angle_value,
            "default_orb_deg": default_orb_value,
        }

        # story 24-1: support orb_luminaries_override_deg (new) and orb_luminaries (legacy).
        # Validate bounds when provided.
        if "orb_luminaries_override_deg" in item:
            orb_lum_raw = item.get("orb_luminaries_override_deg")
        else:
            orb_lum_raw = item.get("orb_luminaries")
        if orb_lum_raw is not None:
            try:
                orb_lum_value = float(orb_lum_raw)
            except (TypeError, ValueError):
                _raise_invalid_reference(version, "aspects", "invalid_orb_luminaries_override_deg")
            lum_in_bounds = isfinite(orb_lum_value) and MIN_ORB_DEG <= orb_lum_value <= MAX_ORB_DEG
            if not lum_in_bounds:
                _raise_invalid_reference(version, "aspects", "invalid_orb_luminaries_override_deg")
            aspect_definition["orb_luminaries"] = orb_lum_value

        # AC1 story 24-1: validate orb_pair_overrides values within bounds.
        # Prioritize 'orb_pair_overrides' then 'orb_pairs' then 'orb_overrides'.
        pair_overrides_raw = item.get("orb_pair_overrides")
        if pair_overrides_raw is None:
            pair_overrides_raw = item.get("orb_pairs") or item.get("orb_overrides")

        if pair_overrides_raw is not None:
            if not isinstance(pair_overrides_raw, dict):
                _raise_invalid_reference(version, "aspects", "invalid_orb_pair_overrides")
            for pair_val in pair_overrides_raw.values():
                try:
                    pair_orb = float(pair_val)
                except (TypeError, ValueError):
                    _raise_invalid_reference(version, "aspects", "invalid_orb_pair_override_value")
                pair_in_bounds = isfinite(pair_orb) and MIN_ORB_DEG <= pair_orb <= MAX_ORB_DEG
                if not pair_in_bounds:
                    _raise_invalid_reference(version, "aspects", "invalid_orb_pair_override_value")
            aspect_definition["orb_pair_overrides"] = pair_overrides_raw

        aspect_definitions.append(aspect_definition)
    if not aspect_definitions:
        _raise_invalid_reference(version, "aspects", "missing_code_or_angle")
    aspect_definitions.sort(key=lambda item: (float(item["angle"]), str(item["code"])))

    # story 24-2 Task 3: limit to major aspects only
    major_aspect_definitions = [
        d for d in aspect_definitions
        if str(d.get("code", "")).strip().lower() in MAJOR_ASPECT_CODES
    ]

    aspects_raw = calculate_major_aspects(positions_raw, major_aspect_definitions)
    if timeout_check is not None:
        timeout_check()

    # story 24-2 Observability: track aspects calculated and rejected by orb
    increment_counter(f"aspects_calculated_total_{aspect_school}", float(len(aspects_raw)))
    _total_checks = math.comb(len(positions_raw), 2) * len(major_aspect_definitions)
    _rejected = _total_checks - len(aspects_raw)
    if _rejected > 0:
        increment_counter("aspects_rejected_orb_total", float(_rejected))

    positions = [PlanetPosition.model_validate(item) for item in positions_raw]
    houses = [HouseResult.model_validate(item) for item in houses_raw]
    aspects = [AspectResult.model_validate(item) for item in aspects_raw]

    return NatalResult(
        reference_version=version,
        ruleset_version=ruleset_version,
        house_system=effective_house_system,
        engine=engine,
        zodiac=zodiac,
        frame=frame,
        ayanamsa=ayanamsa,
        altitude_m=altitude_m,
        ephemeris_path_version=ephemeris_path_version,
        ephemeris_path_hash=ephemeris_path_hash,
        time_scale=prepared.time_scale,
        aspect_school=aspect_school,
        aspect_rules_version=aspect_rules_version,
        prepared_input=prepared,
        planet_positions=positions,
        houses=houses,
        aspects=aspects,
    )
