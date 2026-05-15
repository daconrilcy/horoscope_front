"""Crée et alimente les définitions d'axes de maisons astrales.

Revision ID: 20260515_0109
Revises: 20260515_0108
Create Date: 2026-05-15
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260515_0109"
down_revision: Union[str, Sequence[str], None] = "20260515_0108"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "astral_house_axis_definitions"


def _source_path() -> Path:
    """Retourne le chemin du JSON canonique des axes de maisons."""
    return (
        Path(__file__).resolve().parents[3]
        / "docs"
        / "recherches astro"
        / "astral_house_axis_definitions.json"
    )


def _load_axis_rows() -> list[dict[str, object]]:
    """Charge et valide les lignes de seed des axes de maisons."""
    with _source_path().open(encoding="utf-8") as stream:
        raw = json.load(stream)

    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("astral_house_axis_definitions.json must contain a non-empty data list")

    parsed_rows: list[dict[str, object]] = []
    seen_ids: set[int] = set()
    seen_scopes: set[tuple[int, int, str, int]] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeError("house axis definition rows must be objects")

        axis_id = _required_positive_int(row, "id")
        astral_system_id = _required_positive_int(row, "astral_system_id")
        key = _required_text(row, "key", max_length=64)
        title = _required_text(row, "title", max_length=128)
        summary = _required_text(row, "summary")
        language_id = _required_positive_int(row, "language_id")
        micro_note = _optional_text(row, "micro_note")
        scope = (astral_system_id, key, language_id)

        if axis_id in seen_ids or scope in seen_scopes:
            raise RuntimeError("house axis definition ids and scoped keys must be unique")
        seen_ids.add(axis_id)
        seen_scopes.add(scope)
        parsed_rows.append(
            {
                "id": axis_id,
                "astral_system_id": astral_system_id,
                "key": key,
                "title": title,
                "summary": summary,
                "language_id": language_id,
                "micro_note": micro_note,
            }
        )
    return parsed_rows


def _required_positive_int(row: dict[str, object], field_name: str) -> int:
    """Extrait un identifiant entier strictement positif."""
    value = row.get(field_name)
    if not isinstance(value, int) or value <= 0:
        raise RuntimeError(f"{field_name} must be a positive integer")
    return value


def _required_text(row: dict[str, object], field_name: str, max_length: int | None = None) -> str:
    """Extrait un texte obligatoire et vérifie sa longueur éventuelle."""
    value = row.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"{field_name} must be a non-empty string")
    if max_length is not None and len(value) > max_length:
        raise RuntimeError(f"{field_name} must be at most {max_length} characters")
    return value


def _optional_text(row: dict[str, object], field_name: str) -> str | None:
    """Extrait un texte optionnel compatible avec une colonne nullable."""
    value = row.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"{field_name} must be null or a non-empty string")
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


def _seed_house_axis_definitions() -> None:
    """Insère les axes absents sans écraser une base déjà personnalisée."""
    connection = op.get_bind()
    for row in _load_axis_rows():
        connection.execute(
            sa.text(
                f"""
                INSERT INTO {TABLE_NAME} (
                    id,
                    astral_system_id,
                    key,
                    title,
                    summary,
                    language_id,
                    micro_note
                )
                SELECT
                    :id,
                    :astral_system_id,
                    :key,
                    :title,
                    :summary,
                    :language_id,
                    :micro_note
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM {TABLE_NAME}
                    WHERE id = :id
                        OR (
                            astral_system_id = :astral_system_id
                            AND key = :key
                            AND language_id = :language_id
                        )
                )
                """
            ),
            row,
        )


def upgrade() -> None:
    """Crée la table des axes de maisons et insère les définitions canoniques."""
    if not _table_exists(TABLE_NAME):
        op.create_table(
            TABLE_NAME,
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("astral_system_id", sa.Integer(), nullable=False),
            sa.Column("key", sa.String(length=64), nullable=False),
            sa.Column("title", sa.String(length=128), nullable=False),
            sa.Column("summary", sa.Text(), nullable=False),
            sa.Column("language_id", sa.Integer(), nullable=False),
            sa.Column("micro_note", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(["astral_system_id"], ["astral_systems.id"]),
            sa.ForeignKeyConstraint(["language_id"], ["languages.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "astral_system_id",
                "key",
                "language_id",
                name="uq_astral_house_axis_definitions_scope",
            ),
        )
    if not _index_exists(TABLE_NAME, "ix_astral_house_axis_definitions_astral_system_id"):
        op.create_index(
            "ix_astral_house_axis_definitions_astral_system_id",
            TABLE_NAME,
            ["astral_system_id"],
            unique=False,
        )
    if not _index_exists(TABLE_NAME, "ix_astral_house_axis_definitions_language_id"):
        op.create_index(
            "ix_astral_house_axis_definitions_language_id",
            TABLE_NAME,
            ["language_id"],
            unique=False,
        )
    if not _index_exists(TABLE_NAME, "ix_astral_house_axis_definitions_key"):
        op.create_index(
            "ix_astral_house_axis_definitions_key",
            TABLE_NAME,
            ["key"],
            unique=False,
        )
    _seed_house_axis_definitions()


def downgrade() -> None:
    """Supprime la table des définitions d'axes de maisons."""
    for index_name in (
        "ix_astral_house_axis_definitions_key",
        "ix_astral_house_axis_definitions_language_id",
        "ix_astral_house_axis_definitions_astral_system_id",
    ):
        if _index_exists(TABLE_NAME, index_name):
            op.drop_index(index_name, table_name=TABLE_NAME)
    if _table_exists(TABLE_NAME):
        op.drop_table(TABLE_NAME)
