"""Calcul des signes zodiacaux contenus par un intervalle de maison."""

from __future__ import annotations

from app.domain.astrology.zodiac import ZODIAC_SIGNS, normalize_360, sign_from_longitude


def resolve_contained_signs(start_longitude: float, end_longitude: float) -> list[str]:
    """Liste les signes touchés par une maison, wrap 360 degrés inclus."""
    start = normalize_360(start_longitude)
    end = normalize_360(end_longitude)
    start_sign = sign_from_longitude(start)
    end_sign = sign_from_longitude(end)

    if start_sign == end_sign and start != end:
        return [start_sign]

    signs: list[str] = []
    index = ZODIAC_SIGNS.index(start_sign)
    end_index = ZODIAC_SIGNS.index(end_sign)

    while True:
        signs.append(ZODIAC_SIGNS[index])
        if index == end_index:
            break
        index = (index + 1) % len(ZODIAC_SIGNS)

    return signs
