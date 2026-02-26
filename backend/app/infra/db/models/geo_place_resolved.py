from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Float,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class GeoPlaceResolvedModel(Base):
    """Lieu de naissance résolu de manière canonique.

    Source de vérité stable pour les coordonnées utilisées dans les
    calculs d'éphémérides. Séparé de geocoding_query_cache (TTL) :
    cette table n'a pas de date d'expiration — elle représente la vérité
    terrain durable.

    Convention : country_code stocké en UPPERCASE ISO2 (ex: "FR", "DE").
    """

    __tablename__ = "geo_place_resolved"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # --- Identité provider ---
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    provider_place_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    osm_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    osm_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    display_name: Mapped[str] = mapped_column(String(1024), nullable=False)
    place_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    place_class: Mapped[str | None] = mapped_column(String(128), nullable=True)
    importance: Mapped[float | None] = mapped_column(Float, nullable=True)
    place_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # --- Coordonnées (DECIMAL — reproductibilité des calculs, AC2) ---
    latitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)

    # --- Hiérarchie géographique ---
    country_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    county: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postcode: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # --- Timezone (optionnel) ---
    timezone_iana: Mapped[str | None] = mapped_column(String(64), nullable=True)
    timezone_source: Mapped[str | None] = mapped_column(String(32), nullable=True)
    timezone_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- Qualité / traçabilité ---
    normalized_query: Mapped[str | None] = mapped_column(String(512), nullable=True)
    query_language: Mapped[str | None] = mapped_column(String(32), nullable=True)
    query_country_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    raw_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    __table_args__ = (
        # AC4 — idempotence : une seule ligne par couple (provider, provider_place_id)
        UniqueConstraint(
            "provider",
            "provider_place_id",
            name="uq_geo_place_resolved_provider_place_id",
        ),
        # Index pour lookup par coordonnées
        Index("ix_geo_place_resolved_lat_lon", "latitude", "longitude"),
        # Index pour déduplication par requête normalisée
        Index("ix_geo_place_resolved_normalized_query", "normalized_query"),
        # AC2 — contraintes de plage lat/lon
        CheckConstraint(
            "latitude >= -90 AND latitude <= 90",
            name="ck_geo_place_resolved_lat_range",
        ),
        CheckConstraint(
            "longitude >= -180 AND longitude <= 180",
            name="ck_geo_place_resolved_lon_range",
        ),
        # AC3 — provider borné à 'nominatim' (validation applicative + DB)
        CheckConstraint(
            "provider = 'nominatim'",
            name="ck_geo_place_resolved_provider",
        ),
    )
