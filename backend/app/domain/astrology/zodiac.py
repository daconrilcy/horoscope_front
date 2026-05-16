"""Utilitaires zodiacaux partagés par les calculs astrologiques."""

from __future__ import annotations

import json
from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path


def normalize_360(value: float) -> float:
    """Normalise une longitude dans l'intervalle zodiacal [0, 360)."""
    normalized = value % 360.0
    return normalized if normalized >= 0 else normalized + 360.0


def sign_from_longitude(longitude: float, sign_codes: Sequence[str] | None = None) -> str:
    """Retourne le signe zodiacal correspondant à une longitude."""
    ordered_codes = ordered_sign_codes(sign_codes)
    normalized = normalize_360(longitude)
    index = int(normalized // 30.0) % len(ordered_codes)
    return ordered_codes[index]


def ordered_sign_codes(sign_codes: Sequence[str] | None = None) -> tuple[str, ...]:
    """Retourne l'ordre zodiacal canonique utilise par les calculs geometriques."""
    if sign_codes is None:
        sign_codes = _load_seeded_sign_codes()
    ordered_codes = tuple(str(code).strip().lower() for code in sign_codes if str(code).strip())
    if len(ordered_codes) != 12 or len(set(ordered_codes)) != 12:
        raise ValueError("zodiac sign catalog must contain 12 unique codes")
    return ordered_codes


@lru_cache(maxsize=1)
def _load_seeded_sign_codes() -> tuple[str, ...]:
    """Charge l'ordre canonique depuis le JSON qui alimente la table astral_signs."""
    source_path = Path(__file__).resolve().parents[4] / "docs" / "db_seeder" / "astrology"
    with (source_path / "astral_signs.json").open(encoding="utf-8") as stream:
        raw = json.load(stream)
    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list):
        raise ValueError("astral_signs source must contain data rows")
    ordered_rows = sorted(rows, key=lambda row: int(row["id"]))
    return tuple(str(row["code"]) for row in ordered_rows)
