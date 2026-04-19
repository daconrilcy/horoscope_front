"""remap_llm_prompt_archived_to_inactive

Revision ID: 20260419_0070
Revises: 20260417_0069
Create Date: 2026-04-19 11:15:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260419_0070"
down_revision: Union[str, Sequence[str], None] = "20260417_0069"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE llm_prompt_versions
            SET status = 'inactive'
            WHERE status = 'archived'
            """
        )
    )


def downgrade() -> None:
    # This data remap is intentionally irreversible because the original
    # archived/inactive provenance is not preserved once normalized.
    return None
