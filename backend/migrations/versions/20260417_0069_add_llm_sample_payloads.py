"""add_llm_sample_payloads

Revision ID: 20260417_0069
Revises: 8a572a8336bf
Create Date: 2026-04-17 17:10:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260417_0069"
down_revision: Union[str, Sequence[str], None] = "8a572a8336bf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "llm_sample_payloads",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("feature", sa.String(length=64), nullable=False),
        sa.Column("locale", sa.String(length=16), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_llm_sample_payloads_feature",
        "llm_sample_payloads",
        ["feature"],
        unique=False,
    )
    op.create_index(
        "ix_llm_sample_payloads_locale",
        "llm_sample_payloads",
        ["locale"],
        unique=False,
    )
    op.create_index(
        "ix_llm_sample_payload_feature_locale_name_unique",
        "llm_sample_payloads",
        ["feature", "locale", "name"],
        unique=True,
    )
    op.create_index(
        "ix_llm_sample_payload_feature_locale_default_unique",
        "llm_sample_payloads",
        ["feature", "locale"],
        unique=True,
        sqlite_where=sa.text("is_default = 1"),
        postgresql_where=sa.text("is_default = true"),
    )


def downgrade() -> None:
    op.drop_index(
        "ix_llm_sample_payload_feature_locale_default_unique", table_name="llm_sample_payloads"
    )
    op.drop_index(
        "ix_llm_sample_payload_feature_locale_name_unique", table_name="llm_sample_payloads"
    )
    op.drop_index("ix_llm_sample_payloads_locale", table_name="llm_sample_payloads")
    op.drop_index("ix_llm_sample_payloads_feature", table_name="llm_sample_payloads")
    op.drop_table("llm_sample_payloads")
