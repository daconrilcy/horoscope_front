import json
import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.llm.llm_observability import LlmCallLogModel
from app.infra.db.models.llm.llm_persona import LlmPersonaModel
from app.infra.db.session import SessionLocal, engine
from app.main import app
from app.services.auth_service import AuthService

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(LlmCallLogModel))
        db.execute(delete(LlmPersonaModel))
        db.commit()


def _register_user_with_role_and_token(email: str, role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token


def _seed_persona(name: str = "Astrologue Standard") -> uuid.UUID:
    with SessionLocal() as db:
        persona = LlmPersonaModel(id=uuid.uuid4(), name=name)
        db.add(persona)
        db.commit()
        return persona.id


def _build_log(**overrides: object) -> LlmCallLogModel:
    now = datetime.now(timezone.utc)
    defaults: dict[str, object] = {
        "id": uuid.uuid4(),
        "use_case": "chat_astrologer",
        "feature": "chat",
        "plan": "free",
        "model": "gpt-4o",
        "latency_ms": 500,
        "tokens_in": 100,
        "tokens_out": 200,
        "cost_usd_estimated": 0.005,
        "validation_status": "valid",
        "repair_attempted": False,
        "fallback_triggered": False,
        "request_id": f"req-{uuid.uuid4()}",
        "trace_id": f"trace-{uuid.uuid4()}",
        "input_hash": f"hash-{uuid.uuid4()}",
        "environment": "test",
        "pipeline_kind": "nominal_canonical",
        "execution_path_kind": "canonical_assembly",
        "requested_provider": "openai",
        "resolved_provider": "openai",
        "executed_provider": "openai",
        "context_quality": "full",
        "max_output_tokens_source": "length_budget_global",
        "active_snapshot_id": uuid.uuid4(),
        "active_snapshot_version": "release-2026-04-13",
        "manifest_entry_id": "manifest-entry-1",
        "timestamp": now - timedelta(minutes=5),
    }
    defaults.update(overrides)
    return LlmCallLogModel(**defaults)


def test_llm_ops_dashboard_requires_ops_role() -> None:
    _cleanup_tables()
    user_token = _register_user_with_role_and_token("llm-ops-user@example.com", "user")

    response = client.get(
        "/v1/ops/monitoring/llm/dashboard",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 403


def test_llm_ops_dashboard_exposes_canonical_views_and_release_correlation() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("llm-ops@example.com", "ops")
    persona_id = _seed_persona()
    snapshot_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            _build_log(
                persona_id=persona_id,
                active_snapshot_id=snapshot_id,
                active_snapshot_version="release-a",
                manifest_entry_id="manifest-a",
            )
        )
        db.add(
            _build_log(
                feature="guidance",
                use_case="guidance",
                model="claude-3-sonnet",
                latency_ms=1200,
                requested_provider="openai",
                resolved_provider="anthropic",
                executed_provider="anthropic",
                context_quality="partial",
                max_output_tokens_source="execution_profile",
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=2),
            )
        )
        db.commit()

    response = client.get(
        "/v1/ops/monitoring/llm/dashboard",
        params={"window": "1h"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    dashboards = payload["dashboards"]

    assert "family" in dashboards
    assert "persona" in dashboards
    assert "snapshot_id" in dashboards
    assert "family_execution_path" in dashboards
    assert "family_fallback" in dashboards
    assert "family_provider_triplet" in dashboards
    assert "family_context_quality" in dashboards
    assert "family_max_tokens_source" in dashboards

    persona_metrics = dashboards["persona"]
    assert len(persona_metrics) == 2
    persona_entry = next(item for item in persona_metrics if item["value"] == str(persona_id))
    assert persona_entry["display_value"] == "Astrologue Standard"

    snapshot_values = {item["value"] for item in dashboards["snapshot_id"]}
    assert str(snapshot_id) in snapshot_values

    triplet_values = {item["value"] for item in dashboards["family_provider_triplet"]}
    assert "guidance:openai:anthropic:anthropic" in triplet_values

    quality_values = {item["value"] for item in dashboards["family_context_quality"]}
    assert "chat:full" in quality_values
    assert "guidance:partial" in quality_values

    token_source_values = {item["value"] for item in dashboards["family_max_tokens_source"]}
    assert "chat:length_budget_global" in token_source_values
    assert "guidance:execution_profile" in token_source_values

    alerts = {item["code"]: item for item in payload["alerts"]}
    divergence_alert = alerts["llm_provider_divergence"]
    assert divergence_alert["labels"]["requested"] == "openai"
    assert divergence_alert["labels"]["resolved"] == "anthropic"
    assert divergence_alert["labels"]["executed"] == "anthropic"
    assert "requested_vs_resolved" in divergence_alert["labels"]["divergence_types"]


def test_llm_ops_repair_hike_uses_previous_window_baseline_and_canonical_persona_label() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("llm-ops-repair@example.com", "ops")
    persona_id = _seed_persona("Persona Repair")
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        for index in range(40):
            db.add(
                _build_log(
                    persona_id=persona_id,
                    timestamp=now - timedelta(hours=2) + timedelta(minutes=index),
                    validation_status="repair_success" if index == 0 else "valid",
                    repair_attempted=index == 0,
                )
            )
        for index in range(15):
            db.add(
                _build_log(
                    persona_id=persona_id,
                    timestamp=now - timedelta(minutes=30) + timedelta(seconds=index),
                    validation_status="repair_success" if index < 4 else "valid",
                    repair_attempted=index < 4,
                )
            )
        db.commit()

    response = client.get(
        "/v1/ops/monitoring/llm/dashboard",
        params={"window": "1h"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    alerts = [
        item for item in response.json()["data"]["alerts"] if item["code"] == "llm_repair_rate_hike"
    ]
    assert len(alerts) == 1
    alert = alerts[0]
    assert alert["labels"]["persona"] == str(persona_id)
    assert "baseline: 2.5%" in alert["message"]


def test_llm_ops_unknown_path_alert_and_payload_is_safe() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("llm-ops-unknown@example.com", "ops")

    with SessionLocal() as db:
        db.add(
            _build_log(
                feature="natal",
                use_case="natal",
                execution_path_kind="unknown",
                context_quality="minimal",
                max_output_tokens_source="verbosity_fallback",
            )
        )
        db.add(
            _build_log(
                feature="natal",
                use_case="natal",
                execution_path_kind="legacy_use_case_fallback",
                fallback_kind="legacy_wrapper",
                fallback_triggered=True,
            )
        )
        db.commit()

    response = client.get(
        "/v1/ops/monitoring/llm/dashboard",
        params={"window": "1h"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    alerts = {item["code"]: item for item in payload["alerts"]}

    assert "llm_unknown_path_violation" in alerts
    assert alerts["llm_unknown_path_violation"]["labels"]["pipeline"] == "nominal_canonical"
    assert "llm_impossible_state_detected" in alerts

    serialized = json.dumps(payload)
    assert "raw_output" not in serialized
    assert "structured_output" not in serialized
    assert "prompt" not in serialized
    assert "user_input" not in serialized
