from __future__ import annotations

from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.prediction.exceptions import PredictionContextError
from app.prediction.persisted_relative_score import PersistedRelativeScore
from app.prediction.persisted_snapshot import PersistedPredictionSnapshot
from app.services.daily_prediction_service import (
    DailyPredictionService,
    ServiceResult,
)
from app.services.daily_prediction_types import (
    ComputeMode,
    DailyPredictionServiceError,
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


def _build_mock_snapshot(
    run_id: int = 1,
    user_id: int = 1,
    local_date_val: date = date(2026, 3, 7),
    input_hash: str = "hash123",
) -> PersistedPredictionSnapshot:
    return PersistedPredictionSnapshot(
        run_id=run_id,
        user_id=user_id,
        local_date=local_date_val,
        timezone="Europe/Paris",
        computed_at=datetime(2026, 3, 7, 10, 0),
        input_hash=input_hash,
        reference_version_id=10,
        ruleset_id=20,
        house_system_effective="placidus",
        is_provisional_calibration=False,
        calibration_label=None,
        overall_summary="Summary",
        overall_tone="neutral",
        category_scores=[],
        turning_points=[],
        time_blocks=[],
    )


def test_user_without_natal(service, db):
    res_path = "app.services.prediction_request_resolver"
    with (
        patch(f"{res_path}.UserBirthProfileRepository") as mock_profile_repo,
        patch(f"{res_path}.ChartResultRepository") as mock_chart_repo,
        patch(f"{res_path}.PredictionRulesetRepository") as mock_ruleset_repo,
    ):
        mock_prof = MagicMock()
        mock_prof.current_timezone = "Europe/Paris"
        mock_prof.birth_timezone = "Europe/Paris"
        mock_prof.current_lat = 48.8
        mock_prof.current_lon = 2.3

        mock_profile_repo.return_value.get_by_user_id.return_value = mock_prof
        mock_chart_repo.return_value.get_latest_by_user_id.return_value = None

        def scalar_side_effect(stmt, *args, **kwargs):
            return 10

        db.scalar.side_effect = scalar_side_effect

        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )

        with pytest.raises(DailyPredictionServiceError) as excinfo:
            service.get_or_compute(user_id=1, db=db)
        assert excinfo.value.code == "natal_missing"


def test_user_missing_profile(service, db):
    res_path = "app.services.prediction_request_resolver"
    with patch(f"{res_path}.UserBirthProfileRepository") as mock_profile_repo:
        mock_profile_repo.return_value.get_by_user_id.return_value = None

        with pytest.raises(DailyPredictionServiceError) as excinfo:
            service.get_or_compute(user_id=1, db=db)
        assert excinfo.value.code == "profile_missing"


def test_timezone_missing_raises(service, db):
    res_path = "app.services.prediction_request_resolver"
    with patch(f"{res_path}.UserBirthProfileRepository") as mock_profile_repo:
        mock_prof = MagicMock()
        mock_prof.current_timezone = None
        mock_prof.birth_timezone = None
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_prof

        with pytest.raises(DailyPredictionServiceError) as excinfo:
            service.get_or_compute(user_id=1, db=db)
        assert excinfo.value.code == "timezone_missing"


def test_location_missing_raises(service, db):
    res_path = "app.services.prediction_request_resolver"
    with (
        patch(f"{res_path}.UserBirthProfileRepository") as mock_profile_repo,
        patch(f"{res_path}.UserBirthProfileService.resolve_coordinates") as mock_resolve,
    ):
        mock_prof = MagicMock()
        mock_prof.current_timezone = "Europe/Paris"
        mock_prof.current_lat = None
        mock_prof.current_lon = None
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_prof
        mock_resolve.return_value = MagicMock(birth_lat=None, birth_lon=None)

        with pytest.raises(DailyPredictionServiceError) as excinfo:
            service.get_or_compute(user_id=1, db=db)
        assert excinfo.value.code == "location_missing"


def test_birth_coordinates_fallback_when_current_location_missing(service, db):
    res_path = "app.services.prediction_request_resolver"
    reuse_path = "app.services.prediction_run_reuse_policy"
    comp_path = "app.services.prediction_compute_runner"

    with (
        patch(f"{res_path}.UserBirthProfileRepository") as mock_profile_repo,
        patch(f"{res_path}.UserBirthProfileService.resolve_coordinates") as mock_resolve,
        patch(f"{res_path}.ChartResultRepository") as mock_chart_repo,
        patch(f"{reuse_path}.DailyPredictionRepository") as mock_daily_repo,
        patch(f"{res_path}.PredictionRulesetRepository") as mock_ruleset_repo,
        patch(f"{comp_path}.EngineOrchestrator") as mock_orchestrator,
    ):
        mock_prof = MagicMock()
        mock_prof.user_id = 1
        mock_prof.current_timezone = "Europe/Paris"
        mock_prof.current_lat = None
        mock_prof.current_lon = None
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_prof

        mock_resolve.return_value = MagicMock(birth_lat=48.8566, birth_lon=2.3522)
        mock_chart_repo.return_value.get_latest_by_user_id.return_value = MagicMock(
            result_payload={"planets": []}
        )
        mock_daily_repo.return_value.get_run_for_reuse.return_value = None

        def scalar_side_effect(stmt, *args, **kwargs):
            return 10

        db.scalar.side_effect = scalar_side_effect

        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )

        mock_bundle = MagicMock()
        mock_bundle.core.turning_points = []
        mock_orchestrator.return_value.run.return_value = mock_bundle

        mock_snapshot = _build_mock_snapshot()
        service.persistence_service.save.return_value = MagicMock(
            run=mock_snapshot, was_reused=False
        )

        result = service.get_or_compute(user_id=1, db=db)

        assert isinstance(result, ServiceResult)
        assert result.run == mock_snapshot
        mock_resolve.assert_called_once_with(db, mock_prof)


def test_ruleset_auto_seed_in_local_dev(service, db):
    repair_path = "app.services.prediction_context_repair_service"

    with (
        patch(f"{repair_path}.settings") as mock_settings,
        patch(
            "app.services.prediction_context_repair_service.PredictionContextRepairService.try_repair",
            return_value=True,
        ),
    ):
        mock_settings.app_env = "development"
        mock_settings.active_ruleset_version = "2.0.0"

        ruleset_repo = MagicMock()
        ruleset_repo.get_ruleset.side_effect = [
            None,
            MagicMock(id=20, reference_version_id=10, version="2.0.0"),
        ]

        with patch(
            "app.services.prediction_request_resolver.PredictionRulesetRepository",
            return_value=ruleset_repo,
        ):
            ruleset_id = service.resolver._resolve_ruleset_id(
                db, "2.0.0", expected_reference_version_id=10
            )
            assert ruleset_id == 20


def test_reference_version_auto_seed_in_local_dev(service, db):
    repair_path = "app.services.prediction_context_repair_service"

    with (
        patch(f"{repair_path}.settings") as mock_settings,
        patch(
            "app.services.prediction_context_repair_service.PredictionContextRepairService.try_repair",
            return_value=True,
        ),
    ):
        mock_settings.app_env = "development"
        mock_settings.active_reference_version = "2.0.0"

        def scalar_side_effect(stmt, *args, **kwargs):
            # Simulation: first call returns None, second returns 10
            if not hasattr(scalar_side_effect, "called"):
                scalar_side_effect.called = True
                return None
            return 10

        db.scalar.side_effect = scalar_side_effect

        reference_version_id = service.resolver._resolve_reference_version_id(db, "2.0.0")
        assert reference_version_id == 10


def test_ruleset_auto_seed_repairs_locked_incomplete_reference(service, db):
    # This test checks the repair service logic
    from app.services.prediction_context_repair_service import PredictionContextRepairService
    from scripts.seed_31_prediction_reference_v2 import SeedAbortError

    repair_service = PredictionContextRepairService()

    locked_version = MagicMock(id=10, version="2.0.0", is_locked=True)
    seed_error = (
        "ERROR: 2.0.0 exists and is LOCKED but is incomplete. Manual investigation required."
    )

    with (
        patch("app.services.prediction_context_repair_service.settings") as mock_settings,
        patch("scripts.seed_31_prediction_reference_v2.run_seed") as mock_run_seed,
        patch("app.services.reference_data_service.ReferenceDataService.seed_reference_version"),
    ):
        mock_settings.app_env = "development"
        mock_settings.active_ruleset_version = "2.0.0"
        mock_settings.active_reference_version = "2.0.0"

        db.get.return_value = locked_version
        # Raise real SeedAbortError
        mock_run_seed.side_effect = [SeedAbortError(seed_error), None]

        # Use a dynamic mock for db.scalar to find the version model
        db.scalar.return_value = locked_version

        success = repair_service.try_repair(db, reference_version="2.0.0", ruleset_version="2.0.0")

        assert success is True
        assert locked_version.is_locked is False
        assert mock_run_seed.call_count == 2
        db.rollback.assert_called_once()
        assert db.commit.call_count >= 1


def test_ruleset_seed_abort_is_wrapped_as_service_error(service, db):
    # Testing that resolver raises ruleset_missing if repair fails
    with patch.object(service.repair_service, "try_repair", return_value=False):
        ruleset_repo = MagicMock()
        ruleset_repo.get_ruleset.return_value = None

        with patch(
            "app.services.prediction_request_resolver.PredictionRulesetRepository",
            return_value=ruleset_repo,
        ):
            with pytest.raises(DailyPredictionServiceError) as excinfo:
                service.resolver._resolve_ruleset_id(db, "2.0.0")
            assert excinfo.value.code == "ruleset_missing"


def test_incomplete_prediction_context_is_auto_repaired_in_local_dev(service, db):
    from app.services.prediction_compute_runner import ComputeResult

    res_path = "app.services.prediction_request_resolver"
    reuse_path = "app.services.prediction_run_reuse_policy"

    with (
        patch(f"{res_path}.UserBirthProfileRepository") as mock_profile_repo,
        patch(f"{res_path}.ChartResultRepository") as mock_chart_repo,
        patch(f"{reuse_path}.DailyPredictionRepository") as mock_daily_repo,
        patch(f"{res_path}.PredictionRulesetRepository") as mock_ruleset_repo,
        patch.object(service.compute_runner, "run_with_timeout") as mock_compute,
        patch.object(service.repair_service, "try_repair", return_value=True) as mock_repair,
    ):
        mock_prof = MagicMock()
        mock_prof.user_id = 1
        mock_prof.current_timezone = "Europe/Paris"
        mock_prof.current_lat = 48.8
        mock_prof.current_lon = 2.3
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_prof

        mock_chart_repo.return_value.get_latest_by_user_id.return_value = MagicMock(
            result_payload={"planets": []}
        )
        mock_daily_repo.return_value.get_run_for_reuse.return_value = None

        def scalar_side_effect(stmt, *args, **kwargs):
            return 10

        db.scalar.side_effect = scalar_side_effect

        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )

        mock_bundle = MagicMock()
        mock_bundle.core.turning_points = []
        mock_output = ComputeResult(bundle=mock_bundle)

        mock_compute.side_effect = [
            PredictionContextError("Prediction context has no planet profiles"),
            mock_output,
        ]

        mock_snapshot = _build_mock_snapshot()
        service.persistence_service.save.return_value = MagicMock(
            run=mock_snapshot, was_reused=False
        )

        result = service.get_or_compute(user_id=1, db=db)

        assert result.run == mock_snapshot
        assert mock_compute.call_count == 2
        mock_repair.assert_called_once()


def test_user_with_natal_full_compute(service, db):
    res_path = "app.services.prediction_request_resolver"
    reuse_path = "app.services.prediction_run_reuse_policy"
    comp_path = "app.services.prediction_compute_runner"

    with (
        patch(f"{res_path}.UserBirthProfileRepository") as mock_profile_repo,
        patch(f"{res_path}.ChartResultRepository") as mock_chart_repo,
        patch(f"{reuse_path}.DailyPredictionRepository") as mock_daily_repo,
        patch(f"{res_path}.PredictionRulesetRepository") as mock_ruleset_repo,
        patch(f"{comp_path}.EngineOrchestrator") as mock_orchestrator,
    ):
        mock_prof = MagicMock()
        mock_prof.user_id = 1
        mock_prof.current_timezone = "Europe/Paris"
        mock_prof.current_lat = 48.8
        mock_prof.current_lon = 2.3
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_prof

        mock_chart_repo.return_value.get_latest_by_user_id.return_value = MagicMock(
            result_payload={"planets": []}
        )
        mock_daily_repo.return_value.get_run_for_reuse.return_value = None

        def scalar_side_effect(stmt, *args, **kwargs):
            return 10

        db.scalar.side_effect = scalar_side_effect

        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )

        mock_bundle = MagicMock()
        mock_bundle.core.turning_points = []
        mock_orchestrator.return_value.run.return_value = mock_bundle

        mock_snapshot = _build_mock_snapshot()
        service.persistence_service.save.return_value = MagicMock(
            run=mock_snapshot, was_reused=False
        )

        result = service.get_or_compute(user_id=1, db=db)

        assert result.run == mock_snapshot
        assert result.was_reused is False
        mock_orchestrator.return_value.run.assert_called_once()


def test_identical_hash_not_recomputed(service, db):
    res_path = "app.services.prediction_request_resolver"
    reuse_path = "app.services.prediction_run_reuse_policy"

    with (
        patch(f"{res_path}.UserBirthProfileRepository") as mock_profile_repo,
        patch(f"{res_path}.ChartResultRepository") as mock_chart_repo,
        patch(f"{reuse_path}.DailyPredictionRepository") as mock_daily_repo,
        patch(f"{res_path}.PredictionRulesetRepository") as mock_ruleset_repo,
    ):
        mock_prof = MagicMock()
        mock_prof.user_id = 1
        mock_prof.current_timezone = "Europe/Paris"
        mock_prof.current_lat = 48.8
        mock_prof.current_lon = 2.3
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_prof

        mock_chart_repo.return_value.get_latest_by_user_id.return_value = MagicMock(
            result_payload={"planets": []}
        )

        mock_snapshot = _build_mock_snapshot()
        mock_daily_repo.return_value.get_run_for_reuse.return_value = mock_snapshot

        def scalar_side_effect(stmt, *args, **kwargs):
            return 10

        db.scalar.side_effect = scalar_side_effect

        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )

        result = service.get_or_compute(user_id=1, db=db, mode=ComputeMode.compute_if_missing)

        assert result.run == mock_snapshot
        assert result.was_reused is True
        assert result.bundle is None


def test_read_only_existing(service, db):
    res_path = "app.services.prediction_request_resolver"

    with (
        patch(f"{res_path}.UserBirthProfileRepository") as mock_profile_repo,
        patch(
            "app.infra.db.repositories.daily_prediction_repository.DailyPredictionRepository.get_run"
        ) as mock_get_run,
        patch(
            "app.infra.db.repositories.daily_prediction_repository.DailyPredictionRepository.get_snapshot"
        ) as mock_get_snap,
        patch(f"{res_path}.PredictionRulesetRepository") as mock_ruleset_repo,
    ):
        mock_prof = MagicMock()
        mock_prof.user_id = 1
        mock_prof.current_timezone = "Europe/Paris"
        mock_prof.current_lat = 48.8
        mock_prof.current_lon = 2.3
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_prof

        mock_run_model = MagicMock()
        mock_get_run.return_value = mock_run_model

        mock_snapshot = _build_mock_snapshot()
        mock_get_snap.return_value = mock_snapshot

        def scalar_side_effect(stmt, *args, **kwargs):
            return 10

        db.scalar.side_effect = scalar_side_effect

        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )

        result = service.get_or_compute(user_id=1, db=db, mode=ComputeMode.read_only)

        assert result.run == mock_snapshot
        assert result.was_reused is True
        assert result.bundle is None


def test_relative_enrichment_preserves_absolute_snapshot_fields(service, db):
    res_path = "app.services.prediction_request_resolver"
    reuse_path = "app.services.prediction_run_reuse_policy"

    with (
        patch(f"{res_path}.UserBirthProfileRepository") as mock_profile_repo,
        patch(f"{res_path}.ChartResultRepository") as mock_chart_repo,
        patch(f"{reuse_path}.DailyPredictionRepository") as mock_daily_repo,
        patch(f"{res_path}.PredictionRulesetRepository") as mock_ruleset_repo,
        patch.object(service.relative_scoring_service, "enrich_snapshot") as mock_enrich,
        patch.object(service.compute_runner, "run_with_timeout") as mock_compute,
    ):
        mock_prof = MagicMock()
        mock_prof.user_id = 1
        mock_prof.current_timezone = "Europe/Paris"
        mock_prof.current_lat = 48.8
        mock_prof.current_lon = 2.3
        mock_profile_repo.return_value.get_by_user_id.return_value = mock_prof

        mock_chart_repo.return_value.get_latest_by_user_id.return_value = MagicMock(
            result_payload={"planets": []}
        )
        mock_daily_repo.return_value.get_run_for_reuse.return_value = None
        db.scalar.side_effect = lambda stmt, *args, **kwargs: 10

        mock_ruleset_repo.return_value.get_ruleset.return_value = MagicMock(
            id=20, reference_version_id=10
        )

        absolute_snapshot = _build_mock_snapshot()
        enriched_snapshot = PersistedPredictionSnapshot(
            **{
                **absolute_snapshot.__dict__,
                "relative_scores": {
                    "love": PersistedRelativeScore(
                        category_code="love",
                        relative_z_score=1.2,
                        relative_percentile=0.85,
                        relative_rank=1,
                        is_available=True,
                        fallback_reason=None,
                    )
                },
            }
        )
        service.persistence_service.save.return_value = MagicMock(
            run=absolute_snapshot, was_reused=False
        )
        mock_enrich.return_value = enriched_snapshot
        mock_compute.return_value = MagicMock(bundle=MagicMock())

        result = service.get_or_compute(user_id=1, db=db)

        assert result.run.category_scores == absolute_snapshot.category_scores
        assert result.run.overall_summary == absolute_snapshot.overall_summary
        assert result.run.overall_tone == absolute_snapshot.overall_tone
        assert result.run.relative_scores["love"].relative_rank == 1
        mock_enrich.assert_called_once_with(db, absolute_snapshot)
