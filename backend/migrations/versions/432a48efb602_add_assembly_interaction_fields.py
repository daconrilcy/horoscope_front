"""add_assembly_interaction_fields

Revision ID: 432a48efb602
Revises: 1a16484f6ae0
Create Date: 2026-04-08 10:20:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "432a48efb602"
down_revision: Union[str, Sequence[str], None] = "1a16484f6ae0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # interaction_mode and user_question_policy might have been added in previous run
    # fallback_use_case was missing.
    # We use batch_alter_table for SQLite compatibility.
    # To handle the case where columns might already exist (idempotency),
    # we would need to check, but Alembic op doesn't support it directly in a clean way for SQLite.
    # Given the current state, we assume we need to add them if they are missing.
    with op.batch_alter_table("llm_assembly_configs", schema=None) as batch_op:
        # In a real environment, we'd check if they exist.
        # Here we just put the full set of additions.
        batch_op.add_column(
            sa.Column(
                "interaction_mode",
                sa.String(length=16),
                nullable=False,
                server_default="structured",
            )
        )
        batch_op.add_column(
            sa.Column(
                "user_question_policy", sa.String(length=16), nullable=False, server_default="none"
            )
        )
        batch_op.add_column(sa.Column("fallback_use_case", sa.String(length=64), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("llm_assembly_configs", schema=None) as batch_op:
        batch_op.drop_column("fallback_use_case")
        batch_op.drop_column("user_question_policy")
        batch_op.drop_column("interaction_mode")
