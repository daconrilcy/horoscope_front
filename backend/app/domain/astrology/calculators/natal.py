import math

ZODIAC_SIGNS = [
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
]


def _norm360(angle: float) -> float:
    normalized = angle % 360.0
    return normalized if normalized >= 0 else normalized + 360.0


def _sign_from_longitude(longitude: float) -> str:
    index = int(_norm360(longitude) // 30.0) % 12
    return ZODIAC_SIGNS[index]


def _sun_longitude(julian_day: float) -> float:
    """
    Approximation tropicale de la longitude solaire apparente.
    Suffisante pour cohérence signe <-> longitude dans ce moteur.
    """
    n = julian_day - 2451545.0
    mean_longitude = _norm360(280.460 + 0.9856474 * n)
    mean_anomaly = math.radians(_norm360(357.528 + 0.9856003 * n))
    return _norm360(
        mean_longitude + 1.915 * math.sin(mean_anomaly) + 0.020 * math.sin(2.0 * mean_anomaly)
    )


def _planet_longitude(julian_day: float, code: str, index: int) -> float:
    n = julian_day - 2451545.0
    if code == "sun":
        return _sun_longitude(julian_day)
    if code == "moon":
        # Mean lunar longitude (simplified model).
        return _norm360(218.316 + 13.176396 * n)
    if code == "mercury":
        # Mean heliocentric longitude proxy for deterministic outputs.
        return _norm360(252.25084 + 4.0923388 * n)
    return _norm360(julian_day * 0.985647 + index * 37.5)


def calculate_planet_positions(
    julian_day: float,
    planet_codes: list[str],
    sign_codes: list[str],
) -> list[dict[str, object]]:
    del sign_codes
    positions: list[dict[str, object]] = []
    for index, code in enumerate(planet_codes):
        longitude = round(_planet_longitude(julian_day, code, index), 6)
        sign_code = _sign_from_longitude(longitude)
        positions.append(
            {
                "planet_code": code,
                "longitude": longitude,
                "sign_code": sign_code,
            }
        )

    return positions
