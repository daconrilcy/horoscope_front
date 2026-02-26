"""add geocoding_query_cache table (short-term TTL cache, separate from geo_place_resolved)

Revision ID: 20260226_0024
Revises: 20260225_0023
Create Date: 2026-02-26

Architecture note:
  - geocoding_query_cache: optimisation court terme (TTL configurable, défaut 1h)
  - geo_place_resolved (story 19-4): vérité terrain long terme (pas de TTL)
  Ces deux tables sont explicitement séparées et indépendantes.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260226_0024"
down_revision: Union[str, Sequence[str], None] = "20260225_0023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "geocoding_query_cache",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("query_key", sa.String(length=64), nullable=False),
        sa.Column("response_json", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_geocoding_query_cache_query_key",
        "geocoding_query_cache",
        ["query_key"],
        unique=True,
    )
    op.create_index(
        "ix_geocoding_query_cache_expires_at",
        "geocoding_query_cache",
        ["expires_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_geocoding_query_cache_expires_at", table_name="geocoding_query_cache")
    op.drop_index("ix_geocoding_query_cache_query_key", table_name="geocoding_query_cache")
    op.drop_table("geocoding_query_cache")
