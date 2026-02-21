"""add enterprise account billing plan mapping

Revision ID: 20260220_0016
Revises: 20260220_0015
Create Date: 2026-02-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260220_0016"
down_revision: Union[str, Sequence[str], None] = "20260220_0015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "enterprise_account_billing_plans",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("enterprise_account_id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["enterprise_account_id"], ["enterprise_accounts.id"]),
        sa.ForeignKeyConstraint(["plan_id"], ["enterprise_billing_plans.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "enterprise_account_id",
            name="uq_enterprise_account_billing_plans_account",
        ),
    )
    op.create_index(
        "ix_enterprise_account_billing_plans_enterprise_account_id",
        "enterprise_account_billing_plans",
        ["enterprise_account_id"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_account_billing_plans_plan_id",
        "enterprise_account_billing_plans",
        ["plan_id"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_account_billing_plans_created_at",
        "enterprise_account_billing_plans",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_account_billing_plans_updated_at",
        "enterprise_account_billing_plans",
        ["updated_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_enterprise_account_billing_plans_updated_at",
        table_name="enterprise_account_billing_plans",
    )
    op.drop_index(
        "ix_enterprise_account_billing_plans_created_at",
        table_name="enterprise_account_billing_plans",
    )
    op.drop_index(
        "ix_enterprise_account_billing_plans_plan_id",
        table_name="enterprise_account_billing_plans",
    )
    op.drop_index(
        "ix_enterprise_account_billing_plans_enterprise_account_id",
        table_name="enterprise_account_billing_plans",
    )
    op.drop_table("enterprise_account_billing_plans")
