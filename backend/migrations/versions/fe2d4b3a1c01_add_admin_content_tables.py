"""add admin content tables

Revision ID: fe2d4b3a1c01
Revises: fd1d41d35808
Create Date: 2026-04-06 02:50:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "fe2d4b3a1c01"
down_revision = "fd1d41d35808"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "config_texts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_config_texts_category"), "config_texts", ["category"], unique=False)
    op.create_index(op.f("ix_config_texts_key"), "config_texts", ["key"], unique=True)
    op.create_index(
        op.f("ix_config_texts_updated_at"), "config_texts", ["updated_at"], unique=False
    )
    op.create_index(
        op.f("ix_config_texts_updated_by_user_id"),
        "config_texts",
        ["updated_by_user_id"],
        unique=False,
    )

    op.create_table(
        "editorial_template_versions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("template_code", sa.String(length=64), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("expected_tags", sa.JSON(), nullable=False),
        sa.Column("example_render", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_editorial_template_versions_created_by_user_id"),
        "editorial_template_versions",
        ["created_by_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_editorial_template_versions_status"),
        "editorial_template_versions",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_editorial_template_versions_template_code"),
        "editorial_template_versions",
        ["template_code"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_editorial_template_versions_template_code"),
        table_name="editorial_template_versions",
    )
    op.drop_index(
        op.f("ix_editorial_template_versions_status"), table_name="editorial_template_versions"
    )
    op.drop_index(
        op.f("ix_editorial_template_versions_created_by_user_id"),
        table_name="editorial_template_versions",
    )
    op.drop_table("editorial_template_versions")

    op.drop_index(op.f("ix_config_texts_updated_by_user_id"), table_name="config_texts")
    op.drop_index(op.f("ix_config_texts_updated_at"), table_name="config_texts")
    op.drop_index(op.f("ix_config_texts_key"), table_name="config_texts")
    op.drop_index(op.f("ix_config_texts_category"), table_name="config_texts")
    op.drop_table("config_texts")
