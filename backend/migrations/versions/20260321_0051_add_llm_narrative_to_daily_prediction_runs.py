"""add llm_narrative_json to daily_prediction_runs

Revision ID: 20260321_0051
Revises: 20260320_0050
Create Date: 2026-03-21 19:10:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260321_0051"
down_revision = "20260320_0050"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "daily_prediction_runs",
        sa.Column("llm_narrative_json", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("daily_prediction_runs", "llm_narrative_json")
