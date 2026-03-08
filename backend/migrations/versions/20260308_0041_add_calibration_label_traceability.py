"""add calibration label traceability

Revision ID: 20260308_0041
Revises: 20260308_0040
Create Date: 2026-03-08 18:30:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260308_0041"
down_revision = "20260308_0040"
branch_labels = None
depends_on = None


def upgrade():
    # 1. DailyPredictionRunModel — traceability columns
    op.add_column(
        "daily_prediction_runs",
        sa.Column("calibration_label", sa.String(length=64), nullable=True),
    )

    # 2. CategoryCalibrationModel — calibration associated with percentiles
    op.add_column(
        "category_calibrations",
        sa.Column(
            "calibration_label",
            sa.String(length=64),
            nullable=False,
            server_default="provisional",
        ),
    )


def downgrade():
    op.drop_column("category_calibrations", "calibration_label")
    op.drop_column("daily_prediction_runs", "calibration_label")
