from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models.prediction_reference import PredictionCategoryModel
from app.infra.db.models.prediction_ruleset import PredictionRulesetModel
from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.repositories.user_prediction_baseline_repository import (
    UserPredictionBaselineRepository,
)
from app.prediction.schemas import (
    CoreEngineOutput,
    EffectiveContext,
    PersistablePredictionBundle,
)
from app.services.user_profile.prediction_baseline_service import UserPredictionBaselineService


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
    session.flush()

    profile = UserBirthProfileModel(
        user_id=user.id,
        birth_date=date(1990, 1, 1),
        birth_timezone="UTC",
        birth_place="Paris",
        birth_lat=48.8566,
        birth_lon=2.3522,
    )
    session.add(profile)

    ref_version = ReferenceVersionModel(version="2.0.0", is_locked=False)
    session.add(ref_version)
    session.flush()

    ruleset = PredictionRulesetModel(
        version="2.0.0", reference_version_id=ref_version.id, house_system="placidus"
    )
    session.add(ruleset)
    session.flush()

    category = PredictionCategoryModel(
        reference_version_id=ref_version.id,
        code="love",
        name="Love",
        display_name="Love",
    )
    session.add(category)

    # Need a chart result for the resolver
    from app.infra.db.models.chart_result import ChartResultModel

    chart = ChartResultModel(
        user_id=user.id,
        chart_id="test-chart",
        reference_version="2.0.0",
        ruleset_version="2.0.0",
        input_hash="hash",
        result_payload={
            "planets": [{"code": "sun", "longitude": 0.0}],
            "houses": [{"number": i, "cusp_longitude": i * 30.0} for i in range(1, 13)],
        },
    )
    session.add(chart)

    session.commit()
    return user, ref_version, ruleset, category


def test_migration_baseline_table_exists(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    engine = _setup_engine(monkeypatch, tmp_path, "test-baseline-migration.db")
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    assert "user_prediction_baselines" in tables

    indexes = {idx["name"] for idx in inspector.get_indexes("user_prediction_baselines")}
    assert "ix_user_prediction_baselines_user_id" in indexes
    assert "ix_user_prediction_baselines_category_id" in indexes
    engine.dispose()


def test_baseline_repository_upsert(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    engine = _setup_engine(monkeypatch, tmp_path, "test-baseline-repo.db")
    with Session(engine) as session:
        user, ref_v, ruleset, category = _seed_data(session)
        repo = UserPredictionBaselineRepository(session)

        stats = {
            "mean_raw_score": 10.5,
            "std_raw_score": 2.1,
            "mean_note_20": 12.0,
            "std_note_20": 1.5,
            "p10": 8.0,
            "p50": 10.5,
            "p90": 13.0,
            "sample_size_days": 365,
        }

        baseline = repo.upsert_baseline(
            user_id=user.id,
            category_id=category.id,
            reference_version_id=ref_v.id,
            ruleset_id=ruleset.id,
            house_system_effective="placidus",
            window_days=365,
            window_start_date=date(2025, 1, 1),
            window_end_date=date(2025, 12, 31),
            stats=stats,
        )

        assert baseline.mean_raw_score == 10.5
        assert baseline.category_code == "love"
        assert baseline.window_start_date == date(2025, 1, 1)
        assert baseline.window_end_date == date(2025, 12, 31)

        # Test update
        stats["mean_raw_score"] = 11.0
        baseline2 = repo.upsert_baseline(
            user_id=user.id,
            category_id=category.id,
            reference_version_id=ref_v.id,
            ruleset_id=ruleset.id,
            house_system_effective="placidus",
            window_days=365,
            window_start_date=date(2025, 1, 1),
            window_end_date=date(2025, 12, 31),
            stats=stats,
        )
        assert baseline2.id == baseline.id
        assert baseline2.mean_raw_score == 11.0
    engine.dispose()


def test_baseline_repository_versions_and_windows_are_distinct(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    engine = _setup_engine(monkeypatch, tmp_path, "test-baseline-versioning.db")
    with Session(engine) as session:
        user, ref_v, ruleset, category = _seed_data(session)
        repo = UserPredictionBaselineRepository(session)

        stats = {
            "mean_raw_score": 10.5,
            "std_raw_score": 2.1,
            "mean_note_20": 12.0,
            "std_note_20": 1.5,
            "p10": 8.0,
            "p50": 10.5,
            "p90": 13.0,
            "sample_size_days": 365,
        }

        first = repo.upsert_baseline(
            user_id=user.id,
            category_id=category.id,
            reference_version_id=ref_v.id,
            ruleset_id=ruleset.id,
            house_system_effective="placidus",
            window_days=365,
            window_start_date=date(2025, 1, 1),
            window_end_date=date(2025, 12, 31),
            stats=stats,
        )
        second = repo.upsert_baseline(
            user_id=user.id,
            category_id=category.id,
            reference_version_id=ref_v.id,
            ruleset_id=ruleset.id,
            house_system_effective="placidus",
            window_days=365,
            window_start_date=date(2025, 2, 1),
            window_end_date=date(2026, 1, 31),
            stats=stats,
        )

        assert first.id != second.id
        baselines = repo.get_baselines_for_user(
            user_id=user.id,
            reference_version_id=ref_v.id,
            ruleset_id=ruleset.id,
            house_system_effective="placidus",
            window_days=365,
            window_start_date=date(2025, 1, 1),
            window_end_date=date(2025, 12, 31),
        )
        assert [baseline.id for baseline in baselines] == [first.id]
    engine.dispose()


def test_baseline_service_generation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    engine = _setup_engine(monkeypatch, tmp_path, "test-baseline-service.db")
    with Session(engine) as session:
        user, ref_v, ruleset, category = _seed_data(session)

        # Mock dependencies
        mock_ctx_loader = MagicMock()
        mock_orchestrator = MagicMock()

        # Mock orchestrator run to return fixed scores
        def mock_run(engine_input, **kwargs):
            return PersistablePredictionBundle(
                core=CoreEngineOutput(
                    effective_context=EffectiveContext(
                        house_system_requested="placidus",
                        house_system_effective="placidus",
                        timezone="UTC",
                        input_hash="hash",
                    ),
                    run_metadata={},
                    category_scores={
                        "love": {"raw_score": 10.0, "note_20": 12},
                    },
                    time_blocks=[],
                    turning_points=[],
                    decision_windows=[],
                )
            )

        mock_orchestrator.with_context_loader.return_value = mock_orchestrator
        mock_orchestrator.run.side_effect = mock_run

        service = UserPredictionBaselineService(
            context_loader=mock_ctx_loader,
            orchestrator=mock_orchestrator,
        )

        # Generate baseline for 3 days to be fast
        results = service.generate_baseline(
            db=session,
            user_id=user.id,
            window_days=3,
            reference_version="2.0.0",
            ruleset_version="2.0.0",
            end_date=date(2026, 3, 10),
        )

        assert "love" in results
        baseline = results["love"]
        assert baseline.mean_raw_score == 10.0
        assert baseline.sample_size_days == 3
        assert baseline.std_raw_score == 0.0  # Constant scores
        assert baseline.window_start_date == date(2026, 3, 8)
        assert baseline.window_end_date == date(2026, 3, 10)

        # Verify orchestrator was called 3 times
        assert mock_orchestrator.run.call_count == 3

    engine.dispose()


def test_baseline_service_degenerated_cases(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    engine = _setup_engine(monkeypatch, tmp_path, "test-baseline-degenerated.db")
    with Session(engine) as session:
        user, ref_v, ruleset, category = _seed_data(session)

        # Mock dependencies
        mock_ctx_loader = MagicMock()
        mock_orchestrator = MagicMock()

        # Mock orchestrator run to return fixed scores (zero variance)
        def mock_run(engine_input, **kwargs):
            return PersistablePredictionBundle(
                core=CoreEngineOutput(
                    effective_context=EffectiveContext(
                        house_system_requested="placidus",
                        house_system_effective="placidus",
                        timezone="UTC",
                        input_hash="hash",
                    ),
                    run_metadata={},
                    category_scores={
                        "love": {"raw_score": 10.0, "note_20": 12},
                        "money": {"raw_score": 5.0, "note_20": 10},
                    },
                    time_blocks=[],
                    turning_points=[],
                    decision_windows=[],
                )
            )

        mock_orchestrator.with_context_loader.return_value = mock_orchestrator
        mock_orchestrator.run.side_effect = mock_run

        service = UserPredictionBaselineService(
            context_loader=mock_ctx_loader,
            orchestrator=mock_orchestrator,
        )

        # 1. Test null variance (same score every day)
        results = service.generate_baseline(
            db=session,
            user_id=user.id,
            window_days=2,
            reference_version="2.0.0",
            ruleset_version="2.0.0",
            end_date=date(2026, 3, 10),
        )
        assert results["love"].std_raw_score == 0.0

        # 2. Test category missing in DB (e.g. "money" not seeded)
        # We only seeded "love" in _seed_data
        assert "money" not in results

    engine.dispose()


def test_baseline_service_skips_incomplete_history(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    engine = _setup_engine(monkeypatch, tmp_path, "test-baseline-incomplete.db")
    with Session(engine) as session:
        user, ref_v, ruleset, category = _seed_data(session)

        mock_ctx_loader = MagicMock()
        mock_orchestrator = MagicMock()
        run_count = 0

        def mock_run(engine_input, **kwargs):
            nonlocal run_count
            run_count += 1
            category_scores = {"love": {"raw_score": 10.0, "note_20": 12}}
            if run_count == 1:
                category_scores["friendship"] = {"raw_score": 7.0, "note_20": 11}
            return PersistablePredictionBundle(
                core=CoreEngineOutput(
                    effective_context=EffectiveContext(
                        house_system_requested="placidus",
                        house_system_effective="placidus",
                        timezone="UTC",
                        input_hash="hash",
                    ),
                    run_metadata={},
                    category_scores=category_scores,
                    time_blocks=[],
                    turning_points=[],
                    decision_windows=[],
                )
            )

        session.add(
            PredictionCategoryModel(
                reference_version_id=ref_v.id,
                code="friendship",
                name="Friendship",
                display_name="Friendship",
                sort_order=2,
            )
        )
        session.commit()

        mock_orchestrator.with_context_loader.return_value = mock_orchestrator
        mock_orchestrator.run.side_effect = mock_run

        service = UserPredictionBaselineService(
            context_loader=mock_ctx_loader,
            orchestrator=mock_orchestrator,
        )

        results = service.generate_baseline(
            db=session,
            user_id=user.id,
            window_days=2,
            reference_version="2.0.0",
            ruleset_version="2.0.0",
            end_date=date(2026, 3, 10),
        )

        assert "love" in results
        assert "friendship" not in results
    engine.dispose()
