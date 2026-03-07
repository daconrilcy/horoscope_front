"""migration b prediction ruleset tables

Revision ID: 20260307_0033
Revises: 20260307_0032
Create Date: 2026-03-07
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260307_0033"
down_revision: Union[str, Sequence[str], None] = "20260307_0032"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. prediction_rulesets
    op.create_table(
        "prediction_rulesets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("reference_version_id", sa.Integer(), nullable=False),
        sa.Column("zodiac_type", sa.String(length=16), server_default="tropical", nullable=False),
        sa.Column(
            "coordinate_mode", sa.String(length=16), server_default="geocentric", nullable=False
        ),
        sa.Column("house_system", sa.String(length=16), server_default="placidus", nullable=False),
        sa.Column("time_step_minutes", sa.Integer(), server_default="30", nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_locked", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["reference_version_id"], ["reference_versions.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("version"),
    )
    op.create_index(
        op.f("ix_prediction_rulesets_reference_version_id"),
        "prediction_rulesets",
        ["reference_version_id"],
        unique=False,
    )

    # 2. ruleset_event_types
    op.create_table(
        "ruleset_event_types",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ruleset_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("event_group", sa.String(length=64), nullable=True),
        sa.Column("priority", sa.Integer(), server_default="0", nullable=False),
        sa.Column("base_weight", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["ruleset_id"], ["prediction_rulesets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ruleset_id", "code"),
    )
    op.create_index(
        op.f("ix_ruleset_event_types_ruleset_id"),
        "ruleset_event_types",
        ["ruleset_id"],
        unique=False,
    )

    # 3. ruleset_parameters
    op.create_table(
        "ruleset_parameters",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ruleset_id", sa.Integer(), nullable=False),
        sa.Column("param_key", sa.String(length=64), nullable=False),
        sa.Column("param_value", sa.Text(), nullable=False),
        sa.Column("data_type", sa.String(length=16), server_default="string", nullable=False),
        sa.CheckConstraint(
            "data_type IN ('string', 'float', 'int', 'bool', 'json')",
            name="ck_ruleset_parameters_data_type",
        ),
        sa.ForeignKeyConstraint(["ruleset_id"], ["prediction_rulesets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ruleset_id", "param_key"),
    )
    op.create_index(
        op.f("ix_ruleset_parameters_ruleset_id"),
        "ruleset_parameters",
        ["ruleset_id"],
        unique=False,
    )

    # 4. category_calibrations
    op.create_table(
        "category_calibrations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ruleset_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("p05", sa.Float(), nullable=True),
        sa.Column("p25", sa.Float(), nullable=True),
        sa.Column("p50", sa.Float(), nullable=True),
        sa.Column("p75", sa.Float(), nullable=True),
        sa.Column("p95", sa.Float(), nullable=True),
        sa.Column("sample_size", sa.Integer(), nullable=True),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["prediction_categories.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["ruleset_id"], ["prediction_rulesets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ruleset_id", "category_id", "valid_from"),
    )
    op.create_index(
        op.f("ix_category_calibrations_ruleset_id"),
        "category_calibrations",
        ["ruleset_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_category_calibrations_category_id"),
        "category_calibrations",
        ["category_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_category_calibrations_category_id"), table_name="category_calibrations")
    op.drop_index(op.f("ix_category_calibrations_ruleset_id"), table_name="category_calibrations")
    op.drop_table("category_calibrations")
    op.drop_index(op.f("ix_ruleset_parameters_ruleset_id"), table_name="ruleset_parameters")
    op.drop_table("ruleset_parameters")
    op.drop_index(op.f("ix_ruleset_event_types_ruleset_id"), table_name="ruleset_event_types")
    op.drop_table("ruleset_event_types")
    op.drop_index(
        op.f("ix_prediction_rulesets_reference_version_id"), table_name="prediction_rulesets"
    )
    op.drop_table("prediction_rulesets")
