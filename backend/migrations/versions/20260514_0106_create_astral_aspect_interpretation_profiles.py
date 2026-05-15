"""Cree les profils editoriaux d'interpretation des aspects.

Revision ID: 20260514_0106
Revises: 20260514_0105
Create Date: 2026-05-14
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260514_0106"
down_revision: Union[str, Sequence[str], None] = "20260514_0105"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "astral_aspect_interpretation_profiles"
INDEX_SPECS = (
    (
        "ix_astral_aspect_interpretation_profiles_reference_version_id",
        ["reference_version_id"],
    ),
    ("ix_astral_aspect_interpretation_profiles_aspect_id", ["aspect_id"]),
    ("ix_astral_aspect_interpretation_profiles_astral_system_id", ["astral_system_id"]),
)
EXPECTED_COLUMNS = {
    "id",
    "reference_version_id",
    "aspect_id",
    "astral_system_id",
    "language",
    "title",
    "summary",
    "core_keywords_json",
    "shadow_keywords_json",
    "psychological_keywords_json",
    "relationship_keywords_json",
    "career_keywords_json",
    "spiritual_keywords_json",
    "energetic_dynamics_json",
    "growth_patterns_json",
    "conflict_patterns_json",
    "archetypes_json",
    "dos_json",
    "donts_json",
    "prompt_hints_json",
    "micro_note",
}
EXPECTED_UNIQUE_COLUMNS = (
    "reference_version_id",
    "aspect_id",
    "astral_system_id",
    "language",
)
EXPECTED_FOREIGN_KEYS = {
    ("reference_version_id",): "astral_reference_versions",
    ("aspect_id",): "astral_aspects",
    ("astral_system_id",): "astral_systems",
}
JSON_FIELD_NAMES = (
    "core_keywords_json",
    "shadow_keywords_json",
    "psychological_keywords_json",
    "relationship_keywords_json",
    "career_keywords_json",
    "spiritual_keywords_json",
    "energetic_dynamics_json",
    "growth_patterns_json",
    "conflict_patterns_json",
    "archetypes_json",
    "dos_json",
    "donts_json",
    "prompt_hints_json",
)


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe dans le schéma courant."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _index_names(table_name: str) -> set[str]:
    """Retourne les noms d'index d'une table."""
    return {str(index["name"]) for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def _create_index_if_missing(index_name: str, columns: list[str]) -> None:
    """Crée un index attendu sans doublonner une base reprise."""
    if index_name not in _index_names(TABLE_NAME):
        op.create_index(index_name, TABLE_NAME, columns, unique=False)


def _drop_index_if_exists(index_name: str) -> None:
    """Supprime un index uniquement s'il est présent."""
    if _table_exists(TABLE_NAME) and index_name in _index_names(TABLE_NAME):
        op.drop_index(index_name, table_name=TABLE_NAME)


def _validate_existing_table() -> None:
    """Refuse de valider une table préexistante partielle ou divergente."""
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns(TABLE_NAME)}
    if columns != EXPECTED_COLUMNS:
        raise RuntimeError(f"{TABLE_NAME} exists with unexpected columns")

    unique_columns = {
        tuple(constraint["column_names"])
        for constraint in inspector.get_unique_constraints(TABLE_NAME)
    }
    if EXPECTED_UNIQUE_COLUMNS not in unique_columns:
        raise RuntimeError(f"{TABLE_NAME} exists without expected unique constraint")

    foreign_keys = {
        tuple(foreign_key["constrained_columns"]): foreign_key["referred_table"]
        for foreign_key in inspector.get_foreign_keys(TABLE_NAME)
    }
    if foreign_keys != EXPECTED_FOREIGN_KEYS:
        raise RuntimeError(f"{TABLE_NAME} exists with unexpected foreign keys")


def _research_path(file_name: str) -> Path:
    """Construit le chemin vers les JSON de référence astrologique."""
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


def _load_profiles() -> list[dict[str, object]]:
    """Charge les profils éditoriaux des aspects depuis la source documentaire."""
    with _research_path("astral_aspect_interpretation_profiles.json").open(
        encoding="utf-8"
    ) as stream:
        raw = json.load(stream)
    if not isinstance(raw, dict) or raw.get("table") != TABLE_NAME:
        raise RuntimeError("astral_aspect_interpretation_profiles.json targets an unexpected table")
    profiles = raw.get("profiles")
    if not isinstance(profiles, list) or len(profiles) != 20:
        raise RuntimeError("astral_aspect_interpretation_profiles.json must contain 20 profiles")
    return profiles


def _ids_by_code(table_name: str) -> dict[str, int]:
    """Retourne le mapping code -> id pour une table de référence."""
    rows = op.get_bind().execute(sa.text(f"SELECT id, code FROM {table_name}")).mappings()
    return {str(row["code"]): int(row["id"]) for row in rows}


def _system_ids_by_name() -> dict[str, int]:
    """Retourne le mapping name -> id des systèmes astrologiques."""
    rows = op.get_bind().execute(sa.text("SELECT id, name FROM astral_systems")).mappings()
    return {str(row["name"]): int(row["id"]) for row in rows}


def _reference_version_ids() -> list[int]:
    """Retourne les versions de référence existantes à backfiller."""
    rows = op.get_bind().execute(sa.text("SELECT id FROM astral_reference_versions")).all()
    return [int(row[0]) for row in rows]


def _encode_json_list(profile: dict[str, object], field_name: str) -> str:
    """Encode une liste JSON du profil source pour stockage texte."""
    values = profile.get(field_name)
    if not isinstance(values, list) or not values:
        raise RuntimeError(f"missing {field_name} for aspect interpretation profile")
    return json.dumps([str(value) for value in values], ensure_ascii=False)


def _seed_profiles() -> None:
    """Insère ou met à jour les profils éditoriaux pour chaque version existante."""
    version_ids = _reference_version_ids()
    if not version_ids:
        return
    aspect_ids = _ids_by_code("astral_aspects")
    system_ids = _system_ids_by_name()
    profiles_table = sa.table(
        TABLE_NAME,
        sa.column("id", sa.Integer()),
        sa.column("reference_version_id", sa.Integer()),
        sa.column("aspect_id", sa.Integer()),
        sa.column("astral_system_id", sa.Integer()),
        sa.column("language", sa.String()),
        sa.column("title", sa.String()),
        sa.column("summary", sa.Text()),
        sa.column("core_keywords_json", sa.Text()),
        sa.column("shadow_keywords_json", sa.Text()),
        sa.column("psychological_keywords_json", sa.Text()),
        sa.column("relationship_keywords_json", sa.Text()),
        sa.column("career_keywords_json", sa.Text()),
        sa.column("spiritual_keywords_json", sa.Text()),
        sa.column("energetic_dynamics_json", sa.Text()),
        sa.column("growth_patterns_json", sa.Text()),
        sa.column("conflict_patterns_json", sa.Text()),
        sa.column("archetypes_json", sa.Text()),
        sa.column("dos_json", sa.Text()),
        sa.column("donts_json", sa.Text()),
        sa.column("prompt_hints_json", sa.Text()),
        sa.column("micro_note", sa.Text()),
    )
    connection = op.get_bind()
    for version_id in version_ids:
        for profile in _load_profiles():
            aspect_code = str(profile["aspect_code"])
            system_code = str(profile["astral_system_code"])
            payload = {
                "reference_version_id": version_id,
                "aspect_id": aspect_ids[aspect_code],
                "astral_system_id": system_ids[system_code],
                "language": str(profile.get("language") or "en"),
                "title": str(profile["title"]),
                "summary": str(profile["summary"]),
                "micro_note": str(profile["micro_note"]),
                **{
                    field_name: _encode_json_list(profile, field_name)
                    for field_name in JSON_FIELD_NAMES
                },
            }
            existing_id = connection.execute(
                sa.select(profiles_table.c.id).where(
                    profiles_table.c.reference_version_id == payload["reference_version_id"],
                    profiles_table.c.aspect_id == payload["aspect_id"],
                    profiles_table.c.astral_system_id == payload["astral_system_id"],
                    profiles_table.c.language == payload["language"],
                )
            ).scalar_one_or_none()
            if existing_id is None:
                connection.execute(sa.insert(profiles_table).values(**payload))
                continue
            connection.execute(
                sa.update(profiles_table)
                .where(profiles_table.c.id == existing_id)
                .values(
                    title=payload["title"],
                    summary=payload["summary"],
                    micro_note=payload["micro_note"],
                    **{field_name: payload[field_name] for field_name in JSON_FIELD_NAMES},
                )
            )


def upgrade() -> None:
    """Ajoute le referentiel editorial versionne des aspects."""
    if _table_exists(TABLE_NAME):
        _validate_existing_table()
        for index_name, columns in INDEX_SPECS:
            _create_index_if_missing(index_name, columns)
        _seed_profiles()
        return

    op.create_table(
        TABLE_NAME,
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("reference_version_id", sa.Integer(), nullable=False),
        sa.Column("aspect_id", sa.Integer(), nullable=False),
        sa.Column("astral_system_id", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("core_keywords_json", sa.Text(), nullable=True),
        sa.Column("shadow_keywords_json", sa.Text(), nullable=True),
        sa.Column("psychological_keywords_json", sa.Text(), nullable=True),
        sa.Column("relationship_keywords_json", sa.Text(), nullable=True),
        sa.Column("career_keywords_json", sa.Text(), nullable=True),
        sa.Column("spiritual_keywords_json", sa.Text(), nullable=True),
        sa.Column("energetic_dynamics_json", sa.Text(), nullable=True),
        sa.Column("growth_patterns_json", sa.Text(), nullable=True),
        sa.Column("conflict_patterns_json", sa.Text(), nullable=True),
        sa.Column("archetypes_json", sa.Text(), nullable=True),
        sa.Column("dos_json", sa.Text(), nullable=True),
        sa.Column("donts_json", sa.Text(), nullable=True),
        sa.Column("prompt_hints_json", sa.Text(), nullable=True),
        sa.Column("micro_note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["reference_version_id"],
            ["astral_reference_versions.id"],
            name="fk_astral_aspect_interpretation_profiles_reference_version_id",
        ),
        sa.ForeignKeyConstraint(
            ["aspect_id"],
            ["astral_aspects.id"],
            name="fk_astral_aspect_interpretation_profiles_aspect_id",
        ),
        sa.ForeignKeyConstraint(
            ["astral_system_id"],
            ["astral_systems.id"],
            name="fk_astral_aspect_interpretation_profiles_astral_system_id",
        ),
        sa.UniqueConstraint(
            "reference_version_id",
            "aspect_id",
            "astral_system_id",
            "language",
            name="uq_astral_aspect_interpretation_profiles_version_aspect_system_language",
        ),
    )
    for index_name, columns in INDEX_SPECS:
        _create_index_if_missing(index_name, columns)
    _seed_profiles()


def downgrade() -> None:
    """Supprime le referentiel editorial versionne des aspects."""
    for index_name, _columns in reversed(INDEX_SPECS):
        _drop_index_if_exists(index_name)
    if _table_exists(TABLE_NAME):
        op.drop_table(TABLE_NAME)
