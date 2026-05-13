"""Constantes applicatives pour les systèmes de maisons astrologiques."""

from __future__ import annotations


class HouseSystemCode:
    """Codes stables alignés avec le référentiel SQL `astral_house_systems`."""

    PLACIDUS = "placidus"
    WHOLE_SIGN = "whole_sign"
    EQUAL = "equal"
    PORPHYRY = "porphyry"

    ALL = frozenset({PLACIDUS, WHOLE_SIGN, EQUAL, PORPHYRY})


HOUSE_SYSTEM_REFERENCE_ROWS = {
    HouseSystemCode.PLACIDUS: {
        "name": "Placidus",
        "description": (
            "Quadrant house system widely used in modern Western astrology. Houses are "
            "calculated from time-based divisions of the diurnal arc."
        ),
        "astronomical_family": "quadrant",
        "supports_polar_regions": False,
        "is_quadrant_based": True,
        "requires_precise_birth_time": True,
        "sort_order": 10,
    },
    HouseSystemCode.WHOLE_SIGN: {
        "name": "Whole Sign",
        "description": (
            "Ancient house system where each house corresponds to one full zodiac sign, "
            "starting from the Ascendant sign."
        ),
        "astronomical_family": "sign_based",
        "supports_polar_regions": True,
        "is_quadrant_based": False,
        "requires_precise_birth_time": False,
        "sort_order": 20,
    },
    HouseSystemCode.EQUAL: {
        "name": "Equal House",
        "description": (
            "House system where all houses are exactly 30 degrees, starting from the "
            "Ascendant degree."
        ),
        "astronomical_family": "ascendant_based",
        "supports_polar_regions": True,
        "is_quadrant_based": False,
        "requires_precise_birth_time": True,
        "sort_order": 30,
    },
    HouseSystemCode.PORPHYRY: {
        "name": "Porphyry",
        "description": (
            "Quadrant house system dividing each quadrant between Ascendant, Midheaven, "
            "Descendant and Imum Coeli into three equal parts."
        ),
        "astronomical_family": "quadrant",
        "supports_polar_regions": True,
        "is_quadrant_based": True,
        "requires_precise_birth_time": True,
        "sort_order": 40,
    },
}
