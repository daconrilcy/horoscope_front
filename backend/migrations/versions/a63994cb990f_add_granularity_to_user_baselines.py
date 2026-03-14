"""add granularity to user baselines

Revision ID: a63994cb990f
Revises: fbdf4f0c6837
Create Date: 2026-03-11 19:11:53.030436
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a63994cb990f"
down_revision: Union[str, Sequence[str], None] = "fbdf4f0c6837"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("user_prediction_baselines", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "granularity_type",
                sa.Enum("DAY", "SLOT", "SEASON", "MONTH", name="baselinegranularity"),
                nullable=False,
                server_default="DAY",
            )
        )
        batch_op.add_column(
            sa.Column(
                "granularity_value", sa.String(length=32), nullable=False, server_default="all"
            )
        )

    # Backfill legacy rows (should already be covered by server_default
    # but safer for existing data before constraint application)
    op.execute(
        "UPDATE user_prediction_baselines "
        "SET granularity_value = 'all' "
        "WHERE granularity_value IS NULL"
    )

    with op.batch_alter_table("user_prediction_baselines", schema=None) as batch_op:
        batch_op.drop_constraint("uq_user_prediction_baseline", type_="unique")
        batch_op.create_unique_constraint(
            "uq_user_prediction_baseline",
            [
                "user_id",
                "category_id",
                "granularity_type",
                "granularity_value",
                "window_start_date",
                "window_end_date",
                "reference_version_id",
                "ruleset_id",
                "house_system_effective",
            ],
        )
        batch_op.create_index(
            batch_op.f("ix_user_prediction_baselines_granularity_type"),
            ["granularity_type"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_user_prediction_baselines_granularity_value"),
            ["granularity_value"],
            unique=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("user_prediction_baselines", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_user_prediction_baselines_granularity_value"))
        batch_op.drop_index(batch_op.f("ix_user_prediction_baselines_granularity_type"))
        batch_op.drop_constraint("uq_user_prediction_baseline", type_="unique")
        batch_op.create_unique_constraint(
            "uq_user_prediction_baseline",
            [
                "user_id",
                "category_id",
                "window_start_date",
                "window_end_date",
                "reference_version_id",
                "ruleset_id",
                "house_system_effective",
            ],
        )
        batch_op.drop_column("granularity_value")
        batch_op.drop_column("granularity_type")
