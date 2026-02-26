from __future__ import annotations

import hashlib
import json
import logging
import math
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.core.config import settings

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class GeocodingServiceError(Exception):
    """Exception levée lors d'erreurs de géocodage."""

    def __init__(self, code: str, message: str, details: dict | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class GeocodingAddress(BaseModel):
    country_code: str | None = None
    country: str | None = None
    state: str | None = None
    county: str | None = None
    city: str | None = None
    postcode: str | None = None


class GeocodingSearchResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    provider: Literal["nominatim"] = "nominatim"
    provider_place_id: int
    osm_type: str
    osm_id: int
    type: str
    class_: str = Field(alias="class")
    display_name: str
    lat: float
    lon: float
    importance: float
    place_rank: int
    address: GeocodingAddress = Field(default_factory=GeocodingAddress)


def _extract_city(address_raw: dict) -> str | None:
    """Chaîne de fallback Nominatim pour le champ city."""
    for key in ("city", "town", "village", "municipality", "suburb"):
        if address_raw.get(key):
            return address_raw[key]
    return None


def _required_int(raw: dict[str, Any], key: str, *, minimum: int = 1) -> int:
    value = raw.get(key)
    if value is None:
        raise ValueError(f"missing {key}")
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid {key}") from exc
    if parsed < minimum:
        raise ValueError(f"invalid {key}")
    return parsed


def _required_float(raw: dict[str, Any], key: str) -> float:
    value = raw.get(key)
    if value is None:
        raise ValueError(f"missing {key}")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid {key}") from exc
    if not math.isfinite(parsed):
        raise ValueError(f"invalid {key}")
    return parsed


def _required_text(raw: dict[str, Any], key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str):
        raise ValueError(f"missing {key}")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"invalid {key}")
    return normalized


def _required_text_any(raw: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = raw.get(key)
        if isinstance(value, str):
            normalized = value.strip()
            if normalized:
                return normalized
    if keys:
        raise ValueError(f"missing {keys[0]}")
    raise ValueError("missing value")


def _map_nominatim_result(raw: dict) -> GeocodingSearchResult:
    """Mappe un résultat brut Nominatim jsonv2 vers le DTO persistable."""
    if not isinstance(raw, dict):
        raise ValueError("invalid result")

    try:
        lat = _required_float(raw, "lat")
        lon = _required_float(raw, "lon")
    except ValueError as exc:
        raise ValueError("invalid coordinates") from exc

    address_raw_raw = raw.get("address", {})
    if address_raw_raw is None:
        address_raw_raw = {}
    if not isinstance(address_raw_raw, dict):
        raise ValueError("invalid address")
    address_raw: dict[str, Any] = address_raw_raw

    return GeocodingSearchResult(
        provider_place_id=_required_int(raw, "place_id"),
        osm_type=_required_text(raw, "osm_type"),
        osm_id=_required_int(raw, "osm_id"),
        type=_required_text_any(raw, "type", "addresstype"),
        class_=_required_text_any(raw, "class", "category"),
        display_name=_required_text(raw, "display_name"),
        lat=lat,
        lon=lon,
        importance=_required_float(raw, "importance"),
        place_rank=_required_int(raw, "place_rank", minimum=0),
        address=GeocodingAddress(
            country_code=address_raw.get("country_code"),
            country=address_raw.get("country"),
            state=address_raw.get("state"),
            county=address_raw.get("county"),
            city=_extract_city(address_raw),
            postcode=address_raw.get("postcode"),
        ),
    )


def _build_query_key(
    q_norm: str,
    limit: int,
    country_code: str | None = None,
    lang: str | None = None,
) -> str:
    """Hash SHA256 stable de l'objet normalisé — clé de cache.

    Le hash couvre {q_norm, country_code, lang, limit} pour garantir
    l'unicité par combinaison de paramètres de recherche.
    La requête brute n'est jamais stockée ni loggée.
    """
    payload = json.dumps(
        {
            "q_norm": q_norm,
            "country_code": country_code,
            "lang": lang,
            "limit": limit,
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class GeocodingService:
    """Client Nominatim côté serveur — proxy géocodage."""

    @classmethod
    def search(
        cls,
        query: str,
        limit: int,
        country_code: str | None = None,
        lang: str | None = None,
    ) -> list[GeocodingSearchResult]:
        """Recherche des lieux via Nominatim (jsonv2 + addressdetails=1).

        Args:
            query: Requête normalisée (déjà validée).
            limit: Nombre max de résultats (déjà validé, 1-10).

        Raises:
            GeocodingServiceError: rate_limited, provider_unavailable, ou réponse invalide.
        """
        payload = {
            "q": query,
            "format": "jsonv2",
            "addressdetails": "1",
            "limit": str(limit),
        }
        if country_code:
            payload["countrycodes"] = country_code
        if lang:
            payload["accept-language"] = lang
        params = urllib.parse.urlencode(payload)
        url = f"{settings.nominatim_url}?{params}"
        user_agent = f"{settings.nominatim_user_agent} (contact: {settings.nominatim_contact})"

        # AC4: Timeout strict et retries=0. urllib.request.Request n'implémente
        # pas de retry par défaut, garantissant le respect de la contrainte.
        req = urllib.request.Request(
            url,
            headers={"User-Agent": user_agent, "Accept": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=settings.nominatim_timeout_seconds) as resp:
                raw_bytes = resp.read()
        except urllib.error.HTTPError as err:
            if err.code == 429:
                raise GeocodingServiceError(
                    code="geocoding_rate_limited",
                    message="Nominatim rate limit exceeded",
                ) from err
            raise GeocodingServiceError(
                code="geocoding_provider_unavailable",
                message=f"Nominatim returned HTTP {err.code}",
            ) from err
        except urllib.error.URLError as err:
            raise GeocodingServiceError(
                code="geocoding_provider_unavailable",
                message="Nominatim service unavailable",
            ) from err

        try:
            raw_data = json.loads(raw_bytes.decode("utf-8"))
            if not isinstance(raw_data, list):
                raise ValueError("invalid payload")
            return [_map_nominatim_result(r) for r in raw_data]
        except (KeyError, ValueError, TypeError) as err:
            raise GeocodingServiceError(
                code="geocoding_provider_unavailable",
                message="Invalid response from Nominatim",
            ) from err

    @classmethod
    def search_with_cache(
        cls,
        db: Session,
        query: str,
        limit: int,
        nocache: bool = False,
        country_code: str | None = None,
        lang: str | None = None,
    ) -> list[GeocodingSearchResult]:
        """Recherche avec couche cache DB (geocoding_query_cache).

        Séparation stricte : le cache n'interagit jamais avec geo_place_resolved.
        Les logs utilisent query_key (hash) — jamais la requête brute.

        Args:
            db: Session SQLAlchemy.
            query: Requête normalisée.
            limit: Nombre max de résultats (1-10).
            nocache: Bypass du cache (usage dev/admin uniquement).
            country_code: Code pays optionnel pour la clé de cache.
            lang: Langue optionnelle pour la clé de cache.
        """
        from sqlalchemy import select

        from app.infra.db.models.geocoding_query_cache import GeocodingQueryCacheModel

        query_key = _build_query_key(query, limit, country_code=country_code, lang=lang)

        logger.info(
            "geocoding_search query_key=%s limit=%d nocache=%s",
            query_key,
            limit,
            nocache,
        )

        if not nocache:
            now = datetime.now(timezone.utc)
            cached = db.execute(
                select(GeocodingQueryCacheModel)
                .where(GeocodingQueryCacheModel.query_key == query_key)
                .where(GeocodingQueryCacheModel.expires_at > now)
            ).scalar_one_or_none()

            if cached is not None:
                logger.info("geocoding_cache_hit query_key=%s", query_key)
                try:
                    raw_data = json.loads(cached.response_json)
                    if not isinstance(raw_data, list):
                        raise ValueError("invalid cached payload")
                    return [GeocodingSearchResult.model_validate(d) for d in raw_data]
                except (json.JSONDecodeError, TypeError, ValueError, ValidationError):
                    logger.warning(
                        "geocoding_cache_corrupt query_key=%s",
                        query_key,
                    )

        logger.info("geocoding_cache_miss query_key=%s nocache=%s", query_key, nocache)
        results = cls.search(query, limit, country_code=country_code, lang=lang)

        if not nocache:
            expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=settings.geocoding_cache_ttl_seconds
            )
            serialized = json.dumps([r.model_dump(mode="json") for r in results])

            # Upsert : met à jour si entrée existante (même key, TTL expiré), insère sinon.
            existing = db.execute(
                select(GeocodingQueryCacheModel).where(
                    GeocodingQueryCacheModel.query_key == query_key
                )
            ).scalar_one_or_none()

            if existing is not None:
                existing.response_json = serialized
                existing.expires_at = expires_at
            else:
                db.add(
                    GeocodingQueryCacheModel(
                        query_key=query_key,
                        response_json=serialized,
                        expires_at=expires_at,
                    )
                )
            db.commit()

        return results

    @staticmethod
    def _build_nominatim_details_url() -> str:
        parsed = urllib.parse.urlparse(settings.nominatim_url)
        if not parsed.scheme or not parsed.netloc:
            raise GeocodingServiceError(
                code="geocoding_provider_unavailable",
                message="Invalid Nominatim base URL",
            )
        return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, "/details.php", "", "", ""))

    @staticmethod
    def _map_nominatim_details_result(raw: dict[str, Any]) -> GeocodingSearchResult:
        if not isinstance(raw, dict):
            raise ValueError("invalid details payload")

        addresstags = raw.get("addresstags")
        address: dict[str, Any]
        if isinstance(addresstags, dict):
            address = dict(addresstags)
        else:
            address = {}

        latitude = raw.get("lat")
        longitude = raw.get("lon")
        if (latitude is None or longitude is None) and isinstance(raw.get("centroid"), dict):
            coords = raw["centroid"].get("coordinates")
            if isinstance(coords, list) and len(coords) >= 2:
                longitude = coords[0]
                latitude = coords[1]

        mapped = {
            "place_id": raw.get("place_id"),
            "osm_type": raw.get("osm_type") or raw.get("osmtype"),
            "osm_id": raw.get("osm_id") or raw.get("osmid"),
            "type": raw.get("type") or "unknown",
            "class": raw.get("class") or raw.get("category") or "place",
            "display_name": raw.get("display_name") or raw.get("localname"),
            "lat": latitude,
            "lon": longitude,
            "importance": raw.get("importance", 0.0),
            "place_rank": raw.get("place_rank", 0),
            "address": address,
        }
        return _map_nominatim_result(mapped)

    @classmethod
    def resolve_place_snapshot(
        cls,
        *,
        provider: str,
        provider_place_id: int,
    ) -> GeocodingSearchResult:
        if provider != "nominatim":
            raise GeocodingServiceError(
                code="unsupported_geocoding_provider",
                message="Unsupported geocoding provider",
                details={"provider": provider},
            )

        details_url = cls._build_nominatim_details_url()
        params = urllib.parse.urlencode(
            {
                "place_id": str(provider_place_id),
                "format": "json",
                "addressdetails": "1",
            }
        )
        url = f"{details_url}?{params}"
        user_agent = f"{settings.nominatim_user_agent} (contact: {settings.nominatim_contact})"

        # AC4: Timeout strict et retries=0.
        req = urllib.request.Request(
            url,
            headers={"User-Agent": user_agent, "Accept": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=settings.nominatim_timeout_seconds) as resp:
                raw_bytes = resp.read()
        except urllib.error.HTTPError as err:
            if err.code == 429:
                raise GeocodingServiceError(
                    code="geocoding_rate_limited",
                    message="Nominatim rate limit exceeded",
                ) from err
            raise GeocodingServiceError(
                code="geocoding_provider_unavailable",
                message=f"Nominatim returned HTTP {err.code}",
            ) from err
        except urllib.error.URLError as err:
            raise GeocodingServiceError(
                code="geocoding_provider_unavailable",
                message="Nominatim service unavailable",
            ) from err

        try:
            raw_data = json.loads(raw_bytes.decode("utf-8"))
            return cls._map_nominatim_details_result(raw_data)
        except (json.JSONDecodeError, TypeError, ValueError) as err:
            raise GeocodingServiceError(
                code="geocoding_provider_unavailable",
                message="Invalid response from Nominatim details API",
            ) from err
