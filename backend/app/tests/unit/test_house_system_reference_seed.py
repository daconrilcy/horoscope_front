"""Tests du seed canonique des systèmes de maisons astrologiques."""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.reference import AstralHouseSystemModel
from app.infra.db.repositories.astrology_reference_sources import load_astral_house_system_rows
from app.infra.db.repositories.house_system_reference import sync_house_system_seed_data

REPO_ROOT = Path(__file__).resolve().parents[4]
HOUSE_SYSTEM_SOURCE = REPO_ROOT / "docs" / "db_seeder" / "astrology" / "astral_house_system.json"


def test_load_astral_house_system_rows_reads_canonical_json() -> None:
    """Vérifie que le loader expose les lignes du JSON documentaire canonique."""
    with HOUSE_SYSTEM_SOURCE.open(encoding="utf-8") as stream:
        source_rows = json.load(stream)["data"]

    loaded_rows = load_astral_house_system_rows()

    assert loaded_rows == tuple(dict(row) for row in source_rows)


def test_sync_house_system_seed_data_uses_canonical_json(db_session: Session) -> None:
    """Vérifie que le seed insère et met à jour depuis la source JSON canonique."""
    db_session.add(
        AstralHouseSystemModel(
            id=1,
            code="placidus",
            name="Ancien nom",
            description="Ancienne description",
            astronomical_family="sign_based",
            supports_polar_regions=True,
            is_quadrant_based=False,
            requires_precise_birth_time=False,
            sort_order=999,
        )
    )
    db_session.flush()

    sync_house_system_seed_data(db_session)
    db_session.flush()

    systems = db_session.scalars(
        select(AstralHouseSystemModel).order_by(AstralHouseSystemModel.sort_order)
    ).all()
    source_rows = load_astral_house_system_rows()

    assert [system.code for system in systems] == [str(row["code"]) for row in source_rows]
    placidus_source = next(row for row in source_rows if row["code"] == "placidus")
    placidus = next(system for system in systems if system.code == "placidus")
    assert placidus.name == placidus_source["name"]
    assert placidus.description == placidus_source["description"]
    assert placidus.astronomical_family == placidus_source["astronomical_family"]
    assert placidus.supports_polar_regions is bool(placidus_source["supports_polar_regions"])
    assert placidus.is_quadrant_based is bool(placidus_source["is_quadrant_based"])
    assert placidus.requires_precise_birth_time is bool(
        placidus_source["requires_precise_birth_time"]
    )
    assert placidus.sort_order == placidus_source["sort_order"]
