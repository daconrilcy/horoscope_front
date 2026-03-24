"""add stripe billing profiles

Revision ID: 20260324_0053
Revises: dd729c20741e
Create Date: 2026-03-24 00:53:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '20260324_0053'
down_revision: Union[str, Sequence[str], None] = 'dd729c20741e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'stripe_billing_profiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stripe_customer_id', sa.String(length=128), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=128), nullable=True),
        sa.Column('stripe_price_id', sa.String(length=128), nullable=True),
        sa.Column('subscription_status', sa.String(length=64), nullable=True),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancel_at_period_end', sa.Boolean(), nullable=False),
        sa.Column('entitlement_plan', sa.String(length=32), nullable=False),
        sa.Column('billing_email', sa.String(length=255), nullable=True),
        sa.Column('last_stripe_event_id', sa.String(length=128), nullable=True),
        sa.Column('last_stripe_event_created', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_stripe_event_type', sa.String(length=64), nullable=True),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_stripe_billing_profiles_user_id')
    )
    op.create_index(
        'ix_stripe_billing_profiles_stripe_customer_id',
        'stripe_billing_profiles',
        ['stripe_customer_id'],
        unique=False
    )
    op.create_index(
        'ix_stripe_billing_profiles_stripe_subscription_id',
        'stripe_billing_profiles',
        ['stripe_subscription_id'],
        unique=False
    )
    op.create_index(
        'ix_stripe_billing_profiles_last_stripe_event_id',
        'stripe_billing_profiles',
        ['last_stripe_event_id'],
        unique=False
    )
    op.create_index(
        'ix_stripe_billing_profiles_user_id',
        'stripe_billing_profiles',
        ['user_id'],
        unique=False
    )

    # Index uniques partiels PostgreSQL
    op.create_index(
        'uq_stripe_billing_profiles_customer_id',
        'stripe_billing_profiles',
        ['stripe_customer_id'],
        unique=True,
        postgresql_where=sa.text('stripe_customer_id IS NOT NULL')
    )
    op.create_index(
        'uq_stripe_billing_profiles_subscription_id',
        'stripe_billing_profiles',
        ['stripe_subscription_id'],
        unique=True,
        postgresql_where=sa.text('stripe_subscription_id IS NOT NULL')
    )


def downgrade() -> None:
    op.drop_index(
        'uq_stripe_billing_profiles_subscription_id',
        table_name='stripe_billing_profiles',
        postgresql_where=sa.text('stripe_subscription_id IS NOT NULL')
    )
    op.drop_index(
        'uq_stripe_billing_profiles_customer_id',
        table_name='stripe_billing_profiles',
        postgresql_where=sa.text('stripe_customer_id IS NOT NULL')
    )
    op.drop_index(
        'ix_stripe_billing_profiles_user_id',
        table_name='stripe_billing_profiles'
    )
    op.drop_index(
        'ix_stripe_billing_profiles_last_stripe_event_id',
        table_name='stripe_billing_profiles'
    )
    op.drop_index(
        'ix_stripe_billing_profiles_stripe_subscription_id',
        table_name='stripe_billing_profiles'
    )
    op.drop_index(
        'ix_stripe_billing_profiles_stripe_customer_id',
        table_name='stripe_billing_profiles'
    )
    op.drop_table('stripe_billing_profiles')
