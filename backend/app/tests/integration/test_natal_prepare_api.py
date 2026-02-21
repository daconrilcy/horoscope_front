from fastapi.testclient import TestClient

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
    assert payload["error"]["code"] == "invalid_birth_input"
