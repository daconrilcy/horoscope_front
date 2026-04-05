from pathlib import Path
from datetime import UTC, datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db import session as db_session_module
from app.infra.db.base import Base
from app.infra.db.models.user import UserModel
from app.infra.db.models.llm_observability import LlmCallLogModel, LlmValidationStatus
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
            astrologer_profile="standard"
        )
        db.add(admin)
        db.commit()
    
    response = client.post("/v1/auth/login", json={
        "email": "admin-ai@example.com",
        "password": "admin123"
    })
    return response.json()["data"]["tokens"]["access_token"]

def test_get_ai_metrics_success(admin_token):
    with db_session_module.SessionLocal() as db:
        log1 = LlmCallLogModel(
            use_case="chat_astrologer",
            model="gpt-4o",
            latency_ms=500,
            tokens_in=100,
            tokens_out=200,
            cost_usd_estimated=0.003,
            validation_status=LlmValidationStatus.VALID,
            request_id="req1",
            trace_id="trace1",
            input_hash="hash1",
            environment="test"
        )
        log2 = LlmCallLogModel(
            use_case="chat_astrologer",
            model="gpt-4o",
            latency_ms=1000,
            tokens_in=100,
            tokens_out=200,
            cost_usd_estimated=0.003,
            validation_status=LlmValidationStatus.ERROR,
            request_id="req2",
            trace_id="trace2",
            input_hash="hash2",
            environment="test"
        )
        db.add_all([log1, log2])
        db.commit()

    response = client.get("/v1/admin/ai/metrics?period=30d", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) >= 1
    m = [x for x in data if x["use_case"] == "chat_astrologer"][0]
    assert m["call_count"] == 2
    assert m["error_rate"] == 0.5

def test_get_use_case_detail_success(admin_token):
    with db_session_module.SessionLocal() as db:
        log = LlmCallLogModel(
            use_case="natal_interpretation",
            model="gpt-4o",
            latency_ms=2000,
            tokens_in=500,
            tokens_out=1500,
            cost_usd_estimated=0.02,
            validation_status=LlmValidationStatus.ERROR,
            request_id="req_fail",
            trace_id="trace_fail",
            input_hash="hash_fail",
            environment="test"
        )
        db.add(log)
        db.commit()

    response = client.get("/v1/admin/ai/metrics/natal_interpretation?period=30d", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["use_case"] == "natal_interpretation"
    assert len(data["recent_failed_calls"]) >= 1
    assert data["recent_failed_calls"][0]["user_id_masked"] == "req_fail..."
