"""Calcul des signes zodiacaux contenus par un intervalle de maison."""

from __future__ import annotations

from app.domain.astrology.zodiac import normalize_360, ordered_sign_codes, sign_from_longitude


def resolve_contained_signs(start_longitude: float, end_longitude: float) -> list[str]:
    """Liste les signes touchés par une maison, wrap 360 degrés inclus."""
    start = normalize_360(start_longitude)
    end = normalize_360(end_longitude)
    start_sign = sign_from_longitude(start)
    end_sign = sign_from_longitude(end)

    if start_sign == end_sign and start != end:
        return [start_sign]

    sign_codes = ordered_sign_codes()
    signs: list[str] = []
    index = sign_codes.index(start_sign)
    end_index = sign_codes.index(end_sign)

    while True:
        signs.append(sign_codes[index])
        if index == end_index:
            break
        index = (index + 1) % len(sign_codes)

    return signs
