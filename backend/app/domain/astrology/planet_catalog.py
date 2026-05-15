"""Catalogue planétaire canonique partagé par les calculs astrologiques."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True, slots=True)
class PlanetCatalogItem:
    """Ligne canonique de `astral_planets` utile au domaine."""

    id: int
    code: str
    name: str
    swe_id: int

    @property
    def runtime_code(self) -> str:
        """Retourne le code historique utilisé par le moteur daily."""
        return self.name


def _seed_path() -> Path:
    """Construit le chemin vers le JSON qui alimente `astral_planets`."""
    repo_root = Path(__file__).resolve().parents[4]
    return repo_root / "docs" / "db_seeder" / "astrology" / "astral_planets.json"


@lru_cache(maxsize=1)
def load_default_planet_catalog() -> tuple[PlanetCatalogItem, ...]:
    """Charge les planètes par défaut depuis le seed canonique."""
    with _seed_path().open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if not isinstance(raw, dict) or raw.get("name") != "astral_planets":
        raise ValueError("astral_planets seed targets an unexpected table")
    rows = raw.get("data")
    if not isinstance(rows, list) or not rows:
        raise ValueError("astral_planets seed must contain data rows")

    catalog: list[PlanetCatalogItem] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("astral_planets seed rows must be objects")
        catalog.append(
            PlanetCatalogItem(
                id=int(row["id"]),
                code=str(row["code"]).strip().lower(),
                name=str(row["name"]).strip(),
                swe_id=int(row["swe_id"]),
            )
        )
    return tuple(catalog)


def planet_swe_ids_by_code() -> Mapping[str, int]:
    """Retourne code SQL minuscule -> identifiant SwissEph."""
    return MappingProxyType({item.code: item.swe_id for item in load_default_planet_catalog()})


def planet_swe_ids_by_runtime_code() -> Mapping[str, int]:
    """Retourne code runtime historique -> identifiant SwissEph."""
    return MappingProxyType(
        {item.runtime_code: item.swe_id for item in load_default_planet_catalog()}
    )


def planet_runtime_codes() -> tuple[str, ...]:
    """Retourne les codes runtime dans l'ordre du seed canonique."""
    return tuple(item.runtime_code for item in load_default_planet_catalog())


def planet_codes() -> tuple[str, ...]:
    """Retourne les codes SQL dans l'ordre du seed canonique."""
    return tuple(item.code for item in load_default_planet_catalog())
