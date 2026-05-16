"""Calcul des signes zodiacaux contenus par un intervalle de maison."""

from __future__ import annotations

from collections.abc import Sequence

from app.domain.astrology.zodiac import normalize_360, ordered_sign_codes, sign_from_longitude


def resolve_contained_signs(
    start_longitude: float,
    end_longitude: float,
    sign_codes: Sequence[str] | None = None,
) -> list[str]:
    """Liste les signes touchés par une maison, wrap 360 degrés inclus."""
    ordered_codes = ordered_sign_codes(sign_codes)
    start = normalize_360(start_longitude)
    end = normalize_360(end_longitude)
    start_sign = sign_from_longitude(start, ordered_codes)
    end_sign = sign_from_longitude(end, ordered_codes)

    if start_sign == end_sign and start != end:
        return [start_sign]

    signs: list[str] = []
    index = ordered_codes.index(start_sign)
    end_index = ordered_codes.index(end_sign)

    while True:
        signs.append(ordered_codes[index])
        if index == end_index:
            break
        index = (index + 1) % len(ordered_codes)

    return signs
