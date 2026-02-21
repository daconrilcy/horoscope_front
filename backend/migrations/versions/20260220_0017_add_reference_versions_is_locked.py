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
    op.add_column(
        "reference_versions",
        sa.Column(
            "is_locked",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.alter_column("reference_versions", "is_locked", server_default=None)


def downgrade() -> None:
    op.drop_column("reference_versions", "is_locked")
