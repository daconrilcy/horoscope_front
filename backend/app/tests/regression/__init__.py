from datetime import UTC, date, datetime

import pytest
from sqlalchemy.orm import Session

from app.infra.db.models.daily_prediction import DailyPredictionRunModel
from app.infra.db.models.prediction_reference import PredictionCategoryModel
from app.infra.db.models.prediction_ruleset import PredictionRulesetModel
from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.repositories.daily_prediction_repository import DailyPredictionRepository
from app.prediction.persistence_service import PredictionPersistenceService
from app.prediction.schemas import (
    CoreEngineOutput,
    EffectiveContext,
    PersistablePredictionBundle,
    SamplePoint,
    V3DailyMetrics,
    V3EngineOutput,
    V3SignalLayer,
    V3ThemeSignal,
)


@pytest.fixture
def seed_data(db_session: Session):
    version = ReferenceVersionModel(version="1.0.0")
    db_session.add(version)
    db_session.flush()

    ruleset = PredictionRulesetModel(
        reference_version_id=version.id, version="1.0.0", house_system="placidus"
    )
    db_session.add(ruleset)

    category = PredictionCategoryModel(
        reference_version_id=version.id,
        code="work",
        name="Work",
        display_name="Travail",
        sort_order=1,
        is_enabled=True,
    )
    db_session.add(category)
    db_session.commit()
    return {"version_id": version.id, "ruleset_id": ruleset.id, "category_id": category.id}


def test_v3_persistence_save_and_load(db_session: Session, seed_data):
    # Setup
    user_id = 1
    theme_code = "work"
    local_time = datetime(2026, 3, 11, 12, 0, tzinfo=UTC)

    v3_metrics = V3DailyMetrics(
        score_20=15.0,
        level_day=1.5,
        dominance_day=0.8,
        stability_day=0.9,
        intensity_day=1.2,
        rarity_percentile=5.0,
        avg_score=1.5,
        max_score=2.0,
        min_score=1.0,
        volatility=0.2,
    )

    v3_signal = V3ThemeSignal(
        theme_code=theme_code, timeline={local_time: V3SignalLayer(1.0, 0.5, 0.0, 0.0, 1.5)}
    )

    v3_core = V3EngineOutput(
        engine_version="v3.0.0-test",
        snapshot_version="1.0",
        evidence_pack_version="1.0",
        theme_signals={theme_code: v3_signal},
        daily_metrics={theme_code: v3_metrics},
        run_metadata={"test": True},
        computed_at=datetime.now(UTC),
    )

    core = CoreEngineOutput(
        effective_context=EffectiveContext(
            house_system_requested="placidus",
            house_system_effective="placidus",
            timezone="UTC",
            input_hash="hash_v3_test",
            local_date=date(2026, 3, 11),
        ),
        run_metadata={"engine_mode": "v3"},
        category_scores={theme_code: {"note_20": 15}},
        time_blocks=[],
        turning_points=[],
        decision_windows=[],
        detected_events=[],
        sampling_timeline=[SamplePoint(0.0, local_time)],
    )

    bundle = PersistablePredictionBundle(core=core, v3_core=v3_core)

    # Save
    service = PredictionPersistenceService()
    result = service.save(
        bundle=bundle,
        user_id=user_id,
        local_date=date(2026, 3, 11),
        reference_version_id=seed_data["version_id"],
        ruleset_id=seed_data["ruleset_id"],
        db=db_session,
    )

    assert not result.was_reused
    run_id = result.run.run_id

    # Reload via repository
    repo = DailyPredictionRepository(db_session)
    run_model = db_session.get(DailyPredictionRunModel, run_id)
    snapshot = repo.get_snapshot(run_model)

    assert snapshot is not None
    assert snapshot.engine_version == "v3.0.0-test"
    assert snapshot.engine_mode == "v3"
    assert snapshot.v3_metrics is not None
    assert snapshot.v3_metrics["engine_version"] == "v3.0.0-test"

    # Check category metrics
    cat_score = next(s for s in snapshot.category_scores if s.category_code == theme_code)
    assert cat_score.score_20 == 15.0
    assert cat_score.rarity_percentile == 5.0
    assert cat_score.level_day == 1.5
    assert cat_score.intensity_day == 1.2


def test_v3_persistence_v2_compatibility(db_session: Session, seed_data):
    # Verify that a V2 bundle (no v3_core) still persists and loads
    user_id = 1

    core = CoreEngineOutput(
        effective_context=EffectiveContext(
            house_system_requested="placidus",
            house_system_effective="placidus",
            timezone="UTC",
            input_hash="hash_v2_compat",
            local_date=date(2026, 3, 11),
        ),
        run_metadata={"engine_mode": "v2"},
        category_scores={"work": {"note_20": 10}},
        time_blocks=[],
        turning_points=[],
        decision_windows=[],
        detected_events=[],
    )
    bundle = PersistablePredictionBundle(core=core)

    service = PredictionPersistenceService()
    result = service.save(
        bundle=bundle,
        user_id=user_id,
        local_date=date(2026, 3, 11),
        reference_version_id=seed_data["version_id"],
        ruleset_id=seed_data["ruleset_id"],
        db=db_session,
    )

    repo = DailyPredictionRepository(db_session)
    run_model = db_session.get(DailyPredictionRunModel, result.run.run_id)
    snapshot = repo.get_snapshot(run_model)

    assert snapshot is not None
    assert snapshot.engine_mode == "v2"
    assert snapshot.engine_version is None

    cat_score = next(s for s in snapshot.category_scores if s.category_code == "work")
    assert cat_score.note_20 == 10
    assert cat_score.score_20 is None
