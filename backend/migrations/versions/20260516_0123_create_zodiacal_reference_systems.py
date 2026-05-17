"""Crée et alimente les systèmes de référence zodiacaux.

Revision ID: 20260516_0123
Revises: 20260516_0122
Create Date: 2026-05-16
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260516_0123"
down_revision: Union[str, Sequence[str], None] = "20260516_0122"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "astral_zodiacal_reference_systems"
CATEGORY_TABLE_NAME = "astral_zodiacal_reference_system_categories"
FK_NAME = "fk_astral_zodiacal_reference_systems_category_id"


def _table_exists(table_name: str) -> bool:
    """Indique si la table existe dans le schéma courant."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _columns(table_name: str) -> set[str]:
    """Retourne les colonnes existantes d'une table."""
    if not _table_exists(table_name):
        return set()
    return {str(column["name"]) for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def _index_exists(table_name: str, index_name: str) -> bool:
    """Indique si un index existe déjà sur la table."""
    if not _table_exists(table_name):
        return False
    return index_name in {
        str(index["name"]) for index in sa.inspect(op.get_bind()).get_indexes(table_name)
    }


def _foreign_key_exists(table_name: str, foreign_key_name: str) -> bool:
    """Indique si une clé étrangère nommée existe déjà."""
    if not _table_exists(table_name):
        return False
    return foreign_key_name in {
        str(foreign_key["name"])
        for foreign_key in sa.inspect(op.get_bind()).get_foreign_keys(table_name)
        if foreign_key["name"]
    }


def _source_path() -> Path:
    """Retourne le chemin du seed JSON canonique des systèmes zodiacaux."""
    return (
        Path(__file__).resolve().parents[3]
        / "docs"
        / "db_seeder"
        / "astrology"
        / "astral_zodiacal_reference_systems.json"
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
    """Crée la table, ses index et sa FK pour une migration reprenable."""
    if not _table_exists(CATEGORY_TABLE_NAME):
        raise RuntimeError(f"{CATEGORY_TABLE_NAME} must be migrated before {TABLE_NAME}")
    if not _table_exists(TABLE_NAME):
        op.create_table(
            TABLE_NAME,
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("key", sa.String(length=64), nullable=False),
            sa.Column("display_name", sa.String(length=128), nullable=False),
            sa.Column("category_id", sa.Integer(), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column(
                "requires_ayanamsha", sa.Boolean(), nullable=False, server_default=sa.false()
            ),
            sa.Column("usage_note", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(["category_id"], [f"{CATEGORY_TABLE_NAME}.id"], name=FK_NAME),
            sa.UniqueConstraint("key", name="uq_astral_zodiacal_reference_systems_key"),
        )
    if "category_id" not in _columns(TABLE_NAME):
        op.add_column(TABLE_NAME, sa.Column("category_id", sa.Integer(), nullable=False))
    if not _index_exists(TABLE_NAME, "ix_astral_zodiacal_reference_systems_key"):
        op.create_index("ix_astral_zodiacal_reference_systems_key", TABLE_NAME, ["key"])
    if not _index_exists(TABLE_NAME, "ix_astral_zodiacal_reference_systems_category_id"):
        op.create_index(
            "ix_astral_zodiacal_reference_systems_category_id", TABLE_NAME, ["category_id"]
        )
    if not _foreign_key_exists(TABLE_NAME, FK_NAME):
        with op.batch_alter_table(TABLE_NAME) as batch_op:
            batch_op.create_foreign_key(
                FK_NAME,
                CATEGORY_TABLE_NAME,
                ["category_id"],
                ["id"],
            )


def _seed_rows() -> None:
    """Synchronise les systèmes zodiacaux depuis la section data du JSON."""
    connection = op.get_bind()
    for row in _load_rows():
        params = {
            "id": int(row["id"]),
            "key": str(row["key"]),
            "display_name": str(row["display_name"]),
            "category_id": int(row["category_id"]),
            "description": str(row["description"]),
            "requires_ayanamsha": bool(row["requires_ayanamsha"]),
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
                        id, key, display_name, category_id, description,
                        requires_ayanamsha, usage_note
                    )
                    VALUES (
                        :id, :key, :display_name, :category_id, :description,
                        :requires_ayanamsha, :usage_note
                    )
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
                    category_id = :category_id,
                    description = :description,
                    requires_ayanamsha = :requires_ayanamsha,
                    usage_note = :usage_note
                WHERE id = :id OR key = :key
                """
            ),
            params,
        )


def upgrade() -> None:
    """Crée et seed le référentiel global des systèmes zodiacaux."""
    _ensure_schema()
    _seed_rows()


def downgrade() -> None:
    """Supprime le référentiel des systèmes zodiacaux."""
    if _table_exists(TABLE_NAME):
        op.drop_index("ix_astral_zodiacal_reference_systems_category_id", table_name=TABLE_NAME)
        op.drop_index("ix_astral_zodiacal_reference_systems_key", table_name=TABLE_NAME)
        op.drop_table(TABLE_NAME)
