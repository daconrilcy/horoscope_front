from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from app.infra.db.models.calibration import CalibrationRawDayModel
from app.infra.db.repositories.calibration_repository import CalibrationRepository
from app.jobs.calibration.runtime import ResolvedCalibrationRuntime
from app.jobs.generate_daily_calibration_dataset import run_job
from app.tests.regression.helpers import create_session

_MOCK_RUNTIME = ResolvedCalibrationRuntime(reference_version="2.0.0", ruleset_version="2.0.0")


@pytest.fixture
def db_session():
    session = create_session()
    try:
        yield session
    finally:
        if "engine" in session.info:
            session.info["engine"].dispose()


def _mock_loaded_context(*category_codes: str) -> SimpleNamespace:
    return SimpleNamespace(
        prediction_context=SimpleNamespace(
            categories=tuple(
                SimpleNamespace(code=category_code, is_enabled=True)
                for category_code in category_codes
            )
        )
    )


def test_job_stores_raw_day(db_session):
    with (
        patch("app.jobs.generate_daily_calibration_dataset.EngineOrchestrator") as mock_cls,
        patch("app.jobs.generate_daily_calibration_dataset.PredictionContextLoader") as loader_cls,
        patch(
            "app.jobs.generate_daily_calibration_dataset.resolve_calibration_runtime",
            return_value=_MOCK_RUNTIME,
        ),
        patch(
            "app.jobs.generate_daily_calibration_dataset.CALIBRATION_PROFILES",
            [
                {
                    "label": "test_profile",
                    "natal_chart": {},
                    "timezone": "UTC",
                    "latitude": 0.0,
                    "longitude": 0.0,
                }
            ],
        ),
        patch(
            "app.jobs.generate_daily_calibration_dataset.CALIBRATION_DATE_RANGE",
            {"start": "2024-01-01", "end": "2024-01-01"},
        ),
        patch(
            "app.jobs.generate_daily_calibration_dataset.CALIBRATION_VERSIONS",
            {"reference_version": "2.0.0", "ruleset_version": "2.0.0"},
        ),
        patch("app.jobs.generate_daily_calibration_dataset.SessionLocal", return_value=db_session),
    ):
        loader_cls.return_value.load.return_value = _mock_loaded_context("amour", "travail")
        orchestrator = mock_cls.return_value
        orchestrator.run.return_value = SimpleNamespace(
            category_scores={
                "amour": {"raw_score": 10.5, "power": 0.8, "volatility": 0.2},
                "travail": {"raw_score": -5.0, "power": 0.5, "volatility": 0.1},
            },
            turning_points=[object(), object()],
        )

        run_job()

    results = (
        db_session.query(CalibrationRawDayModel)
        .order_by(CalibrationRawDayModel.category_code)
        .all()
    )
    assert len(results) == 2
    assert [row.category_code for row in results] == ["amour", "travail"]
    assert results[0].profile_label == "test_profile"
    assert results[0].pivot_count == 2
    assert results[0].local_date == date(2024, 1, 1)
    orchestrator.run.assert_called_once()
    _, kwargs = orchestrator.run.call_args
    assert kwargs["category_codes"] == ("amour", "travail")
    assert kwargs["include_editorial"] is False


def test_job_skips_existing_entry(db_session):
    repo = CalibrationRepository(db_session)
    for category_code in ("amour", "travail"):
        repo.save(
            CalibrationRawDayModel(
                profile_label="test_profile",
                local_date=date(2024, 1, 1),
                category_code=category_code,
                raw_score=1.0,
                reference_version="2.0.0",
                ruleset_version="2.0.0",
            )
        )
    db_session.commit()

    with (
        patch("app.jobs.generate_daily_calibration_dataset.EngineOrchestrator") as mock_cls,
        patch("app.jobs.generate_daily_calibration_dataset.PredictionContextLoader") as loader_cls,
        patch(
            "app.jobs.generate_daily_calibration_dataset.resolve_calibration_runtime",
            return_value=_MOCK_RUNTIME,
        ),
        patch(
            "app.jobs.generate_daily_calibration_dataset.CALIBRATION_PROFILES",
            [
                {
                    "label": "test_profile",
                    "natal_chart": {},
                    "timezone": "UTC",
                    "latitude": 0.0,
                    "longitude": 0.0,
                }
            ],
        ),
        patch(
            "app.jobs.generate_daily_calibration_dataset.CALIBRATION_DATE_RANGE",
            {"start": "2024-01-01", "end": "2024-01-01"},
        ),
        patch(
            "app.jobs.generate_daily_calibration_dataset.CALIBRATION_VERSIONS",
            {"reference_version": "2.0.0", "ruleset_version": "2.0.0"},
        ),
        patch("app.jobs.generate_daily_calibration_dataset.SessionLocal", return_value=db_session),
    ):
        loader_cls.return_value.load.return_value = _mock_loaded_context("amour", "travail")

        run_job()

    mock_cls.return_value.run.assert_not_called()


def test_job_resume_after_interruption(db_session):
    repo = CalibrationRepository(db_session)
    repo.save(
        CalibrationRawDayModel(
            profile_label="test_profile",
            local_date=date(2024, 1, 1),
            category_code="amour",
            raw_score=1.0,
            power=0.1,
            volatility=0.2,
            reference_version="2.0.0",
            ruleset_version="2.0.0",
        )
    )
    db_session.commit()

    with (
        patch("app.jobs.generate_daily_calibration_dataset.EngineOrchestrator") as mock_cls,
        patch("app.jobs.generate_daily_calibration_dataset.PredictionContextLoader") as loader_cls,
        patch(
            "app.jobs.generate_daily_calibration_dataset.resolve_calibration_runtime",
            return_value=_MOCK_RUNTIME,
        ),
        patch(
            "app.jobs.generate_daily_calibration_dataset.CALIBRATION_PROFILES",
            [
                {
                    "label": "test_profile",
                    "natal_chart": {},
                    "timezone": "UTC",
                    "latitude": 0.0,
                    "longitude": 0.0,
                }
            ],
        ),
        patch(
            "app.jobs.generate_daily_calibration_dataset.CALIBRATION_DATE_RANGE",
            {"start": "2024-01-01", "end": "2024-01-01"},
        ),
        patch(
            "app.jobs.generate_daily_calibration_dataset.CALIBRATION_VERSIONS",
            {"reference_version": "2.0.0", "ruleset_version": "2.0.0"},
        ),
        patch("app.jobs.generate_daily_calibration_dataset.SessionLocal", return_value=db_session),
    ):
        loader_cls.return_value.load.return_value = _mock_loaded_context("amour", "travail")
        orchestrator = mock_cls.return_value
        orchestrator.run.return_value = SimpleNamespace(
            category_scores={
                "travail": {"raw_score": 7.5, "power": 0.9, "volatility": 0.3},
            },
            turning_points=[object()],
        )

        run_job()

    results = (
        db_session.query(CalibrationRawDayModel)
        .order_by(CalibrationRawDayModel.category_code)
        .all()
    )
    assert len(results) == 2
    assert results[0].category_code == "amour"
    assert results[0].raw_score == 1.0
    assert results[1].category_code == "travail"
    assert results[1].raw_score == 7.5
    _, kwargs = orchestrator.run.call_args
    assert kwargs["category_codes"] == ("travail",)
