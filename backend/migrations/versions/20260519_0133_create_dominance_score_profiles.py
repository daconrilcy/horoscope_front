"""Cree les profils et poids de scoring des dominantes planetaires.

Revision ID: 20260519_0133
Revises: 20260519_0132
Create Date: 2026-05-19
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260519_0133"
down_revision: Union[str, Sequence[str], None] = "20260519_0132"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PROFILE_TABLE = "astral_dominance_score_profiles"
WEIGHT_TABLE = "astral_dominance_score_weights"


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe dans la base migree."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    """Ajoute les tables versionnees de scoring de dominance."""
    if not _table_exists(PROFILE_TABLE):
        op.create_table(
            PROFILE_TABLE,
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("code", sa.String(length=64), nullable=False),
            sa.Column("label", sa.String(length=128), nullable=False),
            sa.Column("tradition_code", sa.String(length=64), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("reference_version_code", sa.String(length=64), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("reference_version_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(
                ["reference_version_id"],
                ["astral_reference_versions.id"],
            ),
            sa.UniqueConstraint(
                "reference_version_id",
                "code",
                name="uq_astral_dominance_score_profiles_scope",
            ),
        )
        op.create_index("ix_astral_dominance_score_profiles_code", PROFILE_TABLE, ["code"])
        op.create_index(
            "ix_astral_dominance_score_profiles_tradition_code",
            PROFILE_TABLE,
            ["tradition_code"],
        )
        op.create_index(
            "ix_astral_dominance_score_profiles_reference_version_id",
            PROFILE_TABLE,
            ["reference_version_id"],
        )

    if not _table_exists(WEIGHT_TABLE):
        op.create_table(
            WEIGHT_TABLE,
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("score_profile_id", sa.Integer(), nullable=False),
            sa.Column("factor_type_id", sa.Integer(), nullable=False),
            sa.Column("weight", sa.Float(), nullable=False),
            sa.Column("min_value", sa.Float(), nullable=False),
            sa.Column("max_value", sa.Float(), nullable=False),
            sa.Column("normalization_method", sa.String(length=64), nullable=False),
            sa.Column("notes", sa.Text(), nullable=False),
            sa.CheckConstraint(
                "weight >= 0",
                name="ck_astral_dominance_score_weights_weight",
            ),
            sa.CheckConstraint(
                "max_value > min_value",
                name="ck_astral_dominance_score_weights_range",
            ),
            sa.ForeignKeyConstraint(
                ["score_profile_id"],
                ["astral_dominance_score_profiles.id"],
            ),
            sa.ForeignKeyConstraint(
                ["factor_type_id"],
                ["astral_dominance_factor_types.id"],
            ),
            sa.UniqueConstraint(
                "score_profile_id",
                "factor_type_id",
                name="uq_astral_dominance_score_weights_scope",
            ),
        )
        op.create_index(
            "ix_astral_dominance_score_weights_score_profile_id",
            WEIGHT_TABLE,
            ["score_profile_id"],
        )
        op.create_index(
            "ix_astral_dominance_score_weights_factor_type_id",
            WEIGHT_TABLE,
            ["factor_type_id"],
        )


def downgrade() -> None:
    """Supprime les tables de scoring de dominance."""
    if _table_exists(WEIGHT_TABLE):
        op.drop_table(WEIGHT_TABLE)
    if _table_exists(PROFILE_TABLE):
        op.drop_table(PROFILE_TABLE)
