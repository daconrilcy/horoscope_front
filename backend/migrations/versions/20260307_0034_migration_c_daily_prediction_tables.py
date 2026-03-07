"""migration c daily prediction tables

Revision ID: 20260307_0034
Revises: 20260307_0033
Create Date: 2026-03-07
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260307_0034"
down_revision: Union[str, Sequence[str], None] = "20260307_0033"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. daily_prediction_runs
    op.create_table(
        "daily_prediction_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("reference_version_id", sa.Integer(), nullable=False),
        sa.Column("ruleset_id", sa.Integer(), nullable=False),
        sa.Column("input_hash", sa.String(length=64), nullable=True),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("overall_summary", sa.Text(), nullable=True),
        sa.Column("overall_tone", sa.String(length=16), nullable=True),
        sa.Column("main_turning_point_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["reference_version_id"], ["reference_versions.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["ruleset_id"], ["prediction_rulesets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "local_date",
            "reference_version_id",
            "ruleset_id",
            name="uq_daily_prediction_runs_user_date_ruleset",
        ),
    )
    op.create_index(
        "ix_daily_prediction_runs_user_id_local_date",
        "daily_prediction_runs",
        ["user_id", "local_date"],
        unique=False,
    )

    # 2. daily_prediction_category_scores
    op.create_table(
        "daily_prediction_category_scores",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("raw_score", sa.Float(), nullable=True),
        sa.Column("normalized_score", sa.Float(), nullable=True),
        sa.Column("note_20", sa.Integer(), nullable=True),
        sa.Column("power", sa.Float(), nullable=True),
        sa.Column("volatility", sa.Float(), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["prediction_categories.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["run_id"], ["daily_prediction_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", "category_id", name="uq_category_scores_run_category"),
    )
    op.create_index(
        op.f("ix_daily_prediction_category_scores_run_id"),
        "daily_prediction_category_scores",
        ["run_id"],
        unique=False,
    )

    # 3. daily_prediction_turning_points
    op.create_table(
        "daily_prediction_turning_points",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("occurred_at_local", sa.DateTime(), nullable=True),
        sa.Column("event_type_id", sa.Integer(), nullable=True),
        sa.Column("severity", sa.Float(), nullable=True),
        sa.Column("driver_json", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["event_type_id"], ["ruleset_event_types.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["run_id"], ["daily_prediction_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_daily_prediction_turning_points_run_id"),
        "daily_prediction_turning_points",
        ["run_id"],
        unique=False,
    )

    # 4. daily_prediction_time_blocks
    op.create_table(
        "daily_prediction_time_blocks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("block_index", sa.Integer(), nullable=False),
        sa.Column("start_at_local", sa.DateTime(), nullable=True),
        sa.Column("end_at_local", sa.DateTime(), nullable=True),
        sa.Column("tone_code", sa.String(length=16), nullable=True),
        sa.Column("dominant_categories_json", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["run_id"], ["daily_prediction_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", "block_index", name="uq_time_blocks_run_block_index"),
    )
    op.create_index(
        op.f("ix_daily_prediction_time_blocks_run_id"),
        "daily_prediction_time_blocks",
        ["run_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_daily_prediction_time_blocks_run_id"), table_name="daily_prediction_time_blocks"
    )
    op.drop_table("daily_prediction_time_blocks")
    op.drop_index(
        op.f("ix_daily_prediction_turning_points_run_id"),
        table_name="daily_prediction_turning_points",
    )
    op.drop_table("daily_prediction_turning_points")
    op.drop_index(
        op.f("ix_daily_prediction_category_scores_run_id"),
        table_name="daily_prediction_category_scores",
    )
    op.drop_table("daily_prediction_category_scores")
    op.drop_index("ix_daily_prediction_runs_user_id_local_date", table_name="daily_prediction_runs")
    op.drop_table("daily_prediction_runs")
