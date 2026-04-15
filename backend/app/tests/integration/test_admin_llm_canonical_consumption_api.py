from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.infra.db.models.llm_observability import LlmCallLogModel, LlmValidationStatus
from app.infra.db.session import SessionLocal
from app.main import app
from app.services.auth_service import AuthService

client = TestClient(app)


def _build_call_log(
    *,
    feature: str,
    subfeature: str | None,
    plan: str,
    timestamp: datetime,
    request_id: str,
    manifest_entry_id: str,
    validation_status: LlmValidationStatus = LlmValidationStatus.VALID,
    latency_ms: int = 400,
) -> LlmCallLogModel:
    import uuid

    return LlmCallLogModel(
        id=uuid.uuid4(),
        use_case=feature,
        feature=feature,
        subfeature=subfeature,
        plan=plan,
        provider="openai",
        model="gpt-4.1-mini",
        latency_ms=latency_ms,
        tokens_in=100,
        tokens_out=50,
        cost_usd_estimated=0.01,
        validation_status=validation_status,
        repair_attempted=False,
        fallback_triggered=False,
        request_id=request_id,
        trace_id=f"trace-{request_id}",
        input_hash=f"hash-{request_id}",
        environment="test",
        requested_provider="openai",
        resolved_provider="openai",
        executed_provider="openai",
        active_snapshot_version="release-2026-04",
        manifest_entry_id=manifest_entry_id,
        timestamp=timestamp,
    )


def _admin_token(email: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="admin123", role="admin")
        db.commit()
        return auth.tokens.access_token


def test_admin_consumption_endpoint_returns_canonical_aggregates() -> None:
    token = _admin_token("admin-consumption@example.com")
    with SessionLocal() as db:
        db.add(
            _build_call_log(
                feature="natal",
                subfeature="full",
                plan="premium",
                timestamp=datetime(2026, 4, 15, 12, 0, tzinfo=timezone.utc),
                request_id="req-admin-consumption",
                manifest_entry_id="natal:full:premium:fr-FR",
                validation_status=LlmValidationStatus.ERROR,
                latency_ms=650,
            )
        )
        db.commit()

    response = client.get(
        "/v1/admin/llm/consumption/canonical",
        params={"granularity": "day", "scope": "all", "refresh": "true"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["timezone"] == "UTC"
    assert payload["meta"]["refresh"] is True
    assert payload["meta"]["count"] >= 1
    first = payload["data"][0]
    assert first["feature"] == "natal"
    assert first["subscription_plan"] == "premium"
