"""add_reasoning_effort_verbosity_to_prompts

Revision ID: 4b2d52442492
Revises: 12216bc815ed
Create Date: 2026-03-02 13:56:18.572176
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4b2d52442492"
down_revision: Union[str, Sequence[str], None] = "12216bc815ed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "llm_prompt_versions",
        sa.Column("reasoning_effort", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "llm_prompt_versions",
        sa.Column("verbosity", sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("llm_prompt_versions", "verbosity")
    op.drop_column("llm_prompt_versions", "reasoning_effort")
