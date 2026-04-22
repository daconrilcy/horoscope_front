"""archive_prompt_fallback_use_case

Revision ID: 20260422_0072
Revises: 20260420_0071
Create Date: 2026-04-22 18:40:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260422_0072"
down_revision: Union[str, Sequence[str], None] = "20260420_0071"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "llm_prompt_version_fallback_archives",
        sa.Column("prompt_version_id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("use_case_key", sa.String(length=64), nullable=False),
        sa.Column("fallback_use_case_key", sa.String(length=64), nullable=False),
        sa.Column(
            "archived_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.execute(
        sa.text(
            """
            INSERT INTO llm_prompt_version_fallback_archives (
                prompt_version_id,
                use_case_key,
                fallback_use_case_key
            )
            SELECT
                CAST(id AS VARCHAR(64)),
                use_case_key,
                fallback_use_case_key
            FROM llm_prompt_versions
            WHERE fallback_use_case_key IS NOT NULL
            """
        )
    )


def downgrade() -> None:
    op.drop_table("llm_prompt_version_fallback_archives")
