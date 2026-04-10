"""add_eval_fields_to_llm_use_case_configs

Revision ID: 20260408_0068
Revises: 432a48efb602
Create Date: 2026-04-08 16:45:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260408_0068"
down_revision: Union[str, Sequence[str], None] = "432a48efb602"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("llm_use_case_configs", schema=None) as batch_op:
        batch_op.add_column(sa.Column("eval_fixtures_path", sa.String(length=255), nullable=True))
        batch_op.add_column(
            sa.Column(
                "eval_failure_threshold",
                sa.Float(),
                nullable=False,
                server_default="0.2",
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("llm_use_case_configs", schema=None) as batch_op:
        batch_op.drop_column("eval_failure_threshold")
        batch_op.drop_column("eval_fixtures_path")
