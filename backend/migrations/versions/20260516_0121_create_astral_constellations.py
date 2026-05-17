"""Crée et alimente le référentiel stable des constellations astrales.

Revision ID: 20260516_0121
Revises: 20260516_0120
Create Date: 2026-05-16
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260516_0121"
down_revision: Union[str, Sequence[str], None] = "20260516_0120"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FK_NAME = "fk_astral_constellations_hemisphere_id"


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
    """Retourne le chemin du seed JSON canonique des constellations."""
    return (
        Path(__file__).resolve().parents[3]
        / "docs"
        / "db_seeder"
        / "astrology"
        / "astral_constellations.json"
    )


def _load_rows() -> list[dict[str, object]]:
    """Charge la section data du fichier documentaire canonique."""
    with _source_path().open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if not isinstance(raw, dict) or raw.get("name") != "astral_constellations":
        raise RuntimeError("astral_constellations seed targets an unexpected table")
    rows = raw.get("data")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("astral_constellations seed must contain a non-empty data list")
    return [dict(row) for row in rows]


def _ensure_schema() -> None:
    """Crée la table, ses index et sa FK pour une migration reprenable."""
    if not _table_exists("astral_constellations"):
        op.create_table(
            "astral_constellations",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("key", sa.String(length=64), nullable=False),
            sa.Column("display_name", sa.String(length=128), nullable=False),
            sa.Column("latin_name", sa.String(length=128), nullable=False),
            sa.Column("abbreviation", sa.String(length=8), nullable=False),
            sa.Column("zodiacal", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("hemisphere_id", sa.Integer(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(
                ["hemisphere_id"],
                ["astral_hemispheres.id"],
                name=FK_NAME,
            ),
            sa.UniqueConstraint("key", name="uq_astral_constellations_key"),
            sa.UniqueConstraint("abbreviation", name="uq_astral_constellations_abbreviation"),
        )
    if "hemisphere_id" not in _columns("astral_constellations"):
        op.add_column("astral_constellations", sa.Column("hemisphere_id", sa.Integer()))
    if not _index_exists("astral_constellations", "ix_astral_constellations_key"):
        op.create_index(
            "ix_astral_constellations_key", "astral_constellations", ["key"], unique=False
        )
    if not _index_exists("astral_constellations", "ix_astral_constellations_abbreviation"):
        op.create_index(
            "ix_astral_constellations_abbreviation",
            "astral_constellations",
            ["abbreviation"],
            unique=False,
        )
    if not _index_exists("astral_constellations", "ix_astral_constellations_hemisphere_id"):
        op.create_index(
            "ix_astral_constellations_hemisphere_id",
            "astral_constellations",
            ["hemisphere_id"],
            unique=False,
        )
    if not _foreign_key_exists("astral_constellations", FK_NAME):
        with op.batch_alter_table("astral_constellations") as batch_op:
            batch_op.create_foreign_key(
                FK_NAME,
                "astral_hemispheres",
                ["hemisphere_id"],
                ["id"],
            )


def _seed_rows() -> None:
    """Synchronise les constellations depuis la section data du JSON."""
    connection = op.get_bind()
    for row in _load_rows():
        params = {
            "id": int(row["id"]),
            "key": str(row["key"]),
            "display_name": str(row["display_name"]),
            "latin_name": str(row["latin_name"]),
            "abbreviation": str(row["abbreviation"]),
            "zodiacal": bool(row["zodiacal"]),
            "hemisphere_id": None
            if row.get("hemisphere_id") is None
            else int(row["hemisphere_id"]),
            "notes": None if row.get("notes") is None else str(row["notes"]),
        }
        existing = connection.execute(
            sa.text("SELECT id FROM astral_constellations WHERE id = :id OR key = :key"),
            params,
        ).first()
        if existing is None:
            connection.execute(
                sa.text(
                    """
                    INSERT INTO astral_constellations (
                        id, key, display_name, latin_name, abbreviation, zodiacal,
                        hemisphere_id, notes
                    )
                    VALUES (
                        :id, :key, :display_name, :latin_name, :abbreviation, :zodiacal,
                        :hemisphere_id, :notes
                    )
                    """
                ),
                params,
            )
            continue
        connection.execute(
            sa.text(
                """
                UPDATE astral_constellations
                SET key = :key,
                    display_name = :display_name,
                    latin_name = :latin_name,
                    abbreviation = :abbreviation,
                    zodiacal = :zodiacal,
                    hemisphere_id = :hemisphere_id,
                    notes = :notes
                WHERE id = :id OR key = :key
                """
            ),
            params,
        )


def upgrade() -> None:
    """Crée et seed le référentiel global des constellations."""
    if not _table_exists("astral_hemispheres"):
        raise RuntimeError("astral_hemispheres must be migrated before astral_constellations")
    _ensure_schema()
    _seed_rows()


def downgrade() -> None:
    """Supprime le référentiel des constellations."""
    if _table_exists("astral_constellations"):
        op.drop_index("ix_astral_constellations_hemisphere_id", table_name="astral_constellations")
        op.drop_index("ix_astral_constellations_abbreviation", table_name="astral_constellations")
        op.drop_index("ix_astral_constellations_key", table_name="astral_constellations")
        op.drop_table("astral_constellations")
