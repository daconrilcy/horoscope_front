"""add contributors_json

Revision ID: 20260308_0037
Revises: 20260307_0036
Create Date: 2026-03-08 10:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260308_0037"
down_revision = "20260307_0036"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    column_names = {
        column["name"] for column in inspector.get_columns("daily_prediction_category_scores")
    }
    if "contributors_json" in column_names:
        return

    op.add_column(
        "daily_prediction_category_scores",
        sa.Column("contributors_json", sa.Text(), nullable=True),
    )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    column_names = {
        column["name"] for column in inspector.get_columns("daily_prediction_category_scores")
    }
    if "contributors_json" not in column_names:
        return

    op.drop_column("daily_prediction_category_scores", "contributors_json")
