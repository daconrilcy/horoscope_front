# backend/app/tests/unit/test_daily_prediction_metrics.py
import logging
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from app.services.daily_prediction_service import DailyPredictionService


@pytest.fixture
def mock_deps():
    return {
        "context_loader": MagicMock(),
        "persistence_service": MagicMock(),
        "orchestrator": MagicMock()
    }

@pytest.fixture
def service(mock_deps):
    return DailyPredictionService(
        mock_deps["context_loader"],
        mock_deps["persistence_service"],
        orchestrator=mock_deps["orchestrator"]
    )

@patch("app.services.daily_prediction_service.increment_counter")
def test_compute_counter_incremented(mock_increment, service, mock_deps, db_session):
    # Setup mocks to avoid real DB/Engine work
    service._resolve_profile = MagicMock()
    service._resolve_timezone = MagicMock(return_value="UTC")
    service._resolve_location = MagicMock(return_value=(0, 0))
    service._resolve_date = MagicMock(return_value=date(2024, 1, 1))
    service._resolve_reference_version_id = MagicMock(return_value=1)
    service._resolve_ruleset_id = MagicMock(return_value=1)
    service._resolve_natal_chart = MagicMock(return_value={})
    service._compute_input_hash = MagicMock(return_value="hash")
    
    mock_deps["persistence_service"].save.return_value = MagicMock(run=MagicMock())

    service.get_or_compute(user_id=1, db=db_session)
    
    # Verify increment_counter("prediction.compute") called
    mock_increment.assert_any_call("prediction.compute")

@patch("app.services.daily_prediction_service.increment_counter")
def test_reused_counter_incremented(mock_increment, service, db_session):
    # Mock compute_if_missing logic to return existing run
    service._resolve_profile = MagicMock()
    service._resolve_timezone = MagicMock(return_value="UTC")
    service._resolve_location = MagicMock(return_value=(0, 0))
    service._resolve_date = MagicMock(return_value=date(2024, 1, 1))
    service._resolve_reference_version_id = MagicMock(return_value=1)
    service._resolve_ruleset_id = MagicMock(return_value=1)
    service._resolve_natal_chart = MagicMock(return_value={})
    service._compute_input_hash = MagicMock(return_value="hash")
    
    # Mock repository to find existing run
    with patch("app.services.daily_prediction_service.DailyPredictionRepository") as MockRepo:
        MockRepo.return_value.get_run_by_hash_with_details.return_value = MagicMock()
        service.get_or_compute(user_id=1, db=db_session)

    mock_increment.assert_any_call("prediction.compute")
    mock_increment.assert_any_call("prediction.reused")

def test_log_includes_tone_and_pivot_count(caplog, service, mock_deps, db_session):
    service._resolve_profile = MagicMock()
    service._resolve_timezone = MagicMock(return_value="UTC")
    service._resolve_location = MagicMock(return_value=(0, 0))
    service._resolve_date = MagicMock(return_value=date(2024, 1, 1))
    service._resolve_reference_version_id = MagicMock(return_value=1)
    service._resolve_ruleset_id = MagicMock(return_value=1)
    service._resolve_natal_chart = MagicMock(return_value={})
    service._compute_input_hash = MagicMock(return_value="hash")
    
    engine_output = MagicMock()
    engine_output.run_metadata = {"overall_tone": "positive"}
    engine_output.turning_points = [1, 2] # 2 pivots
    
    mock_deps["orchestrator"].with_context_loader.return_value.run.return_value = engine_output
    mock_deps["persistence_service"].save.return_value = MagicMock(run=MagicMock())
    
    with caplog.at_level(logging.INFO):
        service.get_or_compute(user_id=1, db=db_session)
    
    record = next(r for r in caplog.records if "prediction.run" in r.message)
    assert record.user_id == 1
    assert "duration_ms" in record.__dict__
    assert record.was_reused is False
    assert record.has_pivots is True
    assert record.overall_tone == "positive"
