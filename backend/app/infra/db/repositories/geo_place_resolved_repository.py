from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel

logger = logging.getLogger(__name__)


def _compute_raw_hash(payload: dict[str, Any]) -> str:
    """Hash SHA256 stable d'un payload provider brut."""
    serialized = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@dataclass
class GeoPlaceResolvedCreateData:
    """Données nécessaires pour créer ou retrouver un lieu canonique."""

    provider: str
    provider_place_id: int
    display_name: str
    latitude: float
    longitude: float

    osm_type: str | None = None
    osm_id: int | None = None
    place_type: str | None = None
    place_class: str | None = None
    importance: float | None = None
    place_rank: int | None = None

    # Hiérarchie géo (normalisée à l'init)
    country_code: str | None = None
    country: str | None = None
    state: str | None = None
    county: str | None = None
    city: str | None = None
    postcode: str | None = None

    # Timezone (optionnel)
    timezone_iana: str | None = None
    timezone_source: str | None = None
    timezone_confidence: float | None = None

    # Qualité
    normalized_query: str | None = None
    query_language: str | None = None
    query_country_code: str | None = None

    # Payload brut pour traçabilité (jamais persisté — seul le hash l'est)
    raw_payload: dict[str, Any] | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        # Convention ISO2 uppercase pour country_code (AC2)
        if self.country_code is not None:
            self.country_code = self.country_code.upper()

    @property
    def raw_hash(self) -> str | None:
        """Hash SHA256 du payload brut, ou None si absent."""
        if self.raw_payload is None:
            return None
        return _compute_raw_hash(self.raw_payload)


class GeoPlaceResolvedRepository:
    """Repository pour la table canonique geo_place_resolved.

    Stratégie de concurrence :
      1. Lookup par clé unique (provider, provider_place_id)
      2. Si absent, INSERT avec flush
      3. En cas d'IntegrityError (concurrent insert), rollback + re-lookup
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_by_provider_key(
        self, provider: str, provider_place_id: int
    ) -> GeoPlaceResolvedModel | None:
        """Retourne le lieu résolu pour une clé provider donnée, ou None."""
        return self.db.scalar(
            select(GeoPlaceResolvedModel).where(
                GeoPlaceResolvedModel.provider == provider,
                GeoPlaceResolvedModel.provider_place_id == provider_place_id,
            )
        )

    def find_by_id(self, place_resolved_id: int) -> GeoPlaceResolvedModel | None:
        """Retourne un lieu résolu par identifiant interne, ou None."""
        return self.db.scalar(
            select(GeoPlaceResolvedModel).where(GeoPlaceResolvedModel.id == place_resolved_id)
        )

    def find_or_create(
        self, data: GeoPlaceResolvedCreateData
    ) -> tuple[GeoPlaceResolvedModel, bool]:
        """Trouve ou crée un lieu canonique. Retourne (model, was_created).

        Idempotent : deux appels simultanés avec la même clé ne créent
        qu'une seule ligne grâce à la contrainte unique + retry sur conflict.

        Args:
            data: Données du lieu à persister.

        Returns:
            Tuple (modèle persisté, True si nouvellement créé).
        """
        existing = self.find_by_provider_key(data.provider, data.provider_place_id)
        if existing is not None:
            logger.debug(
                "geo_place_resolved cache_hit provider=%s place_id=%s",
                data.provider,
                data.provider_place_id,
            )
            return existing, False

        model = GeoPlaceResolvedModel(
            provider=data.provider,
            provider_place_id=data.provider_place_id,
            display_name=data.display_name,
            latitude=data.latitude,
            longitude=data.longitude,
            osm_type=data.osm_type,
            osm_id=data.osm_id,
            place_type=data.place_type,
            place_class=data.place_class,
            importance=data.importance,
            place_rank=data.place_rank,
            country_code=data.country_code,
            country=data.country,
            state=data.state,
            county=data.county,
            city=data.city,
            postcode=data.postcode,
            timezone_iana=data.timezone_iana,
            timezone_source=data.timezone_source,
            timezone_confidence=data.timezone_confidence,
            normalized_query=data.normalized_query,
            query_language=data.query_language,
            query_country_code=data.query_country_code,
            raw_hash=data.raw_hash,
        )

        try:
            # Use a savepoint to avoid rolling back unrelated work in the outer transaction.
            with self.db.begin_nested():
                self.db.add(model)
                self.db.flush()
            logger.info(
                "geo_place_resolved created provider=%s place_id=%s id=%s",
                data.provider,
                data.provider_place_id,
                model.id,
            )
            return model, True
        except IntegrityError:
            logger.warning(
                "geo_place_resolved concurrent_insert provider=%s place_id=%s — re-fetching",
                data.provider,
                data.provider_place_id,
            )
            existing = self.find_by_provider_key(data.provider, data.provider_place_id)
            if existing is not None:
                return existing, False
            raise
