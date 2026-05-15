"""Regroupe les petites taxonomies runtime non persistantes du domaine astrology."""

from __future__ import annotations

LIGHT_BODY_CODES = frozenset({"sun", "moon"})
OUTER_PLANET_CODES = frozenset({"uranus", "neptune", "pluto"})
ANGLE_POINT_CODES = frozenset({"asc", "dsc", "mc", "ic"})
ANGULAR_HOUSE_NUMBERS = frozenset({1, 4, 7, 10})
SUCCEDENT_HOUSE_NUMBERS = frozenset({2, 5, 8, 11})

BODY_CLASS_BY_CODE = {
    "sun": "luminary",
    "moon": "luminary",
    "mercury": "personal_planet",
    "venus": "personal_planet",
    "mars": "personal_planet",
    "jupiter": "social_planet",
    "saturn": "social_planet",
    "uranus": "transpersonal_planet",
    "neptune": "transpersonal_planet",
    "pluto": "transpersonal_planet",
}


def is_major_aspect_code(aspect_code: str) -> bool:
    """Indique si un code d'aspect appartient a la famille majeure canonique."""
    return aspect_code.strip().lower() in {
        "conjunction",
        "opposition",
        "trine",
        "square",
        "sextile",
    }
