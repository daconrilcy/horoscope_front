"""create canonical_entitlement_mutation_audit_reviews

Revision ID: 20260328_0057
Revises: 20260328_0056
Create Date: 2026-03-28
"""

import sqlalchemy as sa
from alembic import op

revision = "20260328_0057"
down_revision = "20260328_0056"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "canonical_entitlement_mutation_audit_reviews",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "audit_id",
            sa.Integer(),
            sa.ForeignKey("canonical_entitlement_mutation_audits.id"),
            nullable=False,
        ),
        sa.Column("review_status", sa.String(32), nullable=False),
        sa.Column("reviewed_by_user_id", sa.Integer(), nullable=True),
        sa.Column(
            "reviewed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("review_comment", sa.Text(), nullable=True),
        sa.Column("incident_key", sa.String(64), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("audit_id", name="uq_cemar_audit_id"),
    )
    op.create_index(
        "ix_cemar_review_status",
        "canonical_entitlement_mutation_audit_reviews",
        ["review_status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cemar_review_status",
        table_name="canonical_entitlement_mutation_audit_reviews",
    )
    op.drop_table("canonical_entitlement_mutation_audit_reviews")
