"""add user_id to chart_results

Revision ID: 20260218_0005
Revises: 20260218_0004
Create Date: 2026-02-18
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260218_0005"
down_revision: Union[str, Sequence[str], None] = "20260218_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("chart_results", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index("ix_chart_results_user_id", "chart_results", ["user_id"], unique=False)
    op.create_foreign_key(
        "fk_chart_results_user_id_users",
        "chart_results",
        "users",
        ["user_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_chart_results_user_id_users", "chart_results", type_="foreignkey")
    op.drop_index("ix_chart_results_user_id", table_name="chart_results")
    op.drop_column("chart_results", "user_id")
