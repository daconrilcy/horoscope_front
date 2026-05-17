"""Crée et alimente le référentiel stable des hémisphères célestes.

Revision ID: 20260516_0120
Revises: 20260516_0119
Create Date: 2026-05-16
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260516_0120"
down_revision: Union[str, Sequence[str], None] = "20260516_0119"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    """Indique si la table existe dans le schéma courant."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _index_exists(table_name: str, index_name: str) -> bool:
    """Indique si un index existe déjà sur la table."""
    if not _table_exists(table_name):
        return False
    return index_name in {
        str(index["name"]) for index in sa.inspect(op.get_bind()).get_indexes(table_name)
    }


def _source_path() -> Path:
    """Retourne le chemin du seed JSON canonique des hémisphères."""
    return (
        Path(__file__).resolve().parents[3]
        / "docs"
        / "db_seeder"
        / "astrology"
        / "astral_hemispheres.json"
    )


def _load_rows() -> list[dict[str, object]]:
    """Charge la section data du fichier documentaire canonique."""
    with _source_path().open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if not isinstance(raw, dict) or raw.get("name") != "astral_hemispheres":
        raise RuntimeError("astral_hemispheres seed targets an unexpected table")
    rows = raw.get("data")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("astral_hemispheres seed must contain a non-empty data list")
    return [dict(row) for row in rows]


def _ensure_schema() -> None:
    """Crée la table et ses index pour une migration reprenable."""
    if not _table_exists("astral_hemispheres"):
        op.create_table(
            "astral_hemispheres",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("key", sa.String(length=32), nullable=False),
            sa.Column("display_name", sa.String(length=64), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("usage_note", sa.Text(), nullable=True),
            sa.UniqueConstraint("key", name="uq_astral_hemispheres_key"),
        )
    if not _index_exists("astral_hemispheres", "ix_astral_hemispheres_key"):
        op.create_index("ix_astral_hemispheres_key", "astral_hemispheres", ["key"])


def _seed_rows() -> None:
    """Synchronise les hémisphères depuis la section data du JSON."""
    connection = op.get_bind()
    for row in _load_rows():
        params = {
            "id": int(row["id"]),
            "key": str(row["key"]),
            "display_name": str(row["display_name"]),
            "description": str(row["description"]),
            "usage_note": None if row.get("usage_note") is None else str(row["usage_note"]),
        }
        existing = connection.execute(
            sa.text("SELECT id FROM astral_hemispheres WHERE id = :id OR key = :key"),
            params,
        ).first()
        if existing is None:
            connection.execute(
                sa.text(
                    """
                    INSERT INTO astral_hemispheres (
                        id, key, display_name, description, usage_note
                    )
                    VALUES (:id, :key, :display_name, :description, :usage_note)
                    """
                ),
                params,
            )
            continue
        connection.execute(
            sa.text(
                """
                UPDATE astral_hemispheres
                SET key = :key,
                    display_name = :display_name,
                    description = :description,
                    usage_note = :usage_note
                WHERE id = :id OR key = :key
                """
            ),
            params,
        )


def upgrade() -> None:
    """Crée et seed le référentiel global des hémisphères."""
    _ensure_schema()
    _seed_rows()


def downgrade() -> None:
    """Supprime le référentiel des hémisphères."""
    if _table_exists("astral_hemispheres"):
        op.drop_index("ix_astral_hemispheres_key", table_name="astral_hemispheres")
        op.drop_table("astral_hemispheres")
