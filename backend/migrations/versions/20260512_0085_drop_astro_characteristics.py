"""drop astro characteristics

Revision ID: 20260512_0085
Revises: 20260502_0084
Create Date: 2026-05-12
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260512_0085"
down_revision: Union[str, Sequence[str], None] = "20260502_0084"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Supprime la table generique inutilisee des caracteristiques astro."""
    op.drop_index("ix_astro_characteristics_entity_code", table_name="astro_characteristics")
    op.drop_index("ix_astro_characteristics_entity_type", table_name="astro_characteristics")
    op.drop_index(
        "ix_astro_characteristics_reference_version_id",
        table_name="astro_characteristics",
    )
    op.drop_table("astro_characteristics")


def downgrade() -> None:
    """Recree la table historique pour permettre un rollback Alembic."""
    op.create_table(
        "astro_characteristics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("reference_version_id", sa.Integer(), nullable=False),
        sa.Column("entity_type", sa.String(length=32), nullable=False),
        sa.Column("entity_code", sa.String(length=64), nullable=False),
        sa.Column("trait", sa.String(length=64), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["reference_version_id"], ["reference_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "reference_version_id",
            "entity_type",
            "entity_code",
            "trait",
        ),
    )
    op.create_index(
        "ix_astro_characteristics_reference_version_id",
        "astro_characteristics",
        ["reference_version_id"],
        unique=False,
    )
    op.create_index(
        "ix_astro_characteristics_entity_type",
        "astro_characteristics",
        ["entity_type"],
        unique=False,
    )
    op.create_index(
        "ix_astro_characteristics_entity_code",
        "astro_characteristics",
        ["entity_code"],
        unique=False,
    )
