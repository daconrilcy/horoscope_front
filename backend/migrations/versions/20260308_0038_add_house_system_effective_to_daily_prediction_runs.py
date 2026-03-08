"""add house_system_effective to daily prediction runs

Revision ID: 20260308_0038
Revises: 20260308_0037
Create Date: 2026-03-08 11:30:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260308_0038"
down_revision = "20260308_0037"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    column_names = {column["name"] for column in inspector.get_columns("daily_prediction_runs")}
    if "house_system_effective" in column_names:
        return

    op.add_column(
        "daily_prediction_runs",
        sa.Column("house_system_effective", sa.String(length=16), nullable=True),
    )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    column_names = {column["name"] for column in inspector.get_columns("daily_prediction_runs")}
    if "house_system_effective" not in column_names:
        return

    op.drop_column("daily_prediction_runs", "house_system_effective")
