"""Codes applicatifs des systèmes de maisons astrologiques."""

from __future__ import annotations


class HouseSystemCode:
    """Codes stables alignés avec le référentiel SQL `astral_house_systems`."""

    PLACIDUS = "placidus"
    WHOLE_SIGN = "whole_sign"
    EQUAL = "equal"
    PORPHYRY = "porphyry"

    ALL = frozenset({PLACIDUS, WHOLE_SIGN, EQUAL, PORPHYRY})
