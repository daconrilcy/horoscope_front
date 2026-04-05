"""add commercial_gestures to user_subscriptions

Revision ID: 35adfdeeceb4
Revises: ce173983d275
Create Date: 2026-04-05 22:52:45.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '35adfdeeceb4'
down_revision: Union[str, None] = 'ce173983d275'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user_subscriptions', sa.Column('commercial_gestures', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('subscription_plan_changes', sa.Column('commercial_gestures', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('payment_attempts', sa.Column('commercial_gestures', sa.JSON(), nullable=False, server_default='[]'))


def downgrade() -> None:
    op.drop_column('payment_attempts', 'commercial_gestures')
    op.drop_column('subscription_plan_changes', 'commercial_gestures')
    op.drop_column('user_subscriptions', 'commercial_gestures')
