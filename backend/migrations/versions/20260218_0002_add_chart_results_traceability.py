"""add chart results traceability

Revision ID: 20260218_0002
Revises: 20260218_0001
Create Date: 2026-02-18
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260218_0002"
down_revision: Union[str, Sequence[str], None] = "20260218_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chart_results",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("chart_id", sa.String(length=36), nullable=False),
        sa.Column("reference_version", sa.String(length=32), nullable=False),
        sa.Column("ruleset_version", sa.String(length=32), nullable=False),
        sa.Column("input_hash", sa.String(length=64), nullable=False),
        sa.Column("result_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chart_results_chart_id", "chart_results", ["chart_id"], unique=True)
    op.create_index(
        "ix_chart_results_reference_version",
        "chart_results",
        ["reference_version"],
        unique=False,
    )
    op.create_index(
        "ix_chart_results_ruleset_version",
        "chart_results",
        ["ruleset_version"],
        unique=False,
    )
    op.create_index("ix_chart_results_input_hash", "chart_results", ["input_hash"], unique=False)
    op.create_index("ix_chart_results_created_at", "chart_results", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_chart_results_created_at", table_name="chart_results")
    op.drop_index("ix_chart_results_input_hash", table_name="chart_results")
    op.drop_index("ix_chart_results_ruleset_version", table_name="chart_results")
    op.drop_index("ix_chart_results_reference_version", table_name="chart_results")
    op.drop_index("ix_chart_results_chart_id", table_name="chart_results")
    op.drop_table("chart_results")
