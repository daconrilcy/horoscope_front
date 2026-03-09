"""Add is_provisional to daily_prediction_category_scores

Revision ID: 20260308_0042
Revises: 20260308_0041
Create Date: 2026-03-08 19:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260308_0042"
down_revision = "20260308_0041"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "daily_prediction_category_scores",
        sa.Column("is_provisional", sa.Boolean(), nullable=True),
    )


def downgrade():
    op.drop_column("daily_prediction_category_scores", "is_provisional")
