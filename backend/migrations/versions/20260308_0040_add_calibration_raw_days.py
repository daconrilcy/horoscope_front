"""add calibration raw days

Revision ID: 20260308_0040
Revises: 20260308_0039
Create Date: 2026-03-08 17:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260308_0040"
down_revision = "20260308_0039"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "calibration_raw_days",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("profile_label", sa.String(), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("category_code", sa.String(), nullable=False),
        sa.Column("raw_score", sa.Float(), nullable=False),
        sa.Column("power", sa.Float(), nullable=True),
        sa.Column("volatility", sa.Float(), nullable=True),
        sa.Column("pivot_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reference_version", sa.String(), nullable=False),
        sa.Column("ruleset_version", sa.String(), nullable=False),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "profile_label",
            "local_date",
            "category_code",
            "reference_version",
            "ruleset_version",
            name="uq_calibration_raw_day",
        ),
    )


def downgrade():
    op.drop_table("calibration_raw_days")
