from datetime import date
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, inspect, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models.daily_prediction import (
    DailyPredictionCategoryScoreModel,
    DailyPredictionTimeBlockModel,
    DailyPredictionTurningPointModel,
)
from app.infra.db.models.prediction_reference import PredictionCategoryModel
from app.infra.db.models.prediction_ruleset import PredictionRulesetModel, RulesetEventTypeModel
from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.models.user import UserModel
from app.infra.db.repositories.daily_prediction_repository import DailyPredictionRepository

NEW_TABLES_C = [
    "daily_prediction_runs",
    "daily_prediction_category_scores",
    "daily_prediction_turning_points",
    "daily_prediction_time_blocks",
]

EXPECTED_INDEXES_C = {
    "daily_prediction_runs": {
        "ix_daily_prediction_runs_user_id",
        "ix_daily_prediction_runs_user_id_local_date",
    },
    "daily_prediction_category_scores": {"ix_daily_prediction_category_scores_run_id"},
    "daily_prediction_turning_points": {"ix_daily_prediction_turning_points_run_id"},
    "daily_prediction_time_blocks": {"ix_daily_prediction_time_blocks_run_id"},
}


def _alembic_config() -> Config:
    backend_root = Path(__file__).resolve().parents[3]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    return config


def _sqlite_engine(database_url: str) -> Engine:
    engine = create_engine(database_url, future=True)

    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection: object, _: object) -> None:
        del _
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def _setup_engine(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, db_name: str) -> Engine:
    db_path = tmp_path / db_name
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()
    command.upgrade(config, "head")
    return _sqlite_engine(database_url)


def _seed_data(session: Session):
    user = UserModel(email="test@example.com", password_hash="hash", role="user")
    session.add(user)

    ref_version = ReferenceVersionModel(version="1.0.0", is_locked=False)
    session.add(ref_version)
    session.flush()

    ruleset = PredictionRulesetModel(version="v1", reference_version_id=ref_version.id)
    session.add(ruleset)
    session.flush()

    category = PredictionCategoryModel(
        reference_version_id=ref_version.id,
        code="love",
        name="Love",
        display_name="Love",
    )
    session.add(category)
    session.flush()

    event_type = RulesetEventTypeModel(
        ruleset_id=ruleset.id,
        code="aspect_exact",
        name="Aspect Exact",
    )
    session.add(event_type)

    session.commit()
    return user, ref_version, ruleset, category, event_type


def test_migration_c_tables_exist(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    engine = _setup_engine(monkeypatch, tmp_path, "test-c-tables.db")
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    for table in NEW_TABLES_C:
        assert table in tables, f"Table {table} was not created by Alembic"

    for table_name, expected_indexes in EXPECTED_INDEXES_C.items():
        index_names = {index["name"] for index in inspector.get_indexes(table_name)}
        for idx in expected_indexes:
            assert idx in index_names, f"Missing index {idx} on {table_name}"

    engine.dispose()


def test_migration_0035_adds_missing_user_id_index(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "test-c-0035-index-fix.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    command.upgrade(config, "20260307_0034")
    engine_before = _sqlite_engine(database_url)
    before_indexes = {
        index["name"] for index in inspect(engine_before).get_indexes("daily_prediction_runs")
    }
    assert "ix_daily_prediction_runs_user_id" not in before_indexes
    engine_before.dispose()

    command.upgrade(config, "20260307_0035")
    engine_after = _sqlite_engine(database_url)
    after_indexes = {
        index["name"] for index in inspect(engine_after).get_indexes("daily_prediction_runs")
    }
    assert "ix_daily_prediction_runs_user_id" in after_indexes
    engine_after.dispose()


def test_daily_prediction_repository_basic_flow(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    engine = _setup_engine(monkeypatch, tmp_path, "test-c-repo-basic.db")

    with Session(engine) as session:
        user, ref_v, ruleset, category, event_type = _seed_data(session)
        repo = DailyPredictionRepository(session)

        # 1. create_run
        run = repo.create_run(
            user_id=user.id,
            local_date=date(2026, 3, 7),
            timezone="Europe/Paris",
            reference_version_id=ref_v.id,
            ruleset_id=ruleset.id,
            input_hash="hash1",
            house_system_effective="placidus",
        )
        assert run.id is not None

        # 2. get_or_create_run (same hash)
        run2, created = repo.get_or_create_run(
            user_id=user.id,
            local_date=date(2026, 3, 7),
            timezone="Europe/Paris",
            reference_version_id=ref_v.id,
            ruleset_id=ruleset.id,
            input_hash="hash1",
        )
        assert not created
        assert run2.id == run.id
        assert run2.needs_recompute is False

        # 3. add some children
        repo.upsert_category_scores(run.id, [{"category_id": category.id, "note_20": 15}])
        repo.upsert_turning_points(run.id, [{"summary": "Great moment", "severity": 0.8}])
        repo.upsert_time_blocks(run.id, [{"block_index": 0, "summary": "Morning"}])

        full_run = repo.get_full_run(run.id)
        assert full_run is not None
        assert full_run["house_system_effective"] == "placidus"
        assert len(full_run["category_scores"]) == 1
        assert len(full_run["turning_points"]) == 1
        assert len(full_run["time_blocks"]) == 1

        # 4. get_or_create_run (different hash)
        run3, created = repo.get_or_create_run(
            user_id=user.id,
            local_date=date(2026, 3, 7),
            timezone="Europe/Paris",
            reference_version_id=ref_v.id,
            ruleset_id=ruleset.id,
            input_hash="hash2",  # Change hash
        )
        assert not created
        assert run3.id == run.id
        assert run3.input_hash == "hash2"
        assert run3.needs_recompute is True

        run4, created = repo.get_or_create_run(
            user_id=user.id,
            local_date=date(2026, 3, 7),
            timezone="Europe/Paris",
            reference_version_id=ref_v.id,
            ruleset_id=ruleset.id,
            input_hash="hash2",
        )
        assert not created
        assert run4.id == run.id
        assert run4.needs_recompute is False

        # Children should be gone
        full_run_after = repo.get_full_run(run.id)
        assert full_run_after is not None
        assert len(full_run_after["category_scores"]) == 0
        assert len(full_run_after["turning_points"]) == 0
        assert len(full_run_after["time_blocks"]) == 0

    engine.dispose()


def test_daily_prediction_constraints(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    engine = _setup_engine(monkeypatch, tmp_path, "test-c-constraints.db")

    with Session(engine) as session:
        user, ref_v, ruleset, category, event_type = _seed_data(session)
        repo = DailyPredictionRepository(session)

        run = repo.create_run(
            user_id=user.id,
            local_date=date(2026, 3, 7),
            timezone="Europe/Paris",
            reference_version_id=ref_v.id,
            ruleset_id=ruleset.id,
        )

        # Unique constraint on category_scores (run_id, category_id)
        session.add(DailyPredictionCategoryScoreModel(run_id=run.id, category_id=category.id))
        session.flush()

        with session.begin_nested():
            duplicate_score = DailyPredictionCategoryScoreModel(
                run_id=run.id, category_id=category.id
            )
            session.add(duplicate_score)
            with pytest.raises(IntegrityError):
                session.flush()

        # Unique constraint on time_blocks (run_id, block_index)
        session.add(DailyPredictionTimeBlockModel(run_id=run.id, block_index=1))
        session.flush()

        with session.begin_nested():
            duplicate_block = DailyPredictionTimeBlockModel(run_id=run.id, block_index=1)
            session.add(duplicate_block)
            with pytest.raises(IntegrityError):
                session.flush()

    engine.dispose()


def test_upsert_category_scores_idempotence(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """upsert_category_scores() appelé deux fois sur le même run ne crée pas de doublons."""
    engine = _setup_engine(monkeypatch, tmp_path, "test-c-upsert-scores.db")

    with Session(engine) as session:
        user, ref_v, ruleset, category, _ = _seed_data(session)
        repo = DailyPredictionRepository(session)

        run = repo.create_run(
            user_id=user.id,
            local_date=date(2026, 3, 7),
            timezone="Europe/Paris",
            reference_version_id=ref_v.id,
            ruleset_id=ruleset.id,
        )

        # Premier appel
        repo.upsert_category_scores(run.id, [{"category_id": category.id, "note_20": 10}])
        full = repo.get_full_run(run.id)
        assert full is not None
        assert len(full["category_scores"]) == 1
        assert full["category_scores"][0]["note_20"] == 10

        # Deuxième appel avec les mêmes clés — doit écraser, pas dupliquer
        repo.upsert_category_scores(run.id, [{"category_id": category.id, "note_20": 18}])
        full2 = repo.get_full_run(run.id)
        assert full2 is not None
        assert len(full2["category_scores"]) == 1, "doublon détecté — upsert non idempotent"
        assert full2["category_scores"][0]["note_20"] == 18

    engine.dispose()


def test_upsert_turning_points_replaces_existing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """upsert_turning_points() supprime les anciens et insère les nouveaux."""
    engine = _setup_engine(monkeypatch, tmp_path, "test-c-upsert-tp.db")

    with Session(engine) as session:
        user, ref_v, ruleset, _, event_type = _seed_data(session)
        repo = DailyPredictionRepository(session)

        run = repo.create_run(
            user_id=user.id,
            local_date=date(2026, 3, 7),
            timezone="Europe/Paris",
            reference_version_id=ref_v.id,
            ruleset_id=ruleset.id,
        )

        # Premier appel — 2 turning points
        repo.upsert_turning_points(
            run.id,
            [
                {"summary": "Morning shift", "severity": 0.5},
                {"summary": "Evening peak", "severity": 0.9},
            ],
        )
        full = repo.get_full_run(run.id)
        assert full is not None
        assert len(full["turning_points"]) == 2

        # Deuxième appel — doit remplacer, pas cumuler
        repo.upsert_turning_points(run.id, [{"summary": "Single event", "severity": 0.3}])
        full2 = repo.get_full_run(run.id)
        assert full2 is not None
        assert len(full2["turning_points"]) == 1, "anciens turning_points non supprimés"
        assert full2["turning_points"][0]["summary"] == "Single event"

        # Vérification directe en DB — aucun orphelin
        remaining = session.scalars(
            select(DailyPredictionTurningPointModel).where(
                DailyPredictionTurningPointModel.run_id == run.id
            )
        ).all()
        assert len(remaining) == 1

    engine.dispose()


def test_get_user_history(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """get_user_history() retourne les runs dans la plage de dates, ordonnés par date."""
    engine = _setup_engine(monkeypatch, tmp_path, "test-c-history.db")

    with Session(engine) as session:
        user, ref_v, ruleset, _, _ = _seed_data(session)
        repo = DailyPredictionRepository(session)

        dates = [date(2026, 3, 5), date(2026, 3, 6), date(2026, 3, 7), date(2026, 3, 8)]
        for d in dates:
            repo.create_run(
                user_id=user.id,
                local_date=d,
                timezone="Europe/Paris",
                reference_version_id=ref_v.id,
                ruleset_id=ruleset.id,
            )
        session.flush()

        # Plage partielle
        history = repo.get_user_history(user.id, date(2026, 3, 6), date(2026, 3, 7))
        assert len(history) == 2
        assert history[0].local_date == date(2026, 3, 6)
        assert history[1].local_date == date(2026, 3, 7)

        # Plage entière
        all_runs = repo.get_user_history(user.id, date(2026, 3, 5), date(2026, 3, 8))
        assert len(all_runs) == 4

        # Plage hors période — aucun résultat
        empty = repo.get_user_history(user.id, date(2026, 3, 1), date(2026, 3, 4))
        assert len(empty) == 0

    engine.dispose()


def test_get_full_run_not_found(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """get_full_run() retourne None pour un run inexistant."""
    engine = _setup_engine(monkeypatch, tmp_path, "test-c-full-run-none.db")

    with Session(engine) as session:
        repo = DailyPredictionRepository(session)
        result = repo.get_full_run(99999)
        assert result is None

    engine.dispose()


def test_migration_c_downgrade(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "test-c-downgrade.db"
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    config = _alembic_config()

    command.upgrade(config, "20260307_0035")
    command.downgrade(config, "20260307_0033")

    engine = _sqlite_engine(database_url)
    tables_after_downgrade = set(inspect(engine).get_table_names())
    for table in NEW_TABLES_C:
        assert table not in tables_after_downgrade, f"Table {table} still exists after downgrade"
    engine.dispose()
