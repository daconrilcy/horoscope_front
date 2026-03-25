"""add default_astrologer_id to users

Revision ID: dd729c20741e
Revises: f1274b6a70ac
Create Date: 2026-03-24 14:02:06.371115
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'dd729c20741e'
down_revision: Union[str, Sequence[str], None] = 'f1274b6a70ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('default_astrologer_id', sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'default_astrologer_id')
