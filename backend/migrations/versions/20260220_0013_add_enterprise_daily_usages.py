"""add enterprise daily usages table

Revision ID: 20260220_0013
Revises: 20260220_0012
Create Date: 2026-02-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260220_0013"
down_revision: Union[str, Sequence[str], None] = "20260220_0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "enterprise_daily_usages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("enterprise_account_id", sa.Integer(), nullable=False),
        sa.Column("credential_id", sa.Integer(), nullable=False),
        sa.Column("usage_date", sa.Date(), nullable=False),
        sa.Column("used_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["credential_id"], ["enterprise_api_credentials.id"]),
        sa.ForeignKeyConstraint(["enterprise_account_id"], ["enterprise_accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "enterprise_account_id",
            "credential_id",
            "usage_date",
            name="uq_enterprise_daily_usages_account_credential_date",
        ),
    )
    op.create_index(
        "ix_enterprise_daily_usages_enterprise_account_id",
        "enterprise_daily_usages",
        ["enterprise_account_id"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_daily_usages_credential_id",
        "enterprise_daily_usages",
        ["credential_id"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_daily_usages_usage_date",
        "enterprise_daily_usages",
        ["usage_date"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_enterprise_daily_usages_usage_date", table_name="enterprise_daily_usages")
    op.drop_index("ix_enterprise_daily_usages_credential_id", table_name="enterprise_daily_usages")
    op.drop_index(
        "ix_enterprise_daily_usages_enterprise_account_id",
        table_name="enterprise_daily_usages",
    )
    op.drop_table("enterprise_daily_usages")
