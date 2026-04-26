"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

import logging
from typing import Any

from fastapi.responses import JSONResponse

from app.api.v1.errors import api_error_response

logger = logging.getLogger(__name__)
_NATAL_TECHNICAL_ERROR_CODES = frozenset(
    {
        "ephemeris_calc_failed",
        "houses_calc_failed",
    }
)


def _error_response(
    *,
    status_code: int,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any],
) -> JSONResponse:
    return api_error_response(
        status_code=status_code,
        request_id=request_id,
        code=code,
        message=message,
        details=details,
    )


def _status_code_for_natal_error(error_code: str) -> int:
    if error_code == "reference_version_not_found":
        return 404
    if error_code in _NATAL_TECHNICAL_ERROR_CODES:
        return 503
    return 422


def _build_engine_diff(
    *,
    simplified_result: dict[str, Any],
    swisseph_result: dict[str, Any],
) -> dict[str, Any]:
    simplified_planets = {
        str(item["planet_code"]): float(item["longitude"])
        for item in simplified_result.get("planet_positions", [])
        if isinstance(item, dict)
        and isinstance(item.get("planet_code"), str)
        and item.get("longitude") is not None
    }
    swisseph_planets = {
        str(item["planet_code"]): float(item["longitude"])
        for item in swisseph_result.get("planet_positions", [])
        if isinstance(item, dict)
        and isinstance(item.get("planet_code"), str)
        and item.get("longitude") is not None
    }

    simplified_houses = {
        int(item["number"]): float(item["cusp_longitude"])
        for item in simplified_result.get("houses", [])
        if isinstance(item, dict)
        and item.get("number") is not None
        and item.get("cusp_longitude") is not None
    }
    swisseph_houses = {
        int(item["number"]): float(item["cusp_longitude"])
        for item in swisseph_result.get("houses", [])
        if isinstance(item, dict)
        and item.get("number") is not None
        and item.get("cusp_longitude") is not None
    }

    planet_diffs: list[dict[str, Any]] = []
    for planet_code in sorted(set(simplified_planets).intersection(swisseph_planets)):
        simplified_longitude = simplified_planets[planet_code]
        swisseph_longitude = swisseph_planets[planet_code]
        planet_diffs.append(
            {
                "planet_code": planet_code,
                "simplified_longitude": simplified_longitude,
                "swisseph_longitude": swisseph_longitude,
                "delta_degrees": round(simplified_longitude - swisseph_longitude, 6),
            }
        )

    house_diffs: list[dict[str, Any]] = []
    for house_number in sorted(set(simplified_houses).intersection(swisseph_houses)):
        simplified_cusp = simplified_houses[house_number]
        swisseph_cusp = swisseph_houses[house_number]
        house_diffs.append(
            {
                "house_number": house_number,
                "simplified_cusp_longitude": simplified_cusp,
                "swisseph_cusp_longitude": swisseph_cusp,
                "delta_degrees": round(simplified_cusp - swisseph_cusp, 6),
            }
        )

    max_planet_delta = max(
        (abs(float(item["delta_degrees"])) for item in planet_diffs), default=0.0
    )
    max_house_delta = max((abs(float(item["delta_degrees"])) for item in house_diffs), default=0.0)

    return {
        "planet_positions": planet_diffs,
        "houses": house_diffs,
        "summary": {
            "planet_positions_count": len(planet_diffs),
            "houses_count": len(house_diffs),
            "max_planet_delta_degrees": round(max_planet_delta, 6),
            "max_house_delta_degrees": round(max_house_delta, 6),
        },
    }
