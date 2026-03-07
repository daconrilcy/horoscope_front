"""add reference_versions.is_locked

Revision ID: 20260220_0017
Revises: 20260220_0016
Create Date: 2026-02-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260220_0017"
down_revision: Union[str, Sequence[str], None] = "20260220_0016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("reference_versions", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_locked",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            )
        )
        batch_op.alter_column("is_locked", server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("reference_versions", schema=None) as batch_op:
        batch_op.drop_column("is_locked")
