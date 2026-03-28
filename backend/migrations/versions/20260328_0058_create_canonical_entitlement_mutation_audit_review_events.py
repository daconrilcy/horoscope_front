"""create canonical_entitlement_mutation_audit_review_events

Revision ID: 20260328_0058
Revises: 20260328_0057
Create Date: 2026-03-28
"""

import sqlalchemy as sa
from alembic import op

revision = "20260328_0058"
down_revision = "20260328_0057"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "canonical_entitlement_mutation_audit_review_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "audit_id",
            sa.Integer(),
            sa.ForeignKey("canonical_entitlement_mutation_audits.id"),
            nullable=False,
        ),
        sa.Column("previous_review_status", sa.String(32), nullable=True),
        sa.Column("new_review_status", sa.String(32), nullable=False),
        sa.Column("previous_review_comment", sa.Text(), nullable=True),
        sa.Column("new_review_comment", sa.Text(), nullable=True),
        sa.Column("previous_incident_key", sa.String(64), nullable=True),
        sa.Column("new_incident_key", sa.String(64), nullable=True),
        sa.Column("reviewed_by_user_id", sa.Integer(), nullable=True),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("request_id", sa.String(64), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_cemaret_audit_id",
        "canonical_entitlement_mutation_audit_review_events",
        ["audit_id"],
    )
    op.create_index(
        "ix_cemaret_occurred_at",
        "canonical_entitlement_mutation_audit_review_events",
        ["occurred_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cemaret_occurred_at",
        table_name="canonical_entitlement_mutation_audit_review_events",
    )
    op.drop_index(
        "ix_cemaret_audit_id",
        table_name="canonical_entitlement_mutation_audit_review_events",
    )
    op.drop_table("canonical_entitlement_mutation_audit_review_events")
