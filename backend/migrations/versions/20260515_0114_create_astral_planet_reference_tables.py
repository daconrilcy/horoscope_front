"""Crée et alimente les référentiels planétaires issus des JSON de recherche.

Revision ID: 20260515_0114
Revises: 20260515_0113
Create Date: 2026-05-15
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260515_0114"
down_revision: Union[str, Sequence[str], None] = "20260515_0113"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TYPICAL_POLARITIES_TABLE = "astral_typical_polarities"
SPEED_TABLE = "astral_speed"
PLANET_DEFINITIONS_TABLE = "astral_planet_definitions"
PLANET_INTERPRETATION_TABLE = "astral_planet_interpretation_profiles"

PLANET_INTERPRETATION_JSON_FIELDS = (
    "core_keywords_json",
    "shadow_keywords_json",
    "psychological_expression_json",
    "relational_expression_json",
    "vocational_expression_json",
    "spiritual_expression_json",
    "energetic_dynamics_json",
    "growth_patterns_json",
    "conflict_patterns_json",
    "archetypes_json",
    "dos_json",
    "donts_json",
    "prompt_hints_json",
)


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


def _load_table_rows(file_name: str, expected_name: str) -> list[dict[str, object]]:
    """Charge les lignes `data` d'un JSON de table et vérifie sa cible."""
    with _research_path(file_name).open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if not isinstance(raw, dict) or raw.get("name") != expected_name:
        raise RuntimeError(f"{file_name} targets an unexpected table")
    rows = raw.get("data")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError(f"{file_name} must contain a non-empty data list")
    if not all(isinstance(row, dict) for row in rows):
        raise RuntimeError(f"{file_name} data rows must be objects")
    return rows


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe déjà dans le schéma courant."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _index_exists(table_name: str, index_name: str) -> bool:
    """Indique si un index est déjà présent sur une table."""
    if not _table_exists(table_name):
        return False
    return index_name in {
        str(index["name"]) for index in sa.inspect(op.get_bind()).get_indexes(table_name)
    }


def _required_positive_int(row: dict[str, object], field_name: str) -> int:
    """Extrait un entier strictement positif depuis une ligne de seed."""
    value = row.get(field_name)
    if not isinstance(value, int) or value <= 0:
        raise RuntimeError(f"{field_name} must be a positive integer")
    return value


def _optional_positive_int(row: dict[str, object], field_name: str) -> int | None:
    """Extrait un entier positif optionnel depuis une ligne de seed."""
    value = row.get(field_name)
    if value is None:
        return None
    if not isinstance(value, int) or value <= 0:
        raise RuntimeError(f"{field_name} must be null or a positive integer")
    return value


def _required_non_negative_int(row: dict[str, object], field_name: str) -> int:
    """Extrait un entier positif ou nul depuis une ligne de seed."""
    value = row.get(field_name)
    if not isinstance(value, int) or value < 0:
        raise RuntimeError(f"{field_name} must be a non-negative integer")
    return value


def _required_text(row: dict[str, object], field_name: str, max_length: int | None = None) -> str:
    """Extrait un texte obligatoire depuis une ligne de seed."""
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


def _json_string_list(row: dict[str, object], field_name: str) -> str:
    """Encode une liste de chaînes en JSON texte pour les colonnes éditoriales."""
    values = row.get(field_name)
    if not isinstance(values, list) or not values:
        raise RuntimeError(f"{field_name} must be a non-empty list")
    if not all(isinstance(value, str) and value.strip() for value in values):
        raise RuntimeError(f"{field_name} must only contain non-empty strings")
    return json.dumps(values, ensure_ascii=False)


def _create_typical_polarities_table() -> None:
    """Crée la table des polarités usuelles si nécessaire."""
    if not _table_exists(TYPICAL_POLARITIES_TABLE):
        op.create_table(
            TYPICAL_POLARITIES_TABLE,
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("name", sa.String(length=32), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name", name="uq_astral_typical_polarities_name"),
        )
    if not _index_exists(TYPICAL_POLARITIES_TABLE, "ix_astral_typical_polarities_name"):
        op.create_index(
            "ix_astral_typical_polarities_name",
            TYPICAL_POLARITIES_TABLE,
            ["name"],
            unique=False,
        )


def _create_speed_table() -> None:
    """Crée la table des vitesses relatives si nécessaire."""
    if not _table_exists(SPEED_TABLE):
        op.create_table(
            SPEED_TABLE,
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("name", sa.String(length=32), nullable=False),
            sa.Column("speed_rank", sa.Integer(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name", name="uq_astral_speed_name"),
        )
    if not _index_exists(SPEED_TABLE, "ix_astral_speed_name"):
        op.create_index("ix_astral_speed_name", SPEED_TABLE, ["name"], unique=False)


def _create_planet_definitions_table() -> None:
    """Crée la table des définitions structurelles de planètes si nécessaire."""
    if not _table_exists(PLANET_DEFINITIONS_TABLE):
        op.create_table(
            PLANET_DEFINITIONS_TABLE,
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("planet_id", sa.Integer(), nullable=False),
            sa.Column("object_type_id", sa.Integer(), nullable=False),
            sa.Column("astrological_role_id", sa.Integer(), nullable=False),
            sa.Column("calculation_type_id", sa.Integer(), nullable=False),
            sa.Column("speed_rank", sa.Integer(), nullable=False),
            sa.Column("speed_class_id", sa.Integer(), nullable=False),
            sa.Column("typical_polarity_id", sa.Integer(), nullable=False),
            sa.Column("is_physical_body", sa.Boolean(), nullable=False),
            sa.Column("is_luminary", sa.Boolean(), nullable=False),
            sa.Column("is_planet", sa.Boolean(), nullable=False),
            sa.Column("is_visible_to_naked_eye", sa.Boolean(), nullable=False),
            sa.Column("micro_note", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(
                ["planet_id"],
                ["astral_planets.id"],
                name="fk_astral_planet_definitions_planet_id",
            ),
            sa.ForeignKeyConstraint(
                ["object_type_id"],
                ["astral_object_types.id"],
                name="fk_astral_planet_definitions_object_type_id",
            ),
            sa.ForeignKeyConstraint(
                ["astrological_role_id"],
                ["astral_astrological_roles.id"],
                name="fk_astral_planet_definitions_astrological_role_id",
            ),
            sa.ForeignKeyConstraint(
                ["calculation_type_id"],
                ["astral_calculation_types.id"],
                name="fk_astral_planet_definitions_calculation_type_id",
            ),
            sa.ForeignKeyConstraint(
                ["speed_class_id"],
                ["astral_speed.id"],
                name="fk_astral_planet_definitions_speed_class_id",
            ),
            sa.ForeignKeyConstraint(
                ["typical_polarity_id"],
                ["astral_typical_polarities.id"],
                name="fk_astral_planet_definitions_typical_polarity_id",
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("planet_id", name="uq_astral_planet_definitions_planet_id"),
        )
    for index_name, columns in (
        ("ix_astral_planet_definitions_planet_id", ["planet_id"]),
        ("ix_astral_planet_definitions_object_type_id", ["object_type_id"]),
        ("ix_astral_planet_definitions_astrological_role_id", ["astrological_role_id"]),
        ("ix_astral_planet_definitions_calculation_type_id", ["calculation_type_id"]),
        ("ix_astral_planet_definitions_speed_class_id", ["speed_class_id"]),
        ("ix_astral_planet_definitions_typical_polarity_id", ["typical_polarity_id"]),
    ):
        if not _index_exists(PLANET_DEFINITIONS_TABLE, index_name):
            op.create_index(index_name, PLANET_DEFINITIONS_TABLE, columns, unique=False)


def _create_planet_interpretation_table() -> None:
    """Crée la table des profils éditoriaux planétaires si nécessaire."""
    if not _table_exists(PLANET_INTERPRETATION_TABLE):
        op.create_table(
            PLANET_INTERPRETATION_TABLE,
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("reference_version_id", sa.Integer(), nullable=False),
            sa.Column("planet_id", sa.Integer(), nullable=False),
            sa.Column("astral_system_id", sa.Integer(), nullable=False),
            sa.Column("language_id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=128), nullable=False),
            sa.Column("summary", sa.Text(), nullable=False),
            sa.Column("core_keywords_json", sa.Text(), nullable=False),
            sa.Column("shadow_keywords_json", sa.Text(), nullable=False),
            sa.Column("psychological_expression_json", sa.Text(), nullable=False),
            sa.Column("relational_expression_json", sa.Text(), nullable=False),
            sa.Column("vocational_expression_json", sa.Text(), nullable=False),
            sa.Column("spiritual_expression_json", sa.Text(), nullable=False),
            sa.Column("energetic_dynamics_json", sa.Text(), nullable=False),
            sa.Column("growth_patterns_json", sa.Text(), nullable=False),
            sa.Column("conflict_patterns_json", sa.Text(), nullable=False),
            sa.Column("archetypes_json", sa.Text(), nullable=False),
            sa.Column("dos_json", sa.Text(), nullable=False),
            sa.Column("donts_json", sa.Text(), nullable=False),
            sa.Column("prompt_hints_json", sa.Text(), nullable=False),
            sa.Column("micro_note", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(
                ["reference_version_id"],
                ["astral_reference_versions.id"],
                name="fk_astral_planet_interpretation_profiles_reference_version_id",
            ),
            sa.ForeignKeyConstraint(
                ["planet_id"],
                ["astral_planets.id"],
                name="fk_astral_planet_interpretation_profiles_planet_id",
            ),
            sa.ForeignKeyConstraint(
                ["astral_system_id"],
                ["astral_systems.id"],
                name="fk_astral_planet_interpretation_profiles_astral_system_id",
            ),
            sa.ForeignKeyConstraint(
                ["language_id"],
                ["languages.id"],
                name="fk_astral_planet_interpretation_profiles_language_id",
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "reference_version_id",
                "planet_id",
                "astral_system_id",
                "language_id",
                name="uq_astral_planet_interpretation_profiles_scope",
            ),
        )
    for index_name, columns in (
        (
            "ix_astral_planet_interpretation_profiles_reference_version_id",
            ["reference_version_id"],
        ),
        ("ix_astral_planet_interpretation_profiles_planet_id", ["planet_id"]),
        ("ix_astral_planet_interpretation_profiles_astral_system_id", ["astral_system_id"]),
        ("ix_astral_planet_interpretation_profiles_language_id", ["language_id"]),
    ):
        if not _index_exists(PLANET_INTERPRETATION_TABLE, index_name):
            op.create_index(index_name, PLANET_INTERPRETATION_TABLE, columns, unique=False)


def _seed_typical_polarities() -> None:
    """Insère les polarités usuelles sans écraser les lignes existantes."""
    connection = op.get_bind()
    for raw_row in _load_table_rows(
        "astral_typical_polarities.json",
        TYPICAL_POLARITIES_TABLE,
    ):
        row = {
            "id": _required_positive_int(raw_row, "id"),
            "name": _required_text(raw_row, "name", max_length=32),
        }
        connection.execute(
            sa.text(
                f"""
                INSERT INTO {TYPICAL_POLARITIES_TABLE} (id, name)
                SELECT :id, :name
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM {TYPICAL_POLARITIES_TABLE}
                    WHERE id = :id OR name = :name
                )
                """
            ),
            row,
        )


def _seed_speed() -> None:
    """Insère les classes de vitesse sans écraser les lignes existantes."""
    connection = op.get_bind()
    for raw_row in _load_table_rows("astral_speed.json", SPEED_TABLE):
        row = {
            "id": _required_positive_int(raw_row, "id"),
            "name": _required_text(raw_row, "name", max_length=32),
            "speed_rank": _optional_positive_int(raw_row, "speed_rank"),
        }
        connection.execute(
            sa.text(
                f"""
                INSERT INTO {SPEED_TABLE} (id, name, speed_rank)
                SELECT :id, :name, :speed_rank
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM {SPEED_TABLE}
                    WHERE id = :id OR name = :name
                )
                """
            ),
            row,
        )


def _required_bool(row: dict[str, object], field_name: str) -> bool:
    """Extrait un booléen obligatoire depuis une ligne de seed."""
    value = row.get(field_name)
    if not isinstance(value, bool):
        raise RuntimeError(f"{field_name} must be a boolean")
    return value


def _planet_definition_payload(raw_row: dict[str, object]) -> dict[str, object]:
    """Normalise une ligne JSON en payload SQL pour une définition planétaire."""
    return {
        "id": _required_positive_int(raw_row, "id"),
        "planet_id": _required_positive_int(raw_row, "planet_id"),
        "object_type_id": _required_positive_int(raw_row, "object_type_id"),
        "astrological_role_id": _required_positive_int(raw_row, "astrological_role_id"),
        "calculation_type_id": _required_positive_int(raw_row, "calculation_type_id"),
        "speed_rank": _required_non_negative_int(raw_row, "speed_rank"),
        "speed_class_id": _required_positive_int(raw_row, "speed_class_id"),
        "typical_polarity_id": _required_positive_int(raw_row, "typical_polarity_id"),
        "is_physical_body": _required_bool(raw_row, "is_physical_body"),
        "is_luminary": _required_bool(raw_row, "is_luminary"),
        "is_planet": _required_bool(raw_row, "is_planet"),
        "is_visible_to_naked_eye": _required_bool(raw_row, "is_visible_to_naked_eye"),
        "micro_note": _optional_text(raw_row, "micro_note"),
    }


def _seed_planet_definitions() -> None:
    """Remplace les définitions planétaires par la source JSON canonique."""
    connection = op.get_bind()
    connection.execute(sa.text(f"DELETE FROM {PLANET_DEFINITIONS_TABLE}"))
    columns = (
        "id",
        "planet_id",
        "object_type_id",
        "astrological_role_id",
        "calculation_type_id",
        "speed_rank",
        "speed_class_id",
        "typical_polarity_id",
        "is_physical_body",
        "is_luminary",
        "is_planet",
        "is_visible_to_naked_eye",
        "micro_note",
    )
    column_sql = ", ".join(columns)
    value_sql = ", ".join(f":{column}" for column in columns)
    for raw_row in _load_table_rows("astral_planet_definitions.json", PLANET_DEFINITIONS_TABLE):
        row = _planet_definition_payload(raw_row)
        connection.execute(
            sa.text(
                f"""
                INSERT INTO {PLANET_DEFINITIONS_TABLE} ({column_sql})
                VALUES ({value_sql})
                """
            ),
            row,
        )


def _planet_interpretation_payload(raw_row: dict[str, object]) -> dict[str, object]:
    """Normalise une ligne JSON en payload SQL pour un profil planétaire."""
    return {
        "id": _required_positive_int(raw_row, "id"),
        "reference_version_id": _required_positive_int(raw_row, "reference_version_id"),
        "planet_id": _required_positive_int(raw_row, "planet_id"),
        "astral_system_id": _required_positive_int(raw_row, "astral_system_id"),
        "language_id": _required_positive_int(raw_row, "language_id"),
        "title": _required_text(raw_row, "title", max_length=128),
        "summary": _required_text(raw_row, "summary"),
        "micro_note": _optional_text(raw_row, "micro_note"),
        **{
            field_name: _json_string_list(raw_row, field_name)
            for field_name in PLANET_INTERPRETATION_JSON_FIELDS
        },
    }


def _seed_planet_interpretation_profiles() -> None:
    """Remplace les profils planétaires par la source JSON canonique."""
    connection = op.get_bind()
    connection.execute(sa.text(f"DELETE FROM {PLANET_INTERPRETATION_TABLE}"))
    columns = (
        "id",
        "reference_version_id",
        "planet_id",
        "astral_system_id",
        "language_id",
        "title",
        "summary",
        *PLANET_INTERPRETATION_JSON_FIELDS,
        "micro_note",
    )
    column_sql = ", ".join(columns)
    value_sql = ", ".join(f":{column}" for column in columns)
    for raw_row in _load_table_rows(
        "astral_planet_interpretation_profiles.json",
        PLANET_INTERPRETATION_TABLE,
    ):
        row = _planet_interpretation_payload(raw_row)
        connection.execute(
            sa.text(
                f"""
                INSERT INTO {PLANET_INTERPRETATION_TABLE} ({column_sql})
                VALUES ({value_sql})
                """
            ),
            row,
        )


def upgrade() -> None:
    """Crée les tables planétaires décrites et les alimente depuis `data`."""
    _create_typical_polarities_table()
    _seed_typical_polarities()
    _create_speed_table()
    _seed_speed()
    _create_planet_definitions_table()
    _seed_planet_definitions()
    _create_planet_interpretation_table()
    _seed_planet_interpretation_profiles()


def downgrade() -> None:
    """Supprime les tables planétaires créées par cette migration."""
    for index_name in (
        "ix_astral_planet_interpretation_profiles_language_id",
        "ix_astral_planet_interpretation_profiles_astral_system_id",
        "ix_astral_planet_interpretation_profiles_planet_id",
        "ix_astral_planet_interpretation_profiles_reference_version_id",
    ):
        if _index_exists(PLANET_INTERPRETATION_TABLE, index_name):
            op.drop_index(index_name, table_name=PLANET_INTERPRETATION_TABLE)
    if _table_exists(PLANET_INTERPRETATION_TABLE):
        op.drop_table(PLANET_INTERPRETATION_TABLE)
    for index_name in (
        "ix_astral_planet_definitions_typical_polarity_id",
        "ix_astral_planet_definitions_speed_class_id",
        "ix_astral_planet_definitions_calculation_type_id",
        "ix_astral_planet_definitions_astrological_role_id",
        "ix_astral_planet_definitions_object_type_id",
        "ix_astral_planet_definitions_planet_id",
    ):
        if _index_exists(PLANET_DEFINITIONS_TABLE, index_name):
            op.drop_index(index_name, table_name=PLANET_DEFINITIONS_TABLE)
    if _table_exists(PLANET_DEFINITIONS_TABLE):
        op.drop_table(PLANET_DEFINITIONS_TABLE)
    if _index_exists(SPEED_TABLE, "ix_astral_speed_name"):
        op.drop_index("ix_astral_speed_name", table_name=SPEED_TABLE)
    if _table_exists(SPEED_TABLE):
        op.drop_table(SPEED_TABLE)
    if _index_exists(TYPICAL_POLARITIES_TABLE, "ix_astral_typical_polarities_name"):
        op.drop_index(
            "ix_astral_typical_polarities_name",
            table_name=TYPICAL_POLARITIES_TABLE,
        )
    if _table_exists(TYPICAL_POLARITIES_TABLE):
        op.drop_table(TYPICAL_POLARITIES_TABLE)
