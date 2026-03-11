"""add_v3_daily_metrics_to_category_scores

Revision ID: 20260311_0045
Revises: 20260311_0044
Create Date: 2026-03-11 10:45:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260311_0045"
down_revision: Union[str, Sequence[str], None] = "20260311_0044"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("daily_prediction_category_scores", schema=None) as batch_op:
        batch_op.add_column(sa.Column("score_20", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("intensity_20", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("confidence_20", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("rarity_percentile", sa.Float(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("daily_prediction_category_scores", schema=None) as batch_op:
        batch_op.drop_column("rarity_percentile")
        batch_op.drop_column("confidence_20")
        batch_op.drop_column("intensity_20")
        batch_op.drop_column("score_20")
