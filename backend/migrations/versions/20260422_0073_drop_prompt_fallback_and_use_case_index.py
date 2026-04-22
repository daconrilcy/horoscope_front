"""drop_prompt_fallback_and_use_case_index

Revision ID: 20260422_0073
Revises: 20260422_0072
Create Date: 2026-04-22 18:50:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260422_0073"
down_revision: Union[str, Sequence[str], None] = "20260422_0072"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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
              AND NOT EXISTS (
                  SELECT 1
                  FROM llm_prompt_version_fallback_archives AS archive
                  WHERE archive.prompt_version_id = CAST(llm_prompt_versions.id AS VARCHAR(64))
              )
            """
        )
    )
    op.drop_index("ix_llm_call_logs_use_case_timestamp", table_name="llm_call_logs")
    with op.batch_alter_table("llm_prompt_versions") as batch_op:
        batch_op.drop_column("fallback_use_case_key")


def downgrade() -> None:
    with op.batch_alter_table("llm_prompt_versions") as batch_op:
        batch_op.add_column(sa.Column("fallback_use_case_key", sa.String(length=64), nullable=True))

    op.execute(
        sa.text(
            """
            UPDATE llm_prompt_versions
            SET fallback_use_case_key = (
                SELECT archive.fallback_use_case_key
                FROM llm_prompt_version_fallback_archives AS archive
                WHERE archive.prompt_version_id = CAST(llm_prompt_versions.id AS VARCHAR(64))
            )
            WHERE EXISTS (
                SELECT 1
                FROM llm_prompt_version_fallback_archives AS archive
                WHERE archive.prompt_version_id = CAST(llm_prompt_versions.id AS VARCHAR(64))
            )
            """
        )
    )
    op.create_index(
        "ix_llm_call_logs_use_case_timestamp",
        "llm_call_logs",
        ["use_case", "timestamp"],
        unique=False,
    )
