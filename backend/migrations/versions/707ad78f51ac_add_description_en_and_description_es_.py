"""add description_en and description_es to support ticket categories

Revision ID: 707ad78f51ac
Revises: d5db148d2557
Create Date: 2026-04-01 21:56:27.912901
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '707ad78f51ac'
down_revision: Union[str, Sequence[str], None] = 'd5db148d2557'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('support_ticket_categories', sa.Column('description_en', sa.Text(), nullable=True))
    op.add_column('support_ticket_categories', sa.Column('description_es', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('support_ticket_categories', 'description_es')
    op.drop_column('support_ticket_categories', 'description_en')
