"""add input_schema to assembly

Revision ID: 8b2d52442493
Revises: 8a839be9fea4
Create Date: 2026-04-11 15:30:00.000000

"""
from typing import Sequence, Union, Optional

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b2d52442493'
down_revision: Union[str, Sequence[str], None] = '8a839be9fea4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Story 66.29: Add input_schema column to llm_assembly_configs for Stage 1.5 validation support
    op.add_column('llm_assembly_configs', sa.Column('input_schema', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('llm_assembly_configs', 'input_schema')
