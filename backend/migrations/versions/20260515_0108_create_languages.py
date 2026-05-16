"""Crée et alimente le référentiel des langues.

Revision ID: 20260515_0108
Revises: 20260514_0107
Create Date: 2026-05-15
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260515_0108"
down_revision: Union[str, Sequence[str], None] = "20260514_0107"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _languages_path() -> Path:
    """Retourne le chemin de la source documentaire des langues."""
    return Path(__file__).resolve().parents[3] / "docs" / "db_seeder" / "languages.json"


def _load_language_rows() -> list[dict[str, object]]:
    """Charge et valide les lignes de langues à insérer."""
    with _languages_path().open(encoding="utf-8") as stream:
        raw = json.load(stream)

    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("docs/db_seeder/languages.json must contain a non-empty data list")

    parsed_rows: list[dict[str, object]] = []
    seen_ids: set[int] = set()
    seen_codes: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeError("language rows must be objects")
        language_id = row.get("id")
        code = row.get("code")
        name = row.get("name")
        if not isinstance(language_id, int) or language_id <= 0:
            raise RuntimeError("language id must be a positive integer")
        if not isinstance(code, str) or not code.strip():
            raise RuntimeError("language code must be a non-empty string")
        if not isinstance(name, str) or not name.strip():
            raise RuntimeError("language name must be a non-empty string")
        if language_id in seen_ids or code in seen_codes:
            raise RuntimeError("language ids and codes must be unique")
        seen_ids.add(language_id)
        seen_codes.add(code)
        parsed_rows.append({"id": language_id, "code": code, "name": name})
    return parsed_rows


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe déjà pour rendre la migration reprenable."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _index_exists(table_name: str, index_name: str) -> bool:
    """Indique si un index existe déjà sur la table."""
    if not _table_exists(table_name):
        return False
    indexes = sa.inspect(op.get_bind()).get_indexes(table_name)
    return index_name in {index["name"] for index in indexes}


def _seed_languages() -> None:
    """Insère les langues absentes sans modifier les lignes existantes."""
    connection = op.get_bind()
    for row in _load_language_rows():
        connection.execute(
            sa.text(
                """
                INSERT INTO languages (id, code, name)
                SELECT :id, :code, :name
                WHERE NOT EXISTS (
                    SELECT 1 FROM languages WHERE id = :id OR code = :code
                )
                """
            ),
            row,
        )


def upgrade() -> None:
    """Crée la table des langues et insère les valeurs canoniques."""
    if not _table_exists("languages"):
        op.create_table(
            "languages",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("code", sa.String(length=16), nullable=False),
            sa.Column("name", sa.String(length=64), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("code"),
        )
    if not _index_exists("languages", "ix_languages_code"):
        op.create_index("ix_languages_code", "languages", ["code"], unique=False)
    _seed_languages()


def downgrade() -> None:
    """Supprime le référentiel des langues."""
    if _index_exists("languages", "ix_languages_code"):
        op.drop_index("ix_languages_code", table_name="languages")
    if _table_exists("languages"):
        op.drop_table("languages")
