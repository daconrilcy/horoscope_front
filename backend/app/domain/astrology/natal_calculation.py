from __future__ import annotations

from collections.abc import Callable
from math import isfinite

from pydantic import BaseModel

from app.domain.astrology.angle_utils import contains_angle
from app.domain.astrology.calculators import (
    calculate_houses,
    calculate_major_aspects,
    calculate_planet_positions,
)
from app.domain.astrology.calculators.houses import HOUSE_SYSTEM_CODE, assign_house_number
from app.domain.astrology.natal_preparation import BirthInput, BirthPreparedData, prepare_birth_data


class PlanetPosition(BaseModel):
    planet_code: str
    longitude: float
    sign_code: str
    house_number: int


class HouseResult(BaseModel):
    number: int
    cusp_longitude: float


class AspectResult(BaseModel):
    aspect_code: str
    planet_a: str
    planet_b: str
    angle: float
    orb: float


class NatalResult(BaseModel):
    reference_version: str
    ruleset_version: str
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


def build_natal_result(
    birth_input: BirthInput,
    reference_data: dict[str, object],
    ruleset_version: str,
    timeout_check: Callable[[], None] | None = None,
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

    prepared = prepare_birth_data(birth_input)
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

    positions_raw = calculate_planet_positions(prepared.julian_day, planet_codes, sign_codes)
    if timeout_check is not None:
        timeout_check()
    houses_raw = calculate_houses(prepared.julian_day, house_numbers)
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
                    "house_system": HOUSE_SYSTEM_CODE,
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
                    "house_system": HOUSE_SYSTEM_CODE,
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
                    "house_system": HOUSE_SYSTEM_CODE,
                },
            )

    aspect_definitions: list[tuple[str, float]] = []
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
        aspect_definitions.append((code_value.strip(), angle_value))
    if not aspect_definitions:
        _raise_invalid_reference(version, "aspects", "missing_code_or_angle")
    aspect_definitions.sort(key=lambda item: (item[1], item[0]))
    aspects_raw = calculate_major_aspects(positions_raw, aspect_definitions)
    if timeout_check is not None:
        timeout_check()

    positions = [PlanetPosition.model_validate(item) for item in positions_raw]
    houses = [HouseResult.model_validate(item) for item in houses_raw]
    aspects = [AspectResult.model_validate(item) for item in aspects_raw]

    return NatalResult(
        reference_version=version,
        ruleset_version=ruleset_version,
        prepared_input=prepared,
        planet_positions=positions,
        houses=houses,
        aspects=aspects,
    )
