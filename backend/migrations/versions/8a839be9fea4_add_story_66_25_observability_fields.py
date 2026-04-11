"""Add story 66.25 observability fields

Revision ID: 8a839be9fea4
Revises: 5e52f7244424
Create Date: 2026-04-11 02:14:04.754770
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8a839be9fea4'
down_revision: Union[str, Sequence[str], None] = '5e52f7244424'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('llm_call_logs', schema=None) as batch_op:
        # provider might already exist in some environments or not
        # To be safe, we check if we need to add it or if it was missed in previous migrations
        # But here we just follow autogenerate for the new fields
        batch_op.add_column(sa.Column('pipeline_kind', sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column('execution_path_kind', sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column('fallback_kind', sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column('requested_provider', sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column('resolved_provider', sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column('executed_provider', sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column('context_compensation_status', sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column('max_output_tokens_source', sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column('max_output_tokens_final', sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('llm_call_logs', schema=None) as batch_op:
        batch_op.drop_column('max_output_tokens_final')
        batch_op.drop_column('max_output_tokens_source')
        batch_op.drop_column('context_compensation_status')
        batch_op.drop_column('executed_provider')
        batch_op.drop_column('resolved_provider')
        batch_op.drop_column('requested_provider')
        batch_op.drop_column('fallback_kind')
        batch_op.drop_column('execution_path_kind')
        batch_op.drop_column('pipeline_kind')
