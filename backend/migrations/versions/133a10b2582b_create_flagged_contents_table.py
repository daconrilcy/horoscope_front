"""create flagged_contents table

Revision ID: 133a10b2582b
Revises: 35adfdeeceb4
Create Date: 2026-04-05 23:05:45.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '133a10b2582b'
down_revision: Union[str, None] = '35adfdeeceb4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('flagged_contents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=32), nullable=False),
        sa.Column('content_ref_id', sa.String(length=128), nullable=False),
        sa.Column('excerpt', sa.Text(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('reported_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=16), nullable=False),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_flagged_contents_reported_at'), 'flagged_contents', ['reported_at'], unique=False)
    op.create_index(op.f('ix_flagged_contents_status'), 'flagged_contents', ['status'], unique=False)
    op.create_index(op.f('ix_flagged_contents_user_id'), 'flagged_contents', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_flagged_contents_user_id'), table_name='flagged_contents')
    op.drop_index(op.f('ix_flagged_contents_status'), table_name='flagged_contents')
    op.drop_index(op.f('ix_flagged_contents_reported_at'), table_name='flagged_contents')
    op.drop_table('flagged_contents')
