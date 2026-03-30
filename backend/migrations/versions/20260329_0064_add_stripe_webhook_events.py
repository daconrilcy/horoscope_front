"""add_stripe_webhook_events

Revision ID: 20260329_0064
Revises: 20260329_0063
Create Date: 2026-03-29 12:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260329_0064"
down_revision = "20260329_0063"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stripe_webhook_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("stripe_event_id", sa.String(255), nullable=False),
        sa.Column("event_type", sa.String(255), nullable=False),
        sa.Column("stripe_object_id", sa.String(255), nullable=True),
        sa.Column("livemode", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("status", sa.String(32), nullable=False, server_default="processing"),
        sa.Column("processing_attempts", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.UniqueConstraint("stripe_event_id", name="uq_stripe_webhook_events_event_id"),
    )
    op.create_index(
        "ix_stripe_webhook_events_event_type",
        "stripe_webhook_events",
        ["event_type"],
    )
    op.create_index(
        "ix_stripe_webhook_events_stripe_object_id",
        "stripe_webhook_events",
        ["stripe_object_id"],
    )
    op.create_index("ix_stripe_webhook_events_status", "stripe_webhook_events", ["status"])


def downgrade() -> None:
    op.drop_index("ix_stripe_webhook_events_status", "stripe_webhook_events")
    op.drop_index("ix_stripe_webhook_events_stripe_object_id", "stripe_webhook_events")
    op.drop_index("ix_stripe_webhook_events_event_type", "stripe_webhook_events")
    op.drop_table("stripe_webhook_events")
