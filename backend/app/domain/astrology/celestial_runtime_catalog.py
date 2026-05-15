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


def is_major_aspect_code(aspect: object) -> bool:
    """Lit le statut majeur depuis un contrat d'aspect déjà validé."""
    is_major = getattr(aspect, "is_major", None)
    if isinstance(is_major, bool):
        return is_major
    raise TypeError("is_major_aspect_code requires a typed aspect contract")
