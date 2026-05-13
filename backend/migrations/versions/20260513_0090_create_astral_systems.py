"""Cree et alimente les systemes astrologiques de reference.

Revision ID: 20260513_0090
Revises: 20260513_0089
Create Date: 2026-05-13
"""

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260513_0090"
down_revision: Union[str, Sequence[str], None] = "20260513_0089"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _load_astral_system_names() -> list[str]:
    """Charge les noms de systemes depuis la source documentaire canonique."""
    migration_path = Path(__file__).resolve()
    candidate_paths = (
        migration_path.parents[3] / "docs" / "recherches astro" / "astral_systems.json",
        migration_path.parents[2] / "docs" / "recherches astro" / "astral_systems.json",
    )
    systems_path = next((path for path in candidate_paths if path.exists()), None)
    if systems_path is None:
        raise RuntimeError("missing docs/recherches astro/astral_systems.json")

    with systems_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    names = raw.get("name") if isinstance(raw, dict) else None
    if not isinstance(names, list) or not names:
        raise RuntimeError("astral systems source must contain a non-empty name list")
    if not all(isinstance(name, str) and name.strip() for name in names):
        raise RuntimeError("astral system names must be non-empty strings")
    if len(set(names)) != len(names):
        raise RuntimeError("astral system names must be unique")
    return names


def upgrade() -> None:
    """Cree la table et injecte les systemes astrologiques documentes."""
    op.create_table(
        "astral_systems",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.UniqueConstraint("name"),
    )
    op.bulk_insert(
        sa.table(
            "astral_systems",
            sa.column("name", sa.String),
        ),
        [{"name": name} for name in _load_astral_system_names()],
    )


def downgrade() -> None:
    """Supprime la table des systemes astrologiques."""
    op.drop_table("astral_systems")
