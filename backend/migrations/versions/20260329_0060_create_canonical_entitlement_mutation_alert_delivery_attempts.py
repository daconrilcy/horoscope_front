"""create canonical_entitlement_mutation_alert_delivery_attempts

Revision ID: 20260329_0060
Revises: 20260329_0059
Create Date: 2026-03-29 12:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260329_0060"
down_revision = "20260329_0059"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "canonical_entitlement_mutation_alert_delivery_attempts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("alert_event_id", sa.Integer(), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["alert_event_id"], ["canonical_entitlement_mutation_alert_events.id"]
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "alert_event_id",
            "attempt_number",
            name="uq_alert_delivery_attempt",
        ),
    )
    op.create_index(
        op.f("ix_canonical_entitlement_mutation_alert_delivery_attempts_alert_event_id"),
        "canonical_entitlement_mutation_alert_delivery_attempts",
        ["alert_event_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_canonical_entitlement_mutation_alert_delivery_attempts_created_at"),
        "canonical_entitlement_mutation_alert_delivery_attempts",
        ["created_at"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_canonical_entitlement_mutation_alert_delivery_attempts_created_at"),
        table_name="canonical_entitlement_mutation_alert_delivery_attempts",
    )
    op.drop_index(
        op.f("ix_canonical_entitlement_mutation_alert_delivery_attempts_alert_event_id"),
        table_name="canonical_entitlement_mutation_alert_delivery_attempts",
    )
    op.drop_table("canonical_entitlement_mutation_alert_delivery_attempts")
