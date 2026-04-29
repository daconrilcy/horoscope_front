from sqlalchemy import delete

from app.domain.astrology.natal_calculation import NatalResult
from app.domain.astrology.natal_preparation import BirthInput
from app.infra.db.base import Base
from app.infra.db.models.chart_result import ChartResultModel
from app.services.chart.result_service import ChartResultService, ChartResultServiceError
from app.services.natal.calculation_service import NatalCalculationService
from app.services.reference_data_service import ReferenceDataService
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session


def _cleanup_chart_results() -> None:
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())
    with open_app_test_db_session() as db:
        db.execute(delete(ChartResultModel))
        db.commit()


def test_compute_input_hash_is_deterministic() -> None:
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    first = ChartResultService.compute_input_hash(payload, "1.0.0", "1.0.0")
    second = ChartResultService.compute_input_hash(payload, "1.0.0", "1.0.0")
    assert first == second


def test_compute_input_hash_changes_with_ruleset_version() -> None:
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    first = ChartResultService.compute_input_hash(payload, "1.0.0", "1.0.0")
    second = ChartResultService.compute_input_hash(payload, "1.0.0", "1.1.0")
    assert first != second


def test_persist_trace_requires_versions() -> None:
    _cleanup_chart_results()
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    invalid_result = NatalResult(
        reference_version="",
        ruleset_version="1.0.0",
        house_system="equal",
        prepared_input={
            "birth_datetime_local": "1990-06-15T10:30:00+02:00",
            "birth_datetime_utc": "1990-06-15T08:30:00+00:00",
            "timestamp_utc": 645438600,
            "julian_day": 2448057.8541666665,
            "birth_timezone": "Europe/Paris",
        },
        planet_positions=[],
        houses=[],
        aspects=[],
    )
    with open_app_test_db_session() as db:
        try:
            ChartResultService.persist_trace(db, payload, invalid_result)
        except ChartResultServiceError as error:
            assert error.code == "invalid_chart_result"
        else:
            raise AssertionError("Expected ChartResultServiceError")


def test_persist_and_get_audit_record() -> None:
    _cleanup_chart_results()
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        result = NatalCalculationService.calculate(db, payload, reference_version="1.0.0")
        chart_id = ChartResultService.persist_trace(db, payload, result)
        db.commit()

    with open_app_test_db_session() as db:
        record = ChartResultService.get_audit_record(db, chart_id)
    assert record.chart_id == chart_id
    assert record.reference_version == "1.0.0"


def test_persist_trace_generates_unique_chart_ids_for_identical_inputs() -> None:
    _cleanup_chart_results()
    payload = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        result = NatalCalculationService.calculate(db, payload, reference_version="1.0.0")
        first_chart_id = ChartResultService.persist_trace(
            db,
            payload,
            result,
        )
        second_chart_id = ChartResultService.persist_trace(
            db,
            payload,
            result,
        )
        db.commit()

    assert first_chart_id != second_chart_id
