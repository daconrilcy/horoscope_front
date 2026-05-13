"""Utilitaires zodiacaux partagés par les calculs astrologiques."""

from __future__ import annotations

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


def normalize_360(value: float) -> float:
    """Normalise une longitude dans l'intervalle zodiacal [0, 360)."""
    normalized = value % 360.0
    return normalized if normalized >= 0 else normalized + 360.0


def sign_from_longitude(longitude: float) -> str:
    """Retourne le signe zodiacal correspondant à une longitude."""
    normalized = normalize_360(longitude)
    index = int(normalized // 30.0) % len(ZODIAC_SIGNS)
    return ZODIAC_SIGNS[index]
