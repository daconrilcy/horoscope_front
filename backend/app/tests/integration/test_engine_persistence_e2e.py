import json
from pathlib import Path

from sqlalchemy import select

from app.infra.db.models.daily_prediction import DailyPredictionRunModel
from app.infra.db.models.prediction_ruleset import PredictionRulesetModel
from app.infra.db.models.reference import ReferenceVersionModel
from app.prediction.persistence_service import PredictionPersistenceService
from app.tests.regression.helpers import cleanup_session, create_orchestrator, create_session
from app.tests.regression.test_engine_non_regression import build_engine_input, load_json


def test_engine_output_persists_without_manual_mapping() -> None:
    session = create_session()
    try:
        fixture_path = (
            Path(__file__).resolve().parents[1] / "regression" / "fixtures" / "F01_calm_day.json"
        )
        engine_input = build_engine_input(load_json(fixture_path)["input"])
        orchestrator = create_orchestrator(session)
        bundle = orchestrator.run(engine_input)
        core_output = bundle.core

        reference_version_id = session.scalar(
            select(ReferenceVersionModel.id).where(
                ReferenceVersionModel.version == engine_input.reference_version
            )
        )
        ruleset_id = session.scalar(
            select(PredictionRulesetModel.id).where(
                PredictionRulesetModel.version == engine_input.ruleset_version
            )
        )
        assert reference_version_id is not None
        assert ruleset_id is not None

        service = PredictionPersistenceService()
        result = service.save(
            bundle,
            user_id=1,
            local_date=engine_input.local_date,
            reference_version_id=reference_version_id,
            ruleset_id=ruleset_id,
            db=session,
        )
        session.commit()

        assert result.was_reused is False
        assert result.run.id is not None
        assert all(isinstance(score, dict) for score in core_output.category_scores.values())

        persisted_run = session.get(DailyPredictionRunModel, result.run.id)
        assert persisted_run is not None
        assert (
            persisted_run.is_provisional_calibration
            == core_output.run_metadata["is_provisional_calibration"]
        )
        assert len(persisted_run.category_scores) == len(core_output.category_scores)
        assert len(persisted_run.turning_points) == len(core_output.turning_points)
        assert len(persisted_run.time_blocks) == len(core_output.time_blocks)

        persisted_scores = {score.category.code: score for score in persisted_run.category_scores}
        for code, output_score in core_output.category_scores.items():
            persisted = persisted_scores[code]
            assert persisted.note_20 == output_score["note_20"]
            assert persisted.raw_score == output_score["raw_score"]
            assert persisted.normalized_score == output_score["normalized_score"]
            assert persisted.power == output_score["power"]
            assert persisted.volatility == output_score["volatility"]

        for turning_point in persisted_run.turning_points:
            assert (
                turning_point.driver_json is None
                or json.loads(turning_point.driver_json) is not None
            )
        for time_block in persisted_run.time_blocks:
            assert (
                time_block.dominant_categories_json is None
                or json.loads(time_block.dominant_categories_json) is not None
            )

        reused = service.save(
            bundle,
            user_id=1,
            local_date=engine_input.local_date,
            reference_version_id=reference_version_id,
            ruleset_id=ruleset_id,
            db=session,
        )
        assert reused.was_reused is True
        assert reused.run.id == result.run.id
    finally:
        cleanup_session(session)
