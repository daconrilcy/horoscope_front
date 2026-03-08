"""add is_provisional_calibration to daily prediction runs

Revision ID: 20260308_0039
Revises: 20260308_0038
Create Date: 2026-03-08 14:30:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260308_0039"
down_revision = "20260308_0038"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    column_names = {column["name"] for column in inspector.get_columns("daily_prediction_runs")}
    if "is_provisional_calibration" in column_names:
        return

    op.add_column(
        "daily_prediction_runs",
        sa.Column("is_provisional_calibration", sa.Boolean(), nullable=True),
    )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    column_names = {column["name"] for column in inspector.get_columns("daily_prediction_runs")}
    if "is_provisional_calibration" not in column_names:
        return

    op.drop_column("daily_prediction_runs", "is_provisional_calibration")
