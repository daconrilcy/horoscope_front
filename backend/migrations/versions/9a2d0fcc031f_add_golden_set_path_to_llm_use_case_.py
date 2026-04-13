"""add golden_set_path to llm_use_case_configs

Revision ID: 9a2d0fcc031f
Revises: b91ce4044d7c
Create Date: 2026-04-13 11:07:34.024576
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9a2d0fcc031f"
down_revision: Union[str, Sequence[str], None] = "b91ce4044d7c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "llm_use_case_configs", sa.Column("golden_set_path", sa.String(length=255), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("llm_use_case_configs", "golden_set_path")
