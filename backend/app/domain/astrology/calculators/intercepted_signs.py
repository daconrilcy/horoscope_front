"""Détection des signes interceptés dans une maison natale."""

from __future__ import annotations


def resolve_intercepted_signs(
    contained_signs: list[str],
    cusp_sign: str,
    next_cusp_sign: str,
) -> list[str]:
    """Retourne les signes contenus sans apparaître sur les cuspides voisines."""
    excluded = {cusp_sign, next_cusp_sign}
    return [sign for sign in contained_signs if sign not in excluded]
