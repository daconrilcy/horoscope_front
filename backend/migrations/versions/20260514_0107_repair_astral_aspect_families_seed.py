"""Répare le seed des familles d'aspects astraux.

Revision ID: 20260514_0107
Revises: 20260514_0106
Create Date: 2026-05-14
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260514_0107"
down_revision: Union[str, Sequence[str], None] = "20260514_0106"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe dans le schéma courant."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _family_names() -> tuple[str, ...]:
    """Retourne les familles canoniques du JSON documentaire pluriel."""
    source_path = _research_path("astral_aspect_families.json")
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    families = raw.get("family") if isinstance(raw, dict) else None
    if not isinstance(families, list) or not families:
        raise ValueError("aspect families source must contain a non-empty family list")
    return tuple(str(value) for value in families)


def _aspect_family_by_code() -> dict[str, str]:
    """Retourne le rattachement canonique code aspect -> famille."""
    source_path = _research_path("aspects.json")
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if not isinstance(raw, list) or not raw:
        raise ValueError("aspects source must be a non-empty list")
    return {str(row["code"]): str(row["family"]) for row in raw}


def _research_path(file_name: str) -> Path:
    """Construit le chemin vers une source JSON astrologique canonique."""
    migration_path = Path(__file__).resolve()
    candidates = (
        migration_path.parents[3] / "docs" / "db_seeder" / "astrology" / file_name,
        migration_path.parents[2] / "docs" / "db_seeder" / "astrology" / file_name,
        migration_path.parents[3] / "docs" / "recherches astro" / file_name,
        migration_path.parents[2] / "docs" / "recherches astro" / file_name,
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise RuntimeError(f"missing astrology seed {file_name}")


def upgrade() -> None:
    """Insère les familles manquantes et répare les FK des aspects."""
    if not _table_exists("astral_aspect_families") or not _table_exists("astral_aspects"):
        return

    connection = op.get_bind()
    family_table = sa.table(
        "astral_aspect_families",
        sa.column("name", sa.String(length=32)),
    )
    existing_family_names = {
        str(row.name)
        for row in connection.execute(sa.text("SELECT name FROM astral_aspect_families")).all()
    }
    for name in _family_names():
        if name not in existing_family_names:
            connection.execute(sa.insert(family_table).values(name=name))

    family_ids = {
        str(row.name): int(row.id)
        for row in connection.execute(sa.text("SELECT id, name FROM astral_aspect_families")).all()
    }
    for aspect_code, family_name in _aspect_family_by_code().items():
        family_id = family_ids[family_name]
        connection.execute(
            sa.text(
                """
                UPDATE astral_aspects
                SET family = :family_id
                WHERE code = :aspect_code
                """
            ),
            {"family_id": family_id, "aspect_code": aspect_code},
        )


def downgrade() -> None:
    """Ne supprime pas les familles, car elles sont des données canoniques."""
    return
