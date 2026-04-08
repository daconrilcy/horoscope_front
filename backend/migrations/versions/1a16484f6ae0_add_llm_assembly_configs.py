"""add_llm_assembly_configs

Revision ID: 1a16484f6ae0
Revises: 51bdec8ae9a5
Create Date: 2026-04-08 00:01:05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a16484f6ae0'
down_revision: Union[str, Sequence[str], None] = '51bdec8ae9a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('llm_assembly_configs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('feature', sa.String(length=64), nullable=False),
        sa.Column('subfeature', sa.String(length=64), nullable=True),
        sa.Column('plan', sa.String(length=64), nullable=True),
        sa.Column('locale', sa.String(length=16), nullable=False),
        sa.Column('feature_template_ref', sa.UUID(), nullable=False),
        sa.Column('subfeature_template_ref', sa.UUID(), nullable=True),
        sa.Column('persona_ref', sa.UUID(), nullable=True),
        sa.Column('plan_rules_ref', sa.String(length=64), nullable=True),
        sa.Column('execution_config', sa.JSON(), nullable=False),
        sa.Column('output_contract_ref', sa.String(length=64), nullable=True),
        sa.Column('feature_enabled', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('subfeature_enabled', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('persona_enabled', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('plan_rules_enabled', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(length=16), nullable=False, server_default='draft'),
        sa.Column('created_by', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['feature_template_ref'], ['llm_prompt_versions.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['persona_ref'], ['llm_personas.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['subfeature_template_ref'], ['llm_prompt_versions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('llm_assembly_configs', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_llm_assembly_configs_feature'), ['feature'], unique=False)
        batch_op.create_index(batch_op.f('ix_llm_assembly_configs_locale'), ['locale'], unique=False)
        batch_op.create_index(batch_op.f('ix_llm_assembly_configs_plan'), ['plan'], unique=False)
        batch_op.create_index(batch_op.f('ix_llm_assembly_configs_status'), ['status'], unique=False)
        batch_op.create_index(batch_op.f('ix_llm_assembly_configs_subfeature'), ['subfeature'], unique=False)
        batch_op.create_index(batch_op.f('ix_llm_assembly_configs_created_at'), ['created_at'], unique=False)
        batch_op.create_index(
            'ix_llm_assembly_config_active_unique',
            ['feature', sa.text("coalesce(subfeature, '')"), sa.text("coalesce(plan, '')"), 'locale'],
            unique=True,
            postgresql_where=sa.text("status = 'published'"),
            sqlite_where=sa.text("status = 'published'")
        )

def downgrade() -> None:
    op.drop_table('llm_assembly_configs')
