"""Crée et alimente les époques de référence astronomiques.

Revision ID: 20260516_0124
Revises: 20260516_0123
Create Date: 2026-05-16
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260516_0124"
down_revision: Union[str, Sequence[str], None] = "20260516_0123"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "astral_reference_epochs"


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


def _constraint_exists(table_name: str, constraint_name: str) -> bool:
    """Indique si une contrainte nommée existe déjà sur la table."""
    if not _table_exists(table_name):
        return False
    inspector = sa.inspect(op.get_bind())
    constraint_names = {
        str(constraint["name"])
        for constraint in inspector.get_unique_constraints(table_name)
        if constraint["name"]
    }
    constraint_names.update(
        str(constraint["name"])
        for constraint in inspector.get_check_constraints(table_name)
        if constraint["name"]
    )
    return constraint_name in constraint_names


def _source_path() -> Path:
    """Retourne le chemin du seed JSON canonique des époques."""
    return (
        Path(__file__).resolve().parents[3]
        / "docs"
        / "db_seeder"
        / "astrology"
        / "astral_reference_epochs.json"
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
    """Crée la table et ses contraintes pour une migration reprenable."""
    if not _table_exists(TABLE_NAME):
        op.create_table(
            TABLE_NAME,
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("key", sa.String(length=32), nullable=False),
            sa.Column("display_name", sa.String(length=64), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("epoch_type", sa.String(length=32), nullable=False),
            sa.Column("julian_year", sa.Float(), nullable=True),
            sa.Column("iso_datetime", sa.String(length=32), nullable=True),
            sa.Column("is_standard", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("usage_note", sa.Text(), nullable=True),
            sa.UniqueConstraint("key", name="uq_astral_reference_epochs_key"),
            sa.CheckConstraint(
                "epoch_type IN ('julian_epoch', 'besselian_epoch', 'runtime_epoch')",
                name="ck_astral_reference_epochs_epoch_type",
            ),
        )
    if not _index_exists(TABLE_NAME, "ix_astral_reference_epochs_key"):
        op.create_index("ix_astral_reference_epochs_key", TABLE_NAME, ["key"])
    if not _constraint_exists(TABLE_NAME, "ck_astral_reference_epochs_epoch_type"):
        with op.batch_alter_table(TABLE_NAME) as batch_op:
            batch_op.create_check_constraint(
                "ck_astral_reference_epochs_epoch_type",
                "epoch_type IN ('julian_epoch', 'besselian_epoch', 'runtime_epoch')",
            )


def _seed_rows() -> None:
    """Synchronise les époques depuis la section data du JSON."""
    connection = op.get_bind()
    for row in _load_rows():
        params = {
            "id": int(row["id"]),
            "key": str(row["key"]),
            "display_name": str(row["display_name"]),
            "description": str(row["description"]),
            "epoch_type": str(row["epoch_type"]),
            "julian_year": None if row.get("julian_year") is None else float(row["julian_year"]),
            "iso_datetime": None if row.get("iso_datetime") is None else str(row["iso_datetime"]),
            "is_standard": bool(row["is_standard"]),
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
                        id, key, display_name, description, epoch_type, julian_year,
                        iso_datetime, is_standard, usage_note
                    )
                    VALUES (
                        :id, :key, :display_name, :description, :epoch_type, :julian_year,
                        :iso_datetime, :is_standard, :usage_note
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
                    description = :description,
                    epoch_type = :epoch_type,
                    julian_year = :julian_year,
                    iso_datetime = :iso_datetime,
                    is_standard = :is_standard,
                    usage_note = :usage_note
                WHERE id = :id OR key = :key
                """
            ),
            params,
        )


def upgrade() -> None:
    """Crée et seed le référentiel global des époques."""
    _ensure_schema()
    _seed_rows()


def downgrade() -> None:
    """Supprime le référentiel des époques."""
    if _table_exists(TABLE_NAME):
        op.drop_index("ix_astral_reference_epochs_key", table_name=TABLE_NAME)
        op.drop_table(TABLE_NAME)
