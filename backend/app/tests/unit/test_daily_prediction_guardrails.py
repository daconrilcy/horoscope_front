from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import require_authenticated_user
from app.api.v1.routers.predictions import get_daily_prediction_service
from app.infra.db.models.daily_prediction import DailyPredictionRunModel
from app.main import app
from app.services.daily_prediction_service import (
    DailyPredictionService,
    DailyPredictionServiceError,
)


@pytest.fixture
def mock_deps():
    return {
        "context_loader": MagicMock(),
        "persistence_service": MagicMock(),
        "orchestrator": MagicMock(),
    }


@pytest.fixture
def service(mock_deps):
    return DailyPredictionService(
        mock_deps["context_loader"],
        mock_deps["persistence_service"],
        orchestrator=mock_deps["orchestrator"],
    )


def test_fallback_on_engine_error(service, mock_deps, db_session):
    # Setup mocks to trigger an exception during _compute_with_timeout
    service._resolve_profile = MagicMock()
    service._resolve_timezone = MagicMock(return_value="UTC")
    service._resolve_location = MagicMock(return_value=(0, 0))
    service._resolve_date = MagicMock(return_value=date(2024, 1, 1))
    service._resolve_reference_version_id = MagicMock(return_value=1)
    service._resolve_ruleset_id = MagicMock(return_value=1)
    service._resolve_natal_chart = MagicMock(return_value={})
    service._compute_input_hash = MagicMock(return_value="hash")

    # Force error in engine
    service._compute_with_timeout = MagicMock(side_effect=Exception("Engine boom"))

    # Mock fallback to return a run
    fallback_run = MagicMock(spec=DailyPredictionRunModel)
    fallback_run.id = 123
    fallback_run.local_date = date(2023, 12, 31)
    service._try_read_latest_available = MagicMock(return_value=fallback_run)

    result = service.get_or_compute(user_id=1, db=db_session)

    assert result.was_reused is True
    assert result.run.id == 123
    assert result.engine_output is None


def test_timeout_raises_on_slow_run(service, mock_deps, db_session):
    service._resolve_profile = MagicMock()
    service._resolve_timezone = MagicMock(return_value="UTC")
    service._resolve_location = MagicMock(return_value=(0, 0))
    service._resolve_date = MagicMock(return_value=date(2024, 1, 1))
    service._resolve_reference_version_id = MagicMock(return_value=1)
    service._resolve_ruleset_id = MagicMock(return_value=1)
    service._resolve_natal_chart = MagicMock(return_value={})
    service._compute_input_hash = MagicMock(return_value="hash")

    # Mock _compute_with_timeout directly — avoids patching the stdlib Future class,
    # which is fragile and could affect concurrent code in other tests.
    service._compute_with_timeout = MagicMock(
        side_effect=DailyPredictionServiceError(
            "timeout",
            "Calcul trop long - service temporairement degrade",
        )
    )
    # No fallback available so the timeout error propagates
    service._try_read_latest_available = MagicMock(return_value=None)

    with pytest.raises(DailyPredictionServiceError) as excinfo:
        service.get_or_compute(user_id=1, db=db_session)

    assert excinfo.value.code == "timeout"


def test_latest_run_fallback_found(service, db_session):
    # Integration test of the repository date-filtering query.
    # Uses SQLite in-memory (via conftest db_session) which does NOT enforce FK constraints
    # by default, so reference_version_id=1 and ruleset_id=1 are stored as bare integers
    # without requiring matching rows in the referenced tables.
    # If this test is ever run against a FK-enforcing engine (e.g. PostgreSQL), seed the
    # required ReferenceVersionModel and PredictionRulesetModel rows first.
    from app.infra.db.repositories.daily_prediction_repository import (
        DailyPredictionRepository,
    )

    repo = DailyPredictionRepository(db_session)

    # Seed some runs
    r1 = DailyPredictionRunModel(
        user_id=1,
        local_date=date(2024, 1, 1),
        timezone="UTC",
        reference_version_id=1,
        ruleset_id=1,
        input_hash="h1",
    )
    r2 = DailyPredictionRunModel(
        user_id=1,
        local_date=date(2024, 1, 5),
        timezone="UTC",
        reference_version_id=1,
        ruleset_id=1,
        input_hash="h2",
    )
    db_session.add_all([r1, r2])
    db_session.commit()

    # Search before Jan 10 -> should find r2 (Jan 5)
    fallback = repo.get_latest_run_before(user_id=1, date_local=date(2024, 1, 10))
    assert fallback is not None
    assert fallback.local_date == date(2024, 1, 5)

    # Search before Jan 4 -> should find r1 (Jan 1)
    fallback = repo.get_latest_run_before(user_id=1, date_local=date(2024, 1, 4))
    assert fallback.local_date == date(2024, 1, 1)

    # Search before Jan 1 -> None
    fallback = repo.get_latest_run_before(user_id=1, date_local=date(2024, 1, 1))
    assert fallback is None


def test_log_includes_duration(caplog, service, mock_deps, db_session):
    import logging

    service._resolve_profile = MagicMock()
    service._resolve_timezone = MagicMock(return_value="UTC")
    service._resolve_location = MagicMock(return_value=(0, 0))
    service._resolve_date = MagicMock(return_value=date(2024, 1, 1))
    service._resolve_reference_version_id = MagicMock(return_value=1)
    service._resolve_ruleset_id = MagicMock(return_value=1)
    service._resolve_natal_chart = MagicMock(return_value={})
    service._compute_input_hash = MagicMock(return_value="hash")

    service._compute_with_timeout = MagicMock(
        return_value=MagicMock(
            turning_points=[],
            run_metadata={"overall_tone": "neutral"},
        )
    )
    mock_deps["persistence_service"].save.return_value = MagicMock(run=MagicMock())

    with caplog.at_level(logging.INFO):
        service.get_or_compute(user_id=1, db=db_session)

    record = next(r for r in caplog.records if "prediction.run" in r.message)
    assert hasattr(record, "duration_ms")
    assert isinstance(record.duration_ms, int)
    assert record.duration_ms >= 0


def test_503_on_service_timeout():
    client = TestClient(app)

    mock_service = MagicMock()
    mock_service.get_or_compute.side_effect = DailyPredictionServiceError("timeout", "Slow")

    app.dependency_overrides[get_daily_prediction_service] = lambda: mock_service
    app.dependency_overrides[require_authenticated_user] = lambda: MagicMock(id=1, role="user")

    try:
        response = client.get("/v1/predictions/daily")
        assert response.status_code == 503
        assert response.json()["detail"]["code"] == "timeout"
    finally:
        app.dependency_overrides = {}


def test_503_on_compute_failed():
    client = TestClient(app)

    mock_service = MagicMock()
    mock_service.get_or_compute.side_effect = DailyPredictionServiceError(
        "compute_failed", "Calcul indisponible et aucune prédiction en cache."
    )

    app.dependency_overrides[get_daily_prediction_service] = lambda: mock_service
    app.dependency_overrides[require_authenticated_user] = lambda: MagicMock(id=1, role="user")

    try:
        response = client.get("/v1/predictions/daily")
        assert response.status_code == 503
        assert response.json()["detail"]["code"] == "compute_failed"
    finally:
        app.dependency_overrides = {}
