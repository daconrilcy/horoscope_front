from __future__ import annotations

from datetime import date, datetime
from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.daily_prediction import (
    DailyPredictionCategoryScoreModel,
    DailyPredictionRunModel,
)
from app.infra.db.models.prediction_reference import PredictionCategoryModel
from app.infra.db.models.prediction_ruleset import PredictionRulesetModel
from app.infra.db.models.reference import ReferenceVersionModel
from app.prediction.persistence_service import PredictionPersistenceService
from app.prediction.schemas import EffectiveContext, EngineOutput


def make_effective_context(input_hash: str) -> EffectiveContext:
    return EffectiveContext(
        house_system_requested="placidus",
        house_system_effective="placidus",
        timezone="UTC",
        input_hash=input_hash,
    )


def save_output(
    service: PredictionPersistenceService,
    engine_output: EngineOutput,
    user_id: int,
    local_date: date,
    seed_data: dict[str, object],
    db_session: Session,
):
    return service.save(
        engine_output,
        user_id,
        local_date,
        seed_data["version_id"],
        seed_data["ruleset_id"],
        db_session,
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


def test_create_new_run(db_session: Session, seed_data):
    service = PredictionPersistenceService()
    user_id = 1
    local_date = date(2026, 3, 7)

    engine_output = EngineOutput(
        run_metadata={},
        effective_context=make_effective_context("hash1"),
        category_scores={
            "love": {
                "note_20": 15,
                "raw_score": 0.5,
                "normalized_score": 0.6,
                "power": 0.7,
                "volatility": 0.1,
            },
            "work": {
                "note_20": 18,
                "raw_score": 0.8,
                "normalized_score": 0.9,
                "power": 0.5,
                "volatility": 0.2,
            },
        },
        turning_points=[],
        time_blocks=[],
    )

    result = save_output(service, engine_output, user_id, local_date, seed_data, db_session)

    assert result.was_reused is False
    assert result.run.id is not None

    # Verify DB state
    db_session.expire_all()
    run = db_session.get(DailyPredictionRunModel, result.run.id)
    assert run.user_id == user_id
    assert run.input_hash == "hash1"
    assert run.house_system_effective == "placidus"
    assert len(run.category_scores) == 2


def test_reuse_existing_hash(db_session: Session, seed_data):
    service = PredictionPersistenceService()
    user_id = 1
    local_date = date(2026, 3, 7)
    engine_output = EngineOutput(
        run_metadata={},
        effective_context=make_effective_context("hash1"),
        category_scores={"love": {"note_20": 15}},
        turning_points=[],
        time_blocks=[],
    )

    # First save
    res1 = save_output(service, engine_output, user_id, local_date, seed_data, db_session)
    assert res1.was_reused is False

    # Second save same hash
    res2 = save_output(service, engine_output, user_id, local_date, seed_data, db_session)
    assert res2.was_reused is True
    assert res2.run.id == res1.run.id


def test_rank_correct(db_session: Session, seed_data):
    service = PredictionPersistenceService()
    user_id = 1
    local_date = date(2026, 3, 7)

    # Work (18) should be rank 1, Love (15) rank 2
    engine_output = EngineOutput(
        run_metadata={},
        effective_context=make_effective_context("hash_rank"),
        category_scores={
            "love": {"note_20": 15, "raw_score": 0.5},
            "work": {"note_20": 18, "raw_score": 0.8},
        },
    )

    result = save_output(service, engine_output, user_id, local_date, seed_data, db_session)

    scores = {s.category.code: s.rank for s in result.run.category_scores}
    assert scores["work"] == 1
    assert scores["love"] == 2


def test_rank_tiebreak_sort_order(db_session: Session, seed_data):
    service = PredictionPersistenceService()
    user_id = 1
    local_date = date(2026, 3, 7)

    # Same note 15. Love (sort_order=1) should be rank 1, Work (sort_order=2) rank 2
    engine_output = EngineOutput(
        run_metadata={},
        effective_context=make_effective_context("hash_tie"),
        category_scores={"love": {"note_20": 15}, "work": {"note_20": 15}},
    )

    result = save_output(service, engine_output, user_id, local_date, seed_data, db_session)

    scores = {s.category.code: s.rank for s in result.run.category_scores}
    assert scores["love"] == 1
    assert scores["work"] == 2


def test_turning_points_persisted(db_session: Session, seed_data):
    service = PredictionPersistenceService()
    user_id = 1
    local_date = date(2026, 3, 7)

    engine_output = EngineOutput(
        run_metadata={},
        effective_context=make_effective_context("hash_tp"),
        category_scores={},
        turning_points=[
            {
                "occurred_at_local": datetime(2026, 3, 7, 10, 0),
                "severity": 0.9,
                "summary": "High intensity point",
                "drivers": [{"event": "Sun conjunct Natal Moon", "impact": 0.8}],
            }
        ],
        time_blocks=[],
    )

    result = save_output(service, engine_output, user_id, local_date, seed_data, db_session)

    assert len(result.run.turning_points) == 1
    tp = result.run.turning_points[0]
    assert tp.severity == 0.9
    assert tp.summary == "High intensity point"
    assert "Sun conjunct Natal Moon" in tp.driver_json


def test_time_blocks_persisted(db_session: Session, seed_data):
    service = PredictionPersistenceService()
    user_id = 1
    local_date = date(2026, 3, 7)

    engine_output = EngineOutput(
        run_metadata={},
        effective_context=make_effective_context("hash_blocks"),
        category_scores={},
        turning_points=[],
        time_blocks=[
            {
                "block_index": 0,
                "start_at_local": datetime(2026, 3, 7, 0, 0),
                "end_at_local": datetime(2026, 3, 7, 6, 0),
                "tone_code": "calm",
                "summary": "A peaceful morning",
                "dominant_categories": ["love"],
            }
        ],
    )

    result = save_output(service, engine_output, user_id, local_date, seed_data, db_session)

    assert len(result.run.time_blocks) == 1
    block = result.run.time_blocks[0]
    assert block.block_index == 0
    assert block.tone_code == "calm"
    assert "love" in block.dominant_categories_json


def test_transaction_rollback(db_session: Session, seed_data):
    service = PredictionPersistenceService()
    user_id = 1
    local_date = date(2026, 3, 7)

    engine_output = EngineOutput(
        run_metadata={},
        effective_context=make_effective_context("hash_fail"),
        category_scores={"love": {"note_20": 15}},
        turning_points=[],
        time_blocks=[],
    )

    # Inject a deterministic failure mid-save (after create_run, before children commit)
    with patch.object(service, "_save_scores", side_effect=RuntimeError("injected failure")):
        with pytest.raises(RuntimeError, match="injected failure"):
            service.save(
                engine_output,
                user_id,
                local_date,
                seed_data["version_id"],
                seed_data["ruleset_id"],
                db_session,
            )

    # Rollback simulates what the caller (endpoint/use-case) does on error
    db_session.rollback()
    run = db_session.scalar(
        select(DailyPredictionRunModel).where(DailyPredictionRunModel.input_hash == "hash_fail")
    )
    assert run is None


def test_new_run_on_hash_change(db_session: Session, seed_data):
    service = PredictionPersistenceService()
    user_id = 1

    def make_output(hash_val, local_date):
        return EngineOutput(
            run_metadata={},
            effective_context=make_effective_context(hash_val),
            category_scores={"love": {"note_20": 15}},
            turning_points=[],
            time_blocks=[],
        ), local_date

    output_a, date_a = make_output("hash_a", date(2026, 3, 7))
    output_b, date_b = make_output(
        "hash_b", date(2026, 3, 8)
    )  # different date avoids unique constraint

    res1 = save_output(service, output_a, user_id, date_a, seed_data, db_session)
    res2 = save_output(service, output_b, user_id, date_b, seed_data, db_session)

    assert res1.was_reused is False
    assert res2.was_reused is False
    assert res1.run.id != res2.run.id


def test_scores_persisted(db_session: Session, seed_data):
    service = PredictionPersistenceService()
    user_id = 1
    local_date = date(2026, 3, 7)

    engine_output = EngineOutput(
        run_metadata={},
        effective_context=make_effective_context("hash_scores"),
        category_scores={
            "love": {
                "note_20": 15,
                "raw_score": 0.5,
                "normalized_score": 0.6,
                "power": 0.7,
                "volatility": 0.1,
            },
            "work": {
                "note_20": 18,
                "raw_score": 0.8,
                "normalized_score": 0.9,
                "power": 0.5,
                "volatility": 0.2,
            },
        },
        turning_points=[],
        time_blocks=[],
    )

    result = save_output(service, engine_output, user_id, local_date, seed_data, db_session)

    db_session.expire_all()
    scores = db_session.scalars(
        select(DailyPredictionCategoryScoreModel).where(
            DailyPredictionCategoryScoreModel.run_id == result.run.id
        )
    ).all()
    assert len(scores) == 2
    persisted_category_ids = {s.category_id for s in scores}
    assert seed_data["categories"]["love"] in persisted_category_ids
    assert seed_data["categories"]["work"] in persisted_category_ids


def test_idempotent_double_save(db_session: Session, seed_data):
    service = PredictionPersistenceService()
    user_id = 1
    local_date = date(2026, 3, 7)

    engine_output = EngineOutput(
        run_metadata={},
        effective_context=make_effective_context("hash_idempotent"),
        category_scores={"love": {"note_20": 15}},
        turning_points=[],
        time_blocks=[],
    )

    save_output(service, engine_output, user_id, local_date, seed_data, db_session)
    res2 = save_output(service, engine_output, user_id, local_date, seed_data, db_session)

    assert res2.was_reused is True

    db_session.expire_all()
    runs = db_session.scalars(
        select(DailyPredictionRunModel).where(
            DailyPredictionRunModel.user_id == user_id,
            DailyPredictionRunModel.input_hash == "hash_idempotent",
        )
    ).all()
    assert len(runs) == 1  # AC7: un seul run en DB
