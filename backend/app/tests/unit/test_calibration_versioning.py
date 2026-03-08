from datetime import date

import pytest
from sqlalchemy import select

from app.infra.db.models.daily_prediction import DailyPredictionRunModel
from app.infra.db.models.prediction_ruleset import CategoryCalibrationModel
from app.infra.db.repositories.daily_prediction_repository import DailyPredictionRepository
from app.prediction.context_loader import PredictionContextLoader
from app.prediction.engine_orchestrator import EngineOrchestrator
from app.prediction.persistence_service import PredictionPersistenceService
from app.prediction.schemas import EffectiveContext, EngineInput, EngineOutput
from app.tests.regression.helpers import create_session


@pytest.fixture
def db_session():
    session = create_session()
    yield session
    if "engine" in session.info:
        session.info["engine"].dispose()


def test_calibration_label_in_db(db_session):
    # Check that the model has the field
    assert hasattr(CategoryCalibrationModel, "calibration_label")
    assert hasattr(DailyPredictionRunModel, "calibration_label")


def test_calibration_label_persisted_in_run(db_session):
    persistence = PredictionPersistenceService()

    # Create a mock EngineOutput
    engine_output = EngineOutput(
        run_metadata={
            "is_provisional_calibration": False,
            "calibration_label": "v1",
            "computed_at": "2024-01-01T00:00:00Z",
        },
        effective_context=EffectiveContext(
            house_system_requested="placidus",
            house_system_effective="placidus",
            timezone="UTC",
            input_hash="test_hash",
        ),
        sampling_timeline=[],
        detected_events=[],
        category_scores={},
        time_blocks=[],
        turning_points=[],
        explainability=None,
    )

    # Save the run
    persistence.save(
        engine_output=engine_output,
        user_id=1,
        local_date=date(2024, 1, 1),
        reference_version_id=1,
        ruleset_id=1,
        db=db_session,
    )
    db_session.commit()

    # Verify persistence
    run = db_session.scalar(
        select(DailyPredictionRunModel).where(DailyPredictionRunModel.input_hash == "test_hash")
    )
    assert run is not None
    assert run.calibration_label == "v1"
    assert run.is_provisional_calibration is False


def test_calibration_label_survives_reuse(db_session):
    repo = DailyPredictionRepository(db_session)
    persistence = PredictionPersistenceService()

    input_hash = "reuse_hash"

    # Pre-create a run with a specific label
    repo.create_run(
        user_id=1,
        local_date=date(2024, 1, 1),
        timezone="UTC",
        reference_version_id=1,
        ruleset_id=1,
        input_hash=input_hash,
        calibration_label="v1",
        is_provisional_calibration=False,
    )
    db_session.commit()

    # Mock EngineOutput with DIFFERENT label (should be ignored due to reuse)
    engine_output = EngineOutput(
        run_metadata={
            "is_provisional_calibration": True,
            "calibration_label": "provisional",
            "computed_at": "2024-01-01T00:00:00Z",
        },
        effective_context=EffectiveContext(
            house_system_requested="placidus",
            house_system_effective="placidus",
            timezone="UTC",
            input_hash=input_hash,
        ),
        sampling_timeline=[],
        detected_events=[],
        category_scores={},
        time_blocks=[],
        turning_points=[],
        explainability=None,
    )

    # Attempt to save
    result = persistence.save(
        engine_output=engine_output,
        user_id=1,
        local_date=date(2024, 1, 1),
        reference_version_id=1,
        ruleset_id=1,
        db=db_session,
    )

    assert result.was_reused is True
    assert result.run.calibration_label == "v1"  # Kept the original
    assert result.run.is_provisional_calibration is False


def test_historical_runs_unchanged_after_calibration_change(db_session):
    repo = DailyPredictionRepository(db_session)
    persistence = PredictionPersistenceService()

    # 1. First run with v1
    h1 = "hash1"
    repo.create_run(
        user_id=1,
        local_date=date(2024, 1, 1),
        timezone="UTC",
        reference_version_id=1,
        ruleset_id=1,
        input_hash=h1,
        calibration_label="v1",
    )
    db_session.commit()

    # 2. Second run with v2 (different input hash)
    h2 = "hash2"
    engine_output2 = EngineOutput(
        run_metadata={
            "is_provisional_calibration": False,
            "calibration_label": "v2",
            "computed_at": "2024-01-02T00:00:00Z",
        },
        effective_context=EffectiveContext(
            house_system_requested="placidus",
            house_system_effective="placidus",
            timezone="UTC",
            input_hash=h2,
        ),
        sampling_timeline=[],
        detected_events=[],
        category_scores={},
        time_blocks=[],
        turning_points=[],
        explainability=None,
    )

    persistence.save(
        engine_output=engine_output2,
        user_id=1,
        local_date=date(2024, 1, 2),
        reference_version_id=1,
        ruleset_id=1,
        db=db_session,
    )
    db_session.commit()

    # 3. Verify both labels exist in history
    r1 = db_session.scalar(
        select(DailyPredictionRunModel).where(DailyPredictionRunModel.input_hash == h1)
    )
    r2 = db_session.scalar(
        select(DailyPredictionRunModel).where(DailyPredictionRunModel.input_hash == h2)
    )

    assert r1.calibration_label == "v1"
    assert r2.calibration_label == "v2"


def test_full_run_contains_calibration_traceability(db_session):
    repo = DailyPredictionRepository(db_session)

    run = repo.create_run(
        user_id=1,
        local_date=date(2024, 1, 3),
        timezone="UTC",
        reference_version_id=1,
        ruleset_id=1,
        input_hash="trace_hash",
        calibration_label="v2",
        is_provisional_calibration=False,
    )
    db_session.commit()

    full_run = repo.get_full_run(run.id)

    assert full_run is not None
    assert full_run["calibration_label"] == "v2"
    assert full_run["is_provisional_calibration"] is False


def test_engine_output_has_calibration_metadata(db_session):
    orchestrator = EngineOrchestrator()

    # Mock EngineInput
    engine_input = EngineInput(
        natal_chart={
            "planets": {
                "Sun": 0.0,
                "Moon": 0.0,
                "Mercury": 0.0,
                "Venus": 0.0,
                "Mars": 0.0,
                "Jupiter": 0.0,
                "Saturn": 0.0,
                "Uranus": 0.0,
                "Neptune": 0.0,
                "Pluto": 0.0,
            },
            "houses": {str(i): (i - 1) * 30 for i in range(1, 13)},
            "house_cusps": [(i - 1) * 30 for i in range(1, 13)],
        },
        local_date=date(2024, 1, 1),
        timezone="UTC",
        latitude=0.0,
        longitude=0.0,
        reference_version="2.0.0",
        ruleset_version="1.0.0",
    )

    loader = PredictionContextLoader()

    def mock_load(ref, ruleset, dt):
        return loader.load(db_session, ref, ruleset, dt)

    bound_orchestrator = orchestrator.with_context_loader(mock_load)

    # Run the engine
    output = bound_orchestrator.run(engine_input, include_editorial=False)

    # Verify metadata
    assert "is_provisional_calibration" in output.run_metadata
    assert "calibration_label" in output.run_metadata
    # In seeded DB, calibrations are missing so it should be provisional
    assert output.run_metadata["is_provisional_calibration"] is True
    assert output.run_metadata["calibration_label"] == "provisional"
