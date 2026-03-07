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
    with op.batch_alter_table("chart_results", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_chart_results_user_id", ["user_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_chart_results_user_id_users",
            "users",
            ["user_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("chart_results", schema=None) as batch_op:
        batch_op.drop_constraint("fk_chart_results_user_id_users", type_="foreignkey")
        batch_op.drop_index("ix_chart_results_user_id")
        batch_op.drop_column("user_id")
