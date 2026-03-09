from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.core.versions import ACTIVE_RULESET_VERSION
from app.infra.db.models.daily_prediction import DailyPredictionRunModel
from app.infra.db.models.user_birth_profile import UserBirthProfileModel
from app.prediction.schemas import EngineOutput
from app.services.daily_prediction_service import (
    ComputeMode,
    DailyPredictionService,
    DailyPredictionServiceError,
    ServiceResult,
)


@pytest.fixture
def db():
    return MagicMock(spec=Session)


@pytest.fixture
def context_loader():
    return MagicMock()


@pytest.fixture
def persistence_service():
    return MagicMock()


@pytest.fixture
def service(context_loader, persistence_service):
    return DailyPredictionService(
        context_loader=context_loader,
        persistence_service=persistence_service,
    )


@pytest.fixture
def mock_profile():
    profile = MagicMock(spec=UserBirthProfileModel)
    profile.user_id = 1
    profile.birth_timezone = "Europe/Paris"
    profile.current_timezone = "Europe/Paris"
    profile.current_lat = 48.8566
    profile.current_lon = 2.3522
    return profile


def test_user_without_natal(service, db):
    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo, \
         patch(f"{svc_path}.ChartResultRepository") as mock_chart_repo, \
         patch(f"{svc_path}.PredictionRulesetRepository") as mock_ruleset_repo:

        mock_prof = MagicMock(spec=UserBirthProfileModel)
        mock_prof.current_timezone = "Europe/Paris"
        mock_prof.birth_timezone = "Europe/Paris"
        mock_prof.current_lat = 48.8
        mock_prof.current_lon = 2.3

        mock_profile_repo.return_value.get_by_user_id.return_value = mock_prof
        mock_chart_repo.return_value.get_latest_by_user_id.return_value = None
        db.scalar.return_value = 10  # reference_version_id
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )

        with pytest.raises(DailyPredictionServiceError) as excinfo:
            service.get_or_compute(
                user_id=1,
                db=db,
            )
        assert excinfo.value.code == "natal_missing"


def test_user_missing_profile(service, db):
    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo:
        mock_profile_repo.return_value.get_by_user_id.return_value = None

        with pytest.raises(DailyPredictionServiceError) as excinfo:
            service.get_or_compute(
                user_id=1,
                db=db,
            )
        assert excinfo.value.code == "profile_missing"


def test_timezone_missing_raises(service, db, mock_profile):
    mock_profile.current_timezone = None
    mock_profile.birth_timezone = None
    
    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo:
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile

        with pytest.raises(DailyPredictionServiceError) as excinfo:
            service.get_or_compute(
                user_id=1,
                db=db,
            )
        assert excinfo.value.code == "timezone_missing"


def test_timezone_invalid_raises(service, db, mock_profile):
    mock_profile.current_timezone = "Not/AValidZone"
    mock_profile.birth_timezone = None

    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo:
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile

        with pytest.raises(DailyPredictionServiceError) as excinfo:
            service.get_or_compute(
                user_id=1,
                db=db,
            )
        assert excinfo.value.code == "timezone_invalid"


def test_location_missing_raises(service, db, mock_profile):
    mock_profile.current_lat = None
    mock_profile.current_lon = None

    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo, \
         patch(f"{svc_path}.UserBirthProfileService.resolve_coordinates") as mock_resolve:
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile
        mock_resolve.return_value = MagicMock(birth_lat=None, birth_lon=None)

        with pytest.raises(DailyPredictionServiceError) as excinfo:
            service.get_or_compute(
                user_id=1,
                db=db,
            )
        assert excinfo.value.code == "location_missing"


def test_birth_coordinates_fallback_when_current_location_missing(service, db, mock_profile):
    mock_profile.current_lat = None
    mock_profile.current_lon = None

    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo, \
         patch(f"{svc_path}.UserBirthProfileService.resolve_coordinates") as mock_resolve, \
         patch(f"{svc_path}.ChartResultRepository") as mock_chart_repo, \
         patch(f"{svc_path}.DailyPredictionRepository") as mock_daily_repo, \
         patch(f"{svc_path}.PredictionRulesetRepository") as mock_ruleset_repo, \
         patch(f"{svc_path}.EngineOrchestrator") as mock_orchestrator:

        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile
        mock_resolve.return_value = MagicMock(birth_lat=48.8566, birth_lon=2.3522)
        mock_chart_repo.return_value.get_latest_by_user_id.return_value = MagicMock(
            result_payload={"planets": [{"code": "sun", "longitude": 34.08}]}
        )
        mock_daily_repo.return_value.get_run_by_hash_with_details.return_value = None
        db.scalar.return_value = 10
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )
        mock_output = MagicMock(spec=EngineOutput)
        mock_orchestrator.return_value.run.return_value = mock_output
        mock_run = MagicMock(spec=DailyPredictionRunModel)
        persistence_service = service.persistence_service
        persistence_service.save.return_value = MagicMock(run=mock_run, was_reused=False)

        result = service.get_or_compute(user_id=1, db=db)

        assert isinstance(result, ServiceResult)
        mock_resolve.assert_called_once_with(db, mock_profile)


def test_ruleset_auto_seed_in_local_dev(service, db):
    svc_path = "app.services.daily_prediction_service"
    ruleset_repo = MagicMock()
    ruleset_repo.get_ruleset.side_effect = [
        None,
        MagicMock(id=20, reference_version_id=10, version="2.0.0"),
    ]

    with patch(f"{svc_path}.PredictionRulesetRepository", return_value=ruleset_repo), \
         patch(f"{svc_path}.settings") as mock_settings, \
         patch("scripts.seed_31_prediction_reference_v2.run_seed") as mock_run_seed:
        mock_settings.app_env = "development"
        mock_settings.active_ruleset_version = "2.0.0"

        ruleset_id = service._resolve_ruleset_id(db, "2.0.0", expected_reference_version_id=10)

        assert ruleset_id == 20
        mock_run_seed.assert_called_once_with(db)
        db.commit.assert_called_once()


def test_reference_version_auto_seed_in_local_dev(service, db):
    svc_path = "app.services.daily_prediction_service"

    with patch(f"{svc_path}.settings") as mock_settings, \
         patch(
             "app.services.reference_data_service.ReferenceDataService.seed_reference_version"
         ) as mock_seed_reference:
        mock_settings.app_env = "development"
        mock_settings.active_reference_version = "2.0.0"
        db.scalar.side_effect = [None, 10]

        reference_version_id = service._resolve_reference_version_id(db, "2.0.0")

        assert reference_version_id == 10
        mock_seed_reference.assert_any_call(db, "1.0.0")
        mock_seed_reference.assert_any_call(db, "2.0.0")
        assert mock_seed_reference.call_count == 2


def test_ruleset_missing_without_auto_seed_raises(service, db):
    svc_path = "app.services.daily_prediction_service"
    ruleset_repo = MagicMock()
    ruleset_repo.get_ruleset.return_value = None

    with patch(f"{svc_path}.PredictionRulesetRepository", return_value=ruleset_repo), \
         patch(f"{svc_path}.settings") as mock_settings:
        mock_settings.app_env = "production"
        mock_settings.active_ruleset_version = "2.0.0"

        with pytest.raises(DailyPredictionServiceError) as excinfo:
            service._resolve_ruleset_id(db, "2.0.0", expected_reference_version_id=10)

        assert excinfo.value.code == "ruleset_missing"


def test_ruleset_auto_seed_repairs_locked_incomplete_reference(service, db):
    svc_path = "app.services.daily_prediction_service"
    ruleset_repo = MagicMock()
    ruleset_repo.get_ruleset.side_effect = [
        None,
        MagicMock(id=20, reference_version_id=10, version="2.0.0"),
    ]
    locked_version = MagicMock(id=10, version="2.0.0", is_locked=True)
    seed_error = (
        "ERROR: 2.0.0 exists and is LOCKED but is incomplete. Manual investigation required."
    )

    with patch(f"{svc_path}.PredictionRulesetRepository", return_value=ruleset_repo), \
         patch(f"{svc_path}.settings") as mock_settings, \
         patch("scripts.seed_31_prediction_reference_v2.run_seed") as mock_run_seed, \
         patch("scripts.seed_31_prediction_reference_v2.SeedAbortError", RuntimeError):
        mock_settings.app_env = "development"
        mock_settings.active_ruleset_version = "2.0.0"
        mock_settings.active_reference_version = "2.0.0"
        db.get.return_value = locked_version
        mock_run_seed.side_effect = [RuntimeError(seed_error), None]

        ruleset_id = service._resolve_ruleset_id(db, "2.0.0", expected_reference_version_id=10)

        assert ruleset_id == 20
        assert locked_version.is_locked is False
        assert mock_run_seed.call_count == 2
        db.rollback.assert_called_once()
        assert db.commit.call_count == 2


def test_ruleset_seed_abort_is_wrapped_as_service_error(service, db):
    svc_path = "app.services.daily_prediction_service"
    ruleset_repo = MagicMock()
    ruleset_repo.get_ruleset.return_value = None

    with patch(f"{svc_path}.PredictionRulesetRepository", return_value=ruleset_repo), \
         patch(f"{svc_path}.settings") as mock_settings, \
         patch("scripts.seed_31_prediction_reference_v2.run_seed") as mock_run_seed, \
         patch("scripts.seed_31_prediction_reference_v2.SeedAbortError", RuntimeError):
        mock_settings.app_env = "development"
        mock_settings.active_ruleset_version = "2.0.0"
        mock_settings.active_reference_version = "2.0.0"
        mock_run_seed.side_effect = RuntimeError("manual investigation required")
        db.get.return_value = None
        db.scalar.return_value = None

        with pytest.raises(DailyPredictionServiceError) as excinfo:
            service._resolve_ruleset_id(db, "2.0.0", expected_reference_version_id=10)

        assert excinfo.value.code == "ruleset_seed_failed"


def test_user_with_natal_full_compute(
    service, db, mock_profile, context_loader, persistence_service
):
    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo, \
         patch(f"{svc_path}.ChartResultRepository") as mock_chart_repo, \
         patch(f"{svc_path}.DailyPredictionRepository") as mock_daily_repo, \
         patch(f"{svc_path}.PredictionRulesetRepository") as mock_ruleset_repo, \
         patch(f"{svc_path}.EngineOrchestrator") as mock_orchestrator:
        
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile
        
        mock_chart = MagicMock()
        mock_chart.result_payload = {"some": "natal"}
        mock_chart_repo.return_value.get_latest_by_user_id.return_value = mock_chart
        
        mock_daily_repo.return_value.get_run_by_hash_with_details.return_value = None
        
        # Versions resolution
        db.scalar.return_value = 10  # reference_version_id
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )  # ruleset_id
        
        # Engine run
        mock_output = MagicMock(spec=EngineOutput)
        mock_orchestrator.return_value.run.return_value = mock_output
        
        # Persistence
        mock_run = MagicMock(spec=DailyPredictionRunModel)
        persistence_service.save.return_value = MagicMock(run=mock_run, was_reused=False)

        result = service.get_or_compute(
            user_id=1,
            db=db,
        )

        assert isinstance(result, ServiceResult)
        assert result.run == mock_run
        assert result.was_reused is False
        assert result.engine_output == mock_output
        
        mock_orchestrator.return_value.run.assert_called_once()


def test_modern_natal_payload_is_normalized_for_engine(
    service, db, mock_profile, context_loader, persistence_service
):
    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo, \
         patch(f"{svc_path}.ChartResultRepository") as mock_chart_repo, \
         patch(f"{svc_path}.DailyPredictionRepository") as mock_daily_repo, \
         patch(f"{svc_path}.PredictionRulesetRepository") as mock_ruleset_repo, \
         patch(f"{svc_path}.EngineOrchestrator") as mock_orchestrator:

        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile
        mock_chart_repo.return_value.get_latest_by_user_id.return_value = MagicMock(
            result_payload={
                "planet_positions": [
                    {"planet_code": "sun", "longitude": 34.08},
                    {"planet_code": "moon", "longitude": 112.45},
                ],
                "houses": [
                    {"number": 1, "cusp_longitude": 12.5},
                    {"number": 10, "cusp_longitude": 281.2},
                ],
            }
        )
        mock_daily_repo.return_value.get_run_by_hash_with_details.return_value = None
        db.scalar.return_value = 10
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )

        mock_output = MagicMock(spec=EngineOutput)
        mock_orchestrator.return_value.run.return_value = mock_output
        mock_run = MagicMock(spec=DailyPredictionRunModel)
        persistence_service.save.return_value = MagicMock(run=mock_run, was_reused=False)

        result = service.get_or_compute(user_id=1, db=db)

        assert result is not None
        engine_input = mock_orchestrator.return_value.run.call_args.args[0]
        assert engine_input.natal_chart["planets"] == [
            {"code": "sun", "longitude": 34.08},
            {"code": "moon", "longitude": 112.45},
        ]
        assert engine_input.natal_chart["houses"] == [
            {"number": 1, "cusp_longitude": 12.5},
            {"number": 10, "cusp_longitude": 281.2},
        ]


def test_identical_hash_not_recomputed(
    service, db, mock_profile, context_loader, persistence_service
):
    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo, \
         patch(f"{svc_path}.ChartResultRepository") as mock_chart_repo, \
         patch(f"{svc_path}.DailyPredictionRepository") as mock_daily_repo, \
         patch(f"{svc_path}.PredictionRulesetRepository") as mock_ruleset_repo, \
         patch(f"{svc_path}.EngineOrchestrator") as mock_orchestrator:
        
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile
        mock_chart_repo.return_value.get_latest_by_user_id.return_value = MagicMock(
            result_payload={}
        )
        
        # Mock existing run
        mock_existing_run = MagicMock(spec=DailyPredictionRunModel)
        mock_existing_run.overall_summary = "Some summary"
        mock_existing_run.time_blocks = [MagicMock(summary="Block summary")]
        mock_existing_run.turning_points = [MagicMock(summary="TP summary")]
        mock_daily_repo.return_value.get_run_by_hash_with_details.return_value = mock_existing_run
        
        # Versions resolution
        db.scalar.return_value = 10
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )

        result = service.get_or_compute(
            user_id=1,
            db=db,
            mode=ComputeMode.compute_if_missing
        )

        assert result.run == mock_existing_run
        assert result.was_reused is True
        assert result.engine_output is None
        mock_orchestrator.return_value.run.assert_not_called()


def test_stale_cached_run_without_overall_summary_is_recomputed(
    service, db, mock_profile, context_loader, persistence_service
):
    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo, \
         patch(f"{svc_path}.ChartResultRepository") as mock_chart_repo, \
         patch(f"{svc_path}.DailyPredictionRepository") as mock_daily_repo, \
         patch(f"{svc_path}.PredictionRulesetRepository") as mock_ruleset_repo, \
         patch(f"{svc_path}.EngineOrchestrator") as mock_orchestrator:

        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile
        mock_chart_repo.return_value.get_latest_by_user_id.return_value = MagicMock(
            result_payload={}
        )
        stale_run = MagicMock(spec=DailyPredictionRunModel)
        stale_run.id = 99
        stale_run.overall_summary = None
        mock_daily_repo.return_value.get_run_by_hash_with_details.return_value = stale_run
        db.scalar.return_value = 10
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )

        mock_output = MagicMock(spec=EngineOutput)
        mock_orchestrator.return_value.run.return_value = mock_output
        fresh_run = MagicMock(spec=DailyPredictionRunModel)
        persistence_service.save.return_value = MagicMock(run=fresh_run, was_reused=False)

        result = service.get_or_compute(user_id=1, db=db)

        assert result.run == fresh_run
        assert result.was_reused is False
        db.delete.assert_called_once_with(stale_run)
        db.flush.assert_called()
        mock_orchestrator.return_value.run.assert_called_once()


def test_stale_cached_run_with_missing_block_summaries_is_recomputed(
    service, db, mock_profile, context_loader, persistence_service
):
    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo, \
         patch(f"{svc_path}.ChartResultRepository") as mock_chart_repo, \
         patch(f"{svc_path}.DailyPredictionRepository") as mock_daily_repo, \
         patch(f"{svc_path}.PredictionRulesetRepository") as mock_ruleset_repo, \
         patch(f"{svc_path}.EngineOrchestrator") as mock_orchestrator:

        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile
        mock_chart_repo.return_value.get_latest_by_user_id.return_value = MagicMock(
            result_payload={}
        )
        stale_run = MagicMock(spec=DailyPredictionRunModel)
        stale_run.id = 99
        stale_run.overall_summary = "Some summary"
        stale_run.time_blocks = [MagicMock(summary=None)] # Missing summary
        stale_run.turning_points = [MagicMock(summary="Valid summary")]
        
        mock_daily_repo.return_value.get_run_by_hash_with_details.return_value = stale_run
        db.scalar.return_value = 10
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )

        mock_output = MagicMock(spec=EngineOutput)
        mock_orchestrator.return_value.run.return_value = mock_output
        fresh_run = MagicMock(spec=DailyPredictionRunModel)
        persistence_service.save.return_value = MagicMock(run=fresh_run, was_reused=False)

        result = service.get_or_compute(user_id=1, db=db)

        assert result.run == fresh_run
        assert result.was_reused is False
        db.delete.assert_called_once_with(stale_run)
        db.flush.assert_called()
        mock_orchestrator.return_value.run.assert_called_once()


def test_stale_cached_run_with_technical_tp_summary_is_recomputed(
    service, db, mock_profile, context_loader, persistence_service
):
    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo, \
         patch(f"{svc_path}.ChartResultRepository") as mock_chart_repo, \
         patch(f"{svc_path}.DailyPredictionRepository") as mock_daily_repo, \
         patch(f"{svc_path}.PredictionRulesetRepository") as mock_ruleset_repo, \
         patch(f"{svc_path}.EngineOrchestrator") as mock_orchestrator:

        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile
        mock_chart_repo.return_value.get_latest_by_user_id.return_value = MagicMock(
            result_payload={}
        )
        stale_run = MagicMock(spec=DailyPredictionRunModel)
        stale_run.id = 99
        stale_run.overall_summary = "Some summary"
        stale_run.time_blocks = [MagicMock(summary="Valid summary")]
        stale_run.turning_points = [MagicMock(summary="delta_note")] # Technical summary
        
        mock_daily_repo.return_value.get_run_by_hash_with_details.return_value = stale_run
        db.scalar.return_value = 10
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )

        mock_output = MagicMock(spec=EngineOutput)
        mock_orchestrator.return_value.run.return_value = mock_output
        fresh_run = MagicMock(spec=DailyPredictionRunModel)
        persistence_service.save.return_value = MagicMock(run=fresh_run, was_reused=False)

        result = service.get_or_compute(user_id=1, db=db)

        assert result.run == fresh_run
        assert result.was_reused is False
        db.delete.assert_called_once_with(stale_run)
        db.flush.assert_called()
        mock_orchestrator.return_value.run.assert_called_once()


def test_force_recompute(service, db, mock_profile, context_loader, persistence_service):
    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo, \
         patch(f"{svc_path}.ChartResultRepository") as mock_chart_repo, \
         patch(f"{svc_path}.DailyPredictionRepository") as mock_daily_repo, \
         patch(f"{svc_path}.PredictionRulesetRepository") as mock_ruleset_repo, \
         patch(f"{svc_path}.EngineOrchestrator") as mock_orchestrator:

        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile
        mock_chart_repo.return_value.get_latest_by_user_id.return_value = MagicMock(
            result_payload={}
        )

        # Versions resolution
        db.scalar.return_value = 10
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )

        # Simulate an existing run that must be deleted
        mock_old_run = MagicMock(spec=DailyPredictionRunModel)
        mock_daily_repo.return_value.get_run.return_value = mock_old_run

        # Persistence
        mock_run = MagicMock(spec=DailyPredictionRunModel)
        persistence_service.save.return_value = MagicMock(run=mock_run, was_reused=False)

        result = service.get_or_compute(
            user_id=1,
            db=db,
            mode=ComputeMode.force_recompute
        )

        assert result.was_reused is False
        mock_orchestrator.return_value.run.assert_called_once()
        # Verify old run was deleted before engine run (core force_recompute behaviour)
        db.delete.assert_called_once_with(mock_old_run)
        db.flush.assert_called()


def test_read_only_existing(service, db, mock_profile):
    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo, \
         patch(f"{svc_path}.DailyPredictionRepository") as mock_daily_repo, \
         patch(f"{svc_path}.PredictionRulesetRepository") as mock_ruleset_repo:
        
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile
        
        mock_existing_run = MagicMock(spec=DailyPredictionRunModel)
        mock_daily_repo.return_value.get_run.return_value = mock_existing_run
        
        # Versions resolution
        db.scalar.return_value = 10
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )

        result = service.get_or_compute(
            user_id=1,
            db=db,
            mode=ComputeMode.read_only
        )

        assert result.run == mock_existing_run
        assert result.was_reused is True
        assert result.engine_output is None


def test_version_missing_raises(service, db, mock_profile):
    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo:
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile
        # db.scalar returns None → reference version introuvable
        db.scalar.return_value = None

        with pytest.raises(DailyPredictionServiceError) as excinfo:
            service.get_or_compute(
                user_id=1,
                db=db,
            )
        assert excinfo.value.code == "version_missing"


def test_ruleset_missing_raises(service, db, mock_profile):
    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo, \
         patch(f"{svc_path}.PredictionRulesetRepository") as mock_ruleset_repo:
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile
        db.scalar.return_value = 10  # reference_version_id OK
        mock_ruleset_repo.return_value.get_ruleset.return_value = None  # ruleset introuvable

        with pytest.raises(DailyPredictionServiceError) as excinfo:
            service.get_or_compute(
                user_id=1,
                db=db,
                ruleset_version="unknown_ruleset",
            )
        assert excinfo.value.code == "ruleset_missing"


def test_ruleset_inconsistent_raises(service, db, mock_profile):
    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo, \
         patch(f"{svc_path}.PredictionRulesetRepository") as mock_ruleset_repo:
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile
        db.scalar.return_value = 10  # reference_version_id = 10
        
        # ruleset linked to reference_version_id = 99 (inconsistent)
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=99
        )

        with pytest.raises(DailyPredictionServiceError) as excinfo:
            service.get_or_compute(
                user_id=1,
                db=db,
                ruleset_version="v2",
                reference_version="ref10"
            )
        assert excinfo.value.code == "ruleset_inconsistent"


def test_ruleset_legacy_logs_deprecation(service, db, mock_profile, caplog):
    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo, \
         patch(f"{svc_path}.PredictionRulesetRepository") as mock_ruleset_repo, \
         patch(f"{svc_path}.ChartResultRepository") as mock_chart_repo:
        
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile
        mock_chart_repo.return_value.get_latest_by_user_id.return_value = MagicMock(
            result_payload={}
        )
        # Versions resolution
        db.scalar.return_value = 10
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )

        with caplog.at_level(logging.WARNING):
            # Use compute_if_missing and return existing run to avoid further complexity
            with patch(f"{svc_path}.DailyPredictionRepository") as mock_daily_repo:
                mock_daily_repo.return_value.get_run_by_hash_with_details.return_value = MagicMock()
                service.get_or_compute(
                    user_id=1,
                    db=db,
                    ruleset_version="1.0.0"
                )
        
        assert "DEPRECATION: Legacy ruleset '1.0.0' is being used" in caplog.text
        assert f"canonical version '{ACTIVE_RULESET_VERSION}'" in caplog.text


def test_prediction_run_log_includes_ruleset_version(service, db, mock_profile, caplog):
    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo, \
         patch(f"{svc_path}.ChartResultRepository") as mock_chart_repo, \
         patch(f"{svc_path}.DailyPredictionRepository") as mock_daily_repo, \
         patch(f"{svc_path}.PredictionRulesetRepository") as mock_ruleset_repo:

        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile
        mock_chart_repo.return_value.get_latest_by_user_id.return_value = MagicMock(
            result_payload={}
        )
        mock_existing_run = MagicMock(spec=DailyPredictionRunModel)
        mock_daily_repo.return_value.get_run_by_hash_with_details.return_value = mock_existing_run
        db.scalar.return_value = 10
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )

        with caplog.at_level(logging.INFO):
            result = service.get_or_compute(
                user_id=1,
                db=db,
                ruleset_version="1.0.0",
            )

        assert result is not None
        prediction_run_records = [
            record for record in caplog.records if record.message == "prediction.run"
        ]
        assert prediction_run_records
        assert prediction_run_records[-1].ruleset_version == "1.0.0"
        assert prediction_run_records[-1].was_reused is True


def test_read_only_missing(service, db, mock_profile):
    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo, \
         patch(f"{svc_path}.DailyPredictionRepository") as mock_daily_repo, \
         patch(f"{svc_path}.PredictionRulesetRepository") as mock_ruleset_repo:
        
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile
        mock_daily_repo.return_value.get_run.return_value = None
        
        # Versions resolution
        db.scalar.return_value = 10
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )

        result = service.get_or_compute(
            user_id=1,
            db=db,
            mode=ComputeMode.read_only
        )

        assert result is None
