from copy import deepcopy

from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.astrology.natal_preparation import BirthInput
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
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.repositories.chart_result_repository import ChartResultRepository
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService
from app.services.natal_calculation_service import NatalCalculationService
from app.services.reference_data_service import ReferenceDataService
from app.services.user_natal_chart_service import UserNatalChartServiceError

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            ChartResultModel,
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
    )
    result = NatalCalculationService.calculate(db, payload, reference_version="1.0.0")
    return result.model_dump(mode="json")


def _seed_reference_data() -> None:
    response = client.post(
        "/v1/reference-data/seed?version=1.0.0",
        headers={"x-admin-token": settings.reference_seed_admin_token},
    )
    assert response.status_code == 200


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
        json={"reference_version": "1.0.0"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["chart_id"]
    assert data["metadata"]["reference_version"] == "1.0.0"
    assert data["metadata"]["ruleset_version"] == data["result"]["ruleset_version"]


def test_get_latest_natal_chart_success() -> None:
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
    generated = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"reference_version": "1.0.0"},
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
    assert "created_at" in payload


def test_generate_natal_chart_fails_when_profile_missing() -> None:
    _cleanup_tables()
    _seed_reference_data()
    access_token = _register_and_get_access_token()
    response = client.post(
        "/v1/users/me/natal-chart",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"reference_version": "1.0.0"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "birth_profile_not_found"


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
