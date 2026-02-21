from copy import deepcopy

import pytest
from sqlalchemy import delete
from sqlalchemy.orm import Session

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
from app.services.auth_service import AuthService
from app.services.chart_result_service import ChartResultService
from app.services.natal_calculation_service import NatalCalculationService
from app.services.reference_data_service import ReferenceDataService
from app.services.user_birth_profile_service import UserBirthProfileService
from app.services.user_natal_chart_service import UserNatalChartService, UserNatalChartServiceError


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


def _create_user_and_profile() -> int:
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    with SessionLocal() as db:
        auth = AuthService.register(db, email="user@example.com", password="strong-pass-123")
        UserBirthProfileService.upsert_for_user(db, user_id=auth.user.id, payload=payload)
        db.commit()
        return auth.user.id


def _create_chart_result(
    db: Session,
    *,
    user_id: int,
    chart_id: str,
    input_hash: str,
    result_payload: dict[str, object],
    reference_version: str = "1.0.0",
    ruleset_version: str = "1.0.0",
) -> None:
    ChartResultRepository(db).create(
        user_id=user_id,
        chart_id=chart_id,
        reference_version=reference_version,
        ruleset_version=ruleset_version,
        input_hash=input_hash,
        result_payload=result_payload,
    )


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


def test_generate_for_user_success_includes_versions_and_chart_id() -> None:
    _cleanup_tables()
    user_id = _create_user_and_profile()
    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        generated = UserNatalChartService.generate_for_user(
            db=db,
            user_id=user_id,
            reference_version="1.0.0",
        )
        db.commit()

    assert generated.chart_id
    assert generated.result.reference_version == "1.0.0"
    assert generated.metadata.reference_version == "1.0.0"
    assert generated.metadata.ruleset_version == generated.result.ruleset_version


def test_get_latest_for_user_returns_most_recent_chart() -> None:
    _cleanup_tables()
    user_id = _create_user_and_profile()
    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        first = UserNatalChartService.generate_for_user(
            db=db,
            user_id=user_id,
            reference_version="1.0.0",
        )
        second = UserNatalChartService.generate_for_user(
            db=db,
            user_id=user_id,
            reference_version="1.0.0",
        )
        db.commit()

    with SessionLocal() as db:
        latest = UserNatalChartService.get_latest_for_user(db=db, user_id=user_id)

    assert latest.chart_id == second.chart_id
    assert latest.chart_id != first.chart_id
    assert latest.metadata.reference_version == "1.0.0"


def test_generate_for_user_fails_when_birth_profile_missing() -> None:
    _cleanup_tables()
    with SessionLocal() as db:
        auth = AuthService.register(db, email="user@example.com", password="strong-pass-123")
        db.commit()
        with pytest.raises(UserNatalChartServiceError) as error:
            UserNatalChartService.generate_for_user(db=db, user_id=auth.user.id)
    assert error.value.code == "birth_profile_not_found"


def test_get_latest_for_user_not_found() -> None:
    _cleanup_tables()
    user_id = _create_user_and_profile()
    with SessionLocal() as db:
        with pytest.raises(UserNatalChartServiceError) as error:
            UserNatalChartService.get_latest_for_user(db=db, user_id=user_id)
    assert error.value.code == "natal_chart_not_found"


def test_get_latest_for_user_claims_legacy_chart_without_user_id() -> None:
    _cleanup_tables()
    user_id = _create_user_and_profile()
    with SessionLocal() as db:
        payload = BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        )
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        result = NatalCalculationService.calculate(db, payload, reference_version="1.0.0")
        legacy_chart_id = ChartResultService.persist_trace(
            db=db,
            birth_input=payload,
            natal_result=result,
            user_id=None,
        )
        db.commit()

    with SessionLocal() as db:
        latest = UserNatalChartService.get_latest_for_user(db=db, user_id=user_id)
        db.commit()

    assert latest.chart_id == legacy_chart_id


def test_get_latest_for_user_invalid_payload_returns_stable_error() -> None:
    _cleanup_tables()
    user_id = _create_user_and_profile()
    with SessionLocal() as db:
        from app.infra.db.repositories.chart_result_repository import ChartResultRepository

        ChartResultRepository(db).create(
            user_id=user_id,
            chart_id="11111111-1111-1111-1111-111111111111",
            reference_version="1.0.0",
            ruleset_version="1.0.0",
            input_hash="x" * 64,
            result_payload={"invalid": "payload"},
        )
        db.commit()

    with SessionLocal() as db:
        with pytest.raises(UserNatalChartServiceError) as error:
            UserNatalChartService.get_latest_for_user(db=db, user_id=user_id)

    assert error.value.code == "invalid_chart_result_payload"


def test_generate_for_user_maps_timeout_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _cleanup_tables()
    user_id = _create_user_and_profile()

    def _raise_timeout(*args: object, **kwargs: object) -> object:
        raise TimeoutError("timeout")

    monkeypatch.setattr(
        "app.services.user_natal_chart_service.NatalCalculationService.calculate",
        _raise_timeout,
    )

    with SessionLocal() as db:
        with pytest.raises(UserNatalChartServiceError) as error:
            UserNatalChartService.generate_for_user(db=db, user_id=user_id)

    assert error.value.code == "natal_generation_timeout"
    assert error.value.details["retryable"] == "true"


def test_generate_for_user_enforces_timeout_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    _cleanup_tables()
    user_id = _create_user_and_profile()
    with SessionLocal() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        db.commit()

    call_count = {"n": 0}

    def _fake_perf_counter() -> float:
        call_count["n"] += 1
        if call_count["n"] == 1:
            return 0.0
        return 9999.0

    monkeypatch.setattr("app.services.user_natal_chart_service.perf_counter", _fake_perf_counter)

    with SessionLocal() as db:
        with pytest.raises(UserNatalChartServiceError) as error:
            UserNatalChartService.generate_for_user(
                db=db,
                user_id=user_id,
                reference_version="1.0.0",
            )

    assert error.value.code == "natal_generation_timeout"
    assert error.value.details["retryable"] == "true"


def test_verify_consistency_for_user_returns_consistent_for_identical_payloads() -> None:
    _cleanup_tables()
    user_id = _create_user_and_profile()
    with SessionLocal() as db:
        valid_payload = _build_valid_natal_result_payload(db)
        _create_chart_result(
            db,
            user_id=user_id,
            chart_id="11111111-1111-1111-1111-111111111111",
            input_hash="a" * 64,
            result_payload=deepcopy(valid_payload),
        )
        _create_chart_result(
            db,
            user_id=user_id,
            chart_id="22222222-2222-2222-2222-222222222222",
            input_hash="a" * 64,
            result_payload=deepcopy(valid_payload),
        )
        db.commit()

    with SessionLocal() as db:
        report = UserNatalChartService.verify_consistency_for_user(db=db, user_id=user_id)

    assert report.consistent is True
    assert report.reason == "match"
    assert report.latest_chart_id == "22222222-2222-2222-2222-222222222222"
    assert report.baseline_chart_id == "11111111-1111-1111-1111-111111111111"


def test_verify_consistency_for_user_raises_on_payload_mismatch() -> None:
    _cleanup_tables()
    user_id = _create_user_and_profile()
    with SessionLocal() as db:
        valid_payload = _build_valid_natal_result_payload(db)
        mismatched_payload = deepcopy(valid_payload)
        mismatched_payload["planet_positions"][0]["longitude"] = (
            float(mismatched_payload["planet_positions"][0]["longitude"]) + 1.0
        )
        _create_chart_result(
            db,
            user_id=user_id,
            chart_id="33333333-3333-3333-3333-333333333333",
            input_hash="b" * 64,
            result_payload=deepcopy(valid_payload),
        )
        _create_chart_result(
            db,
            user_id=user_id,
            chart_id="44444444-4444-4444-4444-444444444444",
            input_hash="b" * 64,
            result_payload=mismatched_payload,
        )
        db.commit()

    with SessionLocal() as db:
        with pytest.raises(UserNatalChartServiceError) as error:
            UserNatalChartService.verify_consistency_for_user(db=db, user_id=user_id)

    assert error.value.code == "natal_result_mismatch"
    assert error.value.details["latest_chart_id"] == "44444444-4444-4444-4444-444444444444"
    assert error.value.details["baseline_chart_id"] == "33333333-3333-3333-3333-333333333333"
    assert error.value.details["reason"] == "payload_mismatch"


def test_verify_consistency_for_user_raises_on_version_mismatch() -> None:
    _cleanup_tables()
    user_id = _create_user_and_profile()
    with SessionLocal() as db:
        _create_chart_result(
            db,
            user_id=user_id,
            chart_id="55555555-5555-5555-5555-555555555555",
            input_hash="c" * 64,
            result_payload={"a": 1},
            reference_version="1.0.0",
            ruleset_version="1.0.0",
        )
        _create_chart_result(
            db,
            user_id=user_id,
            chart_id="66666666-6666-6666-6666-666666666666",
            input_hash="d" * 64,
            result_payload={"a": 1},
            reference_version="1.0.1",
            ruleset_version="1.0.0",
        )
        db.commit()

    with SessionLocal() as db:
        with pytest.raises(UserNatalChartServiceError) as error:
            UserNatalChartService.verify_consistency_for_user(db=db, user_id=user_id)

    assert error.value.code == "natal_result_mismatch"
    assert error.value.details["reason"] == "version_mismatch"


def test_verify_consistency_for_user_raises_on_hash_mismatch() -> None:
    _cleanup_tables()
    user_id = _create_user_and_profile()
    with SessionLocal() as db:
        valid_payload = _build_valid_natal_result_payload(db)
        _create_chart_result(
            db,
            user_id=user_id,
            chart_id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            input_hash="1" * 64,
            result_payload=deepcopy(valid_payload),
            reference_version="1.0.0",
            ruleset_version="1.0.0",
        )
        _create_chart_result(
            db,
            user_id=user_id,
            chart_id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            input_hash="2" * 64,
            result_payload=deepcopy(valid_payload),
            reference_version="1.0.0",
            ruleset_version="1.0.0",
        )
        db.commit()

    with SessionLocal() as db:
        with pytest.raises(UserNatalChartServiceError) as error:
            UserNatalChartService.verify_consistency_for_user(db=db, user_id=user_id)

    assert error.value.code == "natal_result_mismatch"
    assert error.value.details["reason"] == "hash_mismatch"


def test_verify_consistency_for_user_raises_when_payload_is_invalid() -> None:
    _cleanup_tables()
    user_id = _create_user_and_profile()
    with SessionLocal() as db:
        _create_chart_result(
            db,
            user_id=user_id,
            chart_id="77777777-7777-7777-7777-777777777777",
            input_hash="h" * 64,
            result_payload={"invalid": "payload"},
        )
        _create_chart_result(
            db,
            user_id=user_id,
            chart_id="88888888-8888-8888-8888-888888888888",
            input_hash="h" * 64,
            result_payload={"invalid": "payload"},
        )
        db.commit()

    with SessionLocal() as db:
        with pytest.raises(UserNatalChartServiceError) as error:
            UserNatalChartService.verify_consistency_for_user(db=db, user_id=user_id)

    assert error.value.code == "invalid_chart_result_payload"


def test_verify_consistency_for_user_finds_comparable_beyond_recent_window() -> None:
    _cleanup_tables()
    user_id = _create_user_and_profile()
    with SessionLocal() as db:
        valid_payload = _build_valid_natal_result_payload(db)
        _create_chart_result(
            db,
            user_id=user_id,
            chart_id="90000000-0000-0000-0000-000000000001",
            input_hash="z" * 64,
            result_payload=deepcopy(valid_payload),
        )
        for idx in range(2, 62):
            _create_chart_result(
                db,
                user_id=user_id,
                chart_id=f"90000000-0000-0000-0000-{idx:012d}",
                input_hash=f"{idx:064d}"[-64:],
                result_payload=deepcopy(valid_payload),
                reference_version="1.0.1",
            )
        _create_chart_result(
            db,
            user_id=user_id,
            chart_id="90000000-0000-0000-0000-000000000062",
            input_hash="z" * 64,
            result_payload=deepcopy(valid_payload),
        )
        db.commit()

    with SessionLocal() as db:
        report = UserNatalChartService.verify_consistency_for_user(db=db, user_id=user_id)

    assert report.consistent is True
    assert report.latest_chart_id == "90000000-0000-0000-0000-000000000062"
    assert report.baseline_chart_id == "90000000-0000-0000-0000-000000000001"
