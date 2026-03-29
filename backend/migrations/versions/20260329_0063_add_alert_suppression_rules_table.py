"""add alert suppression rules table

Revision ID: 20260329_0063
Revises: 20260329_0062
Create Date: 2026-03-29
"""

import sqlalchemy as sa
from alembic import op

revision = "20260329_0063"
down_revision = "20260329_0062"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "canonical_entitlement_mutation_alert_suppression_rules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("alert_kind", sa.String(length=32), nullable=False),
        sa.Column("feature_code", sa.String(length=64), nullable=True),
        sa.Column("plan_code", sa.String(length=64), nullable=True),
        sa.Column("actor_type", sa.String(length=32), nullable=True),
        sa.Column("suppression_key", sa.String(length=64), nullable=True),
        sa.Column("ops_comment", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "alert_kind",
            "feature_code",
            "plan_code",
            "actor_type",
            name="uq_cema_suppression_rules_criteria",
        ),
    )
    op.create_index(
        "ix_cema_suppression_rules_is_active",
        "canonical_entitlement_mutation_alert_suppression_rules",
        ["is_active"],
    )
    op.create_index(
        "ix_cema_suppression_rules_is_active_kind",
        "canonical_entitlement_mutation_alert_suppression_rules",
        ["is_active", "alert_kind"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cema_suppression_rules_is_active_kind",
        table_name="canonical_entitlement_mutation_alert_suppression_rules",
    )
    op.drop_index(
        "ix_cema_suppression_rules_is_active",
        table_name="canonical_entitlement_mutation_alert_suppression_rules",
    )
    op.drop_table("canonical_entitlement_mutation_alert_suppression_rules")
