"""add enterprise editorial configs table

Revision ID: 20260220_0014
Revises: 20260220_0013
Create Date: 2026-02-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260220_0014"
down_revision: Union[str, Sequence[str], None] = "20260220_0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "enterprise_editorial_configs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("enterprise_account_id", sa.Integer(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("tone", sa.String(length=16), nullable=False),
        sa.Column("length_style", sa.String(length=16), nullable=False),
        sa.Column("output_format", sa.String(length=16), nullable=False),
        sa.Column("preferred_terms", sa.JSON(), nullable=False),
        sa.Column("avoided_terms", sa.JSON(), nullable=False),
        sa.Column("created_by_credential_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_credential_id"], ["enterprise_api_credentials.id"]),
        sa.ForeignKeyConstraint(["enterprise_account_id"], ["enterprise_accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "enterprise_account_id",
            "version_number",
            name="uq_enterprise_editorial_configs_account_version",
        ),
    )
    op.create_index(
        "ix_enterprise_editorial_configs_enterprise_account_id",
        "enterprise_editorial_configs",
        ["enterprise_account_id"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_editorial_configs_is_active",
        "enterprise_editorial_configs",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_editorial_configs_created_by_credential_id",
        "enterprise_editorial_configs",
        ["created_by_credential_id"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_editorial_configs_created_at",
        "enterprise_editorial_configs",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_editorial_configs_updated_at",
        "enterprise_editorial_configs",
        ["updated_at"],
        unique=False,
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_enterprise_editorial_configs_one_active_per_account "
        "ON enterprise_editorial_configs (enterprise_account_id) "
        "WHERE is_active IS TRUE"
    )


def downgrade() -> None:
    op.execute("DROP INDEX uq_enterprise_editorial_configs_one_active_per_account")
    op.drop_index(
        "ix_enterprise_editorial_configs_updated_at", table_name="enterprise_editorial_configs"
    )
    op.drop_index(
        "ix_enterprise_editorial_configs_created_at", table_name="enterprise_editorial_configs"
    )
    op.drop_index(
        "ix_enterprise_editorial_configs_created_by_credential_id",
        table_name="enterprise_editorial_configs",
    )
    op.drop_index(
        "ix_enterprise_editorial_configs_is_active", table_name="enterprise_editorial_configs"
    )
    op.drop_index(
        "ix_enterprise_editorial_configs_enterprise_account_id",
        table_name="enterprise_editorial_configs",
    )
    op.drop_table("enterprise_editorial_configs")
