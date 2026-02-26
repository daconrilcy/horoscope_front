"""Tests unitaires pour GeocodingService : mapping DTO et gestion d'erreurs."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from unittest.mock import MagicMock, patch

import pytest

from app.services.geocoding_service import (
    GeocodingAddress,
    GeocodingSearchResult,
    GeocodingService,
    GeocodingServiceError,
    _extract_city,
    _map_nominatim_result,
)

# ---------------------------------------------------------------------------
# Données de test
# ---------------------------------------------------------------------------

NOMINATIM_RESULT_FULL = {
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
        "county": None,
        "city": "Paris",
        "postcode": "75000",
    },
}

# ---------------------------------------------------------------------------
# Tests _extract_city
# ---------------------------------------------------------------------------


def test_extract_city_returns_city_field():
    assert _extract_city({"city": "Paris"}) == "Paris"


def test_extract_city_falls_back_to_town():
    assert _extract_city({"town": "Versailles"}) == "Versailles"


def test_extract_city_falls_back_to_village():
    assert _extract_city({"village": "Thoiry"}) == "Thoiry"


def test_extract_city_returns_none_when_empty():
    assert _extract_city({}) is None


def test_extract_city_prefers_city_over_town():
    assert _extract_city({"city": "Lyon", "town": "NotThis"}) == "Lyon"


# ---------------------------------------------------------------------------
# Tests _map_nominatim_result
# ---------------------------------------------------------------------------


def test_map_nominatim_result_full():
    result = _map_nominatim_result(NOMINATIM_RESULT_FULL)

    assert isinstance(result, GeocodingSearchResult)
    assert result.provider == "nominatim"
    assert result.provider_place_id == 12345
    assert result.osm_type == "relation"
    assert result.osm_id == 7444
    assert result.type == "administrative"
    assert result.class_ == "boundary"
    assert result.display_name == "Paris, Île-de-France, France"
    assert abs(result.lat - 48.8566) < 0.0001
    assert abs(result.lon - 2.3522) < 0.0001
    assert result.importance == 0.9
    assert result.place_rank == 12


def test_map_nominatim_result_address():
    result = _map_nominatim_result(NOMINATIM_RESULT_FULL)

    assert isinstance(result.address, GeocodingAddress)
    assert result.address.country_code == "fr"
    assert result.address.country == "France"
    assert result.address.state == "Île-de-France"
    assert result.address.city == "Paris"
    assert result.address.postcode == "75000"


def test_map_nominatim_result_lat_lon_are_floats():
    result = _map_nominatim_result(NOMINATIM_RESULT_FULL)
    assert isinstance(result.lat, float)
    assert isinstance(result.lon, float)


def test_map_nominatim_result_missing_address_defaults():
    raw = dict(NOMINATIM_RESULT_FULL)
    raw.pop("address")
    result = _map_nominatim_result(raw)
    assert result.address.country_code is None
    assert result.address.city is None


def test_map_nominatim_result_invalid_lat_raises():
    raw = dict(NOMINATIM_RESULT_FULL)
    raw["lat"] = "not_a_number"
    with pytest.raises(ValueError, match="invalid coordinates"):
        _map_nominatim_result(raw)


def test_map_nominatim_result_invalid_lon_raises():
    raw = dict(NOMINATIM_RESULT_FULL)
    raw["lon"] = "nan"
    with pytest.raises(ValueError, match="invalid coordinates"):
        _map_nominatim_result(raw)


def test_map_nominatim_result_inf_lat_raises():
    raw = dict(NOMINATIM_RESULT_FULL)
    raw["lat"] = "inf"
    with pytest.raises(ValueError, match="invalid coordinates"):
        _map_nominatim_result(raw)


def test_map_nominatim_result_missing_place_id_raises():
    raw = dict(NOMINATIM_RESULT_FULL)
    raw.pop("place_id")
    with pytest.raises(ValueError, match="missing place_id"):
        _map_nominatim_result(raw)


def test_map_nominatim_result_empty_class_raises():
    raw = dict(NOMINATIM_RESULT_FULL)
    raw["class"] = " "
    with pytest.raises(ValueError, match="invalid class"):
        _map_nominatim_result(raw)


# ---------------------------------------------------------------------------
# Tests GeocodingService.search — succès
# ---------------------------------------------------------------------------


def _make_urlopen_response(data: object, status: int = 200) -> MagicMock:
    """Simule une réponse urllib.request.urlopen (context manager)."""
    body = json.dumps(data).encode("utf-8")
    mock_resp = MagicMock()
    mock_resp.read.return_value = body
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


def test_search_returns_mapped_results():
    payload = [NOMINATIM_RESULT_FULL]
    mock_resp = _make_urlopen_response(payload)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        results = GeocodingService.search("Paris, France", 1)

    assert len(results) == 1
    assert results[0].display_name == "Paris, Île-de-France, France"
    assert abs(results[0].lat - 48.8566) < 0.0001


def test_search_returns_empty_list_for_no_results():
    mock_resp = _make_urlopen_response([])

    with patch("urllib.request.urlopen", return_value=mock_resp):
        results = GeocodingService.search("XyzUnknownPlace", 5)

    assert results == []


def test_search_forces_jsonv2_and_addressdetails(monkeypatch):
    """Vérifie que les paramètres jsonv2 et addressdetails=1 sont bien envoyés."""
    captured_urls: list[str] = []

    def fake_urlopen(req: urllib.request.Request, timeout: int):
        captured_urls.append(req.full_url)
        mock_resp = _make_urlopen_response([])
        return mock_resp

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    GeocodingService.search("Paris", 3)

    assert len(captured_urls) == 1
    url = captured_urls[0]
    assert "format=jsonv2" in url
    assert "addressdetails=1" in url
    assert "limit=3" in url


def test_search_sends_user_agent(monkeypatch):
    captured_headers: list[dict] = []

    def fake_urlopen(req: urllib.request.Request, timeout: int):
        captured_headers.append(dict(req.headers))
        return _make_urlopen_response([])

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    GeocodingService.search("Berlin", 1)

    assert len(captured_headers) == 1
    user_agent = captured_headers[0].get("User-agent", "")
    assert "horoscope-app" in user_agent.lower() or "horoscope" in user_agent.lower()


# ---------------------------------------------------------------------------
# Tests GeocodingService.search — erreurs upstream
# ---------------------------------------------------------------------------


def test_search_raises_rate_limited_on_429():
    http_error = urllib.error.HTTPError(
        url="http://nominatim/search",
        code=429,
        msg="Too Many Requests",
        hdrs=None,
        fp=None,  # type: ignore[arg-type]
    )
    with patch("urllib.request.urlopen", side_effect=http_error):
        with pytest.raises(GeocodingServiceError) as exc_info:
            GeocodingService.search("Paris", 1)

    assert exc_info.value.code == "geocoding_rate_limited"


def test_search_raises_provider_unavailable_on_503():
    http_error = urllib.error.HTTPError(
        url="http://nominatim/search",
        code=503,
        msg="Service Unavailable",
        hdrs=None,
        fp=None,  # type: ignore[arg-type]
    )
    with patch("urllib.request.urlopen", side_effect=http_error):
        with pytest.raises(GeocodingServiceError) as exc_info:
            GeocodingService.search("Paris", 1)

    assert exc_info.value.code == "geocoding_provider_unavailable"


def test_search_raises_provider_unavailable_on_network_error():
    url_error = urllib.error.URLError(reason="Connection refused")
    with patch("urllib.request.urlopen", side_effect=url_error):
        with pytest.raises(GeocodingServiceError) as exc_info:
            GeocodingService.search("Paris", 1)

    assert exc_info.value.code == "geocoding_provider_unavailable"


def test_search_raises_provider_unavailable_on_timeout():
    timeout_error = urllib.error.URLError(reason="timed out")
    with patch("urllib.request.urlopen", side_effect=timeout_error):
        with pytest.raises(GeocodingServiceError) as exc_info:
            GeocodingService.search("Paris", 1)

    assert exc_info.value.code == "geocoding_provider_unavailable"


def test_search_raises_provider_unavailable_on_invalid_json():
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"not valid json {{{"
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        with pytest.raises(GeocodingServiceError) as exc_info:
            GeocodingService.search("Paris", 1)

    assert exc_info.value.code == "geocoding_provider_unavailable"


def test_search_raises_provider_unavailable_on_invalid_result_structure():
    # Résultat dont lat/lon est non-numérique
    bad_payload = [{"place_id": 1, "lat": "NaN", "lon": "0", "display_name": "x"}]
    mock_resp = _make_urlopen_response(bad_payload)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        with pytest.raises(GeocodingServiceError) as exc_info:
            GeocodingService.search("Paris", 1)

    assert exc_info.value.code == "geocoding_provider_unavailable"


# ---------------------------------------------------------------------------
# Tests limite clamping (défensive, vérifié par le router en amont)
# ---------------------------------------------------------------------------


def test_search_respects_limit_parameter(monkeypatch):
    """Vérifie que le paramètre limit est transmis tel quel à Nominatim."""
    captured: list[str] = []

    def fake_urlopen(req, timeout):
        captured.append(req.full_url)
        return _make_urlopen_response([])

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    GeocodingService.search("Lyon", 7)

    assert "limit=7" in captured[0]
