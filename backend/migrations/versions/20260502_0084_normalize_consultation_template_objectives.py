"""normalise consultation template prompt_content objectives

Revision ID: 20260502_0084
Revises: 20260425_0083
Create Date: 2026-05-02 00:00:00
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260502_0084"
down_revision: Union[str, Sequence[str], None] = "20260425_0083"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CONSULTATION_OBJECTIVES: dict[str, str] = {
    "period": "Comprendre le climat astrologique de la periode demandee.",
    "career": "Eclairer une interaction ou une decision liee au travail.",
    "orientation": "Clarifier une direction de vie ou une decision structurante.",
    "relationship": "Lire la dynamique relationnelle de maniere prudente et non fataliste.",
    "timing": "Identifier le bon tempo d action avec une lecture astrologique prudente.",
}


def upgrade() -> None:
    """Remplace les anciens prompts consultation par des objectifs produit courts."""
    consultation_templates = sa.table(
        "consultation_templates",
        sa.column("key", sa.String()),
        sa.column("prompt_content", sa.Text()),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )

    for template_key, objective in _CONSULTATION_OBJECTIVES.items():
        op.execute(
            consultation_templates.update()
            .where(consultation_templates.c.key == template_key)
            .values(prompt_content=objective, updated_at=sa.func.current_timestamp())
        )


def downgrade() -> None:
    """Ne restaure pas les anciens prompts provider-like retires par cette migration."""
