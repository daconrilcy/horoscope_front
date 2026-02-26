"""Tests d'intégration pour l'endpoint GET /v1/geocoding/search.

Couvre le comportement HTTP de la route et la couche cache DB (story 19-3).
"""

from __future__ import annotations

import urllib.error
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

import app.infra.db.models  # noqa: F401  # enregistrement des modèles SQLAlchemy
from app.core.config import settings
from app.infra.db.base import Base
from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel
from app.infra.db.models.geocoding_query_cache import GeocodingQueryCacheModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.geocoding_service import GeocodingServiceError, _build_query_key

client = TestClient(app)

# ---------------------------------------------------------------------------
# Setup DB
# ---------------------------------------------------------------------------


def _setup_db() -> None:
    """Crée toutes les tables (dont geocoding_query_cache) pour les tests."""
    Base.metadata.create_all(bind=engine)


def _clear_geocoding_cache() -> None:
    with SessionLocal() as db:
        db.execute(delete(GeocodingQueryCacheModel))
        db.commit()


def _clear_geo_place_resolved() -> None:
    with SessionLocal() as db:
        db.execute(delete(GeoPlaceResolvedModel))
        db.commit()


@pytest.fixture(autouse=True)
def _db_setup_and_cleanup():
    _setup_db()
    _clear_geocoding_cache()
    _clear_geo_place_resolved()
    yield
    _clear_geocoding_cache()
    _clear_geo_place_resolved()


# ---------------------------------------------------------------------------
# Payload Nominatim simulé
# ---------------------------------------------------------------------------

NOMINATIM_PARIS = {
    "place_id": 12345,
    "osm_type": "relation",
    "osm_id": 7444,
    "type": "administrative",
    "class": "boundary",
    "display_name": "Paris, Île-de-France, France",
    "lat": "48.8566",
    "lon": "2.3522",
    "importance": 0.9,
    "place_rank": 12,
    "address": {
        "country_code": "fr",
        "country": "France",
        "state": "Île-de-France",
        "city": "Paris",
        "postcode": "75000",
    },
}

RESOLVE_SNAPSHOT_PARIS = {
    "provider_place_id": 12345,
    "osm_type": "relation",
    "osm_id": 7444,
    "type": "administrative",
    "class": "boundary",
    "display_name": "Paris, Île-de-France, France",
    "lat": 48.8566,
    "lon": 2.3522,
    "importance": 0.9,
    "place_rank": 12,
    "address": {
        "country_code": "fr",
        "country": "France",
        "state": "Île-de-France",
        "city": "Paris",
        "postcode": "75000",
    },
}


def _mock_nominatim_response(data: list) -> object:
    """Simule une réponse urllib.request.urlopen."""
    import json
    from unittest.mock import MagicMock

    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(data).encode("utf-8")
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


# ---------------------------------------------------------------------------
# Tests succès (comportement HTTP de base)
# ---------------------------------------------------------------------------


def test_search_returns_results_for_valid_query():
    mock_resp = _mock_nominatim_response([NOMINATIM_PARIS])
    with patch("urllib.request.urlopen", return_value=mock_resp):
        response = client.get(
            "/v1/geocoding/search",
            params={"q": "Paris, France"},
            headers={"x-request-id": "rid-test-01"},
        )

    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "meta" in body
    assert body["meta"]["request_id"] == "rid-test-01"
    results = body["data"]["results"]
    assert len(results) == 1
    assert results[0]["provider"] == "nominatim"
    assert results[0]["display_name"] == "Paris, Île-de-France, France"
    assert abs(results[0]["lat"] - 48.8566) < 0.0001
    assert abs(results[0]["lon"] - 2.3522) < 0.0001
    assert body["data"]["count"] == 1


def test_search_returns_all_required_fields():
    mock_resp = _mock_nominatim_response([NOMINATIM_PARIS])
    with patch("urllib.request.urlopen", return_value=mock_resp):
        response = client.get("/v1/geocoding/search", params={"q": "Paris, France"})

    result = response.json()["data"]["results"][0]
    required_fields = [
        "provider",
        "provider_place_id",
        "osm_type",
        "osm_id",
        "type",
        "class",
        "display_name",
        "lat",
        "lon",
        "importance",
        "place_rank",
        "address",
    ]
    for field in required_fields:
        assert field in result, f"Missing field: {field}"

    address_fields = ["country_code", "country", "state", "county", "city", "postcode"]
    for field in address_fields:
        assert field in result["address"], f"Missing address field: {field}"


def test_search_returns_empty_results_for_unknown_place():
    mock_resp = _mock_nominatim_response([])
    with patch("urllib.request.urlopen", return_value=mock_resp):
        response = client.get("/v1/geocoding/search", params={"q": "XyzUnknownPlace123"})

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["results"] == []
    assert body["data"]["count"] == 0


def test_search_respects_limit_default_5():
    """Vérifie que le limit par défaut est 5."""
    captured: list[str] = []

    def fake_urlopen(req, timeout):
        captured.append(req.full_url)
        return _mock_nominatim_response([])

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        client.get("/v1/geocoding/search", params={"q": "Berlin limit5 test"})

    assert len(captured) == 1
    assert "limit=5" in captured[0]


def test_search_clamps_limit_to_10():
    captured: list[str] = []

    def fake_urlopen(req, timeout):
        captured.append(req.full_url)
        return _mock_nominatim_response([])

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        client.get("/v1/geocoding/search", params={"q": "Rome limit999 test", "limit": "999"})

    assert "limit=10" in captured[0]


def test_search_clamps_limit_to_1():
    captured: list[str] = []

    def fake_urlopen(req, timeout):
        captured.append(req.full_url)
        return _mock_nominatim_response([])

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        client.get("/v1/geocoding/search", params={"q": "Rome limit0 test", "limit": "0"})

    assert "limit=1" in captured[0]


def test_search_sends_jsonv2_and_addressdetails():
    captured: list[str] = []

    def fake_urlopen(req, timeout):
        captured.append(req.full_url)
        return _mock_nominatim_response([])

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        client.get("/v1/geocoding/search", params={"q": "Lyon jsonv2 test"})

    url = captured[0]
    assert "format=jsonv2" in url
    assert "addressdetails=1" in url


# ---------------------------------------------------------------------------
# Tests validation input
# ---------------------------------------------------------------------------


def test_search_rejects_query_too_short():
    response = client.get("/v1/geocoding/search", params={"q": "A"})

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "invalid_geocoding_query"


def test_search_rejects_empty_query():
    response = client.get("/v1/geocoding/search", params={"q": ""})

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "invalid_geocoding_query"


def test_search_normalizes_query_whitespace():
    """Une requête avec espaces multiples est normalisée avant validation."""
    captured: list[str] = []

    def fake_urlopen(req, timeout):
        captured.append(req.full_url)
        return _mock_nominatim_response([])

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        response = client.get("/v1/geocoding/search", params={"q": "  Paris   France  "})

    assert response.status_code == 200
    assert "Paris+France" in captured[0] or "Paris%20France" in captured[0]


def test_search_missing_q_returns_422():
    """Paramètre q obligatoire — FastAPI renvoie 422 standard."""
    response = client.get("/v1/geocoding/search")
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Tests erreurs upstream
# ---------------------------------------------------------------------------


def test_search_returns_429_on_nominatim_rate_limit():
    with patch(
        "app.api.v1.routers.geocoding.GeocodingService.search_with_cache",
        side_effect=GeocodingServiceError(code="geocoding_rate_limited", message="Rate limited"),
    ):
        response = client.get("/v1/geocoding/search", params={"q": "Paris rate429"})

    assert response.status_code == 429
    assert response.json()["error"]["code"] == "geocoding_rate_limited"


def test_search_returns_503_on_nominatim_unavailable():
    with patch(
        "app.api.v1.routers.geocoding.GeocodingService.search_with_cache",
        side_effect=GeocodingServiceError(
            code="geocoding_provider_unavailable", message="Unavailable"
        ),
    ):
        response = client.get("/v1/geocoding/search", params={"q": "Paris 503 test"})

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "geocoding_provider_unavailable"


def test_search_returns_503_on_nominatim_timeout():
    """Timeout Nominatim → URLError → GeocodingServiceError → 503."""
    url_error = urllib.error.URLError(reason="timed out")
    with patch("urllib.request.urlopen", side_effect=url_error):
        response = client.get("/v1/geocoding/search", params={"q": "Paris timeout test"})

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "geocoding_provider_unavailable"


def test_error_response_includes_request_id():
    with patch(
        "app.api.v1.routers.geocoding.GeocodingService.search_with_cache",
        side_effect=GeocodingServiceError(
            code="geocoding_provider_unavailable", message="Unavailable"
        ),
    ):
        response = client.get(
            "/v1/geocoding/search",
            params={"q": "Paris reqid test"},
            headers={"x-request-id": "rid-error-01"},
        )

    assert response.json()["error"]["request_id"] == "rid-error-01"


# ---------------------------------------------------------------------------
# Tests cache DB (story 19-3)
# ---------------------------------------------------------------------------


def test_cache_hit_does_not_call_nominatim():
    """AC1 : un hit cache valide évite l'appel Nominatim."""
    # Premier appel : cache miss → Nominatim appelé, résultat mis en cache
    mock_resp = _mock_nominatim_response([NOMINATIM_PARIS])
    with patch("urllib.request.urlopen", return_value=mock_resp):
        r1 = client.get("/v1/geocoding/search", params={"q": "Paris cache hit test"})
    assert r1.status_code == 200

    # Deuxième appel : même query → cache hit, Nominatim PAS appelé
    with patch("urllib.request.urlopen") as mock_urlopen:
        r2 = client.get("/v1/geocoding/search", params={"q": "Paris cache hit test"})

    assert r2.status_code == 200
    mock_urlopen.assert_not_called()
    assert r2.json()["data"]["results"][0]["display_name"] == "Paris, Île-de-France, France"


def test_cache_miss_after_ttl_expiration_calls_nominatim():
    """AC2 : un miss après expiration TTL déclenche un nouvel appel Nominatim."""
    # Injecter directement une entrée expirée dans le cache
    query = "Paris TTL expiry test"
    query_key = _build_query_key(query, 5)
    with SessionLocal() as db:
        db.add(
            GeocodingQueryCacheModel(
                query_key=query_key,
                response_json="[]",
                expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
            )
        )
        db.commit()

    # Appel avec la même requête: entrée expirée => Nominatim doit être appelé
    mock_resp = _mock_nominatim_response([NOMINATIM_PARIS])
    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_urlopen:
        response = client.get("/v1/geocoding/search", params={"q": query})

    assert response.status_code == 200
    mock_urlopen.assert_called_once()
    assert response.json()["data"]["results"][0]["display_name"] == "Paris, Île-de-France, France"


def test_nocache_bypasses_cache_and_calls_nominatim():
    """AC6 : nocache=true bypass le cache, appelle Nominatim directement."""
    # Premier appel : peuple le cache
    mock_resp = _mock_nominatim_response([NOMINATIM_PARIS])
    with patch("urllib.request.urlopen", return_value=mock_resp):
        client.get("/v1/geocoding/search", params={"q": "Paris nocache test"})

    # Deuxième appel avec nocache=true : Nominatim DOIT être appelé même si cache valide
    with patch(
        "urllib.request.urlopen",
        return_value=_mock_nominatim_response([NOMINATIM_PARIS]),
    ) as mock_urlopen:
        response = client.get(
            "/v1/geocoding/search",
            params={"q": "Paris nocache test", "nocache": "true"},
            headers={"x-admin-token": settings.reference_seed_admin_token},
        )

    assert response.status_code == 200
    mock_urlopen.assert_called_once()


def test_nocache_rejected_without_admin_or_support_ops():
    response = client.get(
        "/v1/geocoding/search",
        params={"q": "Paris nocache denied", "nocache": "true"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized_nocache_access"


def test_cache_written_after_miss():
    """AC1/AC4 : après un miss, les résultats sont écrits dans le cache."""
    mock_resp = _mock_nominatim_response([NOMINATIM_PARIS])
    with patch("urllib.request.urlopen", return_value=mock_resp):
        client.get("/v1/geocoding/search", params={"q": "Paris cache write test"})

    with SessionLocal() as db:
        from sqlalchemy import select

        entries = db.execute(select(GeocodingQueryCacheModel)).scalars().all()

    assert len(entries) == 1
    assert entries[0].query_key is not None
    assert len(entries[0].query_key) == 64  # SHA256 hexdigest
    # SQLite peut retourner un datetime naïf — normalisation pour la comparaison
    stored_expires_at = entries[0].expires_at
    if stored_expires_at.tzinfo is None:
        stored_expires_at = stored_expires_at.replace(tzinfo=timezone.utc)
    assert stored_expires_at > datetime.now(timezone.utc)


def test_cache_separation_from_geo_place_resolved():
    """AC3/AC7 : geocoding_query_cache et geo_place_resolved sont des tables distinctes.

    Vérifie que les opérations de cache n'affectent pas d'autres tables.
    La table geo_place_resolved sera créée en story 19-4.
    """
    from app.infra.db.models.geocoding_query_cache import GeocodingQueryCacheModel

    # Uniquement geocoding_query_cache dans les métadonnées de ce modèle
    assert GeocodingQueryCacheModel.__tablename__ == "geocoding_query_cache"
    assert GeocodingQueryCacheModel.__tablename__ != "geo_place_resolved"

    # Une opération de cache ne touche que geocoding_query_cache
    mock_resp = _mock_nominatim_response([NOMINATIM_PARIS])
    with patch("urllib.request.urlopen", return_value=mock_resp):
        response = client.get("/v1/geocoding/search", params={"q": "Paris separation test"})

    assert response.status_code == 200

    # Vérifie que seule geocoding_query_cache a été peuplée
    with SessionLocal() as db:
        from sqlalchemy import select

        cache_entries = db.execute(select(GeocodingQueryCacheModel)).scalars().all()

    assert len(cache_entries) == 1
    assert cache_entries[0].query_key is not None


def test_get_resolved_place_returns_404_when_missing():
    response = client.get("/v1/geocoding/resolved/999999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "resolved_place_not_found"


def test_get_resolved_place_returns_expected_fields():
    with SessionLocal() as db:
        place = GeoPlaceResolvedModel(
            provider="nominatim",
            provider_place_id=4242,
            display_name="Paris, Île-de-France, France",
            latitude=48.8566,
            longitude=2.3522,
            osm_type="relation",
            osm_id=7444,
            timezone_iana="Europe/Paris",
            timezone_source="nominatim",
            timezone_confidence=0.9,
        )
        db.add(place)
        db.commit()
        db.refresh(place)
        place_id = place.id

    response = client.get(f"/v1/geocoding/resolved/{place_id}")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["id"] == place_id
    assert payload["provider"] == "nominatim"
    assert payload["provider_place_id"] == 4242
    assert payload["osm_type"] == "relation"
    assert payload["osm_id"] == 7444
    assert payload["display_name"] == "Paris, Île-de-France, France"
    assert payload["timezone_iana"] == "Europe/Paris"
    assert payload["timezone_source"] == "nominatim"
    assert payload["timezone_confidence"] == pytest.approx(0.9)


def test_resolve_with_snapshot_persists_and_returns_place():
    response = client.post(
        "/v1/geocoding/resolve",
        json={
            "provider": "nominatim",
            "provider_place_id": 12345,
            "snapshot": RESOLVE_SNAPSHOT_PARIS,
        },
        headers={"x-request-id": "rid-resolve-01"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["request_id"] == "rid-resolve-01"
    data = body["data"]
    assert isinstance(data["id"], int)
    assert data["provider"] == "nominatim"
    assert data["provider_place_id"] == 12345
    assert data["display_name"] == "Paris, Île-de-France, France"
    assert data["latitude"] == pytest.approx(48.8566)
    assert data["longitude"] == pytest.approx(2.3522)

    with SessionLocal() as db:
        from sqlalchemy import select

        rows = db.execute(select(GeoPlaceResolvedModel)).scalars().all()
    assert len(rows) == 1
    assert rows[0].provider_place_id == 12345


def test_resolve_rejects_invalid_snapshot_payload():
    response = client.post(
        "/v1/geocoding/resolve",
        json={
            "provider": "nominatim",
            "provider_place_id": 12345,
            "snapshot": {
                **RESOLVE_SNAPSHOT_PARIS,
                "display_name": "   ",
                "lat": 95.0,
            },
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_geocoding_resolve_payload"


def test_resolve_without_snapshot_uses_lookup_strategy():
    with patch(
        "app.api.v1.routers.geocoding.GeocodingService.resolve_place_snapshot",
        return_value=RESOLVE_SNAPSHOT_PARIS,
    ) as mock_resolve:
        response = client.post(
            "/v1/geocoding/resolve",
            json={
                "provider": "nominatim",
                "provider_place_id": 12345,
            },
        )

    assert response.status_code == 200
    mock_resolve.assert_called_once_with(provider="nominatim", provider_place_id=12345)
    assert response.json()["data"]["provider_place_id"] == 12345


def test_resolve_without_snapshot_maps_provider_error_to_503():
    with patch(
        "app.api.v1.routers.geocoding.GeocodingService.resolve_place_snapshot",
        side_effect=GeocodingServiceError(
            code="geocoding_provider_unavailable",
            message="Nominatim unavailable",
        ),
    ):
        response = client.post(
            "/v1/geocoding/resolve",
            json={
                "provider": "nominatim",
                "provider_place_id": 12345,
            },
        )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "geocoding_provider_unavailable"


def test_resolve_concurrent_requests_return_same_place_id():
    payload = {
        "provider": "nominatim",
        "provider_place_id": 12345,
        "snapshot": RESOLVE_SNAPSHOT_PARIS,
    }

    def _call_resolve() -> int:
        response = client.post("/v1/geocoding/resolve", json=payload)
        assert response.status_code == 200
        return int(response.json()["data"]["id"])

    with ThreadPoolExecutor(max_workers=2) as executor:
        ids = list(executor.map(lambda _: _call_resolve(), range(2)))

    assert ids[0] == ids[1]

    with SessionLocal() as db:
        from sqlalchemy import select

        rows = db.execute(select(GeoPlaceResolvedModel)).scalars().all()
    assert len(rows) == 1
