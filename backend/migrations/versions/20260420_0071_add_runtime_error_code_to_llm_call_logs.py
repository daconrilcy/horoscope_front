"""add_runtime_error_code_to_llm_call_logs

Revision ID: 20260420_0071
Revises: 20260419_0070
Create Date: 2026-04-20 12:10:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260420_0071"
down_revision: Union[str, Sequence[str], None] = "20260419_0070"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "llm_call_logs",
        sa.Column("runtime_error_code", sa.String(length=80), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("llm_call_logs", "runtime_error_code")
