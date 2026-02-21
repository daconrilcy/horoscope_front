"""add user daily quota usage table

Revision ID: 20260219_0007
Revises: 20260219_0006
Create Date: 2026-02-19
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260219_0007"
down_revision: Union[str, Sequence[str], None] = "20260219_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_daily_quota_usages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("quota_date", sa.Date(), nullable=False),
        sa.Column("used_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "quota_date",
            name="uq_user_daily_quota_usages_user_id_quota_date",
        ),
    )
    op.create_index(
        "ix_user_daily_quota_usages_quota_date",
        "user_daily_quota_usages",
        ["quota_date"],
        unique=False,
    )
    op.create_index(
        "ix_user_daily_quota_usages_user_id",
        "user_daily_quota_usages",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_user_daily_quota_usages_user_id", table_name="user_daily_quota_usages")
    op.drop_index("ix_user_daily_quota_usages_quota_date", table_name="user_daily_quota_usages")
    op.drop_table("user_daily_quota_usages")
