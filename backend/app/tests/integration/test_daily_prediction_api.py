from __future__ import annotations

from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.api.v1.routers.predictions import get_daily_prediction_service
from app.infra.db.base import Base
from app.infra.db.models.reference import ReferenceVersionModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService
from app.services.daily_prediction_service import (
    ComputeMode,
    DailyPredictionServiceError,
    ServiceResult,
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides.clear()
    with SessionLocal() as db:
        db.execute(delete(UserModel))
        db.commit()


def _register_and_get_access_token() -> str:
    with SessionLocal() as db:
        auth = AuthService.register(
            db, email="daily-api-user@example.com", password="strong-pass-123", role="user"
        )
        db.commit()
        return auth.tokens.access_token


def _register_admin_and_get_token() -> str:
    with SessionLocal() as db:
        auth = AuthService.register(
            db, email="admin@example.com", password="admin-pass-123", role="admin"
        )
        db.commit()
        return auth.tokens.access_token


def _override_service(service: MagicMock) -> None:
    app.dependency_overrides[get_daily_prediction_service] = lambda: service


def _build_mock_run(
    *,
    run_id: int = 1,
    local_date_value: date = date(2026, 3, 8),
    timezone: str = "Europe/Paris",
    computed_at: datetime = datetime(2026, 3, 8, 10, 0),
    reference_version_id: int = 1,
) -> MagicMock:
    mock_run = MagicMock()
    mock_run.id = run_id
    mock_run.local_date = local_date_value
    mock_run.timezone = timezone
    mock_run.computed_at = computed_at
    mock_run.reference_version_id = reference_version_id
    mock_run.is_provisional_calibration = None
    mock_run.calibration_label = None
    return mock_run


def test_daily_prediction_requires_auth():
    response = client.get("/v1/predictions/daily")
    assert response.status_code == 401


def test_daily_prediction_nominal_200():
    token = _register_and_get_access_token()
    mock_run = _build_mock_run()
    mock_run.is_provisional_calibration = False
    mock_run.calibration_label = "v1"
    mock_result = ServiceResult(run=mock_run, engine_output=None, was_reused=True)
    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    mock_full_run = {
        "id": 1,
        "local_date": "2026-03-08",
        "timezone": "Europe/Paris",
        "computed_at": "2026-03-08T10:00:00",
        "overall_summary": "Summary",
        "overall_tone": "positive",
        "category_scores": [
            {
                "category_id": 1,
                "note_20": 15,
                "raw_score": 0.5,
                "power": 0.7,
                "volatility": 0.1,
                "rank": 1,
                "summary": "Love summary",
            }
        ],
        "turning_points": [],
        "time_blocks": [],
    }

    mock_categories = [MagicMock(id=1, code="love")]
    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"

    with (
        patch(repo_path, return_value=mock_full_run),
        patch(ref_path, return_value=mock_categories),
    ):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert "meta" in data
    assert "summary" in data
    assert "categories" in data
    assert "timeline" in data
    assert "turning_points" in data
    assert data["meta"]["was_reused"] is True
    assert data["meta"]["is_provisional_calibration"] is False
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


def test_daily_prediction_422_for_non_natal_service_error():
    token = _register_and_get_access_token()
    mock_service = MagicMock()
    mock_service.get_or_compute.side_effect = DailyPredictionServiceError(
        code="timezone_missing",
        message="Timezone missing",
    )
    _override_service(mock_service)

    response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 422
    assert response.json()["detail"] == {
        "code": "timezone_missing",
        "message": "Timezone missing",
    }


def test_daily_prediction_profile_missing_is_422():
    token = _register_and_get_access_token()
    mock_service = MagicMock()
    mock_service.get_or_compute.side_effect = DailyPredictionServiceError(
        code="profile_missing",
        message="Profil de naissance introuvable",
    )
    _override_service(mock_service)

    response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 422
    assert response.json()["detail"] == {
        "code": "profile_missing",
        "message": "Profil de naissance introuvable",
    }


def test_daily_prediction_categories_sorted_by_rank():
    token = _register_and_get_access_token()
    mock_run = _build_mock_run()
    mock_result = ServiceResult(run=mock_run, engine_output=None, was_reused=True)
    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    mock_full_run = {
        "id": 1,
        "category_scores": [
            {
                "category_id": 2,
                "rank": 2,
                "note_20": 10,
                "raw_score": 0.3,
                "power": 0.4,
                "volatility": 0.5,
                "summary": "S2",
            },
            {
                "category_id": 1,
                "rank": 1,
                "note_20": 15,
                "raw_score": 0.5,
                "power": 0.7,
                "volatility": 0.1,
                "summary": "S1",
            },
        ],
        "turning_points": [],
        "time_blocks": [],
    }

    mock_categories = [MagicMock(id=1, code="cat1"), MagicMock(id=2, code="cat2")]

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"

    with (
        patch(repo_path, return_value=mock_full_run),
        patch(ref_path, return_value=mock_categories),
    ):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    categories = response.json()["categories"]
    assert categories[0]["rank"] == 1
    assert categories[1]["rank"] == 2
    assert categories[0]["code"] == "cat1"


def test_daily_prediction_timeline_chronological():
    token = _register_and_get_access_token()
    mock_run = _build_mock_run()
    mock_result = ServiceResult(run=mock_run, engine_output=None, was_reused=True)
    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    mock_full_run = {
        "id": 1,
        "category_scores": [],
        "turning_points": [
            {
                "occurred_at_local": "2026-03-08T06:15:00+01:00",
                "severity": 0.8,
                "summary": "Pivot",
                "driver_json": '[{"event_type":"aspect"}]',
            }
        ],
        "time_blocks": [
            {
                "start_at_local": "2026-03-08T06:00:00+00:00",
                "end_at_local": "2026-03-08T07:00:00+00:00",
                "tone_code": "neutral",
                "dominant_categories_json": "[]",
                "summary": "S2",
            },
            {
                "start_at_local": "2026-03-08T06:00:00+01:00",
                "end_at_local": "2026-03-08T07:00:00+01:00",
                "tone_code": "neutral",
                "dominant_categories_json": "[]",
                "summary": "S1",
            },
        ],
    }

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"

    with patch(repo_path, return_value=mock_full_run), patch(ref_path, return_value=[]):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    timeline = response.json()["timeline"]
    assert timeline[0]["start_local"] == "2026-03-08T06:00:00+01:00"
    assert timeline[0]["turning_point"] is True
    assert timeline[1]["turning_point"] is False


def test_daily_prediction_date_param():
    token = _register_and_get_access_token()

    target_date = date(2026, 3, 10)
    mock_run = _build_mock_run(
        local_date_value=target_date, computed_at=datetime(2026, 3, 10, 10, 0)
    )
    mock_result = ServiceResult(run=mock_run, engine_output=None, was_reused=True)
    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"

    full_run_empty = {"id": 1, "category_scores": [], "turning_points": [], "time_blocks": []}

    with patch(repo_path, return_value=full_run_empty), patch(ref_path, return_value=[]):
        response = client.get(
            "/v1/predictions/daily",
            params={"date": "2026-03-10"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert response.json()["meta"]["date_local"] == "2026-03-10"
    mock_service.get_or_compute.assert_called_once()
    assert mock_service.get_or_compute.call_args.kwargs["date_local"] == target_date


def test_daily_prediction_returns_500_on_malformed_json_payload():
    token = _register_and_get_access_token()
    mock_run = _build_mock_run()
    mock_result = ServiceResult(run=mock_run, engine_output=None, was_reused=True)
    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    mock_full_run = {
        "id": 1,
        "category_scores": [],
        "turning_points": [],
        "time_blocks": [
            {
                "start_at_local": "2026-03-08T06:00:00+01:00",
                "end_at_local": "2026-03-08T07:00:00+01:00",
                "tone_code": "neutral",
                "dominant_categories_json": "[invalid",
                "summary": "Broken",
            }
        ],
    }

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"

    with patch(repo_path, return_value=mock_full_run), patch(ref_path, return_value=[]):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 500
    assert response.json()["detail"]["code"] == "prediction_payload_invalid"


def test_daily_prediction_meta_uses_run_reference_version_and_house_system_effective():
    token = _register_and_get_access_token()
    with SessionLocal() as db:
        db.add(
            ReferenceVersionModel(id=7, version="legacy-v1", description="Legacy", is_locked=True)
        )
        db.commit()

    mock_run = _build_mock_run(reference_version_id=7)
    mock_result = ServiceResult(run=mock_run, engine_output=None, was_reused=True)
    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    full_run_empty = {
        "id": 1,
        "house_system_effective": "placidus",
        "category_scores": [],
        "turning_points": [],
        "time_blocks": [],
    }
    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"

    with patch(repo_path, return_value=full_run_empty), patch(ref_path, return_value=[]):
        response = client.get("/v1/predictions/daily", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    meta = response.json()["meta"]
    assert meta["reference_version"] == "legacy-v1"
    assert meta["house_system_effective"] == "placidus"


def test_history_requires_auth():
    response = client.get(
        "/v1/predictions/daily/history", params={"from_date": "2026-03-01", "to_date": "2026-03-08"}
    )
    assert response.status_code == 401


def test_history_200_nominal():
    token = _register_and_get_access_token()

    score_love = MagicMock(category_id=1, note_20=15.0)
    score_work = MagicMock(category_id=2, note_20=12.0)
    mock_runs = [
        MagicMock(
            id=1,
            local_date=date(2026, 3, 8),
            reference_version_id=1,
            overall_tone="positive",
            category_scores=[score_love, score_work],
            turning_points=[MagicMock(id=1), MagicMock(id=2)],
        ),
        MagicMock(
            id=2,
            local_date=date(2026, 3, 7),
            reference_version_id=1,
            overall_tone="positive",
            category_scores=[score_love],
            turning_points=[MagicMock(id=3)],
        ),
    ]
    # Set computed_at manually to avoid MagicMock issues with isoformat
    mock_runs[0].computed_at = datetime(2026, 3, 8, 10, 0)
    mock_runs[1].computed_at = datetime(2026, 3, 7, 10, 0)

    repo_history_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_user_history"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"

    mock_categories = [
        MagicMock(id=1, code="love"),
        MagicMock(id=2, code="work"),
    ]

    with (
        patch(repo_history_path, return_value=mock_runs),
        patch(ref_path, return_value=mock_categories),
    ):
        response = client.get(
            "/v1/predictions/daily/history",
            params={"from_date": "2026-03-01", "to_date": "2026-03-08"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["items"][0]["date_local"] == "2026-03-08"
    assert data["items"][0]["categories"]["love"] == 15.0
    assert data["items"][0]["pivot_count"] == 2


def test_history_empty_range():
    token = _register_and_get_access_token()
    repo_history_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_user_history"

    with patch(repo_history_path, return_value=[]):
        response = client.get(
            "/v1/predictions/daily/history",
            params={"from_date": "2026-03-01", "to_date": "2026-03-08"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0}


def test_history_sorted_desc():
    token = _register_and_get_access_token()
    mock_runs = [
        MagicMock(
            id=2,
            local_date=date(2026, 3, 7),
            reference_version_id=1,
            overall_tone="steady",
            category_scores=[],
            turning_points=[],
        ),
        MagicMock(
            id=1,
            local_date=date(2026, 3, 8),
            reference_version_id=1,
            overall_tone="positive",
            category_scores=[],
            turning_points=[],
        ),
    ]
    mock_runs[0].computed_at = datetime(2026, 3, 7, 10, 0)
    mock_runs[1].computed_at = datetime(2026, 3, 8, 10, 0)

    repo_history_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_user_history"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"

    with (
        patch(repo_history_path, return_value=mock_runs),
        patch(ref_path, return_value=[]),
    ):
        response = client.get(
            "/v1/predictions/daily/history",
            params={"from_date": "2026-03-01", "to_date": "2026-03-08"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert [item["date_local"] for item in response.json()["items"]] == [
        "2026-03-08",
        "2026-03-07",
    ]


def test_history_max_range_exceeded_400():
    token = _register_and_get_access_token()
    response = client.get(
        "/v1/predictions/daily/history",
        params={"from_date": "2026-01-01", "to_date": "2026-05-01"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "range_too_large"


def test_history_invalid_dates_400():
    token = _register_and_get_access_token()
    response = client.get(
        "/v1/predictions/daily/history",
        params={"from_date": "2026-03-08", "to_date": "2026-03-01"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_date_range"


def test_history_invalid_calendar_date_422_standard():
    token = _register_and_get_access_token()
    response = client.get(
        "/v1/predictions/daily/history",
        params={"from_date": "2026-02-31", "to_date": "2026-03-01"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "invalid_request_payload"
    assert error["details"]["errors"][0]["loc"][-1] == "from_date"


def test_history_no_recompute():
    token = _register_and_get_access_token()
    mock_service = MagicMock()
    _override_service(mock_service)

    repo_history_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_user_history"
    ref_path = "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories"
    mock_run = MagicMock(
        id=1,
        local_date=date(2026, 3, 8),
        reference_version_id=1,
        overall_tone="positive",
        category_scores=[],
        turning_points=[],
    )
    mock_run.computed_at = datetime(2026, 3, 8, 10, 0)

    with (
        patch(repo_history_path, return_value=[mock_run]),
        patch(ref_path, return_value=[]),
    ):
        response = client.get(
            "/v1/predictions/daily/history",
            params={"from_date": "2026-03-01", "to_date": "2026-03-08"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    mock_service.get_or_compute.assert_not_called()


def test_debug_requires_auth():
    response = client.get("/v1/predictions/daily/debug", params={"target_user_id": 42})
    assert response.status_code == 401


def test_debug_403_non_admin():
    token = _register_and_get_access_token()
    response = client.get(
        "/v1/predictions/daily/debug",
        params={"target_user_id": 42},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "forbidden"


def test_debug_422_when_target_user_id_missing():
    token = _register_admin_and_get_token()
    response = client.get(
        "/v1/predictions/daily/debug",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "invalid_request_payload"
    assert error["details"]["errors"][0]["loc"][-1] == "target_user_id"


def test_debug_404_no_run():
    token = _register_admin_and_get_token()
    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = None
    _override_service(mock_service)

    response = client.get(
        "/v1/predictions/daily/debug",
        params={"target_user_id": 42},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "not_found"


def test_debug_422_when_target_profile_missing():
    token = _register_admin_and_get_token()
    mock_service = MagicMock()
    mock_service.get_or_compute.side_effect = DailyPredictionServiceError(
        code="profile_missing",
        message="Profil de naissance introuvable",
    )
    _override_service(mock_service)

    response = client.get(
        "/v1/predictions/daily/debug",
        params={"target_user_id": 42},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == {
        "code": "profile_missing",
        "message": "Profil de naissance introuvable",
    }


def test_debug_200_admin_nominal():
    token = _register_admin_and_get_token()

    mock_run = _build_mock_run()
    mock_run.input_hash = "debug_hash"
    mock_run.reference_version_id = 1
    mock_run.ruleset_id = 2
    mock_run.is_provisional_calibration = True
    mock_run.calibration_label = "mixed"

    mock_result = ServiceResult(run=mock_run, engine_output=None, was_reused=True)
    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = mock_result
    _override_service(mock_service)

    mock_full_run = {
        "id": 1,
        "input_hash": "debug_hash",
        "reference_version_id": 1,
        "ruleset_id": 2,
        "is_provisional_calibration": True,
        "category_scores": [
            {
                "category_id": 1,
                "category_code": "love",
                "note_20": 15,
                "raw_score": 0.5,
                "power": 0.7,
                "volatility": 0.1,
                "rank": 1,
                "contributors_json": '[{"source":"transit","weight":0.8}]',
            }
        ],
        "turning_points": [
            {
                "occurred_at_local": "2026-03-08T10:00:00+01:00",
                "severity": 0.9,
                "summary": "Big change",
                "driver_json": '[{"event":"Jupiter Conjunct Moon"}]',
            }
        ],
    }

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    with patch(repo_path, return_value=mock_full_run):
        response = client.get(
            "/v1/predictions/daily/debug",
            params={"target_user_id": 42},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["input_hash"] == "debug_hash"
    assert data["reference_version_id"] == 1
    assert data["ruleset_id"] == 2
    assert data["meta"]["is_provisional_calibration"] is True
    assert data["meta"]["calibration_label"] == "mixed"
    assert data["is_provisional_calibration"] is True
    assert data["categories"][0]["contributors"][0]["source"] == "transit"
    assert data["turning_points"][0]["drivers"][0]["event"] == "Jupiter Conjunct Moon"


def test_debug_returns_empty_lists_when_json_fields_are_absent():
    token = _register_admin_and_get_token()
    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = ServiceResult(
        run=_build_mock_run(), engine_output=None, was_reused=True
    )
    _override_service(mock_service)

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    with (
        patch(
            repo_path,
            return_value={
                "reference_version_id": 1,
                "ruleset_id": 2,
                "is_provisional_calibration": None,
                "category_scores": [
                    {
                        "category_id": 1,
                        "note_20": 12,
                        "raw_score": 0.3,
                        "power": 0.4,
                        "volatility": 0.2,
                        "rank": 1,
                        "contributors_json": None,
                    }
                ],
                "turning_points": [
                    {
                        "occurred_at_local": "2026-03-08T10:00:00+01:00",
                        "severity": 0.4,
                        "summary": "Minor shift",
                        "driver_json": None,
                    }
                ],
            },
        ),
        patch(
            "app.api.v1.routers.predictions.PredictionReferenceRepository.get_categories",
            return_value=[MagicMock(id=1, code="love")],
        ),
    ):
        response = client.get(
            "/v1/predictions/daily/debug",
            params={"target_user_id": 42},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["categories"][0]["contributors"] == []
    assert data["turning_points"][0]["drivers"] == []


def test_debug_no_recompute():
    token = _register_admin_and_get_token()
    mock_service = MagicMock()
    mock_service.get_or_compute.return_value = ServiceResult(
        run=_build_mock_run(), engine_output=None, was_reused=True
    )
    _override_service(mock_service)

    repo_path = "app.api.v1.routers.predictions.DailyPredictionRepository.get_full_run"
    with patch(
        repo_path,
        return_value={
            "reference_version_id": 1,
            "ruleset_id": 2,
            "category_scores": [],
            "turning_points": [],
        },
    ):
        client.get(
            "/v1/predictions/daily/debug",
            params={"target_user_id": 42},
            headers={"Authorization": f"Bearer {token}"},
        )

    mock_service.get_or_compute.assert_called_once()
    assert mock_service.get_or_compute.call_args.kwargs["mode"] == ComputeMode.read_only
