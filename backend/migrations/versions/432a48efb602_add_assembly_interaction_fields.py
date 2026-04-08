"""add_assembly_interaction_fields

Revision ID: 432a48efb602
Revises: 1a16484f6ae0
Create Date: 2026-04-08 10:20:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '432a48efb602'
down_revision: Union[str, Sequence[str], None] = '1a16484f6ae0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('llm_assembly_configs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('interaction_mode', sa.String(length=16), nullable=False, server_default='structured'))
        batch_op.add_column(sa.Column('user_question_policy', sa.String(length=16), nullable=False, server_default='none'))

def downgrade() -> None:
    with op.batch_alter_table('llm_assembly_configs', schema=None) as batch_op:
        batch_op.drop_column('user_question_policy')
        batch_op.drop_column('interaction_mode')
