"""Crée les tables de traductions des référentiels astrologiques.

Revision ID: 20260516_0117
Revises: 20260515_0116
Create Date: 2026-05-16
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260516_0117"
down_revision: Union[str, Sequence[str], None] = "20260515_0116"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe déjà dans le schéma courant."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _index_exists(table_name: str, index_name: str) -> bool:
    """Indique si un index existe déjà sur une table."""
    return index_name in {
        index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)
    }


def _create_name_translation_table(
    table_name: str,
    parent_column: str,
    parent_table: str,
    unique_name: str,
) -> None:
    """Crée une table de traduction de libellé stable si elle est absente."""
    if not _table_exists(table_name):
        op.create_table(
            table_name,
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(parent_column, sa.Integer(), nullable=False),
            sa.Column("language_id", sa.Integer(), nullable=False),
            sa.Column("translated_name", sa.String(length=128), nullable=False),
            sa.ForeignKeyConstraint(
                [parent_column],
                [f"{parent_table}.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(["language_id"], ["languages.id"]),
            sa.UniqueConstraint(parent_column, "language_id", name=unique_name),
        )
    _ensure_index(table_name, f"ix_{table_name}_{parent_column}", [parent_column])
    _ensure_index(table_name, f"ix_{table_name}_language_id", ["language_id"])


def _create_profile_translation_table(
    table_name: str,
    parent_table: str,
    unique_name: str,
) -> None:
    """Crée une table de traduction de profil éditorial si elle est absente."""
    if not _table_exists(table_name):
        op.create_table(
            table_name,
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("source_profile_id", sa.Integer(), nullable=False),
            sa.Column("language_id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=128), nullable=False),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("micro_note", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(
                ["source_profile_id"],
                [f"{parent_table}.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(["language_id"], ["languages.id"]),
            sa.UniqueConstraint("source_profile_id", "language_id", name=unique_name),
        )
    _ensure_index(table_name, f"ix_{table_name}_source_profile_id", ["source_profile_id"])
    _ensure_index(table_name, f"ix_{table_name}_language_id", ["language_id"])


def _ensure_index(table_name: str, index_name: str, columns: list[str]) -> None:
    """Crée un index non unique uniquement s'il manque."""
    if not _index_exists(table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=False)


def upgrade() -> None:
    """Crée les tables normalisées de traduction astrologique."""
    _create_name_translation_table(
        "astral_sign_translations",
        "astral_sign_id",
        "astral_signs",
        "uq_astral_sign_translations_sign_language",
    )
    _create_name_translation_table(
        "astral_house_translations",
        "house_id",
        "astral_houses",
        "uq_astral_house_translations_house_language",
    )
    _create_name_translation_table(
        "astral_planet_translations",
        "planet_id",
        "astral_planets",
        "uq_astral_planet_translations_planet_language",
    )
    _create_name_translation_table(
        "astral_aspect_translations",
        "aspect_id",
        "astral_aspects",
        "uq_astral_aspect_translations_aspect_language",
    )
    _create_profile_translation_table(
        "astral_house_interpretation_profile_translations",
        "astral_house_interpretation_profiles",
        "uq_astral_house_interpretation_profile_translations_scope",
    )
    _create_profile_translation_table(
        "astral_planet_interpretation_profile_translations",
        "astral_planet_interpretation_profiles",
        "uq_astral_planet_interpretation_profile_translations_scope",
    )
    _create_profile_translation_table(
        "astral_aspect_interpretation_profile_translations",
        "astral_aspect_interpretation_profiles",
        "uq_astral_aspect_interpretation_profile_translations_scope",
    )


def downgrade() -> None:
    """Supprime les tables de traduction astrologique."""
    for table_name in (
        "astral_aspect_interpretation_profile_translations",
        "astral_planet_interpretation_profile_translations",
        "astral_house_interpretation_profile_translations",
        "astral_aspect_translations",
        "astral_planet_translations",
        "astral_house_translations",
        "astral_sign_translations",
    ):
        if _table_exists(table_name):
            op.drop_table(table_name)
