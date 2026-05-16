"""Calcule des positions planétaires simplifiées pour le moteur natal local."""

import math

from app.domain.astrology.zodiac import normalize_360, sign_from_longitude


def _sun_longitude(julian_day: float) -> float:
    """
    Approximation tropicale de la longitude solaire apparente.
    Suffisante pour cohérence signe <-> longitude dans ce moteur.
    """
    n = julian_day - 2451545.0
    mean_longitude = normalize_360(280.460 + 0.9856474 * n)
    mean_anomaly = math.radians(normalize_360(357.528 + 0.9856003 * n))
    return normalize_360(
        mean_longitude + 1.915 * math.sin(mean_anomaly) + 0.020 * math.sin(2.0 * mean_anomaly)
    )


def _planet_longitude(julian_day: float, code: str, index: int) -> float:
    n = julian_day - 2451545.0
    if code == "sun":
        return _sun_longitude(julian_day)
    if code == "moon":
        # Mean lunar longitude (simplified model).
        return normalize_360(218.316 + 13.176396 * n)
    if code == "mercury":
        # Mean heliocentric longitude proxy for deterministic outputs.
        return normalize_360(252.25084 + 4.0923388 * n)
    return normalize_360(julian_day * 0.985647 + index * 37.5)


def calculate_planet_positions(
    julian_day: float,
    planet_codes: list[str],
    sign_codes: list[str],
) -> list[dict[str, object]]:
    positions: list[dict[str, object]] = []
    for index, code in enumerate(planet_codes):
        longitude = round(_planet_longitude(julian_day, code, index), 6)
        sign_code = sign_from_longitude(longitude, sign_codes)
        positions.append(
            {
                "planet_code": code,
                "longitude": longitude,
                "sign_code": sign_code,
            }
        )

    return positions
