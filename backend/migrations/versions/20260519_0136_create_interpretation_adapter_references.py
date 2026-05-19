"""Cree les referentiels des adaptateurs interpretatifs.

Revision ID: 20260519_0136
Revises: 20260519_0135
Create Date: 2026-05-19
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260519_0136"
down_revision: Union[str, Sequence[str], None] = "20260519_0135"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SIGNAL_TABLE = "astral_interpretation_signal_types"
THEME_TABLE = "astral_interpretation_themes"
RULE_TABLE = "astral_interpretation_adapter_rules"


def _table_exists(table_name: str) -> bool:
    """Indique si une table existe dans la base migree."""
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    """Ajoute les tables versionnees des adaptateurs interpretatifs."""
    if not _table_exists(THEME_TABLE):
        op.create_table(
            THEME_TABLE,
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("code", sa.String(length=96), nullable=False),
            sa.Column("label", sa.String(length=160), nullable=False),
            sa.Column("category", sa.String(length=64), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("reference_version_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["reference_version_id"], ["astral_reference_versions.id"]),
            sa.UniqueConstraint(
                "reference_version_id",
                "code",
                name="uq_astral_interpretation_themes_scope",
            ),
        )
        op.create_index("ix_astral_interpretation_themes_code", THEME_TABLE, ["code"])
        op.create_index("ix_astral_interpretation_themes_category", THEME_TABLE, ["category"])
        op.create_index(
            "ix_astral_interpretation_themes_reference_version_id",
            THEME_TABLE,
            ["reference_version_id"],
        )

    if not _table_exists(SIGNAL_TABLE):
        op.create_table(
            SIGNAL_TABLE,
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("code", sa.String(length=96), nullable=False),
            sa.Column("label", sa.String(length=160), nullable=False),
            sa.Column("category", sa.String(length=64), nullable=False),
            sa.Column("theme_code", sa.String(length=96), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("priority_default", sa.String(length=32), nullable=False),
            sa.Column("priority_default_rank", sa.Integer(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("sort_order", sa.Integer(), nullable=False),
            sa.Column("reference_version_id", sa.Integer(), nullable=False),
            sa.CheckConstraint(
                "priority_default_rank > 0",
                name="ck_astral_interpretation_signal_types_priority_rank",
            ),
            sa.ForeignKeyConstraint(["reference_version_id"], ["astral_reference_versions.id"]),
            sa.UniqueConstraint(
                "reference_version_id",
                "code",
                name="uq_astral_interpretation_signal_types_scope",
            ),
        )
        op.create_index("ix_astral_interpretation_signal_types_code", SIGNAL_TABLE, ["code"])
        op.create_index(
            "ix_astral_interpretation_signal_types_category",
            SIGNAL_TABLE,
            ["category"],
        )
        op.create_index(
            "ix_astral_interpretation_signal_types_theme_code",
            SIGNAL_TABLE,
            ["theme_code"],
        )
        op.create_index(
            "ix_astral_interpretation_signal_types_reference_version_id",
            SIGNAL_TABLE,
            ["reference_version_id"],
        )

    if not _table_exists(RULE_TABLE):
        op.create_table(
            RULE_TABLE,
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("code", sa.String(length=96), nullable=False),
            sa.Column("source_type", sa.String(length=64), nullable=False),
            sa.Column("source_code", sa.String(length=96), nullable=False),
            sa.Column("condition_json", sa.JSON(), nullable=False),
            sa.Column("signal_code", sa.String(length=96), nullable=False),
            sa.Column("priority_override", sa.String(length=32), nullable=True),
            sa.Column("priority_override_rank", sa.Integer(), nullable=True),
            sa.Column("weight", sa.Float(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("reference_version_code", sa.String(length=64), nullable=False),
            sa.Column("reference_version_id", sa.Integer(), nullable=False),
            sa.CheckConstraint(
                "weight >= 0",
                name="ck_astral_interpretation_adapter_rules_weight",
            ),
            sa.ForeignKeyConstraint(["reference_version_id"], ["astral_reference_versions.id"]),
            sa.UniqueConstraint(
                "reference_version_id",
                "code",
                name="uq_astral_interpretation_adapter_rules_scope",
            ),
        )
        op.create_index("ix_astral_interpretation_adapter_rules_code", RULE_TABLE, ["code"])
        op.create_index(
            "ix_astral_interpretation_adapter_rules_source_type",
            RULE_TABLE,
            ["source_type"],
        )
        op.create_index(
            "ix_astral_interpretation_adapter_rules_source_code",
            RULE_TABLE,
            ["source_code"],
        )
        op.create_index(
            "ix_astral_interpretation_adapter_rules_signal_code",
            RULE_TABLE,
            ["signal_code"],
        )
        op.create_index(
            "ix_astral_interpretation_adapter_rules_reference_version_id",
            RULE_TABLE,
            ["reference_version_id"],
        )


def downgrade() -> None:
    """Supprime les tables versionnees des adaptateurs interpretatifs."""
    if _table_exists(RULE_TABLE):
        op.drop_table(RULE_TABLE)
    if _table_exists(SIGNAL_TABLE):
        op.drop_table(SIGNAL_TABLE)
    if _table_exists(THEME_TABLE):
        op.drop_table(THEME_TABLE)
