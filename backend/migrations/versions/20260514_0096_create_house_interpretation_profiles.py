"""Crée les profils éditoriaux d'interprétation des maisons.

Revision ID: 20260514_0096
Revises: 20260513_0095
Create Date: 2026-05-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260514_0096"
down_revision: Union[str, Sequence[str], None] = "20260513_0095"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute le référentiel éditorial versionné sans toucher au runtime maisons."""
    op.create_table(
        "house_interpretation_profiles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("reference_version_id", sa.Integer(), nullable=False),
        sa.Column("house_id", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("tradition", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("core_keywords_json", sa.Text(), nullable=True),
        sa.Column("shadow_keywords_json", sa.Text(), nullable=True),
        sa.Column("psychological_keywords_json", sa.Text(), nullable=True),
        sa.Column("material_keywords_json", sa.Text(), nullable=True),
        sa.Column("relationship_keywords_json", sa.Text(), nullable=True),
        sa.Column("career_keywords_json", sa.Text(), nullable=True),
        sa.Column("health_keywords_json", sa.Text(), nullable=True),
        sa.Column("spiritual_keywords_json", sa.Text(), nullable=True),
        sa.Column("body_parts_json", sa.Text(), nullable=True),
        sa.Column("archetypes_json", sa.Text(), nullable=True),
        sa.Column("dos_json", sa.Text(), nullable=True),
        sa.Column("donts_json", sa.Text(), nullable=True),
        sa.Column("prompt_hints_json", sa.Text(), nullable=True),
        sa.Column("micro_note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["reference_version_id"],
            ["reference_versions.id"],
            name="fk_house_interpretation_profiles_reference_version_id",
        ),
        sa.ForeignKeyConstraint(
            ["house_id"],
            ["astral_houses.id"],
            name="fk_house_interpretation_profiles_house_id",
        ),
        sa.UniqueConstraint(
            "reference_version_id",
            "house_id",
            "language",
            "tradition",
            name="uq_house_interpretation_profiles_version_house_language_tradition",
        ),
    )
    op.create_index(
        "ix_house_interpretation_profiles_reference_version_id",
        "house_interpretation_profiles",
        ["reference_version_id"],
        unique=False,
    )
    op.create_index(
        "ix_house_interpretation_profiles_house_id",
        "house_interpretation_profiles",
        ["house_id"],
        unique=False,
    )


def downgrade() -> None:
    """Supprime le référentiel éditorial des maisons pour rollback."""
    op.drop_index(
        "ix_house_interpretation_profiles_house_id",
        table_name="house_interpretation_profiles",
    )
    op.drop_index(
        "ix_house_interpretation_profiles_reference_version_id",
        table_name="house_interpretation_profiles",
    )
    op.drop_table("house_interpretation_profiles")
