"""create enterprise_feature_usage_counters

Revision ID: 20260327_0055
Revises: 20260327_0054
Create Date: 2026-03-27
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260327_0055"
down_revision = "20260327_0054"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "enterprise_feature_usage_counters",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("enterprise_account_id", sa.Integer(), nullable=False),
        sa.Column("feature_code", sa.String(64), nullable=False),
        sa.Column("quota_key", sa.String(64), nullable=False),
        sa.Column("period_unit", sa.String(16), nullable=False),
        sa.Column("period_value", sa.Integer(), nullable=False),
        sa.Column("reset_mode", sa.String(16), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("used_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint("period_value >= 1", name="ck_enterprise_fuc_period_value_positive"),
        sa.CheckConstraint("used_count >= 0", name="ck_enterprise_fuc_used_count_non_negative"),
        sa.CheckConstraint(
            "LOWER(period_unit) IN ('day', 'week', 'month', 'year', 'lifetime')",
            name="ck_enterprise_fuc_period_unit_valid",
        ),
        sa.CheckConstraint(
            "LOWER(reset_mode) IN ('calendar', 'rolling', 'lifetime')",
            name="ck_enterprise_fuc_reset_mode_valid",
        ),
        sa.CheckConstraint(
            "LOWER(period_unit) = 'lifetime' OR window_end IS NOT NULL",
            name="ck_enterprise_fuc_window_end_required",
        ),
        sa.ForeignKeyConstraint(["enterprise_account_id"], ["enterprise_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "enterprise_account_id", "feature_code", "quota_key",
            "period_unit", "period_value", "reset_mode", "window_start",
            name="uq_enterprise_feature_usage_counters_composite",
        ),
    )
    op.create_index("ix_enterprise_fuc_account_id", "enterprise_feature_usage_counters", ["enterprise_account_id"])
    op.create_index("ix_enterprise_fuc_feature_code", "enterprise_feature_usage_counters", ["feature_code"])
    op.create_index(
        "ix_enterprise_fuc_account_feature_window",
        "enterprise_feature_usage_counters",
        ["enterprise_account_id", "feature_code", "window_start"],
    )


def downgrade() -> None:
    op.drop_index("ix_enterprise_fuc_account_feature_window", table_name="enterprise_feature_usage_counters")
    op.drop_index("ix_enterprise_fuc_feature_code", table_name="enterprise_feature_usage_counters")
    op.drop_index("ix_enterprise_fuc_account_id", table_name="enterprise_feature_usage_counters")
    op.drop_table("enterprise_feature_usage_counters")
