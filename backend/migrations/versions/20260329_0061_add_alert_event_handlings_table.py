"""add alert event handlings table

Revision ID: 20260329_0061
Revises: 20260329_0060
Create Date: 2026-03-29
"""

import sqlalchemy as sa
from alembic import op

revision = "20260329_0061"
down_revision = "20260329_0060"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "canonical_entitlement_mutation_alert_event_handlings",
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("alert_event_id", name="uq_cemae_handling_alert_event_id"),
    )
    op.create_index(
        "ix_cemae_handling_status",
        "canonical_entitlement_mutation_alert_event_handlings",
        ["handling_status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cemae_handling_status",
        table_name="canonical_entitlement_mutation_alert_event_handlings",
    )
    op.drop_table("canonical_entitlement_mutation_alert_event_handlings")
