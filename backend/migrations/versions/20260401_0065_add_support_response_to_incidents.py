"""add support_response to support incidents

Revision ID: 20260401_0065
Revises: 707ad78f51ac
Create Date: 2026-04-01 23:10:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260401_0065"
down_revision: Union[str, Sequence[str], None] = "707ad78f51ac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("support_incidents", sa.Column("support_response", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("support_incidents", "support_response")
