"""Crée et alimente les référentiels structurels des objets astraux.

Revision ID: 20260515_0112
Revises: 20260515_0111
Create Date: 2026-05-15
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260515_0112"
down_revision: Union[str, Sequence[str], None] = "20260515_0111"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _source_path(file_name: str) -> Path:
    """Retourne le chemin d'une source JSON astrologique canonique."""
    return Path(__file__).resolve().parents[3] / "docs" / "recherches astro" / file_name


def _load_rows(file_name: str) -> list[dict[str, object]]:
    """Charge et valide la liste `data` d'un référentiel documentaire."""
    with _source_path(file_name).open(encoding="utf-8") as stream:
        raw = json.load(stream)
    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list) or not rows:
        raise RuntimeError(f"{file_name} must contain a non-empty data list")
    if not all(isinstance(row, dict) for row in rows):
        raise RuntimeError(f"{file_name} rows must be objects")
    return rows


def _required_positive_int(row: dict[str, object], field_name: str) -> int:
    """Extrait un entier strictement positif depuis une ligne de seed."""
    value = row.get(field_name)
    if not isinstance(value, int) or value <= 0:
        raise RuntimeError(f"{field_name} must be a positive integer")
    return value


def _required_text(
    row: dict[str, object],
    field_name: str,
    *,
    max_length: int | None = None,
) -> str:
    """Extrait un texte obligatoire et vérifie sa longueur éventuelle."""
    value = row.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"{field_name} must be a non-empty string")
    if max_length is not None and len(value) > max_length:
        raise RuntimeError(f"{field_name} must be at most {max_length} characters")
    return value


def _optional_text(
    row: dict[str, object],
    field_name: str,
    *,
    max_length: int | None = None,
) -> str | None:
    """Extrait un texte optionnel compatible avec une colonne nullable."""
    value = row.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"{field_name} must be null or a non-empty string")
    if max_length is not None and len(value) > max_length:
        raise RuntimeError(f"{field_name} must be at most {max_length} characters")
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


def _seed_code_label_description_table(table_name: str, file_name: str) -> None:
    """Insère les référentiels simples identifiés par un code."""
    connection = op.get_bind()
    seen_ids: set[int] = set()
    seen_codes: set[str] = set()
    for raw_row in _load_rows(file_name):
        row = {
            "id": _required_positive_int(raw_row, "id"),
            "code": _required_text(raw_row, "code", max_length=32),
            "label": _required_text(raw_row, "label", max_length=64),
            "description": _required_text(raw_row, "description"),
        }
        if row["id"] in seen_ids or row["code"] in seen_codes:
            raise RuntimeError(f"{file_name} ids and codes must be unique")
        seen_ids.add(row["id"])
        seen_codes.add(row["code"])
        connection.execute(
            sa.text(
                f"""
                INSERT INTO {table_name} (id, code, label, description)
                SELECT :id, :code, :label, :description
                WHERE NOT EXISTS (
                    SELECT 1 FROM {table_name} WHERE id = :id OR code = :code
                )
                """
            ),
            row,
        )


def _seed_angle_points() -> None:
    """Insère les angles astrologiques absents depuis le JSON canonique."""
    connection = op.get_bind()
    seen_ids: set[int] = set()
    seen_codes: set[str] = set()
    for raw_row in _load_rows("astral_angle_points.json"):
        row = {
            "id": _required_positive_int(raw_row, "id"),
            "code": _required_text(raw_row, "code", max_length=32),
            "short_label": _required_text(raw_row, "short_label", max_length=16),
            "full_name": _required_text(raw_row, "full_name", max_length=64),
            "axis": _required_text(raw_row, "axis", max_length=16),
            "opposite_angle_code": _optional_text(
                raw_row,
                "opposite_angle_code",
                max_length=32,
            ),
            "associated_house": _required_positive_int(raw_row, "associated_house"),
            "description": _required_text(raw_row, "description"),
        }
        if row["axis"] not in {"horizontal", "vertical"}:
            raise RuntimeError("angle point axis must be horizontal or vertical")
        if row["associated_house"] > 12:
            raise RuntimeError("angle point associated_house must be between 1 and 12")
        if row["id"] in seen_ids or row["code"] in seen_codes:
            raise RuntimeError("angle point ids and codes must be unique")
        seen_ids.add(row["id"])
        seen_codes.add(row["code"])
        connection.execute(
            sa.text(
                """
                INSERT INTO astral_angle_points (
                    id,
                    code,
                    short_label,
                    full_name,
                    axis,
                    opposite_angle_code,
                    associated_house,
                    description
                )
                SELECT
                    :id,
                    :code,
                    :short_label,
                    :full_name,
                    :axis,
                    :opposite_angle_code,
                    :associated_house,
                    :description
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM astral_angle_points
                    WHERE id = :id OR code = :code
                )
                """
            ),
            row,
        )


def _seed_house_modalities() -> None:
    """Insère les modalités de maisons absentes depuis le JSON canonique."""
    connection = op.get_bind()
    seen_ids: set[int] = set()
    seen_names: set[str] = set()
    for raw_row in _load_rows("astral_house_modalities.json"):
        row = {
            "id": _required_positive_int(raw_row, "id"),
            "name": _required_text(raw_row, "name", max_length=32),
        }
        if row["id"] in seen_ids or row["name"] in seen_names:
            raise RuntimeError("house modality ids and names must be unique")
        seen_ids.add(row["id"])
        seen_names.add(row["name"])
        connection.execute(
            sa.text(
                """
                INSERT INTO astral_house_modalities (id, name)
                SELECT :id, :name
                WHERE NOT EXISTS (
                    SELECT 1 FROM astral_house_modalities WHERE id = :id OR name = :name
                )
                """
            ),
            row,
        )


def upgrade() -> None:
    """Crée les référentiels demandés et seed les valeurs documentaires."""
    if not _table_exists("astral_angle_points"):
        op.create_table(
            "astral_angle_points",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("code", sa.String(length=32), nullable=False),
            sa.Column("short_label", sa.String(length=16), nullable=False),
            sa.Column("full_name", sa.String(length=64), nullable=False),
            sa.Column("axis", sa.String(length=16), nullable=False),
            sa.Column("opposite_angle_code", sa.String(length=32), nullable=True),
            sa.Column("associated_house", sa.Integer(), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.CheckConstraint(
                "axis IN ('horizontal', 'vertical')",
                name="ck_astral_angle_points_axis",
            ),
            sa.CheckConstraint(
                "associated_house BETWEEN 1 AND 12",
                name="ck_astral_angle_points_associated_house",
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("code"),
        )
    if not _index_exists("astral_angle_points", "ix_astral_angle_points_code"):
        op.create_index("ix_astral_angle_points_code", "astral_angle_points", ["code"])

    for table_name in (
        "astral_astrological_roles",
        "astral_calculation_types",
        "astral_object_types",
    ):
        if not _table_exists(table_name):
            op.create_table(
                table_name,
                sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
                sa.Column("code", sa.String(length=32), nullable=False),
                sa.Column("label", sa.String(length=64), nullable=False),
                sa.Column("description", sa.Text(), nullable=False),
                sa.PrimaryKeyConstraint("id"),
                sa.UniqueConstraint("code"),
            )
        index_name = f"ix_{table_name}_code"
        if not _index_exists(table_name, index_name):
            op.create_index(index_name, table_name, ["code"])

    if not _table_exists("astral_house_modalities"):
        op.create_table(
            "astral_house_modalities",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("name", sa.String(length=32), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name"),
        )
    if not _index_exists("astral_house_modalities", "ix_astral_house_modalities_name"):
        op.create_index("ix_astral_house_modalities_name", "astral_house_modalities", ["name"])

    _seed_angle_points()
    _seed_code_label_description_table(
        "astral_astrological_roles",
        "astral_astrological_roles.json",
    )
    _seed_code_label_description_table(
        "astral_calculation_types",
        "astral_calculation_types.json",
    )
    _seed_house_modalities()
    _seed_code_label_description_table("astral_object_types", "astral_object_types.json")


def downgrade() -> None:
    """Supprime les référentiels structurels ajoutés."""
    for table_name, index_name in (
        ("astral_object_types", "ix_astral_object_types_code"),
        ("astral_house_modalities", "ix_astral_house_modalities_name"),
        ("astral_calculation_types", "ix_astral_calculation_types_code"),
        ("astral_astrological_roles", "ix_astral_astrological_roles_code"),
        ("astral_angle_points", "ix_astral_angle_points_code"),
    ):
        if _index_exists(table_name, index_name):
            op.drop_index(index_name, table_name=table_name)
        if _table_exists(table_name):
            op.drop_table(table_name)
