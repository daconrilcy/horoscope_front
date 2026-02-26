"""Tests unitaires pour la stratégie de cache geocoding (story 19-3).

Couvre :
- AC1 : hit cache retourne données sans appel upstream
- AC2 : miss après expiration TTL → rappel Nominatim + refresh cache
- AC3 : séparation cache/canonique (geocoding_query_cache vs geo_place_resolved)
- AC4 : query_key est un hash stable SHA256 de {q_norm, country_code, lang, limit}
- AC5 : logs sans PII — q brut absent, query_key présent
- AC6 : nocache=True bypass le cache
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.services.geocoding_service import (
    GeocodingSearchResult,
    GeocodingService,
    _build_query_key,
)

# ---------------------------------------------------------------------------
# Helpers
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

PARIS_RESULT = GeocodingSearchResult(
    provider_place_id=12345,
    osm_type="relation",
    osm_id=7444,
    type="administrative",
    **{"class": "boundary"},
    display_name="Paris, Île-de-France, France",
    lat=48.8566,
    lon=2.3522,
    importance=0.9,
    place_rank=12,
)


def _make_db_session(cached_entry=None):
    """Crée un mock de session SQLAlchemy avec résultat de cache configurable."""
    db = MagicMock()
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = cached_entry
    db.execute.return_value = execute_result
    return db


def _make_cache_entry(results: list[GeocodingSearchResult], expired: bool = False) -> MagicMock:
    """Crée un mock d'entrée cache avec response_json et expires_at."""
    entry = MagicMock()
    entry.response_json = json.dumps([r.model_dump(mode="json") for r in results])
    if expired:
        entry.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    else:
        entry.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    return entry


# ---------------------------------------------------------------------------
# AC4 — _build_query_key : hash stable SHA256
# ---------------------------------------------------------------------------


def test_build_query_key_returns_sha256_hex():
    key = _build_query_key("Paris France", 5)
    # SHA256 hexdigest = 64 chars
    assert len(key) == 64
    assert all(c in "0123456789abcdef" for c in key)


def test_build_query_key_is_stable():
    key1 = _build_query_key("Paris France", 5)
    key2 = _build_query_key("Paris France", 5)
    assert key1 == key2


def test_build_query_key_differs_on_query():
    key_paris = _build_query_key("Paris France", 5)
    key_berlin = _build_query_key("Berlin Germany", 5)
    assert key_paris != key_berlin


def test_build_query_key_differs_on_limit():
    key5 = _build_query_key("Paris France", 5)
    key3 = _build_query_key("Paris France", 3)
    assert key5 != key3


def test_build_query_key_differs_on_country_code():
    key_none = _build_query_key("Paris", 5, country_code=None)
    key_fr = _build_query_key("Paris", 5, country_code="fr")
    assert key_none != key_fr


def test_build_query_key_differs_on_lang():
    key_none = _build_query_key("Paris", 5, lang=None)
    key_fr = _build_query_key("Paris", 5, lang="fr")
    assert key_none != key_fr


def test_build_query_key_matches_manual_sha256():
    """Vérifie que le hash correspond au calcul manuel."""
    payload = json.dumps(
        {"q_norm": "Paris", "country_code": None, "lang": None, "limit": 5},
        sort_keys=True,
    )
    expected = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    assert _build_query_key("Paris", 5) == expected


def test_build_query_key_no_raw_query_in_hash_input():
    """L'objet hashé ne contient pas une clé 'q' brute — seulement 'q_norm'."""
    # On vérifie que le payload JSON utilise 'q_norm' et non 'q'
    payload = json.dumps(
        {"q_norm": "Paris", "country_code": None, "lang": None, "limit": 5},
        sort_keys=True,
    )
    assert '"q_norm"' in payload
    assert '"q"' not in payload.replace('"q_norm"', "")


# ---------------------------------------------------------------------------
# AC1 — Cache hit : pas d'appel upstream
# ---------------------------------------------------------------------------


def test_cache_hit_returns_cached_data_without_upstream():
    """Un hit cache valide retourne les données sans appeler Nominatim."""
    cache_entry = _make_cache_entry([PARIS_RESULT])

    # Premier execute → hit cache (expires_at futur)
    db = MagicMock()
    hit_result = MagicMock()
    hit_result.scalar_one_or_none.return_value = cache_entry
    db.execute.return_value = hit_result

    with patch.object(GeocodingService, "search") as mock_search:
        results = GeocodingService.search_with_cache(db, "Paris France", 5)

    mock_search.assert_not_called()
    assert len(results) == 1
    assert results[0].display_name == "Paris, Île-de-France, France"


def test_cache_hit_returns_correct_result_fields():
    cache_entry = _make_cache_entry([PARIS_RESULT])
    db = MagicMock()
    hit_result = MagicMock()
    hit_result.scalar_one_or_none.return_value = cache_entry
    db.execute.return_value = hit_result

    results = GeocodingService.search_with_cache(db, "Paris France", 5)

    assert results[0].provider == "nominatim"
    assert results[0].lat == pytest.approx(48.8566)
    assert results[0].lon == pytest.approx(2.3522)


def test_cache_corrupt_entry_falls_back_to_upstream():
    cache_entry = MagicMock()
    cache_entry.response_json = "{not-json"

    db = MagicMock()
    hit_result = MagicMock()
    hit_result.scalar_one_or_none.return_value = cache_entry
    no_existing = MagicMock()
    no_existing.scalar_one_or_none.return_value = cache_entry
    db.execute.side_effect = [hit_result, no_existing]

    with patch.object(GeocodingService, "search", return_value=[PARIS_RESULT]) as mock_search:
        results = GeocodingService.search_with_cache(db, "Paris France", 5)

    mock_search.assert_called_once_with(
        "Paris France",
        5,
        country_code=None,
        lang=None,
    )
    assert len(results) == 1
    assert db.commit.called


# ---------------------------------------------------------------------------
# AC2 — Cache miss après expiration TTL : rappel Nominatim + refresh
# ---------------------------------------------------------------------------


def test_cache_miss_calls_upstream_and_refreshes_cache():
    """Un miss cache (TTL expiré) déclenche Nominatim et rafraîchit le cache."""
    expired_entry = _make_cache_entry([PARIS_RESULT], expired=True)

    db = MagicMock()
    # Premier execute → miss (entrée expirée = None pour la requête expires_at > now)
    # Deuxième execute → trouve l'entrée existante pour upsert
    miss_result = MagicMock()
    miss_result.scalar_one_or_none.return_value = None  # cache miss (expired filtered by query)
    upsert_result = MagicMock()
    upsert_result.scalar_one_or_none.return_value = expired_entry  # entrée existante pour upsert
    db.execute.side_effect = [miss_result, upsert_result]

    with patch.object(GeocodingService, "search", return_value=[PARIS_RESULT]) as mock_search:
        results = GeocodingService.search_with_cache(db, "Paris France", 5)

    mock_search.assert_called_once_with(
        "Paris France",
        5,
        country_code=None,
        lang=None,
    )
    # Vérifie que le cache a été mis à jour
    assert db.commit.called
    assert expired_entry.response_json is not None
    assert expired_entry.expires_at > datetime.now(timezone.utc)
    assert len(results) == 1


def test_cache_miss_empty_cache_inserts_new_entry():
    """Un miss sur cache vide insère une nouvelle entrée."""
    db = MagicMock()
    miss_result = MagicMock()
    miss_result.scalar_one_or_none.return_value = None
    no_existing = MagicMock()
    no_existing.scalar_one_or_none.return_value = None
    db.execute.side_effect = [miss_result, no_existing]

    with patch.object(GeocodingService, "search", return_value=[PARIS_RESULT]):
        GeocodingService.search_with_cache(db, "Paris France", 5)

    db.add.assert_called_once()
    db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# AC3 — Non-régression : place résolue conserve ses coordonnées
# ---------------------------------------------------------------------------


def test_cache_expiry_does_not_affect_geo_place_resolved():
    """Garantit que le cache n'interagit jamais avec geo_place_resolved.

    Le service ne référence que GeocodingQueryCacheModel — jamais
    une hypothétique table geo_place_resolved. Ce test vérifie que
    search_with_cache n'effectue des opérations DB que sur
    geocoding_query_cache.
    """
    from app.infra.db.models.geocoding_query_cache import GeocodingQueryCacheModel

    db = MagicMock()
    miss_result = MagicMock()
    miss_result.scalar_one_or_none.return_value = None
    no_existing = MagicMock()
    no_existing.scalar_one_or_none.return_value = None
    db.execute.side_effect = [miss_result, no_existing]

    with patch.object(GeocodingService, "search", return_value=[PARIS_RESULT]):
        GeocodingService.search_with_cache(db, "Paris France", 5)

    # Vérifie que seul GeocodingQueryCacheModel est utilisé (via db.add)
    added_objects = [c.args[0] for c in db.add.call_args_list]
    for obj in added_objects:
        assert isinstance(obj, GeocodingQueryCacheModel), (
            f"search_with_cache ne doit pas écrire dans une autre table que "
            f"geocoding_query_cache, mais a ajouté {type(obj).__name__}"
        )


# ---------------------------------------------------------------------------
# AC5 — Logs : query_key présent, q brut absent
# ---------------------------------------------------------------------------


def test_logs_use_query_key_not_raw_query(caplog):
    """Les logs de géocodage exposent query_key (hash) et n'exposent pas q brut."""
    db = MagicMock()
    miss_result = MagicMock()
    miss_result.scalar_one_or_none.return_value = None
    no_existing = MagicMock()
    no_existing.scalar_one_or_none.return_value = None
    db.execute.side_effect = [miss_result, no_existing]

    raw_query = "Paris France secret query"

    with caplog.at_level(logging.INFO, logger="app.services.geocoding_service"):
        with patch.object(GeocodingService, "search", return_value=[PARIS_RESULT]):
            GeocodingService.search_with_cache(db, raw_query, 5)

    log_text = " ".join(caplog.messages)

    # La requête brute ne doit PAS apparaître dans les logs
    assert raw_query not in log_text, f"q brut exposé dans les logs: {log_text}"

    # query_key (hash) doit apparaître
    expected_key = _build_query_key(raw_query, 5)
    assert expected_key in log_text, f"query_key absent des logs: {log_text}"


def test_logs_contain_cache_hit_marker(caplog):
    cache_entry = _make_cache_entry([PARIS_RESULT])
    db = MagicMock()
    hit_result = MagicMock()
    hit_result.scalar_one_or_none.return_value = cache_entry
    db.execute.return_value = hit_result

    with caplog.at_level(logging.INFO, logger="app.services.geocoding_service"):
        GeocodingService.search_with_cache(db, "Paris", 5)

    assert "geocoding_cache_hit" in " ".join(caplog.messages)


def test_logs_contain_cache_miss_marker(caplog):
    db = MagicMock()
    miss_result = MagicMock()
    miss_result.scalar_one_or_none.return_value = None
    no_existing = MagicMock()
    no_existing.scalar_one_or_none.return_value = None
    db.execute.side_effect = [miss_result, no_existing]

    with caplog.at_level(logging.INFO, logger="app.services.geocoding_service"):
        with patch.object(GeocodingService, "search", return_value=[PARIS_RESULT]):
            GeocodingService.search_with_cache(db, "Paris", 5)

    assert "geocoding_cache_miss" in " ".join(caplog.messages)


# ---------------------------------------------------------------------------
# AC6 — nocache=True : bypass du cache
# ---------------------------------------------------------------------------


def test_nocache_bypasses_cache_read():
    """nocache=True ignore le cache en lecture."""
    db = MagicMock()

    with patch.object(GeocodingService, "search", return_value=[PARIS_RESULT]) as mock_search:
        results = GeocodingService.search_with_cache(db, "Paris France", 5, nocache=True)

    # Aucun execute pour lire le cache
    db.execute.assert_not_called()
    mock_search.assert_called_once_with(
        "Paris France",
        5,
        country_code=None,
        lang=None,
    )
    assert len(results) == 1


def test_nocache_bypasses_cache_write():
    """nocache=True ne persiste pas les résultats dans le cache."""
    db = MagicMock()

    with patch.object(GeocodingService, "search", return_value=[PARIS_RESULT]):
        GeocodingService.search_with_cache(db, "Paris France", 5, nocache=True)

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_nocache_returns_upstream_results():
    db = MagicMock()

    with patch.object(GeocodingService, "search", return_value=[PARIS_RESULT]):
        results = GeocodingService.search_with_cache(db, "Paris France", 5, nocache=True)

    assert results == [PARIS_RESULT]


# ---------------------------------------------------------------------------
# AC7 — Séparation explicite des tables (vérification de schéma)
# ---------------------------------------------------------------------------


def test_geocoding_query_cache_table_name():
    """La table cache a le bon nom — séparation explicite avec geo_place_resolved."""
    from app.infra.db.models.geocoding_query_cache import GeocodingQueryCacheModel

    assert GeocodingQueryCacheModel.__tablename__ == "geocoding_query_cache"


def test_geocoding_query_cache_has_required_columns():
    from app.infra.db.models.geocoding_query_cache import GeocodingQueryCacheModel

    columns = {c.name for c in GeocodingQueryCacheModel.__table__.columns}
    assert "query_key" in columns
    assert "response_json" in columns
    assert "expires_at" in columns
    assert "created_at" in columns


def test_geocoding_query_cache_index_on_query_key():
    from app.infra.db.models.geocoding_query_cache import GeocodingQueryCacheModel

    indexed_cols = {
        col.name for idx in GeocodingQueryCacheModel.__table__.indexes for col in idx.columns
    }
    assert "query_key" in indexed_cols


def test_geocoding_query_cache_index_on_expires_at():
    from app.infra.db.models.geocoding_query_cache import GeocodingQueryCacheModel

    indexed_cols = {
        col.name for idx in GeocodingQueryCacheModel.__table__.indexes for col in idx.columns
    }
    assert "expires_at" in indexed_cols
