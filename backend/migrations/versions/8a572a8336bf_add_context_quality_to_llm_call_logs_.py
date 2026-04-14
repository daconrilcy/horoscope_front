"""Add context_quality to llm_call_logs and code to llm_personas surgical

Revision ID: 8a572a8336bf
Revises: 9a2d0fcc031f
Create Date: 2026-04-13 18:35:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8a572a8336bf"
down_revision: Union[str, Sequence[str], None] = "9a2d0fcc031f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add context_quality to llm_call_logs
    with op.batch_alter_table("llm_call_logs", schema=None) as batch_op:
        batch_op.add_column(sa.Column("context_quality", sa.String(length=32), nullable=True))

    # Add code to llm_personas
    with op.batch_alter_table("llm_personas", schema=None) as batch_op:
        batch_op.add_column(sa.Column("code", sa.String(length=64), nullable=True))
        batch_op.create_index(batch_op.f("ix_llm_personas_code"), ["code"], unique=True)


def downgrade() -> None:
    with op.batch_alter_table("llm_personas", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_llm_personas_code"))
        batch_op.drop_column("code")

    with op.batch_alter_table("llm_call_logs", schema=None) as batch_op:
        batch_op.drop_column("context_quality")
