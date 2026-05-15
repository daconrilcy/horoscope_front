"""add default_orb_deg to aspects

Revision ID: 20260226_0027
Revises: 20260226_0026
Create Date: 2026-02-26
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

FALLBACK_ORB_DEGREES = 6.0
MAJOR_ORB_DEGREES = {
    "conjunction": 8.0,
    "sextile": 4.0,
    "square": 6.0,
    "trine": 6.0,
    "opposition": 8.0,
}

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
                server_default=sa.text(str(FALLBACK_ORB_DEGREES)),
            )
        )

    op.execute(
        sa.text(
            f"""
            UPDATE aspects
            SET default_orb_deg = CASE code
                WHEN 'conjunction' THEN {MAJOR_ORB_DEGREES["conjunction"]}
                WHEN 'sextile' THEN {MAJOR_ORB_DEGREES["sextile"]}
                WHEN 'square' THEN {MAJOR_ORB_DEGREES["square"]}
                WHEN 'trine' THEN {MAJOR_ORB_DEGREES["trine"]}
                WHEN 'opposition' THEN {MAJOR_ORB_DEGREES["opposition"]}
                ELSE {FALLBACK_ORB_DEGREES}
            END
            """
        )
    )

    with op.batch_alter_table("aspects", schema=None) as batch_op:
        batch_op.alter_column("default_orb_deg", nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("aspects", schema=None) as batch_op:
        batch_op.drop_column("default_orb_deg")
