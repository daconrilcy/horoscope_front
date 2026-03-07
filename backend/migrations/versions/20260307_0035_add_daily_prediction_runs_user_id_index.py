"""add daily prediction runs user_id index

Revision ID: 20260307_0035
Revises: 20260307_0034
Create Date: 2026-03-07
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260307_0035"
down_revision: Union[str, Sequence[str], None] = "20260307_0034"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


INDEX_NAME = "ix_daily_prediction_runs_user_id"
TABLE_NAME = "daily_prediction_runs"


def _has_index() -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(index["name"] == INDEX_NAME for index in inspector.get_indexes(TABLE_NAME))


def upgrade() -> None:
    if not _has_index():
        op.create_index(INDEX_NAME, TABLE_NAME, ["user_id"], unique=False)


def downgrade() -> None:
    if _has_index():
        op.drop_index(INDEX_NAME, table_name=TABLE_NAME)
