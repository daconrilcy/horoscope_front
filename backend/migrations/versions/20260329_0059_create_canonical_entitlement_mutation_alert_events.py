"""create canonical_entitlement_mutation_alert_events

Revision ID: 20260329_0059
Revises: 20260328_0058
Create Date: 2026-03-29 00:59:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260329_0059"
down_revision = "20260328_0058"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "canonical_entitlement_mutation_alert_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("audit_id", sa.Integer(), nullable=False),
        sa.Column("dedupe_key", sa.String(length=255), nullable=False),
        sa.Column("alert_kind", sa.String(length=32), nullable=False),
        sa.Column("risk_level_snapshot", sa.String(length=16), nullable=False),
        sa.Column("effective_review_status_snapshot", sa.String(length=32), nullable=True),
        sa.Column("feature_code_snapshot", sa.String(length=64), nullable=False),
        sa.Column("plan_id_snapshot", sa.Integer(), nullable=False),
        sa.Column("plan_code_snapshot", sa.String(length=64), nullable=False),
        sa.Column("actor_type_snapshot", sa.String(length=32), nullable=False),
        sa.Column("actor_identifier_snapshot", sa.String(length=128), nullable=False),
        sa.Column("sla_target_seconds_snapshot", sa.Integer(), nullable=True),
        sa.Column("due_at_snapshot", sa.DateTime(timezone=True), nullable=True),
        sa.Column("age_seconds_snapshot", sa.Integer(), nullable=False),
        sa.Column("delivery_channel", sa.String(length=32), nullable=False),
        sa.Column("delivery_status", sa.String(length=32), nullable=False),
        sa.Column("delivery_error", sa.Text(), nullable=True),
        sa.Column("request_id", sa.String(length=64), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["audit_id"], ["canonical_entitlement_mutation_audits.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dedupe_key"),
    )
    op.create_index(
        op.f("ix_canonical_entitlement_mutation_alert_events_audit_id"),
        "canonical_entitlement_mutation_alert_events",
        ["audit_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_canonical_entitlement_mutation_alert_events_created_at"),
        "canonical_entitlement_mutation_alert_events",
        ["created_at"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_canonical_entitlement_mutation_alert_events_created_at"),
        table_name="canonical_entitlement_mutation_alert_events",
    )
    op.drop_index(
        op.f("ix_canonical_entitlement_mutation_alert_events_audit_id"),
        table_name="canonical_entitlement_mutation_alert_events",
    )
    op.drop_table("canonical_entitlement_mutation_alert_events")
