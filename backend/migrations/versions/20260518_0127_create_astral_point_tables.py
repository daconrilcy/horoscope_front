"""Crée les tables des points astrologiques calculés.

Revision ID: 20260518_0127
Revises: 20260516_0126
Create Date: 2026-05-18
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260518_0127"
down_revision: Union[str, Sequence[str], None] = "20260516_0126"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    """Indique si la table existe déjà dans le schéma courant."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _index_exists(table_name: str, index_name: str) -> bool:
    """Indique si un index existe déjà sur la table."""
    if not _table_exists(table_name):
        return False
    return index_name in {
        str(index["name"]) for index in sa.inspect(op.get_bind()).get_indexes(table_name)
    }


def _ensure_index(table_name: str, index_name: str, columns: list[str]) -> None:
    """Crée un index non unique s'il manque."""
    if not _index_exists(table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=False)


def upgrade() -> None:
    """Crée les tables stables des points astrologiques et de leurs profils."""
    if not _table_exists("astral_point_families"):
        op.create_table(
            "astral_point_families",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("code", sa.String(length=64), nullable=False),
            sa.Column("display_name", sa.String(length=128), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.UniqueConstraint("code", name="uq_astral_point_families_code"),
        )
    _ensure_index("astral_point_families", "ix_astral_point_families_code", ["code"])

    if not _table_exists("astral_points"):
        op.create_table(
            "astral_points",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("code", sa.String(length=64), nullable=False),
            sa.Column("display_name", sa.String(length=128), nullable=False),
            sa.Column("point_family", sa.String(length=64), nullable=False),
            sa.Column("astronomical_type", sa.String(length=64), nullable=False),
            sa.Column("is_physical_body", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("description", sa.Text(), nullable=False),
            sa.ForeignKeyConstraint(["point_family"], ["astral_point_families.code"]),
            sa.UniqueConstraint("code", name="uq_astral_points_code"),
        )
    _ensure_index("astral_points", "ix_astral_points_code", ["code"])
    _ensure_index("astral_points", "ix_astral_points_point_family", ["point_family"])

    if not _table_exists("astral_point_calculation_variants"):
        op.create_table(
            "astral_point_calculation_variants",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("astral_point_code", sa.String(length=64), nullable=False),
            sa.Column("variant_code", sa.String(length=32), nullable=False),
            sa.Column("display_name", sa.String(length=128), nullable=False),
            sa.Column("calculation_mode", sa.String(length=64), nullable=False),
            sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("description", sa.Text(), nullable=False),
            sa.ForeignKeyConstraint(["astral_point_code"], ["astral_points.code"]),
            sa.UniqueConstraint(
                "astral_point_code",
                "variant_code",
                name="uq_astral_point_calculation_variants_scope",
            ),
        )
    _ensure_index(
        "astral_point_calculation_variants",
        "ix_astral_point_calculation_variants_astral_point_code",
        ["astral_point_code"],
    )
    _ensure_index(
        "astral_point_calculation_variants",
        "ix_astral_point_calculation_variants_variant_code",
        ["variant_code"],
    )

    if not _table_exists("astral_point_aliases"):
        op.create_table(
            "astral_point_aliases",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("astral_point_code", sa.String(length=64), nullable=False),
            sa.Column("variant_code", sa.String(length=32), nullable=True),
            sa.Column("alias", sa.String(length=128), nullable=False),
            sa.Column("language_id", sa.Integer(), nullable=False),
            sa.Column("source", sa.String(length=64), nullable=False),
            sa.Column("engine_key", sa.String(length=64), nullable=True),
            sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.ForeignKeyConstraint(["astral_point_code"], ["astral_points.code"]),
            sa.ForeignKeyConstraint(["language_id"], ["languages.id"]),
            sa.ForeignKeyConstraint(
                ["astral_point_code", "variant_code"],
                [
                    "astral_point_calculation_variants.astral_point_code",
                    "astral_point_calculation_variants.variant_code",
                ],
            ),
            sa.UniqueConstraint(
                "astral_point_code",
                "variant_code",
                "alias",
                "language_id",
                "source",
                name="uq_astral_point_aliases_scope",
            ),
        )
    _ensure_index(
        "astral_point_aliases", "ix_astral_point_aliases_astral_point_code", ["astral_point_code"]
    )
    _ensure_index("astral_point_aliases", "ix_astral_point_aliases_variant_code", ["variant_code"])
    _ensure_index("astral_point_aliases", "ix_astral_point_aliases_language_id", ["language_id"])

    if not _table_exists("astral_point_interpretation_keywords"):
        op.create_table(
            "astral_point_interpretation_keywords",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("core_keywords_json", sa.Text(), nullable=False),
            sa.Column("shadow_keywords_json", sa.Text(), nullable=False),
            sa.Column("psychological_keywords_json", sa.Text(), nullable=False),
            sa.Column("spiritual_keywords_json", sa.Text(), nullable=False),
            sa.Column("relationship_keywords_json", sa.Text(), nullable=False),
            sa.Column("career_keywords_json", sa.Text(), nullable=False),
        )

    if not _table_exists("astral_point_interpretation_profiles"):
        op.create_table(
            "astral_point_interpretation_profiles",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("astral_point_code", sa.String(length=64), nullable=False),
            sa.Column("variant_code", sa.String(length=32), nullable=True),
            sa.Column("keyword_set_id", sa.Integer(), nullable=False),
            sa.Column("language_id", sa.Integer(), nullable=False),
            sa.Column("tradition", sa.String(length=64), nullable=False),
            sa.Column("title", sa.String(length=128), nullable=False),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("micro_note", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(["astral_point_code"], ["astral_points.code"]),
            sa.ForeignKeyConstraint(
                ["keyword_set_id"],
                ["astral_point_interpretation_keywords.id"],
            ),
            sa.ForeignKeyConstraint(["language_id"], ["languages.id"]),
            sa.ForeignKeyConstraint(
                ["astral_point_code", "variant_code"],
                [
                    "astral_point_calculation_variants.astral_point_code",
                    "astral_point_calculation_variants.variant_code",
                ],
            ),
            sa.UniqueConstraint(
                "astral_point_code",
                "variant_code",
                "language_id",
                "tradition",
                name="uq_astral_point_interpretation_profiles_scope",
            ),
        )
    _ensure_index(
        "astral_point_interpretation_profiles",
        "ix_astral_point_interpretation_profiles_astral_point_code",
        ["astral_point_code"],
    )
    _ensure_index(
        "astral_point_interpretation_profiles",
        "ix_astral_point_interpretation_profiles_variant_code",
        ["variant_code"],
    )
    _ensure_index(
        "astral_point_interpretation_profiles",
        "ix_astral_point_interpretation_profiles_keyword_set_id",
        ["keyword_set_id"],
    )
    _ensure_index(
        "astral_point_interpretation_profiles",
        "ix_astral_point_interpretation_profiles_language_id",
        ["language_id"],
    )

    if not _table_exists("astral_point_interpretation_keyword_translations"):
        op.create_table(
            "astral_point_interpretation_keyword_translations",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("keyword_set_id", sa.Integer(), nullable=False),
            sa.Column("language_id", sa.Integer(), nullable=False),
            sa.Column("core_keywords_json", sa.Text(), nullable=False),
            sa.Column("shadow_keywords_json", sa.Text(), nullable=False),
            sa.Column("psychological_keywords_json", sa.Text(), nullable=False),
            sa.Column("spiritual_keywords_json", sa.Text(), nullable=False),
            sa.Column("relationship_keywords_json", sa.Text(), nullable=False),
            sa.Column("career_keywords_json", sa.Text(), nullable=False),
            sa.ForeignKeyConstraint(
                ["keyword_set_id"],
                ["astral_point_interpretation_keywords.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(["language_id"], ["languages.id"]),
            sa.UniqueConstraint(
                "keyword_set_id",
                "language_id",
                name="uq_astral_point_interpretation_keyword_translations_scope",
            ),
        )
    _ensure_index(
        "astral_point_interpretation_keyword_translations",
        "ix_astral_point_interpretation_keyword_translations_keyword_set_id",
        ["keyword_set_id"],
    )
    _ensure_index(
        "astral_point_interpretation_keyword_translations",
        "ix_astral_point_interpretation_keyword_translations_language_id",
        ["language_id"],
    )

    if not _table_exists("astral_point_interpretation_profile_translations"):
        op.create_table(
            "astral_point_interpretation_profile_translations",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("source_profile_id", sa.Integer(), nullable=False),
            sa.Column("language_id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=128), nullable=False),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("micro_note", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(
                ["source_profile_id"],
                ["astral_point_interpretation_profiles.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(["language_id"], ["languages.id"]),
            sa.UniqueConstraint(
                "source_profile_id",
                "language_id",
                name="uq_astral_point_interpretation_profile_translations_scope",
            ),
        )
    _ensure_index(
        "astral_point_interpretation_profile_translations",
        "ix_astral_point_interpretation_profile_translations_source_profile_id",
        ["source_profile_id"],
    )
    _ensure_index(
        "astral_point_interpretation_profile_translations",
        "ix_astral_point_interpretation_profile_translations_language_id",
        ["language_id"],
    )


def downgrade() -> None:
    """Supprime les tables des points astrologiques calculés."""
    for table_name in (
        "astral_point_interpretation_profile_translations",
        "astral_point_interpretation_keyword_translations",
        "astral_point_interpretation_profiles",
        "astral_point_interpretation_keywords",
        "astral_point_aliases",
        "astral_point_calculation_variants",
        "astral_points",
        "astral_point_families",
    ):
        if _table_exists(table_name):
            op.drop_table(table_name)
