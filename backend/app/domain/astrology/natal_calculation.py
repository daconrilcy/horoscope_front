from __future__ import annotations

from collections.abc import Callable

from pydantic import BaseModel

from app.domain.astrology.calculators import (
    calculate_houses,
    calculate_major_aspects,
    calculate_planet_positions,
)
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


def _raise_invalid_reference(version: str, field: str, reason: str) -> None:
    raise NatalCalculationError(
        code="invalid_reference_data",
        message=f"{field} reference data is invalid",
        details={"reference_version": version, "field": field, "reason": reason},
    )


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
    planet_codes = sorted(
        str(item["code"])
        for item in planets_data
        if isinstance(item, dict) and isinstance(item.get("code"), str)
    )
    if not planet_codes:
        _raise_invalid_reference(version, "planets", "missing_code")

    sign_codes = sorted(
        str(item["code"])
        for item in signs_data
        if isinstance(item, dict) and isinstance(item.get("code"), str)
    )
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
    if timeout_check is not None:
        timeout_check()

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
