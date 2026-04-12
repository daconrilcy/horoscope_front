"""add_snapshot_version_to_logs

Revision ID: e5b9fe4ad515
Revises: b91ce4044d7c
Create Date: 2026-04-12 10:25:54.844910
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e5b9fe4ad515"
down_revision: Union[str, Sequence[str], None] = "b91ce4044d7c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("llm_call_logs", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("active_snapshot_version", sa.String(length=64), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("llm_call_logs", schema=None) as batch_op:
        batch_op.drop_column("active_snapshot_version")
