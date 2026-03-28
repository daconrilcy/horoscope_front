"""create canonical_entitlement_mutation_audits

Revision ID: 20260328_0056
Revises: 20260327_0055
Create Date: 2026-03-28
"""

import sqlalchemy as sa
from alembic import op

revision = "20260328_0056"
down_revision = "20260327_0055"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "canonical_entitlement_mutation_audits",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("operation", sa.String(64), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("plan_code_snapshot", sa.String(64), nullable=False),
        sa.Column("feature_code", sa.String(64), nullable=False),
        sa.Column("actor_type", sa.String(32), nullable=False),
        sa.Column("actor_identifier", sa.String(128), nullable=False),
        sa.Column("request_id", sa.String(64), nullable=True),
        sa.Column("source_origin", sa.String(64), nullable=False),
        sa.Column("before_payload", sa.JSON(), nullable=False),
        sa.Column("after_payload", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cema_occurred_at", "canonical_entitlement_mutation_audits", ["occurred_at"])
    op.create_index("ix_cema_plan_id", "canonical_entitlement_mutation_audits", ["plan_id"])
    op.create_index(
        "ix_cema_feature_code", "canonical_entitlement_mutation_audits", ["feature_code"]
    )


def downgrade() -> None:
    op.drop_index("ix_cema_feature_code", table_name="canonical_entitlement_mutation_audits")
    op.drop_index("ix_cema_plan_id", table_name="canonical_entitlement_mutation_audits")
    op.drop_index("ix_cema_occurred_at", table_name="canonical_entitlement_mutation_audits")
    op.drop_table("canonical_entitlement_mutation_audits")
