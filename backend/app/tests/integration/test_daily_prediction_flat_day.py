from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import require_authenticated_user
from app.infra.db.session import get_db_session
from app.main import app
from app.prediction.persisted_relative_score import PersistedRelativeScore
from app.prediction.persisted_snapshot import (
    PersistedCategoryScore,
    PersistedPredictionSnapshot,
)

client = TestClient(app)


@pytest.fixture
def mock_snapshot_flat():
    return PersistedPredictionSnapshot(
        run_id=1,
        user_id=42,
        local_date=date(2026, 3, 10),
        timezone="UTC",
        computed_at=datetime.now(),
        input_hash="hash",
        reference_version_id=1,
        ruleset_id=1,
        house_system_effective="placidus",
        is_provisional_calibration=False,
        calibration_label="v1",
        overall_summary="Calme",
        overall_tone="neutral",
        category_scores=[
            PersistedCategoryScore(1, "love", 10, 0.0, 0.0, 0.0, 1, False, None),
            PersistedCategoryScore(2, "work", 10, 0.0, 0.0, 0.0, 2, False, None),
        ],
        turning_points=[],
        time_blocks=[
            MagicMock(
                start_at_local=datetime.now(),
                end_at_local=datetime.now(),
                tone_code="neutral",
                dominant_categories=[],
            )
        ],
        relative_scores={
            "love": PersistedRelativeScore("love", 1.5, 0.8, 1, True),
            "work": PersistedRelativeScore("work", -0.8, 0.2, 2, True),
        },
    )


@pytest.fixture
def mock_snapshot_active():
    return PersistedPredictionSnapshot(
        run_id=2,
        user_id=42,
        local_date=date(2026, 3, 11),
        timezone="UTC",
        computed_at=datetime.now(),
        input_hash="hash2",
        reference_version_id=1,
        ruleset_id=1,
        house_system_effective="placidus",
        is_provisional_calibration=False,
        calibration_label="v1",
        overall_summary="Actif",
        overall_tone="positive",
        category_scores=[
            PersistedCategoryScore(1, "love", 15, 1.0, 1.0, 1.0, 1, False, None),
        ],
        turning_points=[],
        time_blocks=[],
        relative_scores={
            "love": PersistedRelativeScore("love", 2.0, 0.9, 1, True),
        },
    )


def test_flat_day_projection(mock_snapshot_flat):
    # Dependency override for auth
    app.dependency_overrides[require_authenticated_user] = lambda: MagicMock(id=42)
    db = MagicMock()
    db.get.return_value = MagicMock(version="2.0.0")
    app.dependency_overrides[get_db_session] = lambda: db

    with patch("app.api.v1.routers.predictions.DailyPredictionService.get_or_compute") as mock_get:
        mock_res = MagicMock()
        mock_res.run.run_id = 1
        mock_res.bundle = None
        mock_res.was_reused = True
        mock_get.return_value = mock_res

        with patch(
            "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
        ) as mock_repo:
            mock_repo.return_value = mock_snapshot_flat

            with patch(
                "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"
            ) as mock_ref:
                # Mock return objects with id and code attributes
                cat1 = MagicMock(id=1, code="love")
                cat2 = MagicMock(id=2, code="work")
                mock_ref.return_value = [cat1, cat2]

                response = client.get("/v1/predictions/daily")
                assert response.status_code == 200
                data = response.json()

            assert data["summary"]["flat_day"] is True
            assert data["summary"]["relative_summary"] is not None
            assert "amour" in data["summary"]["relative_summary"].lower()

            assert data["micro_trends"] is not None
            assert len(data["micro_trends"]) == 2

            assert data["decision_windows"] is None
            assert data["turning_points"] == []

    app.dependency_overrides.clear()


def test_active_day_no_micro_trends(mock_snapshot_active):
    app.dependency_overrides[require_authenticated_user] = lambda: MagicMock(id=42)
    db = MagicMock()
    db.get.return_value = MagicMock(version="2.0.0")
    app.dependency_overrides[get_db_session] = lambda: db

    with patch("app.api.v1.routers.predictions.DailyPredictionService.get_or_compute") as mock_get:
        mock_res = MagicMock()
        mock_res.run.run_id = 2
        mock_res.bundle = None
        mock_res.was_reused = True
        mock_get.return_value = mock_res

        engine_output = MagicMock()
        engine_output.core.decision_windows = [
            MagicMock(
                start_local=datetime(2026, 3, 11, 9, 0),
                end_local=datetime(2026, 3, 11, 11, 0),
                window_type="favorable",
                score=1.0,
                confidence=1.0,
                dominant_categories=["love"],
            )
        ]
        engine_output.editorial = None
        mock_res.bundle = engine_output

        with (
            patch(
                "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
            ) as mock_repo,
            patch(
                "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"
            ) as mock_ref,
        ):
            mock_repo.return_value = mock_snapshot_active
            mock_ref.return_value = [MagicMock(id=1, code="love")]

            response = client.get("/v1/predictions/daily")
            assert response.status_code == 200
            data = response.json()

            assert data["summary"]["flat_day"] is False
            assert data["summary"]["relative_summary"] is None
            assert data["summary"]["best_window"] is not None
            assert data["micro_trends"] is None
            assert data["decision_windows"] is not None

    app.dependency_overrides.clear()


def test_flat_day_projection_supports_percentile_only_micro_trends(mock_snapshot_flat):
    app.dependency_overrides[require_authenticated_user] = lambda: MagicMock(id=42)
    db = MagicMock()
    db.get.return_value = MagicMock(version="2.0.0")
    app.dependency_overrides[get_db_session] = lambda: db

    percentile_only_snapshot = PersistedPredictionSnapshot(
        **{
            **mock_snapshot_flat.__dict__,
            "relative_scores": {
                "love": PersistedRelativeScore("love", None, 0.82, 1, True, "variance_null"),
                "work": PersistedRelativeScore("work", None, 0.25, 2, True, "variance_null"),
            },
        }
    )

    with (
        patch("app.api.v1.routers.predictions.DailyPredictionService.get_or_compute") as mock_get,
        patch("app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run") as mock_repo,
        patch(
            "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"
        ) as mock_ref,
    ):
        mock_res = MagicMock()
        mock_res.run.run_id = 1
        mock_res.bundle = None
        mock_res.was_reused = True
        mock_get.return_value = mock_res
        mock_repo.return_value = percentile_only_snapshot
        mock_ref.return_value = [MagicMock(id=1, code="love"), MagicMock(id=2, code="work")]

        response = client.get("/v1/predictions/daily")
        assert response.status_code == 200
        data = response.json()

        assert data["summary"]["flat_day"] is True
        assert data["micro_trends"] is not None
        assert data["micro_trends"][0]["z_score"] is None
        assert data["micro_trends"][0]["percentile"] == 0.82

    app.dependency_overrides.clear()


def test_flat_day_summary_stays_consistent_with_micro_trends(mock_snapshot_flat):
    app.dependency_overrides[require_authenticated_user] = lambda: MagicMock(id=42)
    db = MagicMock()
    db.get.return_value = MagicMock(version="2.0.0")
    app.dependency_overrides[get_db_session] = lambda: db

    with (
        patch("app.api.v1.routers.predictions.DailyPredictionService.get_or_compute") as mock_get,
        patch("app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run") as mock_repo,
        patch(
            "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"
        ) as mock_ref,
    ):
        mock_res = MagicMock()
        mock_res.run.run_id = 1
        mock_res.bundle = None
        mock_res.was_reused = True
        mock_get.return_value = mock_res
        mock_repo.return_value = mock_snapshot_flat
        mock_ref.return_value = [MagicMock(id=1, code="love"), MagicMock(id=2, code="work")]

        response = client.get("/v1/predictions/daily")
        assert response.status_code == 200
        data = response.json()

        assert data["summary"]["relative_top_categories"] == [
            trend["category_code"] for trend in data["micro_trends"]
        ]
        assert "avantage relatif" in data["summary"]["relative_summary"].lower()
        assert "retenue" in data["summary"]["relative_summary"].lower()

    app.dependency_overrides.clear()
