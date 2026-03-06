"""dedupe and add uniqueness constraints for user_natal_interpretations

Revision ID: 20260304_0028
Revises: ee2645ed1a1c
Create Date: 2026-03-04
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260304_0028"
down_revision: Union[str, Sequence[str], None] = "ee2645ed1a1c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _dedupe_user_natal_interpretations() -> None:
    # Keep the most recent row per logical key for NULL persona_id.
    op.execute(
        sa.text(
            """
            DELETE FROM user_natal_interpretations
            WHERE id IN (
                SELECT id
                FROM (
                    SELECT
                        id,
                        ROW_NUMBER() OVER (
                            PARTITION BY user_id, chart_id, level
                            ORDER BY created_at DESC, id DESC
                        ) AS rn
                    FROM user_natal_interpretations
                    WHERE persona_id IS NULL
                ) ranked
                WHERE rn > 1
            )
            """
        )
    )

    # Keep the most recent row per logical key for non-NULL persona_id.
    op.execute(
        sa.text(
            """
            DELETE FROM user_natal_interpretations
            WHERE id IN (
                SELECT id
                FROM (
                    SELECT
                        id,
                        ROW_NUMBER() OVER (
                            PARTITION BY user_id, chart_id, level, persona_id
                            ORDER BY created_at DESC, id DESC
                        ) AS rn
                    FROM user_natal_interpretations
                    WHERE persona_id IS NOT NULL
                ) ranked
                WHERE rn > 1
            )
            """
        )
    )


def upgrade() -> None:
    _dedupe_user_natal_interpretations()

    # persona_id NULL: enforce uniqueness on (user_id, chart_id, level)
    op.create_index(
        "uq_user_natal_interpretations_null_persona",
        "user_natal_interpretations",
        ["user_id", "chart_id", "level"],
        unique=True,
        postgresql_where=sa.text("persona_id IS NULL"),
        sqlite_where=sa.text("persona_id IS NULL"),
    )

    # persona_id NOT NULL: enforce uniqueness on (user_id, chart_id, level, persona_id)
    op.create_index(
        "uq_user_natal_interpretations_with_persona",
        "user_natal_interpretations",
        ["user_id", "chart_id", "level", "persona_id"],
        unique=True,
        postgresql_where=sa.text("persona_id IS NOT NULL"),
        sqlite_where=sa.text("persona_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_user_natal_interpretations_with_persona",
        table_name="user_natal_interpretations",
    )
    op.drop_index(
        "uq_user_natal_interpretations_null_persona",
        table_name="user_natal_interpretations",
    )
