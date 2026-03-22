"""create_astrologer_dedicated_tables

Revision ID: c5c208c81831
Revises: 20260321_0051
Create Date: 2026-03-22 18:31:55.975032
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c5c208c81831'
down_revision: Union[str, Sequence[str], None] = '20260321_0051'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'astrologer_profiles',
        sa.Column('persona_id', sa.UUID(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=200), nullable=False),
        sa.Column('gender', sa.String(length=32), nullable=False),
        sa.Column('photo_url', sa.String(length=512), nullable=True),
        sa.Column('public_style_label', sa.String(length=100), nullable=False),
        sa.Column('bio_short', sa.String(length=500), nullable=False),
        sa.Column('bio_long', sa.Text(), nullable=False),
        sa.Column('admin_category', sa.String(length=64), nullable=False),
        sa.Column('specialties', sa.JSON(), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['persona_id'], ['llm_personas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('persona_id')
    )
    op.create_index(
        op.f("ix_astrologer_profiles_admin_category"),
        "astrologer_profiles",
        ["admin_category"],
        unique=False
    )
    op.create_index(
        op.f("ix_astrologer_profiles_is_public"),
        "astrologer_profiles",
        ["is_public"],
        unique=False
    )

    op.create_table(
        "astrologer_prompt_profiles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("persona_id", sa.UUID(), nullable=False),
        sa.Column("prompt_content", sa.Text(), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["persona_id"], ["llm_personas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_astrologer_prompt_profiles_is_active"),
        "astrologer_prompt_profiles",
        ["is_active"],
        unique=False
    )
    op.create_index(
        op.f("ix_astrologer_prompt_profiles_persona_id"),
        "astrologer_prompt_profiles",
        ["persona_id"],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_astrologer_prompt_profiles_persona_id"),
        table_name="astrologer_prompt_profiles"
    )
    op.drop_index(
        op.f("ix_astrologer_prompt_profiles_is_active"),
        table_name="astrologer_prompt_profiles"
    )
    op.drop_table("astrologer_prompt_profiles")
    op.drop_index(
        op.f("ix_astrologer_profiles_is_public"),
        table_name="astrologer_profiles"
    )
    op.drop_index(
        op.f("ix_astrologer_profiles_admin_category"),
        table_name="astrologer_profiles"
    )
    op.drop_table("astrologer_profiles")
