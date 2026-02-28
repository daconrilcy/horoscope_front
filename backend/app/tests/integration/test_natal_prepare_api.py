from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_prepare_natal_success() -> None:
    response = client.post(
        "/v1/astrology-engine/natal/prepare",
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["birth_datetime_utc"] == "1990-06-15T08:30:00+00:00"
    assert payload["data"]["timestamp_utc"] == 645438600
    assert "julian_day" in payload["data"]


def test_prepare_natal_invalid_timezone() -> None:
    response = client.post(
        "/v1/astrology-engine/natal/prepare",
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Mars/Olympus",
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "invalid_timezone"
    assert payload["error"]["message"] == "birth_timezone is invalid"


def test_prepare_natal_invalid_birth_time_format() -> None:
    response = client.post(
        "/v1/astrology-engine/natal/prepare",
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10h30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "invalid_birth_time"


def test_prepare_natal_invalid_birth_date() -> None:
    response = client.post(
        "/v1/astrology-engine/natal/prepare",
        json={
            "birth_date": "1990-31-31",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "invalid_birth_input"
    assert payload["error"]["message"] == "birth input validation failed"


def test_prepare_natal_missing_birth_timezone() -> None:
    response = client.post(
        "/v1/astrology-engine/natal/prepare",
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "missing_timezone"


# ---------------------------------------------------------------------------
# Story 22.1 — Endpoint retourne jd_ut et timezone_used dans prepared_input
# ---------------------------------------------------------------------------


def test_prepare_natal_returns_jd_ut_field() -> None:
    """AC1: l'endpoint retourne jd_ut dans prepared_input."""
    response = client.post(
        "/v1/astrology-engine/natal/prepare",
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert "jd_ut" in data
    assert isinstance(data["jd_ut"], float)
    assert abs(data["jd_ut"] - data["julian_day"]) < 1e-9


def test_prepare_natal_returns_timezone_used_field() -> None:
    """AC1: l'endpoint retourne timezone_used dans prepared_input."""
    response = client.post(
        "/v1/astrology-engine/natal/prepare",
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "America/New_York",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert "timezone_used" in data
    assert data["timezone_used"] == "America/New_York"


def test_prepare_natal_returns_timezone_source_in_meta_for_user_provided() -> None:
    """Story 26.1 AC1: meta expose timezone_source=user_provided."""
    response = client.post(
        "/v1/astrology-engine/natal/prepare",
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["timezone_used"] == "Europe/Paris"
    assert payload["meta"]["timezone_source"] == "user_provided"


def test_prepare_natal_derives_timezone_when_enabled(monkeypatch: object) -> None:
    """Story 26.1 AC2: sans timezone user, la source devient derived si l'option est active."""
    monkeypatch.setattr(settings, "timezone_derived_enabled", True)
    response = client.post(
        "/v1/astrology-engine/natal/prepare",
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_lat": 48.8566,
            "birth_lon": 2.3522,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    data = payload["data"]
    assert data["timezone_source"] == "derived"
    assert data["timezone_iana"] is not None
    assert payload["meta"]["timezone_source"] == "derived"
    assert payload["meta"]["timezone_used"] == data["timezone_iana"]


def test_prepare_natal_all_required_temporal_fields_present() -> None:
    """AC1: les 5 champs temporels obligatoires sont présents dans la réponse."""
    response = client.post(
        "/v1/astrology-engine/natal/prepare",
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    required_fields = (
        "birth_datetime_local",
        "birth_datetime_utc",
        "timestamp_utc",
        "jd_ut",
        "timezone_used",
    )
    for field in required_fields:
        assert field in data, f"Champ obligatoire manquant: {field}"


# ---------------------------------------------------------------------------
# Story 22.2 — TT optionnel: delta_t_sec/jd_tt et metadata.time_scale
# ---------------------------------------------------------------------------


def test_prepare_natal_tt_enabled_true_returns_tt_fields_and_meta() -> None:
    """tt_enabled=true -> data/meta exposent delta_t_sec, jd_tt et time_scale=TT."""
    response = client.post(
        "/v1/astrology-engine/natal/prepare",
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "tt_enabled": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    data = payload["data"]
    meta = payload["meta"]

    assert data["delta_t_sec"] is not None
    assert data["delta_t_sec"] > 0.0
    assert data["jd_tt"] is not None
    assert data["jd_tt"] > data["jd_ut"]
    assert data["time_scale"] == "TT"
    assert meta["time_scale"] == "TT"
    assert meta["delta_t_sec"] == data["delta_t_sec"]
    assert meta["jd_tt"] == data["jd_tt"]


def test_prepare_natal_tt_enabled_false_returns_null_tt_fields_and_ut_meta() -> None:
    """tt_enabled=false -> data/meta exposent des champs TT nuls et time_scale=UT."""
    response = client.post(
        "/v1/astrology-engine/natal/prepare",
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "tt_enabled": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    data = payload["data"]
    meta = payload["meta"]

    assert data["delta_t_sec"] is None
    assert data["jd_tt"] is None
    assert data["time_scale"] == "UT"
    assert meta["time_scale"] == "UT"
    assert meta["delta_t_sec"] is None
    assert meta["jd_tt"] is None
