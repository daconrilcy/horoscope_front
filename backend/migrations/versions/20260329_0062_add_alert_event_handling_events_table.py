"""add alert event handling events table

Revision ID: 20260329_0062
Revises: 20260329_0061
Create Date: 2026-03-29
"""

import sqlalchemy as sa
from alembic import op

revision = "20260329_0062"
down_revision = "20260329_0061"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "canonical_entitlement_mutation_alert_event_handling_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "alert_event_id",
            sa.Integer(),
            sa.ForeignKey("canonical_entitlement_mutation_alert_events.id"),
            nullable=False,
        ),
        sa.Column("handling_status", sa.String(length=32), nullable=False),
        sa.Column("handled_by_user_id", sa.Integer(), nullable=True),
        sa.Column(
            "handled_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("ops_comment", sa.Text(), nullable=True),
        sa.Column("suppression_key", sa.String(length=64), nullable=True),
        sa.Column("request_id", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_cemae_handling_events_alert_event_id",
        "canonical_entitlement_mutation_alert_event_handling_events",
        ["alert_event_id"],
    )
    op.create_index(
        "ix_cemae_handling_events_handled_at",
        "canonical_entitlement_mutation_alert_event_handling_events",
        ["handled_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cemae_handling_events_handled_at",
        table_name="canonical_entitlement_mutation_alert_event_handling_events",
    )
    op.drop_index(
        "ix_cemae_handling_events_alert_event_id",
        table_name="canonical_entitlement_mutation_alert_event_handling_events",
    )
    op.drop_table("canonical_entitlement_mutation_alert_event_handling_events")
