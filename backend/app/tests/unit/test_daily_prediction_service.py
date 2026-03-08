from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

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
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(id=20)

        with pytest.raises(DailyPredictionServiceError) as excinfo:
            service.get_or_compute(
                user_id=1,
                db=db,
                ruleset_version="ruleset_v1",
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
                ruleset_version="ruleset_v1",
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
                ruleset_version="ruleset_v1",
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
                ruleset_version="ruleset_v1",
            )
        assert excinfo.value.code == "timezone_invalid"


def test_location_missing_raises(service, db, mock_profile):
    mock_profile.current_lat = None
    mock_profile.current_lon = None
    
    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo:
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile

        with pytest.raises(DailyPredictionServiceError) as excinfo:
            service.get_or_compute(
                user_id=1,
                db=db,
                ruleset_version="ruleset_v1",
            )
        assert excinfo.value.code == "location_missing"


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
        
        mock_daily_repo.return_value.get_run_by_hash.return_value = None
        
        # Versions resolution
        db.scalar.return_value = 10 # reference_version_id
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(id=20) # ruleset_id
        
        # Engine run
        mock_output = MagicMock(spec=EngineOutput)
        mock_orchestrator.return_value.run.return_value = mock_output
        
        # Persistence
        mock_run = MagicMock(spec=DailyPredictionRunModel)
        persistence_service.save.return_value = MagicMock(run=mock_run, was_reused=False)

        result = service.get_or_compute(
            user_id=1,
            db=db,
            ruleset_version="ruleset_v1",
        )

        assert isinstance(result, ServiceResult)
        assert result.run == mock_run
        assert result.was_reused is False
        assert result.engine_output == mock_output
        
        mock_orchestrator.return_value.run.assert_called_once()


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
        mock_daily_repo.return_value.get_run_by_hash.return_value = mock_existing_run
        
        # Versions resolution
        db.scalar.return_value = 10
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(id=20)

        result = service.get_or_compute(
            user_id=1,
            db=db,
            ruleset_version="ruleset_v1",
            mode=ComputeMode.compute_if_missing
        )

        assert result.run == mock_existing_run
        assert result.was_reused is True
        assert result.engine_output is None
        mock_orchestrator.return_value.run.assert_not_called()


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
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(id=20)

        # Simulate an existing run that must be deleted
        mock_old_run = MagicMock(spec=DailyPredictionRunModel)
        mock_daily_repo.return_value.get_run.return_value = mock_old_run

        # Persistence
        mock_run = MagicMock(spec=DailyPredictionRunModel)
        persistence_service.save.return_value = MagicMock(run=mock_run, was_reused=False)

        result = service.get_or_compute(
            user_id=1,
            db=db,
            ruleset_version="ruleset_v1",
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
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(id=20)

        result = service.get_or_compute(
            user_id=1,
            db=db,
            ruleset_version="ruleset_v1",
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
                ruleset_version="ruleset_v1",
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


def test_read_only_missing(service, db, mock_profile):
    svc_path = "app.services.daily_prediction_service"
    with patch(f"{svc_path}.UserBirthProfileRepository") as mock_profile_repo, \
         patch(f"{svc_path}.DailyPredictionRepository") as mock_daily_repo, \
         patch(f"{svc_path}.PredictionRulesetRepository") as mock_ruleset_repo:
        
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_profile
        mock_daily_repo.return_value.get_run.return_value = None
        
        # Versions resolution
        db.scalar.return_value = 10
        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(id=20)

        result = service.get_or_compute(
            user_id=1,
            db=db,
            ruleset_version="ruleset_v1",
            mode=ComputeMode.read_only
        )

        assert result is None
