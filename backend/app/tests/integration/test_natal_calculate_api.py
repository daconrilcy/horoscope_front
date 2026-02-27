import logging

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.config import settings
from app.domain.astrology.ephemeris_provider import EphemerisCalcError
from app.domain.astrology.natal_calculation import (
    HouseResult,
    NatalCalculationError,
    NatalResult,
    PlanetPosition,
)
from app.domain.astrology.natal_preparation import BirthPreparedData
from app.infra.db.base import Base
from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.reference import (
    AspectModel,
    AstroCharacteristicModel,
    HouseModel,
    PlanetModel,
    ReferenceVersionModel,
    SignModel,
)
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService

client = TestClient(app)


def _cleanup_reference_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            ChartResultModel,
            AstroCharacteristicModel,
            AspectModel,
            HouseModel,
            SignModel,
            PlanetModel,
            ReferenceVersionModel,
        ):
            db.execute(delete(model))
        db.commit()


def _seed_reference_data() -> None:
    response = client.post(
        "/v1/reference-data/seed?version=1.0.0",
        headers={"x-admin-token": settings.reference_seed_admin_token},
    )
    assert response.status_code == 200


def _create_support_access_token(email: str = "support-audit@example.com") -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role="support")
        db.commit()
        return auth.tokens.access_token


def test_calculate_natal_success_and_repeatable() -> None:
    _cleanup_reference_tables()
    _seed_reference_data()
    support_access_token = _create_support_access_token()

    payload = {
        "birth_date": "1990-06-15",
        "birth_time": "10:30",
        "birth_place": "Paris",
        "birth_timezone": "Europe/Paris",
        "reference_version": "1.0.0",
    }
    first = client.post(
        "/v1/astrology-engine/natal/calculate",
        json=payload,
        headers={"x-request-id": "rid-natal-first"},
    )
    second = client.post(
        "/v1/astrology-engine/natal/calculate",
        json=payload,
        headers={"x-request-id": "rid-natal-second"},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    first_data = first.json()["data"]
    second_data = second.json()["data"]
    assert first_data["chart_id"] != second_data["chart_id"]
    assert first_data["result"] == second_data["result"]
    assert first.json()["meta"]["request_id"] == "rid-natal-first"
    assert second.json()["meta"]["request_id"] == "rid-natal-second"
    assert first_data["result"]["reference_version"] == "1.0.0"
    assert "ruleset_version" in first_data["result"]
    assert len(first_data["result"]["houses"]) == 12

    fetch_response = client.get(
        f"/v1/astrology-engine/results/{first_data['chart_id']}",
        headers={
            "Authorization": f"Bearer {support_access_token}",
            "x-request-id": "rid-natal-fetch",
        },
    )
    assert fetch_response.status_code == 200
    fetch_data = fetch_response.json()["data"]
    assert fetch_response.json()["meta"]["request_id"] == "rid-natal-fetch"
    assert fetch_data["chart_id"] == first_data["chart_id"]
    assert fetch_data["reference_version"] == "1.0.0"
    assert fetch_data["ruleset_version"] == first_data["result"]["ruleset_version"]
    assert fetch_data["input_hash"]
    assert fetch_data["result"]["reference_version"] == "1.0.0"


def test_calculate_natal_unknown_reference_version() -> None:
    _cleanup_reference_tables()
    _seed_reference_data()
    response = client.post(
        "/v1/astrology-engine/natal/calculate",
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "reference_version": "9.9.9",
        },
        headers={"x-request-id": "rid-natal-unknown-version"},
    )

    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "reference_version_not_found"
    assert payload["error"]["request_id"] == "rid-natal-unknown-version"


def test_get_chart_result_not_found() -> None:
    _cleanup_reference_tables()
    support_access_token = _create_support_access_token("support-not-found@example.com")
    response = client.get(
        "/v1/astrology-engine/results/00000000-0000-0000-0000-000000000000",
        headers={
            "Authorization": f"Bearer {support_access_token}",
            "x-request-id": "rid-chart-not-found",
        },
    )
    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "chart_result_not_found"
    assert payload["error"]["request_id"] == "rid-chart-not-found"


def test_get_chart_result_requires_admin_token() -> None:
    _cleanup_reference_tables()
    response = client.get(
        "/v1/astrology-engine/results/00000000-0000-0000-0000-000000000000",
        headers={"x-request-id": "rid-chart-auth-missing"},
    )
    assert response.status_code == 401
    payload = response.json()
    assert payload["error"]["code"] == "missing_access_token"
    assert payload["error"]["request_id"] == "rid-chart-auth-missing"


def test_get_chart_result_forbidden_for_user_role() -> None:
    _cleanup_reference_tables()
    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email="regular-user-audit@example.com",
            password="strong-pass-123",
            role="user",
        )
        db.commit()
        token = auth.tokens.access_token

    response = client.get(
        "/v1/astrology-engine/results/00000000-0000-0000-0000-000000000000",
        headers={
            "Authorization": f"Bearer {token}",
            "x-request-id": "rid-chart-role-forbidden",
        },
    )
    assert response.status_code == 403
    payload = response.json()
    assert payload["error"]["code"] == "insufficient_role"
    assert payload["error"]["request_id"] == "rid-chart-role-forbidden"


def test_calculate_natal_fails_when_reference_is_incomplete() -> None:
    _cleanup_reference_tables()
    _seed_reference_data()
    with SessionLocal() as db:
        db.execute(delete(HouseModel))
        db.commit()

    response = client.post(
        "/v1/astrology-engine/natal/calculate",
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "reference_version": "1.0.0",
        },
        headers={"x-request-id": "rid-natal-ref-incomplete"},
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "invalid_reference_data"
    assert payload["error"]["request_id"] == "rid-natal-ref-incomplete"


def test_calculate_natal_returns_422_for_invalid_birth_input() -> None:
    _cleanup_reference_tables()
    _seed_reference_data()

    response = client.post(
        "/v1/astrology-engine/natal/calculate",
        json={
            "birth_date": "1990-15-99",
            "birth_time": "invalid-time",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "reference_version": "1.0.0",
        },
        headers={"x-request-id": "rid-natal-invalid-input"},
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "invalid_birth_input"
    assert payload["error"]["request_id"] == "rid-natal-invalid-input"


def test_compare_dev_only_returns_structured_diff(monkeypatch: object) -> None:
    _cleanup_reference_tables()
    _seed_reference_data()
    support_access_token = _create_support_access_token("support-compare@example.com")

    monkeypatch.setattr(settings, "app_env", "development")
    monkeypatch.setattr(settings, "natal_engine_compare_enabled", True)

    prepared = BirthPreparedData(
        birth_datetime_local="1990-06-15T10:30:00+02:00",
        birth_datetime_utc="1990-06-15T08:30:00Z",
        timestamp_utc=645438600,
        julian_day=2448057.8541666665,
        birth_timezone="Europe/Paris",
    )

    def _fake_calc(*args: object, **kwargs: object) -> NatalResult:
        engine = kwargs.get("engine_override") or "swisseph"
        if engine == "simplified":
            return NatalResult(
                reference_version="1.0.0",
                ruleset_version="1.0.0",
                house_system="equal",
                engine="simplified",
                prepared_input=prepared,
                planet_positions=[
                    PlanetPosition(
                        planet_code="sun", longitude=85.0, sign_code="gemini", house_number=3
                    )
                ],
                houses=[HouseResult(number=1, cusp_longitude=0.0)],
                aspects=[],
            )
        return NatalResult(
            reference_version="1.0.0",
            ruleset_version="1.0.0",
            house_system="placidus",
            engine="swisseph",
            ephemeris_path_version="se-test-v1",
            prepared_input=prepared,
            planet_positions=[
                PlanetPosition(
                    planet_code="sun", longitude=86.0, sign_code="gemini", house_number=3
                )
            ],
            houses=[HouseResult(number=1, cusp_longitude=1.0)],
            aspects=[],
        )

    monkeypatch.setattr(
        "app.api.v1.routers.astrology_engine.NatalCalculationService.calculate",
        _fake_calc,
    )

    response = client.post(
        "/v1/astrology-engine/natal/compare",
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "birth_lat": 48.8566,
            "birth_lon": 2.3522,
        },
        headers={"Authorization": f"Bearer {support_access_token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "simplified_vs_swisseph" in payload["data"]
    assert payload["data"]["swisseph"]["engine"] == "swisseph"
    assert payload["data"]["simplified"]["engine"] == "simplified"
    assert payload["data"]["simplified_vs_swisseph"]["planet_positions"][0]["planet_code"] == "sun"


def test_compare_dev_only_inaccessible_in_production(monkeypatch: object) -> None:
    _cleanup_reference_tables()
    _seed_reference_data()
    support_access_token = _create_support_access_token("support-compare-prod@example.com")

    monkeypatch.setattr(settings, "app_env", "production")
    monkeypatch.setattr(settings, "natal_engine_compare_enabled", True)

    response = client.post(
        "/v1/astrology-engine/natal/compare",
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "birth_lat": 48.8566,
            "birth_lon": 2.3522,
        },
        headers={"Authorization": f"Bearer {support_access_token}"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "endpoint_not_available"


@pytest.mark.parametrize("error_code", ["ephemeris_calc_failed", "houses_calc_failed"])
def test_calculate_natal_maps_technical_errors_to_503(
    monkeypatch: pytest.MonkeyPatch, error_code: str
) -> None:
    _cleanup_reference_tables()
    _seed_reference_data()

    def _raise_technical(*args: object, **kwargs: object) -> None:
        raise NatalCalculationError(
            code=error_code,
            message="technical failure",
            details={"engine": "swisseph"},
        )

    monkeypatch.setattr(
        "app.api.v1.routers.astrology_engine.NatalCalculationService.calculate",
        _raise_technical,
    )

    response = client.post(
        "/v1/astrology-engine/natal/calculate",
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "reference_version": "1.0.0",
        },
        headers={"x-request-id": "rid-natal-technical"},
    )

    assert response.status_code == 503
    payload = response.json()
    assert payload["error"]["code"] == error_code
    assert payload["error"]["request_id"] == "rid-natal-technical"


def test_calculate_natal_sanitizes_request_id_header() -> None:
    _cleanup_reference_tables()
    _seed_reference_data()

    response = client.post(
        "/v1/astrology-engine/natal/calculate",
        json={
            "birth_date": "1990-15-99",
            "birth_time": "invalid-time",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
        headers={"x-request-id": "rid-natal\r\ninject"},
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["request_id"] == "rid-natalinject"


def test_calculate_natal_logs_structured_swisseph_error_fields(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    _cleanup_reference_tables()
    _seed_reference_data()

    class _Bootstrap:
        success = True
        path_version = "se-test-v1"
        path_hash = "abc123"
        error = None

    monkeypatch.setattr("app.services.natal_calculation_service.settings.swisseph_enabled", True)
    monkeypatch.setattr(
        "app.core.ephemeris.get_bootstrap_result",
        lambda: _Bootstrap(),
    )
    monkeypatch.setattr(
        "app.services.natal_calculation_service.build_natal_result",
        lambda *args, **kwargs: (_ for _ in ()).throw(EphemerisCalcError("calc failed")),
    )

    with caplog.at_level(logging.ERROR, logger="app.services.natal_calculation_service"):
        response = client.post(
            "/v1/astrology-engine/natal/calculate",
            json={
                "birth_date": "1990-06-15",
                "birth_time": "10:30",
                "birth_place": "Paris",
                "birth_timezone": "Europe/Paris",
                "reference_version": "1.0.0",
                "accurate": True,
                "birth_lat": 48.8566,
                "birth_lon": 2.3522,
            },
            headers={"x-request-id": "rid-structured-log"},
        )

    assert response.status_code == 503
    log_messages = [
        record.getMessage() for record in caplog.records if record.levelno == logging.ERROR
    ]
    assert any("request_id=rid-structured-log" in msg for msg in log_messages)
    assert any("engine=swisseph" in msg for msg in log_messages)
    assert any("ephe_version=se-test-v1" in msg for msg in log_messages)
    assert any("ephe_hash=abc123" in msg for msg in log_messages)
