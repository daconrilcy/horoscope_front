"""add daily prediction engine identity

Revision ID: 20260311_0044
Revises: 20260310_0043
Create Date: 2026-03-11
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260311_0044"
down_revision: Union[str, Sequence[str], None] = "20260310_0043"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLE_NAME = "daily_prediction_runs"
OLD_CONSTRAINT = "uq_daily_prediction_runs_user_date_ruleset"


def upgrade() -> None:
    with op.batch_alter_table(TABLE_NAME, schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("engine_mode", sa.String(length=16), nullable=False, server_default="v2")
        )
        batch_op.add_column(sa.Column("engine_version", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("snapshot_version", sa.String(length=32), nullable=True))
        batch_op.add_column(
            sa.Column("evidence_pack_version", sa.String(length=32), nullable=True)
        )
        batch_op.drop_constraint(OLD_CONSTRAINT, type_="unique")
        batch_op.create_unique_constraint(
            OLD_CONSTRAINT,
            [
                "user_id",
                "local_date",
                "reference_version_id",
                "ruleset_id",
                "engine_mode",
            ],
        )


def downgrade() -> None:
    with op.batch_alter_table(TABLE_NAME, schema=None) as batch_op:
        batch_op.drop_constraint(OLD_CONSTRAINT, type_="unique")
        batch_op.create_unique_constraint(
            OLD_CONSTRAINT,
            [
                "user_id",
                "local_date",
                "reference_version_id",
                "ruleset_id",
            ],
        )
        batch_op.drop_column("evidence_pack_version")
        batch_op.drop_column("snapshot_version")
        batch_op.drop_column("engine_version")
        batch_op.drop_column("engine_mode")
