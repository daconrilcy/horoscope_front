from datetime import UTC, date, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.prediction_reference import PredictionCategoryModel
from app.infra.db.models.prediction_ruleset import PredictionRulesetModel
from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.infra.db.models.user_prediction_baseline import UserPredictionBaselineModel
from app.infra.db.repositories.user_prediction_baseline_repository import (
    UserPredictionBaselineRepository,
)
from app.jobs.refresh_user_baselines import run_job
from app.prediction.schemas import (
    CoreEngineOutput,
    EffectiveContext,
    PersistablePredictionBundle,
)


def _add_reference_bundle(
    session: Session,
    *,
    version: str,
    house_system: str = "placidus",
    category_code: str = "love",
):
    ref_v = ReferenceVersionModel(version=version, is_locked=False)
    session.add(ref_v)
    session.flush()

    ruleset = PredictionRulesetModel(
        version=version,
        reference_version_id=ref_v.id,
        house_system=house_system,
    )
    session.add(ruleset)
    session.flush()

    category = PredictionCategoryModel(
        reference_version_id=ref_v.id,
        code=category_code,
        name=category_code.title(),
        display_name=category_code.title(),
    )
    session.add(category)
    session.flush()
    return ref_v, ruleset, category


def _seed_minimal_data(session: Session):
    user = UserModel(email="refresh@example.com", password_hash="hash", role="user")
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

    ref_v, ruleset, category = _add_reference_bundle(session, version="2.0.0")

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
    return user, ref_v, ruleset, category


def _store_baseline(
    session: Session,
    *,
    user_id: int,
    category_id: int,
    reference_version_id: int,
    ruleset_id: int,
    house_system_effective: str = "placidus",
) -> UserPredictionBaselineModel:
    repo = UserPredictionBaselineRepository(session)
    baseline = repo.upsert_baseline(
        user_id=user_id,
        category_id=category_id,
        reference_version_id=reference_version_id,
        ruleset_id=ruleset_id,
        house_system_effective=house_system_effective,
        window_days=365,
        window_start_date=date(2025, 3, 11),
        window_end_date=date(2026, 3, 10),
        stats={
            "mean_raw_score": 10.0,
            "std_raw_score": 0.0,
            "mean_note_20": 12.0,
            "std_note_20": 0.0,
            "p10": 10.0,
            "p50": 10.0,
            "p90": 10.0,
            "sample_size_days": 365,
        },
    )
    session.commit()
    model = session.scalar(
        select(UserPredictionBaselineModel).where(UserPredictionBaselineModel.id == baseline.id)
    )
    assert model is not None
    return model


@pytest.fixture
def mock_orchestrator():
    mock = MagicMock()

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
                category_scores={"love": {"raw_score": 10.0, "note_20": 12}},
                time_blocks=[],
                turning_points=[],
                decision_windows=[],
            )
        )

    mock.with_context_loader.return_value = mock
    mock.run.side_effect = mock_run
    return mock


def test_job_refreshes_missing_baseline(db_session, mock_orchestrator):
    user, ref_v, ruleset, _category = _seed_minimal_data(db_session)

    # Patch db_session.close to do nothing during this test
    db_session.close = MagicMock()

    from app.core.config import settings

    with (
        patch.object(settings, "active_reference_version", "2.0.0"),
        patch.object(settings, "_ruleset_version", "2.0.0"),
        patch("app.jobs.refresh_user_baselines.SessionLocal", return_value=db_session),
        patch(
            "app.services.user_prediction_baseline_service.EngineOrchestrator",
            return_value=mock_orchestrator,
        ),
    ):
        # Verify no baseline exists initially
        repo = UserPredictionBaselineRepository(db_session)
        needs = repo.get_users_needing_baseline(
            ref_v.id, ruleset.id, house_system_effective="placidus"
        )
        assert user.id in needs

        # Run the job
        run_job()

        # Verify baseline now exists
        baseline = db_session.scalar(
            select(UserPredictionBaselineModel).where(
                UserPredictionBaselineModel.user_id == user.id
            )
        )
        assert baseline is not None
        assert baseline.mean_raw_score == 10.0


def test_job_idempotence(db_session, mock_orchestrator):
    user, _ref_v, _ruleset, _category = _seed_minimal_data(db_session)
    db_session.close = MagicMock()

    from app.core.config import settings

    with (
        patch.object(settings, "active_reference_version", "2.0.0"),
        patch.object(settings, "_ruleset_version", "2.0.0"),
        patch("app.jobs.refresh_user_baselines.SessionLocal", return_value=db_session),
        patch(
            "app.services.user_prediction_baseline_service.EngineOrchestrator",
            return_value=mock_orchestrator,
        ),
    ):
        run_job()  # First run
        baseline1 = db_session.scalar(
            select(UserPredictionBaselineModel).where(
                UserPredictionBaselineModel.user_id == user.id
            )
        )

        run_job()  # Second run should update the existing row, not create a duplicate
        baseline2 = db_session.scalar(
            select(UserPredictionBaselineModel).where(
                UserPredictionBaselineModel.user_id == user.id
            )
        )

        assert baseline1.id == baseline2.id


def test_job_refreshes_obsolete_baseline(db_session, mock_orchestrator):
    from app.infra.db.models.chart_result import ChartResultModel

    user, ref_v, ruleset, _category = _seed_minimal_data(db_session)
    db_session.close = MagicMock()

    from app.core.config import settings

    with (
        patch.object(settings, "active_reference_version", "2.0.0"),
        patch.object(settings, "_ruleset_version", "2.0.0"),
        patch("app.jobs.refresh_user_baselines.SessionLocal", return_value=db_session),
        patch(
            "app.services.user_prediction_baseline_service.EngineOrchestrator",
            return_value=mock_orchestrator,
        ),
    ):
        run_job()  # Create baseline

        # Manually update birth profile to make baseline obsolete
        profile = db_session.scalar(
            select(UserBirthProfileModel).where(UserBirthProfileModel.user_id == user.id)
        )
        updated_at = datetime.now(UTC) + timedelta(seconds=1)
        profile.updated_at = updated_at
        latest_chart = db_session.scalar(
            select(ChartResultModel).where(ChartResultModel.user_id == user.id)
        )
        latest_chart.created_at = updated_at + timedelta(seconds=1)
        db_session.commit()

        # Verify it needs refresh
        repo = UserPredictionBaselineRepository(db_session)
        needs = repo.get_users_needing_baseline(
            ref_v.id, ruleset.id, house_system_effective="placidus"
        )
        assert user.id in needs

        # Run job again
        run_job()

        # Verify baseline was updated (computed_at should be newer)
        baseline = db_session.scalar(
            select(UserPredictionBaselineModel).where(
                UserPredictionBaselineModel.user_id == user.id
            )
        )
        assert baseline.computed_at > profile.created_at


def test_job_skips_users_until_a_current_natal_chart_exists(db_session):
    user, ref_v, ruleset, _category = _seed_minimal_data(db_session)
    db_session.close = MagicMock()

    profile = db_session.scalar(
        select(UserBirthProfileModel).where(UserBirthProfileModel.user_id == user.id)
    )
    profile.updated_at = datetime.now(UTC) + timedelta(seconds=1)
    db_session.commit()

    repo = UserPredictionBaselineRepository(db_session)
    needs = repo.get_users_needing_baseline(
        ref_v.id,
        ruleset.id,
        house_system_effective="placidus",
    )

    assert needs == []


def test_job_refreshes_baseline_when_house_system_changes(db_session):
    user, ref_v, ruleset, category = _seed_minimal_data(db_session)
    db_session.close = MagicMock()
    _store_baseline(
        db_session,
        user_id=user.id,
        category_id=category.id,
        reference_version_id=ref_v.id,
        ruleset_id=ruleset.id,
        house_system_effective="placidus",
    )
    ruleset.house_system = "whole_sign"
    db_session.commit()

    whole_sign_orchestrator = MagicMock()

    def mock_run(engine_input, **kwargs):
        return PersistablePredictionBundle(
            core=CoreEngineOutput(
                effective_context=EffectiveContext(
                    house_system_requested="whole_sign",
                    house_system_effective="whole_sign",
                    timezone="UTC",
                    input_hash="hash",
                ),
                run_metadata={},
                category_scores={"love": {"raw_score": 10.0, "note_20": 12}},
                time_blocks=[],
                turning_points=[],
                decision_windows=[],
            )
        )

    whole_sign_orchestrator.with_context_loader.return_value = whole_sign_orchestrator
    whole_sign_orchestrator.run.side_effect = mock_run

    from app.core.config import settings

    with (
        patch.object(settings, "active_reference_version", "2.0.0"),
        patch.object(settings, "_ruleset_version", "2.0.0"),
        patch("app.jobs.refresh_user_baselines.SessionLocal", return_value=db_session),
        patch(
            "app.services.user_prediction_baseline_service.EngineOrchestrator",
            return_value=whole_sign_orchestrator,
        ),
    ):
        repo = UserPredictionBaselineRepository(db_session)
        needs = repo.get_users_needing_baseline(
            ref_v.id,
            ruleset.id,
            house_system_effective="whole_sign",
        )
        assert user.id in needs

        run_job()

    baselines = db_session.scalars(
        select(UserPredictionBaselineModel).where(UserPredictionBaselineModel.user_id == user.id)
    ).all()
    assert {baseline.house_system_effective for baseline in baselines} == {
        "placidus",
        "whole_sign",
    }


def test_job_refreshes_baseline_when_active_versions_change(db_session, mock_orchestrator):
    user, ref_v, ruleset, category = _seed_minimal_data(db_session)
    db_session.close = MagicMock()
    _store_baseline(
        db_session,
        user_id=user.id,
        category_id=category.id,
        reference_version_id=ref_v.id,
        ruleset_id=ruleset.id,
    )
    next_ref, next_ruleset, _ = _add_reference_bundle(db_session, version="3.0.0")
    db_session.commit()

    from app.core.config import settings

    with (
        patch.object(settings, "active_reference_version", "3.0.0"),
        patch.object(settings, "_ruleset_version", "3.0.0"),
        patch("app.jobs.refresh_user_baselines.SessionLocal", return_value=db_session),
        patch(
            "app.services.user_prediction_baseline_service.EngineOrchestrator",
            return_value=mock_orchestrator,
        ),
    ):
        repo = UserPredictionBaselineRepository(db_session)
        needs = repo.get_users_needing_baseline(
            next_ref.id,
            next_ruleset.id,
            house_system_effective="placidus",
        )
        assert user.id in needs

        run_job()

    baselines = db_session.scalars(
        select(UserPredictionBaselineModel).where(UserPredictionBaselineModel.user_id == user.id)
    ).all()
    version_pairs = {(baseline.reference_version_id, baseline.ruleset_id) for baseline in baselines}
    assert version_pairs == {(ref_v.id, ruleset.id), (next_ref.id, next_ruleset.id)}


def test_birth_data_api_does_not_trigger_baseline_refresh(db_session):
    from fastapi.testclient import TestClient

    from app.api.dependencies.auth import require_authenticated_user
    from app.infra.db.session import get_db_session
    from app.main import app

    user, _ref_v, _ruleset, _category = _seed_minimal_data(db_session)

    # Mock auth and DB session
    user_id = user.id
    app.dependency_overrides[require_authenticated_user] = lambda: MagicMock(id=user_id)
    app.dependency_overrides[get_db_session] = lambda: db_session

    client = TestClient(app)

    payload = {
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "birth_place": "Paris",
        "birth_timezone": "UTC",
        "birth_lat": 48.8566,
        "birth_lon": 2.3522,
    }

    patch_path = "app.api.v1.routers.users.safe_refresh_user_baseline"
    with patch(patch_path) as mock_refresh:
        response = client.put("/v1/users/me/birth-data", json=payload)
        assert response.status_code == 200

        mock_refresh.assert_not_called()

    app.dependency_overrides.clear()
