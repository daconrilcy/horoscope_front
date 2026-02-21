"""add enterprise billing tables

Revision ID: 20260220_0015
Revises: 20260220_0014
Create Date: 2026-02-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260220_0015"
down_revision: Union[str, Sequence[str], None] = "20260220_0014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "enterprise_billing_plans",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("monthly_fixed_cents", sa.Integer(), nullable=False),
        sa.Column("included_monthly_units", sa.Integer(), nullable=False),
        sa.Column("overage_unit_price_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_enterprise_billing_plans_code", "enterprise_billing_plans", ["code"], unique=True
    )
    op.create_index(
        "ix_enterprise_billing_plans_is_active",
        "enterprise_billing_plans",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_billing_plans_created_at",
        "enterprise_billing_plans",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_billing_plans_updated_at",
        "enterprise_billing_plans",
        ["updated_at"],
        unique=False,
    )

    op.create_table(
        "enterprise_billing_cycles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("enterprise_account_id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("fixed_amount_cents", sa.Integer(), nullable=False),
        sa.Column("included_units", sa.Integer(), nullable=False),
        sa.Column("consumed_units", sa.Integer(), nullable=False),
        sa.Column("billable_units", sa.Integer(), nullable=False),
        sa.Column("unit_price_cents", sa.Integer(), nullable=False),
        sa.Column("variable_amount_cents", sa.Integer(), nullable=False),
        sa.Column("total_amount_cents", sa.Integer(), nullable=False),
        sa.Column("limit_mode", sa.String(length=16), nullable=False),
        sa.Column("overage_applied", sa.Boolean(), nullable=False),
        sa.Column("calculation_snapshot", sa.JSON(), nullable=False),
        sa.Column("closed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["enterprise_account_id"], ["enterprise_accounts.id"]),
        sa.ForeignKeyConstraint(["plan_id"], ["enterprise_billing_plans.id"]),
        sa.ForeignKeyConstraint(["closed_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "enterprise_account_id",
            "period_start",
            "period_end",
            name="uq_enterprise_billing_cycles_account_period",
        ),
    )
    op.create_index(
        "ix_enterprise_billing_cycles_enterprise_account_id",
        "enterprise_billing_cycles",
        ["enterprise_account_id"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_billing_cycles_plan_id",
        "enterprise_billing_cycles",
        ["plan_id"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_billing_cycles_period_start",
        "enterprise_billing_cycles",
        ["period_start"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_billing_cycles_period_end",
        "enterprise_billing_cycles",
        ["period_end"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_billing_cycles_status",
        "enterprise_billing_cycles",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_billing_cycles_closed_by_user_id",
        "enterprise_billing_cycles",
        ["closed_by_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_billing_cycles_created_at",
        "enterprise_billing_cycles",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_enterprise_billing_cycles_updated_at",
        "enterprise_billing_cycles",
        ["updated_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_enterprise_billing_cycles_updated_at", table_name="enterprise_billing_cycles")
    op.drop_index("ix_enterprise_billing_cycles_created_at", table_name="enterprise_billing_cycles")
    op.drop_index(
        "ix_enterprise_billing_cycles_closed_by_user_id", table_name="enterprise_billing_cycles"
    )
    op.drop_index("ix_enterprise_billing_cycles_status", table_name="enterprise_billing_cycles")
    op.drop_index("ix_enterprise_billing_cycles_period_end", table_name="enterprise_billing_cycles")
    op.drop_index(
        "ix_enterprise_billing_cycles_period_start", table_name="enterprise_billing_cycles"
    )
    op.drop_index("ix_enterprise_billing_cycles_plan_id", table_name="enterprise_billing_cycles")
    op.drop_index(
        "ix_enterprise_billing_cycles_enterprise_account_id", table_name="enterprise_billing_cycles"
    )
    op.drop_table("enterprise_billing_cycles")

    op.drop_index("ix_enterprise_billing_plans_updated_at", table_name="enterprise_billing_plans")
    op.drop_index("ix_enterprise_billing_plans_created_at", table_name="enterprise_billing_plans")
    op.drop_index("ix_enterprise_billing_plans_is_active", table_name="enterprise_billing_plans")
    op.drop_index("ix_enterprise_billing_plans_code", table_name="enterprise_billing_plans")
    op.drop_table("enterprise_billing_plans")
