"""add support ticket categories table

Revision ID: d5db148d2557
Revises: d86bb999566a
Create Date: 2026-04-01 21:04:09.270723
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5db148d2557'
down_revision: Union[str, Sequence[str], None] = 'd86bb999566a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'support_ticket_categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('label_fr', sa.String(length=160), nullable=False),
        sa.Column('label_en', sa.String(length=160), nullable=False),
        sa.Column('label_es', sa.String(length=160), nullable=False),
        sa.Column('description_fr', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    with op.batch_alter_table('support_ticket_categories', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_support_ticket_categories_code'), ['code'], unique=True)


def downgrade() -> None:
    op.drop_table('support_ticket_categories')
