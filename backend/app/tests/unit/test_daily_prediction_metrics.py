# backend/app/tests/unit/test_daily_prediction_metrics.py
import logging
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.services.daily_prediction_service import DailyPredictionService
from app.services.prediction.compute_runner import ComputeResult
from app.services.prediction.run_reuse_policy import ReuseDecision


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


def _make_bundle(*, overall_tone: str | None = None, turning_points: list | None = None):
    bundle = MagicMock()
    bundle.core.turning_points = turning_points or []
    bundle.core.run_metadata = {}
    bundle.editorial = None
    if overall_tone is not None:
        bundle.editorial = MagicMock()
        bundle.editorial.data.overall_tone = overall_tone
    return bundle


@patch("app.services.prediction.service.increment_counter")
def test_compute_counter_incremented(mock_increment, service, mock_deps, db_session):
    resolved_request = SimpleNamespace(
        user_id=1,
        engine_input=SimpleNamespace(ruleset_version="2.0.0"),
        resolved_date=None,
        reference_version_id=1,
        ruleset_id=1,
        ruleset_version="2.0.0",
    )
    service.resolver.resolve = MagicMock(return_value=resolved_request)
    service.reuse_policy.decide = MagicMock(return_value=ReuseDecision(should_compute=True))
    service.compute_runner.run_with_timeout = MagicMock(
        return_value=ComputeResult(bundle=_make_bundle())
    )
    mock_deps["persistence_service"].save.return_value = MagicMock(run=MagicMock())

    service.get_or_compute(user_id=1, db=db_session)

    # Verify increment_counter("prediction.compute") called
    mock_increment.assert_any_call("prediction.compute")


@patch("app.services.prediction.service.increment_counter")
def test_reused_counter_incremented(mock_increment, service, db_session):
    resolved_request = SimpleNamespace(
        user_id=1,
        engine_input=SimpleNamespace(ruleset_version="2.0.0"),
        resolved_date=None,
        reference_version_id=1,
        ruleset_id=1,
        ruleset_version="2.0.0",
    )
    service.resolver.resolve = MagicMock(return_value=resolved_request)
    service.reuse_policy.decide = MagicMock(
        return_value=ReuseDecision(should_compute=False, existing_run=MagicMock())
    )

    service.get_or_compute(user_id=1, db=db_session)

    mock_increment.assert_any_call("prediction.compute")
    mock_increment.assert_any_call("prediction.reused")


def test_log_includes_tone_and_pivot_count(caplog, service, mock_deps, db_session):
    resolved_request = SimpleNamespace(
        user_id=1,
        engine_input=SimpleNamespace(ruleset_version="2.0.0"),
        resolved_date=None,
        reference_version_id=1,
        ruleset_id=1,
        ruleset_version="2.0.0",
    )
    service.resolver.resolve = MagicMock(return_value=resolved_request)
    service.reuse_policy.decide = MagicMock(return_value=ReuseDecision(should_compute=True))
    service.compute_runner.run_with_timeout = MagicMock(
        return_value=ComputeResult(
            bundle=_make_bundle(overall_tone="positive", turning_points=[1, 2])
        )
    )
    mock_deps["persistence_service"].save.return_value = MagicMock(run=MagicMock())

    with caplog.at_level(logging.INFO):
        service.get_or_compute(user_id=1, db=db_session)

    record = next(r for r in caplog.records if "prediction.run" in r.message)
    assert record.user_id == 1
    assert "duration_ms" in record.__dict__
    assert record.was_reused is False
    assert record.has_pivots is True
    assert record.overall_tone == "positive"
