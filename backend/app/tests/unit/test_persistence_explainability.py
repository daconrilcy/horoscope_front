import json
from datetime import date, datetime, timezone

import pytest
from sqlalchemy import select

from app.infra.db.models.daily_prediction import (
    DailyPredictionCategoryScoreModel,
    DailyPredictionTurningPointModel,
)
from app.infra.db.models.prediction_reference import PredictionCategoryModel
from app.infra.db.models.prediction_ruleset import PredictionRulesetModel
from app.infra.db.models.reference import ReferenceVersionModel
from app.prediction.editorial_template_engine import EditorialTextOutput
from app.prediction.explainability import (
    CategoryExplainability,
    ContributorEntry,
    ExplainabilityReport,
)
from app.prediction.persistence_service import PredictionPersistenceService
from app.prediction.schemas import AstroEvent, EffectiveContext, EngineOutput
from app.prediction.turning_point_detector import TurningPoint


@pytest.fixture
def seed_data(db_session):
    version = ReferenceVersionModel(version="1.0.0")
    db_session.add(version)
    db_session.flush()

    ruleset = PredictionRulesetModel(
        reference_version_id=version.id, version="1.0.0", house_system="placidus"
    )
    db_session.add(ruleset)

    categories = [
        PredictionCategoryModel(
            reference_version_id=version.id,
            code="love",
            name="Love",
            display_name="Amour",
            sort_order=1,
            is_enabled=True,
        ),
        PredictionCategoryModel(
            reference_version_id=version.id,
            code="work",
            name="Work",
            display_name="Travail",
            sort_order=2,
            is_enabled=True,
        ),
    ]
    db_session.add_all(categories)
    db_session.commit()
    return {
        "version_id": version.id,
        "ruleset_id": ruleset.id,
        "categories": {c.code: c.id for c in categories},
    }


def test_save_with_explainability(db_session, seed_data):
    """Vérifie que les top_contributors sont persistés dans contributors_json."""
    service = PredictionPersistenceService()
    user_id = 1
    local_date = date(2026, 3, 8)
    dt = datetime(2026, 3, 8, 12, 0, tzinfo=timezone.utc)

    # Explainability report
    contributor = ContributorEntry(
        event_type="trine",
        body="Venus",
        target="Mars",
        aspect="trine",
        contribution=5.0,
        local_time=dt,
        orb_deg=0.5,
        phase="direct",
    )
    report = ExplainabilityReport(
        run_input_hash="hash_expl",
        categories={"love": CategoryExplainability("love", [contributor])},
    )

    engine_output = EngineOutput(
        run_metadata={},
        effective_context=EffectiveContext(
            house_system_requested="placidus",
            house_system_effective="placidus",
            local_date=local_date,
            timezone="UTC",
            input_hash="hash_expl",
        ),
        category_scores={"love": {"note_20": 15}},
        turning_points=[],
        time_blocks=[],
        explainability=report,
    )

    result = service.save(
        engine_output=engine_output,
        user_id=user_id,
        local_date=local_date,
        reference_version_id=seed_data["version_id"],
        ruleset_id=seed_data["ruleset_id"],
        db=db_session,
    )

    db_session.flush()
    score = db_session.scalar(
        select(DailyPredictionCategoryScoreModel).where(
            DailyPredictionCategoryScoreModel.run_id == result.run.id,
            DailyPredictionCategoryScoreModel.category_id == seed_data["categories"]["love"],
        )
    )

    assert score.contributors_json is not None
    contributors = json.loads(score.contributors_json)
    assert len(contributors) == 1
    assert contributors[0]["body"] == "Venus"
    assert contributors[0]["contribution"] == 5.0
    assert "2026-03-08T12:00:00" in contributors[0]["local_time"]


def test_save_turning_point_drivers_format(db_session, seed_data):
    """AC3 — Drivers de pivots (vrais AstroEvent) sérialisés en JSON valide."""
    service = PredictionPersistenceService()
    user_id = 1
    local_date = date(2026, 3, 8)
    dt = datetime(2026, 3, 8, 12, 0, tzinfo=timezone.utc)

    driver_event = AstroEvent(
        event_type="conjunction",
        ut_time=0,
        local_time=dt,
        body="Sun",
        target="Moon",
        aspect="conjunction",
        orb_deg=0.5,
        priority=80,
        base_weight=1.0,
    )
    tp = TurningPoint(
        local_time=dt,
        reason="high_priority_event",
        categories_impacted=["love"],
        trigger_event=driver_event,
        severity=0.8,
        driver_events=[driver_event],
    )

    engine_output = EngineOutput(
        run_metadata={},
        effective_context=EffectiveContext(
            house_system_requested="placidus",
            house_system_effective="placidus",
            local_date=local_date,
            timezone="UTC",
            input_hash="hash_tp_drivers",
        ),
        category_scores={},
        turning_points=[tp],
        time_blocks=[],
    )

    result = service.save(
        engine_output=engine_output,
        user_id=user_id,
        local_date=local_date,
        reference_version_id=seed_data["version_id"],
        ruleset_id=seed_data["ruleset_id"],
        db=db_session,
    )

    db_session.flush()
    tp_model = db_session.scalar(
        select(DailyPredictionTurningPointModel).where(
            DailyPredictionTurningPointModel.run_id == result.run.id
        )
    )

    drivers = json.loads(tp_model.driver_json)
    assert len(drivers) == 1
    assert drivers[0]["event_type"] == "conjunction"
    assert drivers[0]["body"] == "Sun"
    assert "2026-03-08T12:00:00" in drivers[0]["local_time"]


def test_save_persists_editorial_text_into_run_and_category_summaries(db_session, seed_data):
    service = PredictionPersistenceService()
    local_date = date(2026, 3, 8)
    engine_output = EngineOutput(
        run_metadata={},
        effective_context=EffectiveContext(
            house_system_requested="placidus",
            house_system_effective="placidus",
            local_date=local_date,
            timezone="UTC",
            input_hash="hash_editorial_text",
        ),
        category_scores={
            "love": {"note_20": 15},
            "work": {"note_20": 12},
        },
        turning_points=[],
        time_blocks=[],
        editorial_text=EditorialTextOutput(
            intro="Journee plutot fluide sur vos axes forts.",
            category_summaries={"love": "L'amour est porteur aujourd'hui."},
            pivot_phrase=None,
            window_phrase=None,
            caution_sante=None,
            caution_argent=None,
        ),
    )

    result = service.save(
        engine_output=engine_output,
        user_id=1,
        local_date=local_date,
        reference_version_id=seed_data["version_id"],
        ruleset_id=seed_data["ruleset_id"],
        db=db_session,
    )

    db_session.flush()
    assert result.run.overall_summary == "Journee plutot fluide sur vos axes forts."

    love_score = db_session.scalar(
        select(DailyPredictionCategoryScoreModel).where(
            DailyPredictionCategoryScoreModel.run_id == result.run.id,
            DailyPredictionCategoryScoreModel.category_id == seed_data["categories"]["love"],
        )
    )
    work_score = db_session.scalar(
        select(DailyPredictionCategoryScoreModel).where(
            DailyPredictionCategoryScoreModel.run_id == result.run.id,
            DailyPredictionCategoryScoreModel.category_id == seed_data["categories"]["work"],
        )
    )

    assert love_score.summary == "L'amour est porteur aujourd'hui."
    assert work_score.summary is None
