from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db import session as db_session_module
from app.infra.db.base import Base
from app.infra.db.models.llm_observability import LlmCallLogModel, LlmValidationStatus
from app.infra.db.models.user import UserModel
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _isolated_database(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'test-admin-ai.db').as_posix()}"
    test_engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        future=True,
    )
    test_session_local = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )
    monkeypatch.setattr(db_session_module, "engine", test_engine)
    monkeypatch.setattr(db_session_module, "SessionLocal", test_session_local)
    Base.metadata.create_all(bind=test_engine)
    try:
        yield
    finally:
        test_engine.dispose()


@pytest.fixture
def admin_token():
    with db_session_module.SessionLocal() as db:
        from app.core.security import hash_password

        admin = UserModel(
            email="admin-ai@example.com",
            password_hash=hash_password("admin123"),
            role="admin",
            astrologer_profile="standard",
        )
        db.add(admin)
        db.commit()

    response = client.post(
        "/v1/auth/login", json={"email": "admin-ai@example.com", "password": "admin123"}
    )
    return response.json()["data"]["tokens"]["access_token"]


def test_get_ai_metrics_success(admin_token):
    with db_session_module.SessionLocal() as db:
        db.add_all(
            [
                LlmCallLogModel(
                    use_case="chat_runtime",
                    feature="chat",
                    subfeature="astrologer",
                    plan="premium",
                    model="gpt-4o",
                    latency_ms=500,
                    tokens_in=100,
                    tokens_out=200,
                    cost_usd_estimated=0.003,
                    validation_status=LlmValidationStatus.VALID,
                    request_id="req1",
                    trace_id="trace1",
                    input_hash="hash1",
                    environment="test",
                ),
                LlmCallLogModel(
                    use_case="chat_runtime",
                    feature="chat",
                    subfeature="astrologer",
                    plan="premium",
                    model="gpt-4o",
                    latency_ms=1000,
                    tokens_in=100,
                    tokens_out=200,
                    cost_usd_estimated=0.003,
                    validation_status=LlmValidationStatus.ERROR,
                    request_id="req2",
                    trace_id="trace2",
                    input_hash="hash2",
                    environment="test",
                ),
                LlmCallLogModel(
                    use_case="natal_psy_profile_runtime",
                    feature="natal",
                    subfeature="psy_profile",
                    plan="premium",
                    model="gpt-4o",
                    latency_ms=1500,
                    tokens_in=50,
                    tokens_out=250,
                    cost_usd_estimated=0.004,
                    validation_status=LlmValidationStatus.VALID,
                    request_id="req3",
                    trace_id="trace3",
                    input_hash="hash3",
                    environment="test",
                ),
            ]
        )
        db.commit()

    response = client.get(
        "/v1/admin/ai/metrics?period=30d", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) >= 7

    metrics_by_key = {item["use_case"]: item for item in data}

    chat_metrics = metrics_by_key["astrologer_chat"]
    assert chat_metrics["display_name"] == "Chat astrologue"
    assert chat_metrics["call_count"] == 2
    assert chat_metrics["error_rate"] == 0.5

    thematic_metrics = metrics_by_key["thematic_consultations"]
    assert thematic_metrics["call_count"] == 1
    assert thematic_metrics["display_name"] == "Consultations thematiques"

    assert metrics_by_key["natal_theme_short_free"]["call_count"] == 0
    assert metrics_by_key["natal_theme_short_paid"]["call_count"] == 0
    assert metrics_by_key["natal_theme_complete_paid"]["call_count"] == 0
    assert metrics_by_key["daily_horoscope"]["call_count"] == 0
    assert metrics_by_key["weekly_horoscope"]["call_count"] == 0


def test_get_use_case_detail_success(admin_token):
    with db_session_module.SessionLocal() as db:
        db.add_all(
            [
                LlmCallLogModel(
                    use_case="natal_interpretation_runtime",
                    feature="natal",
                    subfeature="interpretation",
                    plan="premium",
                    model="gpt-4o",
                    latency_ms=2000,
                    tokens_in=500,
                    tokens_out=1500,
                    cost_usd_estimated=0.02,
                    validation_status=LlmValidationStatus.ERROR,
                    request_id="req_fail",
                    trace_id="trace_fail",
                    input_hash="hash_fail",
                    environment="test",
                ),
                LlmCallLogModel(
                    use_case="natal_interpretation_runtime",
                    feature="natal",
                    subfeature="interpretation",
                    plan="premium",
                    model="gpt-4o",
                    latency_ms=1200,
                    tokens_in=400,
                    tokens_out=1100,
                    cost_usd_estimated=0.015,
                    validation_status=LlmValidationStatus.VALID,
                    request_id="req_ok",
                    trace_id="trace_ok",
                    input_hash="hash_ok",
                    environment="test",
                ),
            ]
        )
        db.commit()

    response = client.get(
        "/v1/admin/ai/metrics/natal_theme_complete_paid?period=30d",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["use_case"] == "natal_theme_complete_paid"
    assert data["metrics"]["display_name"] == "Theme natal complete basic/premium"
    assert data["metrics"]["call_count"] == 2
    assert len(data["recent_failed_calls"]) >= 1
    assert data["recent_failed_calls"][0]["request_id_masked"] == "req_fail..."
    assert data["recent_failed_calls"][0]["error_code"] == "LLM_CALL_ERROR"


def test_get_use_case_detail_uses_canonical_feature_axis_for_derived_categories(admin_token):
    with db_session_module.SessionLocal() as db:
        db.add_all(
            [
                LlmCallLogModel(
                    use_case="legacy_chat_runtime",
                    feature="chat",
                    subfeature="unknown",
                    plan="premium",
                    model="gpt-4o",
                    latency_ms=900,
                    tokens_in=80,
                    tokens_out=120,
                    cost_usd_estimated=0.004,
                    validation_status=LlmValidationStatus.ERROR,
                    request_id="req-feature-fail",
                    trace_id="trace-feature-fail",
                    input_hash="hash-feature-fail",
                    environment="test",
                ),
                LlmCallLogModel(
                    use_case="another_chat_runtime",
                    feature="chat",
                    subfeature="unknown",
                    plan="free",
                    model="gpt-4o",
                    latency_ms=450,
                    tokens_in=50,
                    tokens_out=50,
                    cost_usd_estimated=0.002,
                    validation_status=LlmValidationStatus.VALID,
                    request_id="req-feature-ok",
                    trace_id="trace-feature-ok",
                    input_hash="hash-feature-ok",
                    environment="test",
                ),
            ]
        )
        db.commit()

    response = client.get(
        "/v1/admin/ai/metrics/chat?period=30d",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["use_case"] == "chat"
    assert data["metrics"]["call_count"] == 2
    assert data["metrics"]["display_name"] == "chat"
    assert data["recent_failed_calls"][0]["request_id_masked"] == "req-feat..."


def test_get_use_case_detail_legacy_removed_is_explicitly_bounded(admin_token):
    with db_session_module.SessionLocal() as db:
        db.add_all(
            [
                LlmCallLogModel(
                    use_case="daily_prediction",
                    feature=None,
                    subfeature=None,
                    plan="free",
                    model="gpt-4o",
                    latency_ms=700,
                    tokens_in=40,
                    tokens_out=60,
                    cost_usd_estimated=0.001,
                    validation_status=LlmValidationStatus.ERROR,
                    request_id="req-legacy-bounded",
                    trace_id="trace-legacy-bounded",
                    input_hash="hash-legacy-bounded",
                    environment="test",
                ),
                LlmCallLogModel(
                    use_case="daily_prediction",
                    feature="guidance",
                    subfeature="daily",
                    plan="free",
                    model="gpt-4o",
                    latency_ms=650,
                    tokens_in=30,
                    tokens_out=55,
                    cost_usd_estimated=0.001,
                    validation_status=LlmValidationStatus.ERROR,
                    request_id="req-legacy-ignored",
                    trace_id="trace-legacy-ignored",
                    input_hash="hash-legacy-ignored",
                    environment="test",
                ),
            ]
        )
        db.commit()

    response = client.get(
        "/v1/admin/ai/metrics/legacy_removed?period=30d",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["use_case"] == "legacy_removed"
    assert data["metrics"]["call_count"] == 1
    assert data["recent_failed_calls"][0]["request_id_masked"] == "req-lega..."
