"""Crée et alimente les catégories de systèmes de référence zodiacaux.

Revision ID: 20260516_0122
Revises: 20260516_0121
Create Date: 2026-05-16
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260516_0122"
down_revision: Union[str, Sequence[str], None] = "20260516_0121"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "astral_zodiacal_reference_system_categories"


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
    """Retourne le chemin du seed JSON canonique des catégories zodiacales."""
    return (
        Path(__file__).resolve().parents[3]
        / "docs"
        / "db_seeder"
        / "astrology"
        / "astral_zodiacal_reference_system_categories.json"
    )


def _load_rows() -> list[dict[str, object]]:
    """Charge la section data du fichier documentaire canonique."""
    with _source_path().open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if not isinstance(raw, dict) or raw.get("name") != TABLE_NAME:
        raise RuntimeError(f"{TABLE_NAME} seed targets an unexpected table")
    rows = raw.get("data")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError(f"{TABLE_NAME} seed must contain a non-empty data list")
    return [dict(row) for row in rows]


def _ensure_schema() -> None:
    """Crée la table et son index pour une migration reprenable."""
    if not _table_exists(TABLE_NAME):
        op.create_table(
            TABLE_NAME,
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("key", sa.String(length=64), nullable=False),
            sa.Column("display_name", sa.String(length=128), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("usage_note", sa.Text(), nullable=True),
            sa.UniqueConstraint("key", name="uq_astral_zodiacal_ref_system_categories_key"),
        )
    if not _index_exists(TABLE_NAME, "ix_astral_zodiacal_reference_system_categories_key"):
        op.create_index("ix_astral_zodiacal_reference_system_categories_key", TABLE_NAME, ["key"])


def _seed_rows() -> None:
    """Synchronise les catégories zodiacales depuis la section data du JSON."""
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
            sa.text(f"SELECT id FROM {TABLE_NAME} WHERE id = :id OR key = :key"),
            params,
        ).first()
        if existing is None:
            connection.execute(
                sa.text(
                    f"""
                    INSERT INTO {TABLE_NAME} (
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
                f"""
                UPDATE {TABLE_NAME}
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
    """Crée et seed le référentiel global des catégories zodiacales."""
    _ensure_schema()
    _seed_rows()


def downgrade() -> None:
    """Supprime le référentiel des catégories zodiacales."""
    if _table_exists(TABLE_NAME):
        op.drop_index("ix_astral_zodiacal_reference_system_categories_key", table_name=TABLE_NAME)
        op.drop_table(TABLE_NAME)
