"""Cree les profils editoriaux d'interpretation des aspects.

Revision ID: 20260514_0106
Revises: 20260514_0105
Create Date: 2026-05-14
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260514_0106"
down_revision: Union[str, Sequence[str], None] = "20260514_0105"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ajoute le referentiel editorial versionne des aspects."""
    op.create_table(
        "astral_aspect_interpretation_profiles",
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
    op.create_index(
        "ix_astral_aspect_interpretation_profiles_reference_version_id",
        "astral_aspect_interpretation_profiles",
        ["reference_version_id"],
        unique=False,
    )
    op.create_index(
        "ix_astral_aspect_interpretation_profiles_aspect_id",
        "astral_aspect_interpretation_profiles",
        ["aspect_id"],
        unique=False,
    )
    op.create_index(
        "ix_astral_aspect_interpretation_profiles_astral_system_id",
        "astral_aspect_interpretation_profiles",
        ["astral_system_id"],
        unique=False,
    )


def downgrade() -> None:
    """Supprime le referentiel editorial versionne des aspects."""
    op.drop_index(
        "ix_astral_aspect_interpretation_profiles_astral_system_id",
        table_name="astral_aspect_interpretation_profiles",
    )
    op.drop_index(
        "ix_astral_aspect_interpretation_profiles_aspect_id",
        table_name="astral_aspect_interpretation_profiles",
    )
    op.drop_index(
        "ix_astral_aspect_interpretation_profiles_reference_version_id",
        table_name="astral_aspect_interpretation_profiles",
    )
    op.drop_table("astral_aspect_interpretation_profiles")
