"""Ajoute l'identifiant SwissEph aux planètes canoniques.

Revision ID: 20260515_0116
Revises: 20260515_0115
Create Date: 2026-05-15
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260515_0116"
down_revision: Union[str, Sequence[str], None] = "20260515_0115"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "astral_planets"


def _research_path(file_name: str) -> Path:
    """Construit le chemin robuste vers un JSON de seed astrologique."""
    migration_path = Path(__file__).resolve()
    candidates = (
        migration_path.parents[3] / "docs" / "db_seeder" / "astrology" / file_name,
        migration_path.parents[2] / "docs" / "db_seeder" / "astrology" / file_name,
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise RuntimeError(f"missing astrology seed {file_name}")


def _load_planet_rows() -> list[dict[str, object]]:
    """Charge les lignes de planètes et vérifie leur structure minimale."""
    with _research_path("astral_planets.json").open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if not isinstance(raw, dict) or raw.get("name") != TABLE_NAME:
        raise RuntimeError("astral_planets JSON targets an unexpected table")
    rows = raw.get("data")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("astral_planets JSON must contain a non-empty data list")
    if not all(isinstance(row, dict) for row in rows):
        raise RuntimeError("astral_planets JSON rows must be objects")
    return rows


def _required_int(row: dict[str, object], field_name: str, *, minimum: int = 0) -> int:
    """Extrait un entier obligatoire depuis une ligne JSON."""
    value = row.get(field_name)
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise RuntimeError(f"{field_name} must be an integer >= {minimum}")
    return value


def _required_text(row: dict[str, object], field_name: str, max_length: int) -> str:
    """Extrait un texte obligatoire depuis une ligne JSON."""
    value = row.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"{field_name} must be a non-empty string")
    if len(value) > max_length:
        raise RuntimeError(f"{field_name} must be at most {max_length} characters")
    return value


def _planet_payload(raw_row: dict[str, object]) -> dict[str, object]:
    """Normalise une ligne JSON en payload SQL pour `astral_planets`."""
    return {
        "id": _required_int(raw_row, "id", minimum=1),
        "code": _required_text(raw_row, "code", 32).strip().lower(),
        "name": _required_text(raw_row, "name", 64),
        "swe_id": _required_int(raw_row, "swe_id", minimum=0),
    }


def _seed_planets() -> None:
    """Remplace le contenu canonique des planètes par le JSON dédié."""
    connection = op.get_bind()
    rows = [_planet_payload(raw_row) for raw_row in _load_planet_rows()]
    for row in rows:
        existing = connection.execute(
            sa.text(f"SELECT id FROM {TABLE_NAME} WHERE code = :code"),
            {"code": row["code"]},
        ).first()
        if existing is None:
            connection.execute(
                sa.text(
                    f"""
                    INSERT INTO {TABLE_NAME} (id, code, name, swe_id)
                    VALUES (:id, :code, :name, :swe_id)
                    """
                ),
                row,
            )
            continue
        connection.execute(
            sa.text(
                f"""
                UPDATE {TABLE_NAME}
                SET name = :name, swe_id = :swe_id
                WHERE code = :code
                """
            ),
            row,
        )


def upgrade() -> None:
    """Ajoute la colonne SwissEph puis synchronise les lignes canoniques."""
    with op.batch_alter_table(TABLE_NAME) as batch_op:
        batch_op.add_column(sa.Column("swe_id", sa.Integer(), server_default="0", nullable=False))
    _seed_planets()
    with op.batch_alter_table(TABLE_NAME) as batch_op:
        batch_op.alter_column("swe_id", server_default=None)


def downgrade() -> None:
    """Retire la colonne SwissEph en cas de retour arrière."""
    with op.batch_alter_table(TABLE_NAME) as batch_op:
        batch_op.drop_column("swe_id")
