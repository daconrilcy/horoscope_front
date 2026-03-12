from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.api.v1.routers.predictions import get_daily_prediction_service
from app.core.config import settings
from app.infra.db.base import Base
from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.models.user import UserModel
from app.infra.db.models.user_refresh_token import UserRefreshTokenModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.prediction.persisted_snapshot import (
    PersistedCategoryScore,
    PersistedPredictionSnapshot,
    PersistedTimeBlock,
    PersistedTurningPoint,
)
from app.services.auth_service import AuthService
from app.services.daily_prediction_service import (
    ComputeMode,
    DailyPredictionServiceError,
    ServiceResult,
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_tables():
    Base.metadata.create_all(bind=engine, checkfirst=True)
    app.dependency_overrides.clear()
    with SessionLocal() as db:
        db.execute(delete(UserRefreshTokenModel))
        db.execute(delete(UserModel))
        db.execute(delete(ReferenceVersionModel))
        db.commit()
    yield
    app.dependency_overrides.clear()


def _register_and_get_access_token() -> str:
    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email=f"daily-api-user-{uuid.uuid4()}@example.com",
            password="strong-pass-123",
            role="user",
        )
        db.commit()
        return auth.tokens.access_token


def _register_admin_and_get_token() -> str:
    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email=f"admin-{uuid.uuid4()}@example.com",
            password="admin-pass-123",
            role="admin",
        )
        db.commit()
        return auth.tokens.access_token


def _override_service(service: MagicMock) -> None:
    app.dependency_overrides[get_daily_prediction_service] = lambda: service


def _build_mock_snapshot(
    *,
    run_id: int = 1,
    local_date_value: date = date(2026, 3, 8),
    timezone_str: str = "Europe/Paris",
    computed_at: datetime = datetime(2026, 3, 8, 10, 0),
    reference_version_id: int = 1,
) -> PersistedPredictionSnapshot:
    return PersistedPredictionSnapshot(
        run_id=run_id,
        user_id=1,
        local_date=local_date_value,
        timezone=timezone_str,
        computed_at=computed_at,
        input_hash="hash123",
        reference_version_id=reference_version_id,
        ruleset_id=1,
        house_system_effective="placidus",
        is_provisional_calibration=False,
        calibration_label=None,
        overall_summary="Summary",
        overall_tone="neutral",
        category_scores=[],
        turning_points=[],
        time_blocks=[],
    )


def test_daily_prediction_requires_auth():
    response = client.get("/v1/predictions/daily")
    assert response.status_code == 401


def test_daily_prediction_nominal_200():
    token = _register_and_get_access_token()
    snapshot = _build_mock_snapshot()
    snapshot = PersistedPredictionSnapshot(
        **{
            **snapshot.__dict__,
            "calibration_label": "v1",
            "overall_tone": "positive",
            "category_scores": [
                PersistedCategoryScore(
                    category_id=1,
                    category_code="love",
                    note_20=15,
                    raw_score=0.5,
                    power=0.7,
                    volatility=0.1,
                    rank=1,
                    is_provisional=False,
                    summary="Love summary",
                )
            ],
        }
    )
    mock_result = ServiceResult(run=snapshot, bundle=None, was_reused=True)

    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    mock_categories = [MagicMock(id=1, code="love")]
    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"

    with (
        patch(repo_path, return_value=snapshot),
        patch(ref_path, return_value=mock_categories),
    ):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["was_reused"] is True
    assert data["meta"]["calibration_label"] == "v1"
    assert data["summary"]["overall_tone"] == "positive"
    assert data["categories"][0]["code"] == "love"


def test_daily_prediction_404_no_natal():
    token = _register_and_get_access_token()
    mock_service = MagicMock()
    mock_service.get_or_compute.side_effect = DailyPredictionServiceError(
        code="natal_missing",
        message="Natal missing",
    )
    _override_service(mock_service)

    response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "natal_missing"


def test_daily_prediction_categories_sorted_by_rank():
    token = _register_and_get_access_token()
    snapshot = _build_mock_snapshot()
    snapshot = PersistedPredictionSnapshot(
        **{
            **snapshot.__dict__,
            "category_scores": [
                PersistedCategoryScore(1, "cat1", 10, 0.3, 0.4, 0.5, 2, False, "S2"),
                PersistedCategoryScore(2, "cat2", 15, 0.5, 0.7, 0.1, 1, False, "S1"),
            ],
        }
    )
    mock_result = ServiceResult(run=snapshot, bundle=None, was_reused=True)

    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    mock_categories = [MagicMock(id=1, code="cat1"), MagicMock(id=2, code="cat2")]

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"

    with (
        patch(repo_path, return_value=snapshot),
        patch(ref_path, return_value=mock_categories),
    ):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    categories = response.json()["categories"]
    # Check that assembler sorted them (snapshot was unsorted)
    assert categories[0]["rank"] == 1
    assert categories[1]["rank"] == 2


def test_daily_prediction_timeline_chronological():
    token = _register_and_get_access_token()
    snapshot = _build_mock_snapshot()
    snapshot = PersistedPredictionSnapshot(
        **{
            **snapshot.__dict__,
            "turning_points": [
                PersistedTurningPoint(
                    occurred_at_local=datetime.fromisoformat("2026-03-08T06:15:00+01:00"),
                    severity=0.8,
                    summary="Pivot",
                    drivers=[{"event_type": "aspect"}],
                )
            ],
            "time_blocks": [
                PersistedTimeBlock(
                    0,
                    datetime.fromisoformat("2026-03-08T06:00:00+01:00"),
                    datetime.fromisoformat("2026-03-08T07:00:00+01:00"),
                    "neutral",
                    [],
                    "S1",
                ),
                PersistedTimeBlock(
                    1,
                    datetime.fromisoformat("2026-03-08T07:00:00+01:00"),
                    datetime.fromisoformat("2026-03-08T08:00:00+01:00"),
                    "neutral",
                    [],
                    "S2",
                ),
            ],
        }
    )
    mock_result = ServiceResult(run=snapshot, bundle=None, was_reused=True)

    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"

    with patch(repo_path, return_value=snapshot), patch(ref_path, return_value=[]):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    timeline = response.json()["timeline"]
    assert timeline[0]["turning_point"] is True
    assert timeline[1]["turning_point"] is False


def test_daily_prediction_date_param():
    token = _register_and_get_access_token()

    target_date = date(2026, 3, 10)
    snapshot = _build_mock_snapshot(local_date_value=target_date)
    mock_result = ServiceResult(run=snapshot, bundle=None, was_reused=True)

    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"

    with patch(repo_path, return_value=snapshot), patch(ref_path, return_value=[]):
        response = client.get(
            "/v1/predictions/daily",
            params={"date": "2026-03-10"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert response.json()["meta"]["date_local"] == "2026-03-10"


def test_daily_prediction_returns_500_on_malformed_json_payload():
    token = _register_and_get_access_token()
    snapshot = _build_mock_snapshot()
    mock_result = ServiceResult(run=snapshot, bundle=None, was_reused=True)

    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    # Assembler raises ValueError on malformed data
    with (
        patch(repo_path, return_value=snapshot),
        patch(
            "app.api.v1.routers.predictions.PublicPredictionAssembler.assemble",
            side_effect=ValueError("Broken"),
        ),
    ):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 500
    assert response.json()["detail"]["code"] == "prediction_payload_invalid"


def test_daily_prediction_meta_uses_run_reference_version_and_house_system_effective():
    token = _register_and_get_access_token()
    with SessionLocal() as db:
        db.add(
            ReferenceVersionModel(
                id=7,
                version=settings.active_reference_version,
                description="Active",
                is_locked=True,
            )
        )
        db.commit()

    snapshot = _build_mock_snapshot(reference_version_id=7)
    snapshot = PersistedPredictionSnapshot(
        **{**snapshot.__dict__, "house_system_effective": "placidus"}
    )
    mock_result = ServiceResult(run=snapshot, bundle=None, was_reused=True)

    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"

    with patch(repo_path, return_value=snapshot), patch(ref_path, return_value=[]):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    meta = response.json()["meta"]
    assert meta["reference_version"] == settings.active_reference_version
    assert meta["house_system_effective"] == "placidus"


def test_daily_prediction_meta_falls_back_to_engine_output_house_system_effective():
    token = _register_and_get_access_token()
    snapshot = _build_mock_snapshot(reference_version_id=1)
    snapshot = PersistedPredictionSnapshot(**{**snapshot.__dict__, "house_system_effective": None})

    mock_bundle = MagicMock()
    mock_bundle.core.effective_context.house_system_effective = "placidus"
    mock_result = ServiceResult(run=snapshot, bundle=mock_bundle, was_reused=False)

    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"

    with patch(repo_path, return_value=snapshot), patch(ref_path, return_value=[]):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["meta"]["house_system_effective"] == "placidus"


def test_debug_200_admin_nominal():
    token = _register_admin_and_get_token()

    snapshot = _build_mock_snapshot()
    snapshot = PersistedPredictionSnapshot(
        **{
            **snapshot.__dict__,
            "input_hash": "debug_hash",
            "is_provisional_calibration": True,
            "calibration_label": "mixed",
            "category_scores": [
                PersistedCategoryScore(
                    1, "love", 15, 0.5, 0.7, 0.1, 1, True, "S1", [{"source": "transit"}]
                )
            ],
            "turning_points": [
                PersistedTurningPoint(
                    datetime.fromisoformat("2026-03-08T10:00:00+01:00"),
                    0.9,
                    "Big change",
                    [{"event": "Aspect"}],
                )
            ],
        }
    )

    mock_result = ServiceResult(run=snapshot, bundle=None, was_reused=True)

    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    with patch(repo_path, return_value=snapshot):
        response = client.get(
            "/v1/predictions/daily/debug",
            params={"target_user_id": 42},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["input_hash"] == "debug_hash"
    assert data["categories"][0]["contributors"][0]["source"] == "transit"


def test_debug_no_recompute():
    token = _register_admin_and_get_token()
    snapshot = _build_mock_snapshot()
    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = ServiceResult(
        run=snapshot, bundle=None, was_reused=True
    )
    _override_service(mock_service)

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    with patch(repo_path, return_value=snapshot):
        client.get(
            "/v1/predictions/daily/debug",
            params={"target_user_id": 42},
            headers={"Authorization": f"Bearer {token}"},
        )

    mock_service.get_or_compute.assert_called_once()
    assert mock_service.get_or_compute.call_args.kwargs["mode"] == ComputeMode.read_only


def test_daily_prediction_timeline_summary_non_null():
    token = _register_and_get_access_token()
    snapshot = _build_mock_snapshot()
    snapshot = PersistedPredictionSnapshot(
        **{
            **snapshot.__dict__,
            "time_blocks": [
                PersistedTimeBlock(
                    0,
                    datetime.fromisoformat("2026-03-08T08:00:00+01:00"),
                    datetime.fromisoformat("2026-03-08T11:30:00+01:00"),
                    "positive",
                    ["work"],
                    "Summary text",
                )
            ],
        }
    )
    mock_result = ServiceResult(run=snapshot, bundle=None, was_reused=True)

    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"

    # Important: category_notes must have the category otherwise it's filtered out
    mock_categories = [MagicMock(id=1, code="work")]

    with patch(repo_path, return_value=snapshot), patch(ref_path, return_value=mock_categories):
        # We need to mock category_note_by_code in assembler or ensure snapshot has the score
        snapshot.category_scores.append(
            PersistedCategoryScore(1, "work", 15, 0.5, 0.5, 0.1, 1, False, "OK")
        )
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    timeline = response.json()["timeline"]
    assert len(timeline) == 1
    assert "très porteuse" in timeline[0]["summary"]


def test_daily_prediction_turning_points_summary_humanized():
    token = _register_and_get_access_token()
    snapshot = _build_mock_snapshot()
    snapshot = PersistedPredictionSnapshot(
        **{
            **snapshot.__dict__,
            "turning_points": [
                PersistedTurningPoint(
                    datetime.fromisoformat("2026-03-08T14:15:00+01:00"),
                    0.9,
                    "À 14:15, un basculement critique.",
                    [],
                )
            ],
        }
    )
    mock_result = ServiceResult(run=snapshot, bundle=None, was_reused=True)

    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    with (
        patch(repo_path, return_value=snapshot),
        patch(
            "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories",
            return_value=[],
        ),
    ):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    turning_points = response.json()["turning_points"]
    assert "critique" in turning_points[0]["summary"]


def test_daily_prediction_is_provisional_per_category():
    token = _register_and_get_access_token()
    snapshot = _build_mock_snapshot()
    snapshot = PersistedPredictionSnapshot(
        **{
            **snapshot.__dict__,
            "is_provisional_calibration": True,
            "category_scores": [
                PersistedCategoryScore(1, "love", 14, 0.2, 0.5, 0.1, 1, True, "Prov"),
                PersistedCategoryScore(2, "work", 8, -0.1, 0.3, 0.2, 2, False, "Final"),
            ],
        }
    )
    mock_result = ServiceResult(run=snapshot, bundle=None, was_reused=True)

    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    mock_categories = [MagicMock(id=1, code="love"), MagicMock(id=2, code="work")]
    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"

    with patch(repo_path, return_value=snapshot), patch(ref_path, return_value=mock_categories):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    categories = {c["code"]: c for c in data["categories"]}
    assert categories["love"]["is_provisional"] is True
    assert categories["work"]["is_provisional"] is False


def test_time_block_contains_turning_point_uses_half_open_intervals():
    from app.prediction.public_projection import PublicTimelinePolicy

    policy = PublicTimelinePolicy()

    turning_point_time = datetime(2026, 3, 8, 10, 0, tzinfo=timezone.utc)

    assert (
        policy._contains_turning_point(
            datetime(2026, 3, 8, 8, 0, tzinfo=timezone.utc),
            datetime(2026, 3, 8, 10, 0, tzinfo=timezone.utc),
            [turning_point_time],
        )
        is False
    )
    assert (
        policy._contains_turning_point(
            datetime(2026, 3, 8, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 3, 8, 12, 0, tzinfo=timezone.utc),
            [turning_point_time],
        )
        is True
    )


def test_time_block_contains_turning_point_accepts_mixed_offset_formats():
    from app.prediction.public_projection import PublicTimelinePolicy

    policy = PublicTimelinePolicy()

    tp_aware = datetime(2026, 3, 8, 10, 0, tzinfo=timezone.utc)
    assert (
        policy._contains_turning_point(
            datetime(2026, 3, 8, 9, 0, tzinfo=timezone.utc),
            datetime(2026, 3, 8, 11, 0, tzinfo=timezone.utc),
            [tp_aware],
        )
        is True
    )

    tp_naive = datetime(2026, 3, 8, 10, 0)
    assert (
        policy._contains_turning_point(
            datetime(2026, 3, 8, 9, 0, tzinfo=timezone.utc),
            datetime(2026, 3, 8, 11, 0, tzinfo=timezone.utc),
            [tp_naive],
        )
        is True
    )


def test_daily_prediction_decision_windows():
    token = _register_and_get_access_token()
    snapshot = _build_mock_snapshot()
    mock_result = ServiceResult(run=snapshot, bundle=None, was_reused=True)
    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    with (
        patch(
            "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run",
            return_value=snapshot,
        ),
        patch("app.prediction.public_projection.PublicDecisionWindowPolicy.build") as mock_build,
    ):
        mock_build.return_value = [
            {
                "start_local": "2026-03-08T08:00:00",
                "end_local": "2026-03-08T12:00:00",
                "window_type": "favorable",
                "score": 15.0,
                "confidence": 0.8,
                "dominant_categories": ["love"],
            }
        ]

        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert len(data["decision_windows"]) == 1
    assert data["decision_windows"][0]["window_type"] == "favorable"


def test_daily_prediction_summary_includes_best_window():
    token = _register_and_get_access_token()
    snapshot = _build_mock_snapshot()
    mock_result = ServiceResult(run=snapshot, bundle=None, was_reused=True)
    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    with (
        patch(
            "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run",
            return_value=snapshot,
        ),
        patch("app.prediction.public_projection.PublicDecisionWindowPolicy.build") as mock_dw_build,
    ):
        mock_dw_build.return_value = [
            {
                "start_local": "2026-03-08T10:00:00",
                "end_local": "2026-03-08T12:00:00",
                "window_type": "favorable",
                "score": 18.0,
                "confidence": 0.9,
                "dominant_categories": ["work"],
            }
        ]

        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["best_window"]["dominant_category"] == "work"
    assert data["summary"]["best_window"]["start_local"] == "2026-03-08T10:00:00"


def test_daily_prediction_filters_decision_windows_to_major_aspects():
    token = _register_and_get_access_token()
    snapshot = _build_mock_snapshot()
    snapshot = PersistedPredictionSnapshot(
        **{
            **snapshot.__dict__,
            "category_scores": [
                PersistedCategoryScore(1, "love", 19, 0.7, 0.8, 0.1, 1, False, None),
                PersistedCategoryScore(2, "work", 6, -0.1, 0.2, 0.1, 2, False, None),
            ],
            "time_blocks": [
                PersistedTimeBlock(
                    0,
                    datetime.fromisoformat("2026-03-08T20:00:00+01:00"),
                    datetime.fromisoformat("2026-03-08T22:00:00+01:00"),
                    "positive",
                    ["love", "work"],
                    None,
                )
            ],
        }
    )
    mock_result = ServiceResult(run=snapshot, bundle=None, was_reused=True)

    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    mock_categories = [MagicMock(id=1, code="love"), MagicMock(id=2, code="work")]

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"
    with patch(repo_path, return_value=snapshot), patch(ref_path, return_value=mock_categories):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    # "work" (note 6) should be filtered out from dominant_categories in timeline/windows
    assert data["decision_windows"][0]["dominant_categories"] == ["love"]
    assert data["timeline"][0]["dominant_categories"] == ["love"]


def test_daily_prediction_turning_points_follow_major_aspect_boundaries():
    token = _register_and_get_access_token()
    snapshot = _build_mock_snapshot()
    snapshot = PersistedPredictionSnapshot(
        **{
            **snapshot.__dict__,
            "category_scores": [
                PersistedCategoryScore(1, "love", 18, 0.5, 0.7, 0.1, 1, False, None),
                PersistedCategoryScore(2, "work", 17, 0.4, 0.6, 0.1, 2, False, None),
            ],
            "turning_points": [
                PersistedTurningPoint(
                    datetime.fromisoformat("2026-03-08T22:15:00+01:00"),
                    0.9,
                    "technical_code",
                    [{"event_type": "aspect_exact"}],
                )
            ],
            "time_blocks": [
                PersistedTimeBlock(
                    0,
                    datetime.fromisoformat("2026-03-08T21:30:00+01:00"),
                    datetime.fromisoformat("2026-03-08T22:15:00+01:00"),
                    "positive",
                    ["love"],
                    None,
                ),
                PersistedTimeBlock(
                    1,
                    datetime.fromisoformat("2026-03-08T22:15:00+01:00"),
                    datetime.fromisoformat("2026-03-08T23:15:00+01:00"),
                    "positive",
                    ["work"],
                    None,
                ),
            ],
        }
    )
    mock_result = ServiceResult(run=snapshot, bundle=None, was_reused=True)

    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    mock_categories = [MagicMock(id=1, code="love"), MagicMock(id=2, code="work")]

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"
    with patch(repo_path, return_value=snapshot), patch(ref_path, return_value=mock_categories):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    tps = sorted(data["turning_points"], key=lambda x: x["occurred_at_local"])
    assert len(tps) == 1
    assert tps[0]["occurred_at_local"] == "2026-03-08T22:15:00+01:00"


def test_daily_prediction_turning_points_expose_numeric_severity():
    token = _register_and_get_access_token()
    snapshot = _build_mock_snapshot()
    snapshot = PersistedPredictionSnapshot(
        **{
            **snapshot.__dict__,
            "turning_points": [
                PersistedTurningPoint(
                    datetime.fromisoformat("2026-03-08T22:15:00+01:00"), 0.9, "Pivot lisible", []
                )
            ],
        }
    )
    mock_result = ServiceResult(run=snapshot, bundle=None, was_reused=True)

    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    with (
        patch(repo_path, return_value=snapshot),
        patch(
            "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories",
            return_value=[],
        ),
    ):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    turning_point = response.json()["turning_points"][0]
    assert turning_point["severity"] == 0.9
    assert isinstance(turning_point["severity"], float)


def test_daily_prediction_exposes_enriched_turning_point_fields():
    token = _register_and_get_access_token()
    snapshot = _build_mock_snapshot()
    mock_result = ServiceResult(run=snapshot, bundle=None, was_reused=True)

    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    assembled_payload = {
        "meta": {
            "date_local": "2026-03-08",
            "timezone": "Europe/Paris",
            "computed_at": "2026-03-08T10:00:00",
            "reference_version": settings.active_reference_version,
            "ruleset_version": settings.ruleset_version,
            "was_reused": True,
            "house_system_effective": "placidus",
            "is_provisional_calibration": False,
            "calibration_label": None,
        },
        "summary": {
            "overall_tone": "neutral",
            "overall_summary": "Summary",
            "calibration_note": None,
            "top_categories": [],
            "bottom_categories": [],
            "best_window": None,
            "main_turning_point": None,
            "low_score_variance": False,
            "flat_day": False,
            "relative_top_categories": None,
            "relative_summary": None,
        },
        "categories": [],
        "timeline": [],
        "decision_windows": None,
        "micro_trends": None,
        "turning_points": [
            {
                "occurred_at_local": "2026-03-08T08:45:00+01:00",
                "severity": 0.42,
                "summary": "Bascule durable (theme_rotation)",
                "drivers": [{"label": "Moon square Pluto"}],
                "impacted_categories": ["health", "money", "work"],
                "change_type": "recomposition",
                "previous_categories": ["health", "money", "social_network"],
                "next_categories": ["health", "money", "work"],
                "primary_driver": {
                    "event_type": "aspect_exact_to_personal",
                    "body": "Moon",
                    "target": "Pluto",
                    "aspect": "square",
                    "orb_deg": 0.12,
                    "phase": "applying",
                    "priority": 68,
                    "base_weight": 1.5,
                    "metadata": {"natal_house_target": 8, "natal_house_transited": 5},
                },
                "movement": {
                    "strength": 0.42,
                    "previous_composite": 3.07,
                    "next_composite": 3.19,
                    "delta_composite": 0.12,
                    "direction": "recomposition",
                },
                "category_deltas": [
                    {
                        "code": "work",
                        "direction": "up",
                        "delta_score": 1.08,
                        "delta_intensity": 0.54,
                        "delta_rank": None,
                    }
                ],
            }
        ],
    }

    with patch(
        "app.api.v1.routers.predictions.PublicPredictionAssembler.assemble",
        return_value=assembled_payload,
    ):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    turning_point = response.json()["turning_points"][0]
    assert turning_point["change_type"] == "recomposition"
    assert turning_point["primary_driver"]["body"] == "Moon"
    assert turning_point["movement"]["delta_composite"] == 0.12
    assert turning_point["category_deltas"][0]["code"] == "work"


def test_daily_prediction_hides_non_actionable_turning_points_when_no_windows():
    token = _register_and_get_access_token()
    snapshot = _build_mock_snapshot(local_date_value=date(2026, 3, 10))
    snapshot = PersistedPredictionSnapshot(
        **{
            **snapshot.__dict__,
            "is_provisional_calibration": True,
            "category_scores": [
                PersistedCategoryScore(1, "energy", 10, 0.0, 0.0, 0.0, 1, True, None),
                PersistedCategoryScore(2, "mood", 10, 0.0, 0.0, 0.0, 2, True, None),
            ],
            "time_blocks": [
                PersistedTimeBlock(
                    0,
                    datetime.fromisoformat("2026-03-10T00:00:00+01:00"),
                    datetime.fromisoformat("2026-03-10T12:00:00+01:00"),
                    "neutral",
                    ["energy", "mood"],
                    None,
                )
            ],
            "turning_points": [
                PersistedTurningPoint(
                    datetime.fromisoformat("2026-03-10T06:30:00+01:00"),
                    1.0,
                    "À 06:30, un basculement critique : plusieurs domaines.",
                    [{"event_type": "aspect_exact_to_personal"}],
                )
            ],
        }
    )
    mock_bundle = MagicMock()
    mock_bundle.editorial.data.best_window = MagicMock(
        start_local=datetime.fromisoformat("2026-03-10T00:00:00+01:00"),
        end_local=datetime.fromisoformat("2026-03-10T06:30:00+01:00"),
        dominant_category="career",
    )
    mock_result = ServiceResult(run=snapshot, bundle=mock_bundle, was_reused=False)

    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    mock_categories = [
        MagicMock(id=1, code="energy"),
        MagicMock(id=2, code="mood"),
    ]
    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"

    with patch(repo_path, return_value=snapshot), patch(ref_path, return_value=mock_categories):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["decision_windows"] is None
    assert data["turning_points"] == []
    assert data["summary"]["best_window"] is None
    assert data["summary"]["main_turning_point"] is None
    assert data["timeline"][0]["turning_point"] is False


def test_daily_prediction_pivot_windows_use_score_twelve():
    token = _register_and_get_access_token()
    snapshot = _build_mock_snapshot()
    snapshot = PersistedPredictionSnapshot(
        **{
            **snapshot.__dict__,
            "category_scores": [
                PersistedCategoryScore(1, "love", 14, 0.2, 0.4, 0.3, 1, False, None)
            ],
            "turning_points": [
                PersistedTurningPoint(
                    datetime.fromisoformat("2026-03-08T10:00:00+01:00"), 0.8, "Pivot métier", []
                )
            ],
            "time_blocks": [
                PersistedTimeBlock(
                    0,
                    datetime.fromisoformat("2026-03-08T08:00:00+01:00"),
                    datetime.fromisoformat("2026-03-08T12:00:00+01:00"),
                    "neutral",
                    ["love"],
                    None,
                )
            ],
        }
    )
    mock_result = ServiceResult(run=snapshot, bundle=None, was_reused=True)

    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    mock_categories = [MagicMock(id=1, code="love")]

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"
    with patch(repo_path, return_value=snapshot), patch(ref_path, return_value=mock_categories):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert any(
        dw["window_type"] == "pivot" and dw["score"] == 12.0 for dw in data["decision_windows"]
    )


def test_daily_prediction_rebuilds_decision_windows_for_reused_run():
    token = _register_and_get_access_token()
    snapshot = _build_mock_snapshot()
    snapshot = PersistedPredictionSnapshot(
        **{
            **snapshot.__dict__,
            "category_scores": [
                PersistedCategoryScore(1, "love", 16, 0.8, 0.9, 0.3, 1, False, None),
                PersistedCategoryScore(2, "work", 14, 0.6, 0.7, 0.4, 2, False, None),
            ],
            "time_blocks": [
                PersistedTimeBlock(
                    0,
                    datetime.fromisoformat("2026-03-08T08:00:00+01:00"),
                    datetime.fromisoformat("2026-03-08T10:00:00+01:00"),
                    "positive",
                    ["love", "work"],
                    None,
                )
            ],
        }
    )
    mock_result = ServiceResult(run=snapshot, bundle=None, was_reused=True)

    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    mock_categories = [MagicMock(id=1, code="love"), MagicMock(id=2, code="work")]

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"
    with patch(repo_path, return_value=snapshot), patch(ref_path, return_value=mock_categories):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert len(data["decision_windows"]) == 1
    assert data["decision_windows"][0]["window_type"] == "favorable"
    assert "love" in data["decision_windows"][0]["dominant_categories"]
