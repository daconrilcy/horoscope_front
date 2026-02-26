"""add geo_place_resolved canonical table for reproducible natal calculations

Revision ID: 20260226_0025
Revises: 20260226_0024
Create Date: 2026-02-26

Architecture note:
  - geo_place_resolved: vérité terrain long terme (pas de TTL)
    Source de vérité canonique pour les coordonnées lat/lon utilisées
    dans les calculs d'éphémérides et de maisons.
  - geocoding_query_cache: cache court terme (TTL, table séparée, story 19-3)

Convention country_code : UPPERCASE ISO2 (ex: "FR", "DE").
Type coordonnées : NUMERIC(10,7) — DECIMAL stable, précision sub-métrique.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260226_0025"
down_revision: Union[str, Sequence[str], None] = "20260226_0024"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "geo_place_resolved",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        # Identité provider
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("provider_place_id", sa.BigInteger(), nullable=False),
        sa.Column("osm_type", sa.String(length=32), nullable=True),
        sa.Column("osm_id", sa.BigInteger(), nullable=True),
        sa.Column("display_name", sa.String(length=1024), nullable=False),
        sa.Column("place_type", sa.String(length=128), nullable=True),
        sa.Column("place_class", sa.String(length=128), nullable=True),
        sa.Column("importance", sa.Float(), nullable=True),
        sa.Column("place_rank", sa.Integer(), nullable=True),
        # Coordonnées DECIMAL (reproductibilité, AC2)
        sa.Column("latitude", sa.Numeric(precision=10, scale=7), nullable=False),
        sa.Column("longitude", sa.Numeric(precision=10, scale=7), nullable=False),
        # Hiérarchie géo
        sa.Column("country_code", sa.String(length=2), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("county", sa.String(length=100), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("postcode", sa.String(length=20), nullable=True),
        # Timezone (optionnel)
        sa.Column("timezone_iana", sa.String(length=64), nullable=True),
        sa.Column("timezone_source", sa.String(length=32), nullable=True),
        sa.Column("timezone_confidence", sa.Float(), nullable=True),
        # Qualité / traçabilité
        sa.Column("normalized_query", sa.String(length=512), nullable=True),
        sa.Column("query_language", sa.String(length=32), nullable=True),
        sa.Column("query_country_code", sa.String(length=2), nullable=True),
        sa.Column("raw_hash", sa.String(length=64), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        # Constraints
        sa.CheckConstraint(
            "latitude >= -90 AND latitude <= 90",
            name="ck_geo_place_resolved_lat_range",
        ),
        sa.CheckConstraint(
            "longitude >= -180 AND longitude <= 180",
            name="ck_geo_place_resolved_lon_range",
        ),
        sa.CheckConstraint(
            "provider = 'nominatim'",
            name="ck_geo_place_resolved_provider",
        ),
        sa.UniqueConstraint(
            "provider",
            "provider_place_id",
            name="uq_geo_place_resolved_provider_place_id",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_geo_place_resolved_lat_lon",
        "geo_place_resolved",
        ["latitude", "longitude"],
        unique=False,
    )
    op.create_index(
        "ix_geo_place_resolved_normalized_query",
        "geo_place_resolved",
        ["normalized_query"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_geo_place_resolved_normalized_query", table_name="geo_place_resolved")
    op.drop_index("ix_geo_place_resolved_lat_lon", table_name="geo_place_resolved")
    op.drop_table("geo_place_resolved")
