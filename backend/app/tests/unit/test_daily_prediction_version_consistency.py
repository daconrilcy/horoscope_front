from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.repositories.prediction_ruleset_repository import RulesetData
from app.services.daily_prediction_service import DailyPredictionService
from app.services.daily_prediction_types import ComputeMode, DailyPredictionServiceError


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


@pytest.fixture
def service():
    return DailyPredictionService(context_loader=MagicMock(), persistence_service=MagicMock())


def test_get_or_compute_reads_runtime_versions_at_call_time(
    service, mock_db, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(settings, "active_reference_version", "9.9.9")
    monkeypatch.setattr(settings, "active_ruleset_version", "8.8.8")

    with (
        patch.object(
            service.resolver,
            "_resolve_profile",
            return_value=MagicMock(
                current_timezone="UTC",
                birth_timezone="UTC",
                current_lat=48.85,
                current_lon=2.35,
            ),
        ),
        patch.object(
            service.resolver,
            "_resolve_reference_version_id",
            return_value=101,
        ) as resolve_ref,
        patch.object(service.resolver, "_resolve_ruleset_id", return_value=202) as resolve_ruleset,
        patch("app.services.prediction_run_reuse_policy.DailyPredictionRepository") as daily_repo,
    ):
        daily_repo.return_value.get_run.return_value = None

        result = service.get_or_compute(
            user_id=1,
            db=mock_db,
            mode=ComputeMode.read_only,
        )

    assert result is None
    resolve_ref.assert_called_once_with(mock_db, "9.9.9")
    resolve_ruleset.assert_called_once_with(mock_db, "8.8.8", 101)


def test_resolve_ruleset_id_consistency_check_fails(service, mock_db):
    # Setup: Ruleset 2.0.0 is linked to reference version 1 (not 2)
    mock_ruleset = RulesetData(
        id=10,
        version="2.0.0",
        reference_version_id=1,  # Inconsistent with expected 2
        zodiac_type="tropical",
        coordinate_mode="geocentric",
        house_system="placidus",
        time_step_minutes=30,
        is_locked=True,
    )

    with patch("app.services.prediction_request_resolver.PredictionRulesetRepository") as MockRepo:
        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.get_ruleset.return_value = mock_ruleset

        with pytest.raises(DailyPredictionServiceError) as excinfo:
            service.resolver._resolve_ruleset_id(
                mock_db,
                "2.0.0",
                expected_reference_version_id=2,
            )

        assert excinfo.value.code == "ruleset_inconsistent"
        assert "rattaché à la référence ID 1" in excinfo.value.message
        assert "référence active demandée est ID 2" in excinfo.value.message


def test_resolve_ruleset_id_consistency_check_passes(service, mock_db):
    # Setup: Ruleset 2.0.0 is correctly linked to reference version 2
    mock_ruleset = RulesetData(
        id=10,
        version="2.0.0",
        reference_version_id=2,
        zodiac_type="tropical",
        coordinate_mode="geocentric",
        house_system="placidus",
        time_step_minutes=30,
        is_locked=True,
    )

    with patch("app.services.prediction_request_resolver.PredictionRulesetRepository") as MockRepo:
        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.get_ruleset.return_value = mock_ruleset

        ruleset_id = service.resolver._resolve_ruleset_id(
            mock_db,
            "2.0.0",
            expected_reference_version_id=2,
        )

        assert ruleset_id == 10


def test_resolve_ruleset_id_without_expected_ref_passes(service, mock_db):
    # Setup: No expected reference ID provided (legacy behavior)
    mock_ruleset = RulesetData(
        id=10,
        version="2.0.0",
        reference_version_id=1,
        zodiac_type="tropical",
        coordinate_mode="geocentric",
        house_system="placidus",
        time_step_minutes=30,
        is_locked=True,
    )

    with patch("app.services.prediction_request_resolver.PredictionRulesetRepository") as MockRepo:
        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.get_ruleset.return_value = mock_ruleset

        ruleset_id = service.resolver._resolve_ruleset_id(mock_db, "2.0.0")

        assert ruleset_id == 10
