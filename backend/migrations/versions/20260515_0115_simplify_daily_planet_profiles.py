"""Simplifie les profils planétaires du moteur daily.

Revision ID: 20260515_0115
Revises: 20260515_0114
Create Date: 2026-05-15
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260515_0115"
down_revision: Union[str, Sequence[str], None] = "20260515_0114"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "astral_prediction_daily_planet_profiles"
DAILY_COLUMNS = (
    "id",
    "reference_version_id",
    "planet_id",
    "weight_intraday",
    "weight_day_climate",
    "daily_visibility_score",
    "daily_emotional_impact_score",
    "daily_conscious_activation_score",
    "is_enabled",
    "micro_note",
)
DAILY_INSERT_COLUMNS = tuple(column for column in DAILY_COLUMNS if column != "id")
LEGACY_COLUMNS = (
    "class_code",
    "speed_rank",
    "speed_class",
    "typical_polarity",
    "orb_active_deg",
    "orb_peak_deg",
    "keywords_json",
)
PLANET_CODE_BY_SOURCE_ID = {
    1: "sun",
    2: "moon",
    3: "mercury",
    4: "venus",
    5: "mars",
    6: "jupiter",
    7: "saturn",
    8: "uranus",
    9: "neptune",
    10: "pluto",
}


def _research_path(file_name: str) -> Path:
    """Construit le chemin robuste vers un JSON de recherche astrologique."""
    migration_path = Path(__file__).resolve()
    candidates = (
        migration_path.parents[3] / "docs" / "db_seeder" / "astrology" / file_name,
        migration_path.parents[2] / "docs" / "db_seeder" / "astrology" / file_name,
        migration_path.parents[3] / "docs" / "recherches astro" / file_name,
        migration_path.parents[2] / "docs" / "recherches astro" / file_name,
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise RuntimeError(f"missing astrology seed {file_name}")


def _load_daily_rows() -> list[dict[str, object]]:
    """Charge les lignes daily et vérifie qu'elles ciblent la bonne table."""
    with _research_path("astral_prediction_daily_planet_profiles.json").open(
        encoding="utf-8"
    ) as stream:
        raw = json.load(stream)
    if not isinstance(raw, dict) or raw.get("name") != TABLE_NAME:
        raise RuntimeError("daily planet profiles JSON targets an unexpected table")
    rows = raw.get("data")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("daily planet profiles JSON must contain a non-empty data list")
    if not all(isinstance(row, dict) for row in rows):
        raise RuntimeError("daily planet profiles JSON rows must be objects")
    return rows


def _required_positive_int(row: dict[str, object], field_name: str) -> int:
    """Extrait un entier strictement positif depuis une ligne JSON."""
    value = row.get(field_name)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise RuntimeError(f"{field_name} must be a positive integer")
    return value


def _required_float(row: dict[str, object], field_name: str) -> float:
    """Extrait un nombre obligatoire depuis une ligne JSON."""
    value = row.get(field_name)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise RuntimeError(f"{field_name} must be a number")
    return float(value)


def _required_bool(row: dict[str, object], field_name: str) -> bool:
    """Extrait un booléen obligatoire depuis une ligne JSON."""
    value = row.get(field_name)
    if not isinstance(value, bool):
        raise RuntimeError(f"{field_name} must be a boolean")
    return value


def _optional_text(row: dict[str, object], field_name: str) -> str | None:
    """Extrait un texte optionnel depuis une ligne JSON."""
    value = row.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"{field_name} must be null or a non-empty string")
    return value


def _daily_payload(row: dict[str, object]) -> dict[str, object]:
    """Normalise une ligne JSON en payload SQL daily."""
    return {
        "id": _required_positive_int(row, "id"),
        "reference_version_id": _required_positive_int(row, "reference_version_id"),
        "planet_id": _required_positive_int(row, "planet_id"),
        "weight_intraday": _required_float(row, "weight_intraday"),
        "weight_day_climate": _required_float(row, "weight_day_climate"),
        "daily_visibility_score": _required_float(row, "daily_visibility_score"),
        "daily_emotional_impact_score": _required_float(
            row,
            "daily_emotional_impact_score",
        ),
        "daily_conscious_activation_score": _required_float(
            row,
            "daily_conscious_activation_score",
        ),
        "is_enabled": _required_bool(row, "is_enabled"),
        "micro_note": _optional_text(row, "micro_note"),
    }


def _planet_ids_by_source_id(connection: sa.Connection) -> dict[int, int]:
    """Résout les IDs documentaires des planètes vers les IDs SQL réels."""
    rows = connection.execute(sa.text("SELECT id, code FROM astral_planets")).all()
    ids_by_code = {str(row.code).lower(): int(row.id) for row in rows}
    resolved: dict[int, int] = {}
    for source_id, code in PLANET_CODE_BY_SOURCE_ID.items():
        planet_id = ids_by_code.get(code)
        if planet_id is None:
            raise RuntimeError(f"missing astral_planets row for code {code!r}")
        resolved[source_id] = planet_id
    return resolved


def _seed_daily_rows() -> None:
    """Remplace les anciens profils par les lignes daily pour chaque version existante."""
    connection = op.get_bind()
    version_ids = [
        int(row[0])
        for row in connection.execute(sa.text("SELECT id FROM astral_reference_versions")).all()
    ]
    if not version_ids:
        return
    planet_ids_by_source_id = _planet_ids_by_source_id(connection)
    source_rows = [_daily_payload(raw_row) for raw_row in _load_daily_rows()]
    column_sql = ", ".join(DAILY_INSERT_COLUMNS)
    value_sql = ", ".join(f":{column}" for column in DAILY_INSERT_COLUMNS)
    for version_id in version_ids:
        connection.execute(
            sa.text(f"DELETE FROM {TABLE_NAME} WHERE reference_version_id = :version_id"),
            {"version_id": version_id},
        )
        rows = [
            {
                key: value
                for key, value in {
                    **source_row,
                    "reference_version_id": version_id,
                    "planet_id": planet_ids_by_source_id[int(source_row["planet_id"])],
                }.items()
                if key in DAILY_INSERT_COLUMNS
            }
            for source_row in source_rows
        ]
        connection.execute(
            sa.text(
                f"""
                INSERT INTO {TABLE_NAME} ({column_sql})
                VALUES ({value_sql})
                """
            ),
            rows,
        )


def upgrade() -> None:
    """Réduit la table aux seuls paramètres spécifiques au moteur daily."""
    with op.batch_alter_table(TABLE_NAME) as batch_op:
        batch_op.add_column(
            sa.Column(
                "daily_visibility_score",
                sa.Float(),
                server_default="1.0",
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column(
                "daily_emotional_impact_score",
                sa.Float(),
                server_default="1.0",
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column(
                "daily_conscious_activation_score",
                sa.Float(),
                server_default="1.0",
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column("is_enabled", sa.Boolean(), server_default=sa.true(), nullable=False)
        )
        for column_name in LEGACY_COLUMNS:
            batch_op.drop_column(column_name)
    _seed_daily_rows()


def downgrade() -> None:
    """Restaure le schéma historique minimal en cas de retour arrière."""
    with op.batch_alter_table(TABLE_NAME) as batch_op:
        batch_op.add_column(
            sa.Column("class_code", sa.String(length=32), server_default="", nullable=False)
        )
        batch_op.add_column(
            sa.Column("speed_rank", sa.Integer(), server_default="0", nullable=False)
        )
        batch_op.add_column(
            sa.Column("speed_class", sa.String(length=16), server_default="", nullable=False)
        )
        batch_op.add_column(sa.Column("typical_polarity", sa.String(length=16), nullable=True))
        batch_op.add_column(sa.Column("orb_active_deg", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("orb_peak_deg", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("keywords_json", sa.Text(), nullable=True))
        batch_op.drop_column("daily_visibility_score")
        batch_op.drop_column("daily_emotional_impact_score")
        batch_op.drop_column("daily_conscious_activation_score")
        batch_op.drop_column("is_enabled")
