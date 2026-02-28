import pytest
from copy import deepcopy

from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.astrology.natal_preparation import BirthInput
from app.infra.db.base import Base


@pytest.fixture(autouse=True)
def _mock_swisseph(monkeypatch: object) -> None:
    from app.core import ephemeris

    monkeypatch.setattr("app.services.natal_calculation_service.settings.swisseph_enabled", True)

    mock_result = ephemeris._BootstrapResult(success=True, path_version="test-v1")
    monkeypatch.setattr("app.core.ephemeris.get_bootstrap_result", lambda: mock_result)


from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.geo_place_resolved import GeoPlaceResolvedModel
from app.infra.db.models.reference import (
    AspectModel,
    AstroCharacteristicModel,
    HouseModel,
    PlanetModel,
    ReferenceVersionModel,
    SignModel,
)
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.repositories.chart_result_repository import ChartResultRepository
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService
from app.services.natal_calculation_service import NatalCalculationService
from app.services.reference_data_service import ReferenceDataService
from app.services.user_astro_profile_service import UserAstroProfileServiceError
from app.services.user_natal_chart_service import UserNatalChartServiceError

client = TestClient(app)


def _sign_from_longitude(longitude: float) -> str:
    signs = (
        "aries",
        "taurus",
        "gemini",
        "cancer",
        "leo",
        "virgo",
        "libra",
        "scorpio",
        "sagittarius",
        "capricorn",
        "aquarius",
        "pisces",
    )
    return signs[int((longitude % 360.0) // 30.0) % 12]


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            ChartResultModel,
            GeoPlaceResolvedModel,
            UserBirthProfileModel,
            UserModel,
            AstroCharacteristicModel,
            AspectModel,
            HouseModel,
            SignModel,
            PlanetModel,
            ReferenceVersionModel,
        ):
            db.execute(delete(model))
        db.commit()


def _register_and_get_access_token() -> str:
    register = client.post(
        "/v1/auth/register",
        json={"email": "user@example.com", "password": "strong-pass-123"},
    )
    assert register.status_code == 200
    return register.json()["data"]["tokens"]["access_token"]


def _register_user_with_role_and_token(email: str, role: str) -> tuple[int, str]:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.user.id, auth.tokens.access_token


def _create_chart_result(
    user_id: int,
    chart_id: str,
    input_hash: str,
    result_payload: dict[str, object],
    reference_version: str = "1.0.0",
    ruleset_version: str = "1.0.0",
) -> None:
    with SessionLocal() as db:
        ChartResultRepository(db).create(
            user_id=user_id,
            chart_id=chart_id,
            reference_version=reference_version,
            ruleset_version=ruleset_version,
            input_hash=input_hash,
            result_payload=result_payload,
        )
        db.commit()


def _build_valid_natal_result_payload(db: Session) -> dict[str, object]:
    ReferenceDataService.seed_reference_version(db, version="1.0.0")
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
        birth_lat=48.8566,
        birth_lon=2.3522,
    )
    result = NatalCalculationService.calculate(
        db, payload, reference_version="1.0.0", accurate=True
    )
    return result.model_dump(mode="json")


def _seed_reference_data() -> None:
    response = client.post(
        "/v1/reference-data/seed?version=1.0.0",
        headers={"x-admin-token": settings.reference_seed_admin_token},
    )
    assert response.status_code == 200


def _seed_resolved_place() -> int:
    with SessionLocal() as db:
        place = GeoPlaceResolvedModel(
            provider="nominatim",
            provider_place_id=12345,
            display_name="Paris, France",
            latitude=48.8566,
            longitude=2.3522,
            country_code="FR",
            city="Paris",
        )
        db.add(place)
        db.commit()
        db.refresh(place)
        return place.id


def test_generate_natal_chart_requires_token() -> None:
    _cleanup_tables()
    response = client.post("/v1/users/me/natal-chart", json={})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_access_token"


def test_get_latest_natal_chart_requires_token() -> None:
    _cleanup_tables()
    response = client.get("/v1/users/me/natal-chart/latest")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_access_token"


def test_generate_natal_chart_success() -> None:
    _cleanup_tables()
    _seed_reference_data()
    place_id = _seed_resolved_place()
    access_token = _register_and_get_access_token()
    put_birth = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "place_resolved_id": place_id,
        },
    )
    assert put_birth.status_code == 200

    response = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"reference_version": "1.0.0", "accurate": True},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["chart_id"]
    assert data["metadata"]["reference_version"] == "1.0.0"
    assert data["metadata"]["ruleset_version"] == data["result"]["ruleset_version"]
    assert data["metadata"]["house_system"] == "placidus"


def test_get_latest_natal_chart_success() -> None:
    _cleanup_tables()
    _seed_reference_data()
    place_id = _seed_resolved_place()
    access_token = _register_and_get_access_token()
    client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "place_resolved_id": place_id,
        },
    )
    generated = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"reference_version": "1.0.0", "accurate": True},
    )
    chart_id = generated.json()["data"]["chart_id"]

    latest = client.get(
        "/v1/users/me/natal-chart/latest",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert latest.status_code == 200
    payload = latest.json()["data"]
    assert payload["chart_id"] == chart_id
    assert payload["metadata"]["reference_version"] == "1.0.0"
    assert payload["metadata"]["house_system"] == "placidus"
    assert "created_at" in payload


def test_generate_natal_chart_fails_when_profile_missing() -> None:
    _cleanup_tables()
    _seed_reference_data()
    access_token = _register_and_get_access_token()
    response = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"reference_version": "1.0.0", "accurate": True},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "birth_profile_not_found"


def test_generate_natal_chart_returns_422_when_birth_time_is_missing() -> None:
    _cleanup_tables()
    _seed_reference_data()
    access_token = _register_and_get_access_token()
    put_birth = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": None,
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    assert put_birth.status_code == 200

    response = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"reference_version": "1.0.0", "accurate": True},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "missing_birth_time"


def test_generate_natal_chart_accurate_mode_requires_place_resolved_fk() -> None:
    _cleanup_tables()
    _seed_reference_data()
    access_token = _register_and_get_access_token()
    put_birth = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    assert put_birth.status_code == 200

    response = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"reference_version": "1.0.0", "accurate": True},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "missing_birth_place_resolved"


def test_get_latest_natal_chart_not_found() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.get(
        "/v1/users/me/natal-chart/latest",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "birth_profile_not_found"


def test_get_latest_natal_chart_not_found_with_existing_profile() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    put_birth = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    assert put_birth.status_code == 200

    response = client.get(
        "/v1/users/me/natal-chart/latest",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "natal_chart_not_found"


def test_generate_natal_chart_fails_when_reference_version_missing() -> None:
    _cleanup_tables()
    _seed_reference_data()
    access_token = _register_and_get_access_token()
    client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )

    response = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"reference_version": "9.9.9"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "reference_version_not_found"


def test_generate_natal_chart_timeout_returns_retryable_503(
    monkeypatch: object,
) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()

    def _raise_timeout(*args: object, **kwargs: object) -> object:
        raise UserNatalChartServiceError(
            code="natal_generation_timeout",
            message="natal chart generation timed out",
            details={"retryable": "true"},
        )

    monkeypatch.setattr(
        "app.api.v1.routers.users.UserNatalChartService.generate_for_user",
        _raise_timeout,
    )

    response = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={},
    )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "natal_generation_timeout"


def test_generate_natal_chart_engine_unavailable_returns_retryable_503(
    monkeypatch: object,
) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()

    def _raise_unavailable(*args: object, **kwargs: object) -> object:
        raise UserNatalChartServiceError(
            code="natal_engine_unavailable",
            message="natal engine is unavailable",
            details={"retryable": "true"},
        )

    monkeypatch.setattr(
        "app.api.v1.routers.users.UserNatalChartService.generate_for_user",
        _raise_unavailable,
    )

    response = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={},
    )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "natal_engine_unavailable"


def test_generate_natal_chart_logs_inconsistent_result_event(
    monkeypatch: object,
) -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    logged: list[dict[str, object]] = []
    metrics: list[tuple[str, float]] = []

    def _raise_inconsistent(*args: object, **kwargs: object) -> object:
        raise UserNatalChartServiceError(
            code="inconsistent_natal_result",
            message="planet house does not match cusp interval",
            details={"reference_version": "1.0.0", "house_system": "equal"},
        )

    def _spy_logger_error(message: str, extra: dict[str, object]) -> None:
        logged.append({"message": message, "extra": extra})

    def _spy_increment_counter(name: str, value: float = 1.0) -> None:
        metrics.append((name, value))

    monkeypatch.setattr(
        "app.api.v1.routers.users.UserNatalChartService.generate_for_user",
        _raise_inconsistent,
    )
    monkeypatch.setattr(
        "app.api.v1.routers.users._should_log_inconsistent_result_event",
        lambda: True,
    )
    monkeypatch.setattr(
        "app.api.v1.routers.users.logger.warning",
        _spy_logger_error,
    )
    monkeypatch.setattr(
        "app.api.v1.routers.users.increment_counter",
        _spy_increment_counter,
    )

    response = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "inconsistent_natal_result"
    assert len(logged) == 1
    assert logged[0]["message"] == "natal_inconsistent_result_detected"
    assert logged[0]["extra"]["reference_version"] == "1.0.0"
    assert logged[0]["extra"]["house_system"] == "equal"
    assert logged[0]["extra"]["planet_code"] is None
    assert logged[0]["extra"]["longitude"] is None
    assert logged[0]["extra"]["request_id"]
    assert metrics == [
        ("natal_inconsistent_result_total", 1.0),
        (
            "natal_inconsistent_result_total|reference_version=1.0.0|house_system=equal|planet_code=unknown",
            1.0,
        ),
    ]


def test_generate_natal_chart_invalid_payload_uses_standard_error_envelope() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"reference_version": 123},
    )

    assert response.status_code == 422
    payload = response.json()
    assert "error" in payload
    assert payload["error"]["code"] == "invalid_natal_chart_request"


def test_generate_natal_chart_sidereal_without_ayanamsa_returns_422_missing_ayanamsa(
    _mock_swisseph: None,
) -> None:
    _cleanup_tables()
    _seed_reference_data()
    place_id = _seed_resolved_place()
    access_token = _register_and_get_access_token()
    put_birth = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "place_resolved_id": place_id,
        },
    )
    assert put_birth.status_code == 200

    response = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"reference_version": "1.0.0", "zodiac": "sidereal", "accurate": True},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "missing_ayanamsa"


def test_generate_natal_chart_topocentric_without_altitude_exposes_zero_altitude(
    _mock_swisseph: None,
) -> None:
    _cleanup_tables()
    _seed_reference_data()
    place_id = _seed_resolved_place()
    access_token = _register_and_get_access_token()
    put_birth = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "place_resolved_id": place_id,
        },
    )
    assert put_birth.status_code == 200

    response = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"reference_version": "1.0.0", "frame": "topocentric", "accurate": True},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["result"]["frame"] == "topocentric"
    assert payload["metadata"]["frame"] == "topocentric"
    assert payload["result"]["altitude_m"] == 0.0
    assert payload["metadata"]["altitude_m"] == 0.0
    assert payload["metadata"]["frame"] == payload["result"]["frame"]
    assert payload["metadata"]["altitude_m"] == payload["result"]["altitude_m"]


def test_generate_natal_chart_invalid_zodiac_returns_explicit_business_code() -> None:
    _cleanup_tables()
    _seed_reference_data()
    access_token = _register_and_get_access_token()
    put_birth = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    assert put_birth.status_code == 200

    response = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"reference_version": "1.0.0", "zodiac": "wrong"},
    )

    assert response.status_code == 422
    payload = response.json()["error"]
    assert payload["code"] == "invalid_zodiac"
    assert payload["details"]["allowed"] == "tropical,sidereal"
    assert payload["details"]["actual"] == "wrong"


def test_generate_natal_chart_invalid_frame_returns_explicit_business_code() -> None:
    _cleanup_tables()
    _seed_reference_data()
    access_token = _register_and_get_access_token()
    put_birth = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    assert put_birth.status_code == 200

    response = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"reference_version": "1.0.0", "frame": "wrong"},
    )

    assert response.status_code == 422
    payload = response.json()["error"]
    assert payload["code"] == "invalid_frame"
    assert payload["details"]["allowed"] == "geocentric,topocentric"
    assert payload["details"]["actual"] == "wrong"


def test_generate_natal_chart_invalid_ayanamsa_returns_422() -> None:
    _cleanup_tables()
    _seed_reference_data()
    access_token = _register_and_get_access_token()
    client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    response = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"zodiac": "sidereal", "ayanamsa": "unknown"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_ayanamsa"


def test_generate_natal_chart_sidereal_requires_accurate_mode() -> None:
    _cleanup_tables()
    _seed_reference_data()
    access_token = _register_and_get_access_token()
    client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    response = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"zodiac": "sidereal", "ayanamsa": "lahiri", "accurate": False},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "accurate_mode_required"


def test_generate_natal_chart_topocentric_requires_accurate_mode() -> None:
    _cleanup_tables()
    _seed_reference_data()
    access_token = _register_and_get_access_token()
    client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    response = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"frame": "topocentric", "accurate": False},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "accurate_mode_required"


def test_generate_natal_chart_sidereal_with_simplified_override_fails(monkeypatch: object) -> None:
    _cleanup_tables()
    _seed_reference_data()
    access_token = _register_and_get_access_token()
    client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )

    from app.services.natal_calculation_service import NatalCalculationService
    from app.domain.astrology.natal_preparation import BirthInput

    # Mock settings to allow simplified engine for internal requests
    monkeypatch.setattr(
        "app.services.natal_calculation_service.settings.natal_engine_simplified_enabled", True
    )
    monkeypatch.setattr("app.services.natal_calculation_service.settings.app_env", "test")

    with SessionLocal() as db:
        birth_input = BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
        try:
            NatalCalculationService.calculate(
                db,
                birth_input,
                zodiac="sidereal",
                ayanamsa="lahiri",
                engine_override="simplified",
                internal_request=True,
            )
            pytest.fail("Should have raised NatalCalculationError")
        except Exception as e:
            assert getattr(e, "code", "") == "natal_engine_option_unsupported"


def test_get_natal_chart_consistency_requires_token() -> None:
    _cleanup_tables()
    response = client.get("/v1/users/1/natal-chart/consistency")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_access_token"


def test_get_natal_chart_consistency_forbidden_for_user_role() -> None:
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.get(
        "/v1/users/1/natal-chart/consistency",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_get_natal_chart_consistency_support_role_returns_consistent() -> None:
    _cleanup_tables()
    target_user_id, _ = _register_user_with_role_and_token("target@example.com", "user")
    _, support_token = _register_user_with_role_and_token("support@example.com", "support")
    with SessionLocal() as db:
        valid_payload = _build_valid_natal_result_payload(db)
        db.commit()
    _create_chart_result(
        user_id=target_user_id,
        chart_id="71111111-1111-1111-1111-111111111111",
        input_hash="e" * 64,
        result_payload=deepcopy(valid_payload),
    )
    _create_chart_result(
        user_id=target_user_id,
        chart_id="72222222-2222-2222-2222-222222222222",
        input_hash="e" * 64,
        result_payload=deepcopy(valid_payload),
    )

    response = client.get(
        f"/v1/users/{target_user_id}/natal-chart/consistency",
        headers={"Authorization": f"Bearer {support_token}"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["consistent"] is True
    assert payload["reason"] == "match"
    assert payload["latest_chart_id"] == "72222222-2222-2222-2222-222222222222"
    assert payload["baseline_chart_id"] == "71111111-1111-1111-1111-111111111111"


def test_get_natal_chart_consistency_support_role_returns_mismatch_trace() -> None:
    _cleanup_tables()
    target_user_id, _ = _register_user_with_role_and_token("target2@example.com", "user")
    _, support_token = _register_user_with_role_and_token("support2@example.com", "support")
    with SessionLocal() as db:
        valid_payload = _build_valid_natal_result_payload(db)
        db.commit()
    mismatched_payload = deepcopy(valid_payload)
    mismatched_payload["planet_positions"][0]["longitude"] = (
        float(mismatched_payload["planet_positions"][0]["longitude"]) + 1.0
    )
    _create_chart_result(
        user_id=target_user_id,
        chart_id="73333333-3333-3333-3333-333333333333",
        input_hash="f" * 64,
        result_payload=deepcopy(valid_payload),
    )
    _create_chart_result(
        user_id=target_user_id,
        chart_id="74444444-4444-4444-4444-444444444444",
        input_hash="f" * 64,
        result_payload=mismatched_payload,
    )

    response = client.get(
        f"/v1/users/{target_user_id}/natal-chart/consistency",
        headers={"Authorization": f"Bearer {support_token}"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["consistent"] is False
    assert payload["mismatch_code"] == "natal_result_mismatch"
    assert payload["latest_chart_id"] == "74444444-4444-4444-4444-444444444444"
    assert payload["baseline_chart_id"] == "73333333-3333-3333-3333-333333333333"
    assert payload["reason"] == "payload_mismatch"


def test_get_natal_chart_consistency_support_role_returns_version_mismatch_trace() -> None:
    _cleanup_tables()
    target_user_id, _ = _register_user_with_role_and_token("targetv@example.com", "user")
    _, support_token = _register_user_with_role_and_token("supportv@example.com", "support")
    with SessionLocal() as db:
        valid_payload = _build_valid_natal_result_payload(db)
        db.commit()
    _create_chart_result(
        user_id=target_user_id,
        chart_id="81111111-1111-1111-1111-111111111111",
        input_hash="j" * 64,
        result_payload=deepcopy(valid_payload),
        reference_version="1.0.0",
        ruleset_version="1.0.0",
    )
    _create_chart_result(
        user_id=target_user_id,
        chart_id="82222222-2222-2222-2222-222222222222",
        input_hash="k" * 64,
        result_payload=deepcopy(valid_payload),
        reference_version="1.0.1",
        ruleset_version="1.0.0",
    )

    response = client.get(
        f"/v1/users/{target_user_id}/natal-chart/consistency",
        headers={"Authorization": f"Bearer {support_token}"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["consistent"] is False
    assert payload["mismatch_code"] == "natal_result_mismatch"
    assert payload["reason"] == "version_mismatch"


def test_get_natal_chart_consistency_support_role_returns_hash_mismatch_trace() -> None:
    _cleanup_tables()
    target_user_id, _ = _register_user_with_role_and_token("targeth@example.com", "user")
    _, support_token = _register_user_with_role_and_token("supporth@example.com", "support")
    with SessionLocal() as db:
        valid_payload = _build_valid_natal_result_payload(db)
        db.commit()
    _create_chart_result(
        user_id=target_user_id,
        chart_id="83333333-3333-3333-3333-333333333333",
        input_hash="l" * 64,
        result_payload=deepcopy(valid_payload),
        reference_version="1.0.0",
        ruleset_version="1.0.0",
    )
    _create_chart_result(
        user_id=target_user_id,
        chart_id="84444444-4444-4444-4444-444444444444",
        input_hash="m" * 64,
        result_payload=deepcopy(valid_payload),
        reference_version="1.0.0",
        ruleset_version="1.0.0",
    )

    response = client.get(
        f"/v1/users/{target_user_id}/natal-chart/consistency",
        headers={"Authorization": f"Bearer {support_token}"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["consistent"] is False
    assert payload["mismatch_code"] == "natal_result_mismatch"
    assert payload["reason"] == "hash_mismatch"


def test_get_natal_chart_consistency_returns_404_when_no_comparable_chart() -> None:
    _cleanup_tables()
    target_user_id, _ = _register_user_with_role_and_token("target3@example.com", "user")
    _, ops_token = _register_user_with_role_and_token("ops@example.com", "ops")
    _create_chart_result(
        user_id=target_user_id,
        chart_id="75555555-5555-5555-5555-555555555555",
        input_hash="g" * 64,
        result_payload={"a": 1},
    )

    response = client.get(
        f"/v1/users/{target_user_id}/natal-chart/consistency",
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "no_comparable_charts"


def test_get_natal_chart_consistency_returns_422_when_payload_is_invalid() -> None:
    _cleanup_tables()
    target_user_id, _ = _register_user_with_role_and_token("target4@example.com", "user")
    _, support_token = _register_user_with_role_and_token("support4@example.com", "support")
    _create_chart_result(
        user_id=target_user_id,
        chart_id="76666666-6666-6666-6666-666666666666",
        input_hash="i" * 64,
        result_payload={"invalid": "payload"},
    )
    _create_chart_result(
        user_id=target_user_id,
        chart_id="77777777-7777-7777-7777-777777777777",
        input_hash="i" * 64,
        result_payload={"invalid": "payload"},
    )

    response = client.get(
        f"/v1/users/{target_user_id}/natal-chart/consistency",
        headers={"Authorization": f"Bearer {support_token}"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_chart_result_payload"


# ---------------------------------------------------------------------------
# AC5 — astro_profile présent dans GET /natal-chart/latest
# ---------------------------------------------------------------------------


def test_get_latest_natal_chart_returns_astro_profile_block() -> None:
    """AC5: GET /natal-chart/latest inclut un bloc astro_profile."""
    _cleanup_tables()
    _seed_reference_data()
    place_id = _seed_resolved_place()
    access_token = _register_and_get_access_token()
    client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "place_resolved_id": place_id,
        },
    )
    client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"reference_version": "1.0.0", "accurate": True},
    )
    latest = client.get(
        "/v1/users/me/natal-chart/latest",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert latest.status_code == 200
    data = latest.json()["data"]
    assert "astro_profile" in data


def test_get_latest_natal_chart_astro_profile_matches_result_geometry() -> None:
    _cleanup_tables()
    _seed_reference_data()
    place_id = _seed_resolved_place()
    access_token = _register_and_get_access_token()
    client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1973-04-24",
            "birth_time": "11:00",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "place_resolved_id": place_id,
        },
    )
    client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"reference_version": "1.0.0", "accurate": True},
    )
    latest = client.get(
        "/v1/users/me/natal-chart/latest",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert latest.status_code == 200
    payload = latest.json()["data"]
    astro = payload["astro_profile"]
    assert astro is not None

    sun = next(
        planet for planet in payload["result"]["planet_positions"] if planet["planet_code"] == "sun"
    )
    house1 = next(house for house in payload["result"]["houses"] if house["number"] == 1)
    assert astro["sun_sign_code"] == _sign_from_longitude(float(sun["longitude"]))
    assert astro["ascendant_sign_code"] == _sign_from_longitude(float(house1["cusp_longitude"]))


def test_get_latest_natal_chart_returns_200_when_astro_profile_service_error(
    monkeypatch: object,
) -> None:
    _cleanup_tables()
    _seed_reference_data()
    place_id = _seed_resolved_place()
    access_token = _register_and_get_access_token()
    client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "place_resolved_id": place_id,
        },
    )
    client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"reference_version": "1.0.0", "accurate": True},
    )

    def _raise_service_error(*args: object, **kwargs: object) -> object:
        raise UserAstroProfileServiceError(
            code="reference_version_not_found",
            message="reference version not found",
            details={},
        )

    monkeypatch.setattr(
        "app.api.v1.routers.users.UserAstroProfileService.get_for_user",
        _raise_service_error,
    )

    latest = client.get(
        "/v1/users/me/natal-chart/latest",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert latest.status_code == 200
    assert latest.json()["data"]["astro_profile"] is None


def test_get_latest_natal_chart_returns_500_on_unexpected_astro_profile_error(
    monkeypatch: object,
) -> None:
    _cleanup_tables()
    _seed_reference_data()
    place_id = _seed_resolved_place()
    access_token = _register_and_get_access_token()
    client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
            "place_resolved_id": place_id,
        },
    )
    client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"reference_version": "1.0.0", "accurate": True},
    )

    def _raise_runtime_error(*args: object, **kwargs: object) -> object:
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "app.api.v1.routers.users.UserAstroProfileService.get_for_user",
        _raise_runtime_error,
    )

    latest = client.get(
        "/v1/users/me/natal-chart/latest",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert latest.status_code == 500
    assert latest.json()["error"]["code"] == "astro_profile_computation_error"


def test_get_latest_natal_chart_non_regression_404_codes() -> None:
    """Non-régression: GET /natal-chart/latest sans thème => 404."""
    _cleanup_tables()
    access_token = _register_and_get_access_token()
    response = client.get(
        "/v1/users/me/natal-chart/latest",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "birth_profile_not_found"
