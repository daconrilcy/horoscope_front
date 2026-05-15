"""Crée et alimente les membres des axes de maisons astrales.

Revision ID: 20260515_0110
Revises: 20260515_0109
Create Date: 2026-05-15
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260515_0110"
down_revision: Union[str, Sequence[str], None] = "20260515_0109"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "astral_house_axis_members"


def _source_path() -> Path:
    """Retourne le chemin du JSON canonique des membres d'axes."""
    return (
        Path(__file__).resolve().parents[3]
        / "docs"
        / "recherches astro"
        / "astral_house_axis_members.json"
    )


def _load_member_rows() -> list[dict[str, int]]:
    """Charge et valide les lignes de seed des membres d'axes de maisons."""
    with _source_path().open(encoding="utf-8") as stream:
        raw = json.load(stream)

    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("astral_house_axis_members.json must contain a non-empty data list")

    parsed_rows: list[dict[str, int]] = []
    seen_ids: set[int] = set()
    seen_houses: set[int] = set()
    seen_pairs: set[tuple[int, int]] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeError("house axis member rows must be objects")

        member_id = _required_positive_int(row, "id")
        axis_id = _required_positive_int(row, "axis_id")
        house_id = _required_positive_int(row, "house_id")
        opposite_house_id = _required_positive_int(row, "opposite_house_id")
        pair = (axis_id, house_id)

        if member_id in seen_ids or house_id in seen_houses or pair in seen_pairs:
            raise RuntimeError("house axis member ids, houses and scoped pairs must be unique")
        if house_id == opposite_house_id:
            raise RuntimeError("house_id and opposite_house_id must be different")
        seen_ids.add(member_id)
        seen_houses.add(house_id)
        seen_pairs.add(pair)
        parsed_rows.append(
            {
                "id": member_id,
                "axis_id": axis_id,
                "house_id": house_id,
                "opposite_house_id": opposite_house_id,
            }
        )
    return parsed_rows


def _required_positive_int(row: dict[str, object], field_name: str) -> int:
    """Extrait un identifiant entier strictement positif."""
    value = row.get(field_name)
    if not isinstance(value, int) or value <= 0:
        raise RuntimeError(f"{field_name} must be a positive integer")
    return value


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe déjà dans le schéma courant."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _index_exists(table_name: str, index_name: str) -> bool:
    """Indique si un index existe déjà sur la table."""
    if not _table_exists(table_name):
        return False
    indexes = sa.inspect(op.get_bind()).get_indexes(table_name)
    return index_name in {index["name"] for index in indexes}


def _seed_house_axis_members() -> None:
    """Insère les membres absents sans modifier une base déjà personnalisée."""
    connection = op.get_bind()
    for row in _load_member_rows():
        connection.execute(
            sa.text(
                f"""
                INSERT INTO {TABLE_NAME} (
                    id,
                    axis_id,
                    house_id,
                    opposite_house_id
                )
                SELECT
                    :id,
                    :axis_id,
                    :house_id,
                    :opposite_house_id
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM {TABLE_NAME}
                    WHERE id = :id
                        OR house_id = :house_id
                        OR (
                            axis_id = :axis_id
                            AND house_id = :house_id
                        )
                )
                """
            ),
            row,
        )


def upgrade() -> None:
    """Crée la table des membres d'axes et insère les valeurs canoniques."""
    if not _table_exists(TABLE_NAME):
        op.create_table(
            TABLE_NAME,
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("axis_id", sa.Integer(), nullable=False),
            sa.Column("house_id", sa.Integer(), nullable=False),
            sa.Column("opposite_house_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(
                ["axis_id"],
                ["astral_house_axis_definitions.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(["house_id"], ["astral_houses.id"]),
            sa.ForeignKeyConstraint(["opposite_house_id"], ["astral_houses.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("house_id", name="uq_astral_house_axis_members_house_id"),
            sa.UniqueConstraint(
                "axis_id",
                "house_id",
                name="uq_astral_house_axis_members_axis_house",
            ),
            sa.CheckConstraint(
                "house_id <> opposite_house_id",
                name="ck_astral_house_axis_members_distinct_houses",
            ),
        )
    if not _index_exists(TABLE_NAME, "ix_astral_house_axis_members_axis_id"):
        op.create_index(
            "ix_astral_house_axis_members_axis_id",
            TABLE_NAME,
            ["axis_id"],
            unique=False,
        )
    if not _index_exists(TABLE_NAME, "ix_astral_house_axis_members_house_id"):
        op.create_index(
            "ix_astral_house_axis_members_house_id",
            TABLE_NAME,
            ["house_id"],
            unique=False,
        )
    if not _index_exists(TABLE_NAME, "ix_astral_house_axis_members_opposite_house_id"):
        op.create_index(
            "ix_astral_house_axis_members_opposite_house_id",
            TABLE_NAME,
            ["opposite_house_id"],
            unique=False,
        )
    _seed_house_axis_members()


def downgrade() -> None:
    """Supprime la table des membres d'axes de maisons."""
    for index_name in (
        "ix_astral_house_axis_members_opposite_house_id",
        "ix_astral_house_axis_members_house_id",
        "ix_astral_house_axis_members_axis_id",
    ):
        if _index_exists(TABLE_NAME, index_name):
            op.drop_index(index_name, table_name=TABLE_NAME)
    if _table_exists(TABLE_NAME):
        op.drop_table(TABLE_NAME)
