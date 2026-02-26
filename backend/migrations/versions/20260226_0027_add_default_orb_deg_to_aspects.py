"""add default_orb_deg to aspects

Revision ID: 20260226_0027
Revises: 20260226_0026
Create Date: 2026-02-26
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.core.constants import DEFAULT_ASPECT_ORBS, DEFAULT_FALLBACK_ORB

# revision identifiers, used by Alembic.
revision: str = "20260226_0027"
down_revision: Union[str, Sequence[str], None] = "20260226_0026"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("aspects", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "default_orb_deg",
                sa.Float(),
                nullable=True,
                server_default=sa.text(str(DEFAULT_FALLBACK_ORB)),
            )
        )

    op.execute(
        sa.text(
            f"""
            UPDATE aspects
            SET default_orb_deg = CASE code
                WHEN 'conjunction' THEN {DEFAULT_ASPECT_ORBS['conjunction']}
                WHEN 'sextile' THEN {DEFAULT_ASPECT_ORBS['sextile']}
                WHEN 'square' THEN {DEFAULT_ASPECT_ORBS['square']}
                WHEN 'trine' THEN {DEFAULT_ASPECT_ORBS['trine']}
                WHEN 'opposition' THEN {DEFAULT_ASPECT_ORBS['opposition']}
                ELSE {DEFAULT_FALLBACK_ORB}
            END
            """
        )
    )

    with op.batch_alter_table("aspects", schema=None) as batch_op:
        batch_op.alter_column("default_orb_deg", nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("aspects", schema=None) as batch_op:
        batch_op.drop_column("default_orb_deg")
