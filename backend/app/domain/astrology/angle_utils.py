"""Expose les helpers d'intervalles angulaires astrologiques."""

from app.domain.astrology.zodiac import normalize_360


def contains_angle(longitude: float, start: float, end: float) -> bool:
    """Teste un intervalle semi-ouvert avec support du passage 360 vers 0."""
    longitude = normalize_360(longitude)
    start = normalize_360(start)
    end = normalize_360(end)
    if start <= end:
        return start <= longitude < end
    return longitude >= start or longitude < end
