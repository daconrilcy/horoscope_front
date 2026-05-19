"""Cree les referentiels des conditions planetaires avancees.

Revision ID: 20260519_0134
Revises: 20260519_0133
Create Date: 2026-05-19
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260519_0134"
down_revision: Union[str, Sequence[str], None] = "20260519_0133"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TYPE_TABLE = "astral_advanced_condition_types"
PROFILE_TABLE = "astral_advanced_condition_score_profiles"
WEIGHT_TABLE = "astral_advanced_condition_weights"
PLANET_NATURE_TABLE = "astral_planet_natures"


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe dans la base migree."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _column_exists(table_name: str, column_name: str) -> bool:
    """Indique si une colonne existe dans une table migree."""
    return any(
        column["name"] == column_name
        for column in sa.inspect(op.get_bind()).get_columns(table_name)
    )


def upgrade() -> None:
    """Ajoute les tables runtime des conditions avancees."""
    if _table_exists(PLANET_NATURE_TABLE) and not _column_exists(
        PLANET_NATURE_TABLE, "planet_codes_json"
    ):
        op.add_column(
            PLANET_NATURE_TABLE,
            sa.Column(
                "planet_codes_json",
                sa.JSON(),
                nullable=False,
                server_default=sa.text("'[]'"),
            ),
        )

    if not _table_exists(TYPE_TABLE):
        op.create_table(
            TYPE_TABLE,
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("code", sa.String(length=64), nullable=False),
            sa.Column("label", sa.String(length=128), nullable=False),
            sa.Column("category", sa.String(length=64), nullable=False),
            sa.Column("functional_effect", sa.String(length=64), nullable=False),
            sa.Column("expression_effect", sa.String(length=64), nullable=False),
            sa.Column("intensity_effect", sa.String(length=64), nullable=False),
            sa.Column("visibility_effect", sa.String(length=64), nullable=False),
            sa.Column("default_weight", sa.Float(), nullable=False),
            sa.Column("sort_order", sa.Integer(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("reference_version_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["reference_version_id"], ["astral_reference_versions.id"]),
            sa.UniqueConstraint(
                "reference_version_id",
                "code",
                name="uq_astral_advanced_condition_types_scope",
            ),
        )
        op.create_index("ix_astral_advanced_condition_types_code", TYPE_TABLE, ["code"])
        op.create_index("ix_astral_advanced_condition_types_category", TYPE_TABLE, ["category"])
        op.create_index(
            "ix_astral_advanced_condition_types_reference_version_id",
            TYPE_TABLE,
            ["reference_version_id"],
        )

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
            sa.ForeignKeyConstraint(["reference_version_id"], ["astral_reference_versions.id"]),
            sa.UniqueConstraint(
                "reference_version_id",
                "code",
                name="uq_astral_advanced_condition_score_profiles_scope",
            ),
        )
        op.create_index("ix_astral_advanced_condition_score_profiles_code", PROFILE_TABLE, ["code"])
        op.create_index(
            "ix_astral_advanced_condition_score_profiles_tradition_code",
            PROFILE_TABLE,
            ["tradition_code"],
        )
        op.create_index(
            "ix_astral_advanced_condition_score_profiles_reference_version_id",
            PROFILE_TABLE,
            ["reference_version_id"],
        )

    if not _table_exists(WEIGHT_TABLE):
        op.create_table(
            WEIGHT_TABLE,
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("score_profile_id", sa.Integer(), nullable=False),
            sa.Column("condition_type_id", sa.Integer(), nullable=False),
            sa.Column("functional_strength_weight", sa.Float(), nullable=False),
            sa.Column("visibility_weight", sa.Float(), nullable=False),
            sa.Column("stability_weight", sa.Float(), nullable=False),
            sa.Column("intensity_weight", sa.Float(), nullable=False),
            sa.Column("coherence_weight", sa.Float(), nullable=False),
            sa.Column("support_weight", sa.Float(), nullable=False),
            sa.Column("constraint_weight", sa.Float(), nullable=False),
            sa.Column("ranking_weight", sa.Float(), nullable=False),
            sa.Column(
                "uses_default_weight", sa.Boolean(), nullable=False, server_default=sa.false()
            ),
            sa.Column("notes", sa.Text(), nullable=False),
            sa.ForeignKeyConstraint(
                ["score_profile_id"],
                ["astral_advanced_condition_score_profiles.id"],
            ),
            sa.ForeignKeyConstraint(
                ["condition_type_id"],
                ["astral_advanced_condition_types.id"],
            ),
            sa.UniqueConstraint(
                "score_profile_id",
                "condition_type_id",
                name="uq_astral_advanced_condition_weights_scope",
            ),
        )
        op.create_index(
            "ix_astral_advanced_condition_weights_score_profile_id",
            WEIGHT_TABLE,
            ["score_profile_id"],
        )
        op.create_index(
            "ix_astral_advanced_condition_weights_condition_type_id",
            WEIGHT_TABLE,
            ["condition_type_id"],
        )


def downgrade() -> None:
    """Supprime les tables runtime des conditions avancees."""
    if _table_exists(WEIGHT_TABLE):
        op.drop_table(WEIGHT_TABLE)
    if _table_exists(PROFILE_TABLE):
        op.drop_table(PROFILE_TABLE)
    if _table_exists(TYPE_TABLE):
        op.drop_table(TYPE_TABLE)
    if _table_exists(PLANET_NATURE_TABLE) and _column_exists(
        PLANET_NATURE_TABLE, "planet_codes_json"
    ):
        op.drop_column(PLANET_NATURE_TABLE, "planet_codes_json")
