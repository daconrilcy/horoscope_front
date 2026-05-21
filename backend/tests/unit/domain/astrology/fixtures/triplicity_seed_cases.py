"""Fixtures CS-205 construites depuis les seeds canoniques de triplicite."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from app.domain.astrology.runtime.runtime_reference import (
    AstrologyRuntimeReference,
    TriplicityRulerReferenceData,
)
from tests.factories.astrology_runtime_reference_factory import (
    complete_reference_with_planet_sect_rules,
)

PROJECT_ROOT = Path(__file__).resolve().parents[6]
SEED_DIR = PROJECT_ROOT / "docs/db_seeder/astrology"


def seed_backed_triplicity_reference() -> AstrologyRuntimeReference:
    """Retourne une reference runtime dont les triplicites viennent des seeds."""
    reference = complete_reference_with_planet_sect_rules()
    dignity_reference = reference.dignity_reference
    return replace(
        reference,
        dignity_reference=replace(
            dignity_reference,
            triplicity_rulers=tuple(_seed_triplicity_rulers()),
        ),
    )


def _seed_triplicity_rulers() -> list[TriplicityRulerReferenceData]:
    """Mappe les lignes seed DB en contrats runtime de triplicite."""
    planets = _index_seed_codes("astral_planets.json")
    elements = _index_seed_codes("astral_elements.json")
    sects = _index_seed_codes("astral_sect.json")
    roles = _index_seed_codes("astral_ruler_assignments_role.json")
    systems = _index_seed_values("astral_systems.json", value_field="name")
    rows = _seed_rows("astral_triplicity_ruler_assignments.json")
    return [
        TriplicityRulerReferenceData(
            element_code=elements[int(row["element_id"])],
            sect_code=sects[int(row["sect_id"])],
            planet_code=planets[int(row["planet_id"])],
            role_code=roles[int(row["role_id"])],
            system_code=systems[int(row["astral_system_id"])],
        )
        for row in rows
    ]


def _index_seed_codes(file_name: str) -> dict[int, str]:
    """Indexe les codes seed par identifiant numerique."""
    return _index_seed_values(file_name, value_field="code")


def _index_seed_values(file_name: str, *, value_field: str) -> dict[int, str]:
    """Indexe un champ seed par identifiant numerique."""
    return {int(row["id"]): str(row[value_field]) for row in _seed_rows(file_name)}


def _seed_rows(file_name: str) -> list[dict[str, Any]]:
    """Charge les lignes d'un fichier seed astrologique."""
    payload = json.loads((SEED_DIR / file_name).read_text(encoding="utf-8"))
    return list(payload["data"])
