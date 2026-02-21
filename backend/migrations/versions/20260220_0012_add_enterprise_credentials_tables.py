"""add enterprise accounts and api credentials tables

Revision ID: 20260220_0012
Revises: 20260219_0011
Create Date: 2026-02-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260220_0012"
down_revision: Union[str, Sequence[str], None] = "20260219_0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "enterprise_accounts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("admin_user_id", sa.Integer(), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status in ('active','inactive')", name="ck_enterprise_accounts_status"),
        sa.ForeignKeyConstraint(["admin_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_enterprise_accounts_admin_user_id",
        "enterprise_accounts",
        ["admin_user_id"],
        unique=True,
    )
    op.create_index(
        "ix_enterprise_accounts_status", "enterprise_accounts", ["status"], unique=False
    )
    op.create_index(
        "ix_enterprise_accounts_created_at",
        "enterprise_accounts",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_accounts_updated_at",
        "enterprise_accounts",
        ["updated_at"],
        unique=False,
    )

    op.create_table(
        "enterprise_api_credentials",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("enterprise_account_id", sa.Integer(), nullable=False),
        sa.Column("key_prefix", sa.String(length=24), nullable=False),
        sa.Column("secret_hash", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status in ('active','revoked')",
            name="ck_enterprise_api_credentials_status",
        ),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["enterprise_account_id"], ["enterprise_accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_enterprise_api_credentials_enterprise_account_id",
        "enterprise_api_credentials",
        ["enterprise_account_id"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_api_credentials_key_prefix",
        "enterprise_api_credentials",
        ["key_prefix"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_api_credentials_status",
        "enterprise_api_credentials",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_api_credentials_created_by_user_id",
        "enterprise_api_credentials",
        ["created_by_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_api_credentials_created_at",
        "enterprise_api_credentials",
        ["created_at"],
        unique=False,
    )

    op.execute(
        "CREATE UNIQUE INDEX uq_enterprise_api_credentials_one_active_per_account "
        "ON enterprise_api_credentials (enterprise_account_id) "
        "WHERE status = 'active'"
    )


def downgrade() -> None:
    op.execute("DROP INDEX uq_enterprise_api_credentials_one_active_per_account")
    op.drop_index(
        "ix_enterprise_api_credentials_created_at", table_name="enterprise_api_credentials"
    )
    op.drop_index(
        "ix_enterprise_api_credentials_created_by_user_id",
        table_name="enterprise_api_credentials",
    )
    op.drop_index("ix_enterprise_api_credentials_status", table_name="enterprise_api_credentials")
    op.drop_index(
        "ix_enterprise_api_credentials_key_prefix", table_name="enterprise_api_credentials"
    )
    op.drop_index(
        "ix_enterprise_api_credentials_enterprise_account_id",
        table_name="enterprise_api_credentials",
    )
    op.drop_table("enterprise_api_credentials")

    op.drop_index("ix_enterprise_accounts_updated_at", table_name="enterprise_accounts")
    op.drop_index("ix_enterprise_accounts_created_at", table_name="enterprise_accounts")
    op.drop_index("ix_enterprise_accounts_status", table_name="enterprise_accounts")
    op.drop_index("ix_enterprise_accounts_admin_user_id", table_name="enterprise_accounts")
    op.drop_table("enterprise_accounts")
