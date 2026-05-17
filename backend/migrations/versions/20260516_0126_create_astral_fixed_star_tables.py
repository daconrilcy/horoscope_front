"""Crée et alimente les référentiels des étoiles fixes.

Revision ID: 20260516_0126
Revises: 20260516_0125
Create Date: 2026-05-16
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260516_0126"
down_revision: Union[str, Sequence[str], None] = "20260516_0125"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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


def _source_path(*parts: str) -> Path:
    """Retourne le chemin d'un seed JSON canonique."""
    return Path(__file__).resolve().parents[3] / "docs" / "db_seeder" / "astrology" / Path(*parts)


def _load_data_rows(file_name: str, expected_name: str) -> list[dict[str, Any]]:
    """Charge une liste `data` depuis un seed JSON."""
    with _source_path(file_name).open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if not isinstance(raw, dict) or raw.get("name") != expected_name:
        raise RuntimeError(f"{expected_name} seed targets an unexpected table")
    rows = raw.get("data")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError(f"{expected_name} seed must contain a non-empty data list")
    return [dict(row) for row in rows]


def _load_keyword_translation_rows() -> list[dict[str, Any]]:
    """Charge les traductions des mots-clés d'étoiles fixes."""
    with _source_path("translation", "astral_fixed_star_keyword_translations.json").open(
        encoding="utf-8"
    ) as stream:
        raw = json.load(stream)
    if not isinstance(raw, dict) or raw.get("name") != "astral_fixed_star_keyword_translations":
        raise RuntimeError("astral_fixed_star_keyword_translations targets an unexpected table")
    data = raw.get("data")
    rows = data.get("keywords") if isinstance(data, dict) else None
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("fixed star keyword translations must contain data.keywords rows")
    return [dict(row) for row in rows]


def _ensure_index(table_name: str, index_name: str, columns: list[str]) -> None:
    """Crée un index non unique s'il manque."""
    if not _index_exists(table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=False)


def _ensure_schema() -> None:
    """Crée les tables dans l'ordre de dépendance demandé."""
    if not _table_exists("astral_fixed_stars"):
        op.create_table(
            "astral_fixed_stars",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("key", sa.String(length=64), nullable=False),
            sa.Column("display_name", sa.String(length=128), nullable=False),
            sa.UniqueConstraint("key", name="uq_astral_fixed_stars_key"),
        )
    _ensure_index("astral_fixed_stars", "ix_astral_fixed_stars_key", ["key"])

    if not _table_exists("astral_fixed_star_keywords"):
        op.create_table(
            "astral_fixed_star_keywords",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("keywords_json", sa.Text(), nullable=False),
        )

    if not _table_exists("astral_fixed_star_keyword_translations"):
        op.create_table(
            "astral_fixed_star_keyword_translations",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("astral_fixed_star_keywords_id", sa.Integer(), nullable=False),
            sa.Column("language_id", sa.Integer(), nullable=False),
            sa.Column("keywords_json", sa.Text(), nullable=False),
            sa.ForeignKeyConstraint(
                ["astral_fixed_star_keywords_id"],
                ["astral_fixed_star_keywords.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(["language_id"], ["languages.id"]),
            sa.UniqueConstraint(
                "astral_fixed_star_keywords_id",
                "language_id",
                name="uq_astral_fixed_star_keyword_translations_scope",
            ),
        )
    _ensure_index(
        "astral_fixed_star_keyword_translations",
        "ix_astral_fixed_star_keyword_translations_keywords_id",
        ["astral_fixed_star_keywords_id"],
    )
    _ensure_index(
        "astral_fixed_star_keyword_translations",
        "ix_astral_fixed_star_keyword_translations_language_id",
        ["language_id"],
    )

    if not _table_exists("astral_fixed_star_definitions"):
        op.create_table(
            "astral_fixed_star_definitions",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("fixed_star_id", sa.Integer(), nullable=False),
            sa.Column("constellation_id", sa.Integer(), nullable=False),
            sa.Column("zodiacal_reference_system_id", sa.Integer(), nullable=False),
            sa.Column("reference_epoch_id", sa.Integer(), nullable=False),
            sa.Column("ecliptic_longitude_deg", sa.Float(), nullable=False),
            sa.Column("zodiac_sign_id", sa.Integer(), nullable=False),
            sa.Column("zodiac_degree", sa.Float(), nullable=False),
            sa.Column("declination_deg", sa.Float(), nullable=True),
            sa.Column("right_ascension_deg", sa.Float(), nullable=True),
            sa.Column("visual_magnitude", sa.Float(), nullable=True),
            sa.Column("astral_fixed_star_keywords_id", sa.Integer(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("source_id", sa.Integer(), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(["fixed_star_id"], ["astral_fixed_stars.id"]),
            sa.ForeignKeyConstraint(["constellation_id"], ["astral_constellations.id"]),
            sa.ForeignKeyConstraint(
                ["zodiacal_reference_system_id"],
                ["astral_zodiacal_reference_systems.id"],
            ),
            sa.ForeignKeyConstraint(["reference_epoch_id"], ["astral_reference_epochs.id"]),
            sa.ForeignKeyConstraint(["zodiac_sign_id"], ["astral_signs.id"]),
            sa.ForeignKeyConstraint(
                ["astral_fixed_star_keywords_id"],
                ["astral_fixed_star_keywords.id"],
            ),
            sa.ForeignKeyConstraint(["source_id"], ["astral_reference_sources.id"]),
            sa.UniqueConstraint(
                "fixed_star_id",
                name="uq_astral_fixed_star_definitions_fixed_star_id",
            ),
        )
    for column in (
        "fixed_star_id",
        "constellation_id",
        "zodiacal_reference_system_id",
        "reference_epoch_id",
        "zodiac_sign_id",
        "astral_fixed_star_keywords_id",
        "source_id",
    ):
        _ensure_index(
            "astral_fixed_star_definitions",
            f"ix_astral_fixed_star_definitions_{column}",
            [column],
        )


def _upsert_fixed_stars() -> None:
    """Seed les étoiles fixes."""
    connection = op.get_bind()
    for row in _load_data_rows("astral_fixed_stars.json", "astral_fixed_stars"):
        params = {
            "id": int(row["id"]),
            "key": str(row["key"]),
            "display_name": str(row["display_name"]),
        }
        existing = connection.execute(
            sa.text("SELECT id FROM astral_fixed_stars WHERE id = :id OR key = :key"),
            params,
        ).first()
        if existing is None:
            connection.execute(
                sa.text(
                    """
                    INSERT INTO astral_fixed_stars (id, key, display_name)
                    VALUES (:id, :key, :display_name)
                    """
                ),
                params,
            )
        else:
            connection.execute(
                sa.text(
                    """
                    UPDATE astral_fixed_stars
                    SET key = :key, display_name = :display_name
                    WHERE id = :id OR key = :key
                    """
                ),
                params,
            )


def _upsert_keywords() -> None:
    """Seed les groupes de mots-clés."""
    connection = op.get_bind()
    for row in _load_data_rows("astral_fixed_star_keywords.json", "astral_fixed_star_keywords"):
        params = {
            "id": int(row["id"]),
            "keywords_json": json.dumps(
                list(row["keywords_json"]),
                ensure_ascii=False,
                separators=(",", ":"),
            ),
        }
        existing = connection.execute(
            sa.text("SELECT id FROM astral_fixed_star_keywords WHERE id = :id"),
            params,
        ).first()
        if existing is None:
            connection.execute(
                sa.text(
                    """
                    INSERT INTO astral_fixed_star_keywords (id, keywords_json)
                    VALUES (:id, :keywords_json)
                    """
                ),
                params,
            )
        else:
            connection.execute(
                sa.text(
                    """
                    UPDATE astral_fixed_star_keywords
                    SET keywords_json = :keywords_json
                    WHERE id = :id
                    """
                ),
                params,
            )


def _upsert_keyword_translations() -> None:
    """Seed les traductions des groupes de mots-clés."""
    connection = op.get_bind()
    language_ids = dict(connection.execute(sa.text("SELECT code, id FROM languages")).all())
    for row in _load_keyword_translation_rows():
        keyword_id = int(row["astral_fixed_star_keywords_id"])
        translations = row.get("translations")
        if not isinstance(translations, dict):
            raise RuntimeError("fixed star keyword translation row must contain translations")
        for locale, translated_values in translations.items():
            if not isinstance(translated_values, dict):
                raise RuntimeError("fixed star keyword translation values must be objects")
            language_id = language_ids.get(str(locale))
            if language_id is None:
                raise RuntimeError(f"unknown translation locale: {locale}")
            params = {
                "astral_fixed_star_keywords_id": keyword_id,
                "language_id": int(language_id),
                "keywords_json": json.dumps(
                    list(translated_values["keywords_json"]),
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
            }
            existing = connection.execute(
                sa.text(
                    """
                    SELECT id
                    FROM astral_fixed_star_keyword_translations
                    WHERE astral_fixed_star_keywords_id = :astral_fixed_star_keywords_id
                        AND language_id = :language_id
                    """
                ),
                params,
            ).first()
            if existing is None:
                connection.execute(
                    sa.text(
                        """
                        INSERT INTO astral_fixed_star_keyword_translations (
                            astral_fixed_star_keywords_id, language_id, keywords_json
                        )
                        VALUES (
                            :astral_fixed_star_keywords_id, :language_id, :keywords_json
                        )
                        """
                    ),
                    params,
                )
            else:
                connection.execute(
                    sa.text(
                        """
                        UPDATE astral_fixed_star_keyword_translations
                        SET keywords_json = :keywords_json
                        WHERE astral_fixed_star_keywords_id = :astral_fixed_star_keywords_id
                            AND language_id = :language_id
                        """
                    ),
                    params,
                )


def _upsert_definitions() -> None:
    """Seed les définitions des étoiles fixes."""
    connection = op.get_bind()
    for row in _load_data_rows(
        "astral_fixed_star_definitions.json",
        "astral_fixed_star_definitions",
    ):
        params = {
            "id": int(row["id"]),
            "fixed_star_id": int(row["fixed_star_id"]),
            "constellation_id": int(row["constellation_id"]),
            "zodiacal_reference_system_id": int(row["zodiacal_reference_system_id"]),
            "reference_epoch_id": int(row["reference_epoch_id"]),
            "ecliptic_longitude_deg": float(row["ecliptic_longitude_deg"]),
            "zodiac_sign_id": int(row["zodiac_sign_id"]),
            "zodiac_degree": float(row["zodiac_degree"]),
            "declination_deg": None
            if row.get("declination_deg") is None
            else float(row["declination_deg"]),
            "right_ascension_deg": None
            if row.get("right_ascension_deg") is None
            else float(row["right_ascension_deg"]),
            "visual_magnitude": None
            if row.get("visual_magnitude") is None
            else float(row["visual_magnitude"]),
            "astral_fixed_star_keywords_id": int(row["astral_fixed_star_keywords_id"]),
            "is_active": bool(row["is_active"]),
            "source_id": int(row["source_id"]),
            "notes": None if row.get("notes") is None else str(row["notes"]),
        }
        existing = connection.execute(
            sa.text(
                """
                SELECT id
                FROM astral_fixed_star_definitions
                WHERE id = :id OR fixed_star_id = :fixed_star_id
                """
            ),
            params,
        ).first()
        if existing is None:
            connection.execute(
                sa.text(
                    """
                    INSERT INTO astral_fixed_star_definitions (
                        id, fixed_star_id, constellation_id, zodiacal_reference_system_id,
                        reference_epoch_id, ecliptic_longitude_deg, zodiac_sign_id,
                        zodiac_degree, declination_deg, right_ascension_deg, visual_magnitude,
                        astral_fixed_star_keywords_id, is_active, source_id, notes
                    )
                    VALUES (
                        :id, :fixed_star_id, :constellation_id,
                        :zodiacal_reference_system_id, :reference_epoch_id,
                        :ecliptic_longitude_deg, :zodiac_sign_id, :zodiac_degree,
                        :declination_deg, :right_ascension_deg, :visual_magnitude,
                        :astral_fixed_star_keywords_id, :is_active, :source_id, :notes
                    )
                    """
                ),
                params,
            )
        else:
            connection.execute(
                sa.text(
                    """
                    UPDATE astral_fixed_star_definitions
                    SET constellation_id = :constellation_id,
                        zodiacal_reference_system_id = :zodiacal_reference_system_id,
                        reference_epoch_id = :reference_epoch_id,
                        ecliptic_longitude_deg = :ecliptic_longitude_deg,
                        zodiac_sign_id = :zodiac_sign_id,
                        zodiac_degree = :zodiac_degree,
                        declination_deg = :declination_deg,
                        right_ascension_deg = :right_ascension_deg,
                        visual_magnitude = :visual_magnitude,
                        astral_fixed_star_keywords_id = :astral_fixed_star_keywords_id,
                        is_active = :is_active,
                        source_id = :source_id,
                        notes = :notes
                    WHERE id = :id OR fixed_star_id = :fixed_star_id
                    """
                ),
                params,
            )


def upgrade() -> None:
    """Crée et seed les tables des étoiles fixes."""
    _ensure_schema()
    _upsert_fixed_stars()
    _upsert_keywords()
    _upsert_keyword_translations()
    _upsert_definitions()


def downgrade() -> None:
    """Supprime les tables des étoiles fixes."""
    for table_name in (
        "astral_fixed_star_definitions",
        "astral_fixed_star_keyword_translations",
        "astral_fixed_star_keywords",
        "astral_fixed_stars",
    ):
        if _table_exists(table_name):
            op.drop_table(table_name)
