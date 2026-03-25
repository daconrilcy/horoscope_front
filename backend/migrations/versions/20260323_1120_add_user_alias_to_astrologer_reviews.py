"""add user alias to astrologer reviews

Revision ID: 20260323_1120
Revises: 20260323_0905
Create Date: 2026-03-23 11:20:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260323_1120"
down_revision: Union[str, Sequence[str], None] = "20260323_0905"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("astrologer_reviews")}

    if "user_alias" not in existing_columns:
        with op.batch_alter_table("astrologer_reviews", schema=None) as batch_op:
            batch_op.add_column(
                sa.Column("user_alias", sa.String(length=120), nullable=False, server_default="")
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("astrologer_reviews")}

    if "user_alias" in existing_columns:
        with op.batch_alter_table("astrologer_reviews", schema=None) as batch_op:
            batch_op.drop_column("user_alias")
