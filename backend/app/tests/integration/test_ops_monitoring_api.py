from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.infra.observability.metrics import increment_counter, observe_duration, reset_metrics
from app.main import app
from app.services.auth_service import AuthService

client = TestClient(app)


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    reset_metrics()
    with SessionLocal() as db:
        db.execute(delete(UserModel))
        db.commit()


def _register_user_with_role_and_token(email: str, role: str) -> str:
    with SessionLocal() as db:
        auth = AuthService.register(db, email=email, password="strong-pass-123", role=role)
        db.commit()
        return auth.tokens.access_token


def _activate_entry_plan(access_token: str, idempotency_key: str) -> None:
    response = client.post(
        "/v1/billing/checkout",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "plan_code": "basic-entry",
            "payment_method_token": "pm_card_ok",
            "idempotency_key": idempotency_key,
        },
    )
    assert response.status_code == 200


def _seed_birth_profile(access_token: str) -> None:
    response = client.put(
        "/v1/users/me/birth-data",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "birth_date": "1990-06-15",
            "birth_time": "10:30",
            "birth_place": "Paris",
            "birth_timezone": "Europe/Paris",
        },
    )
    assert response.status_code == 200


def test_ops_monitoring_requires_token() -> None:
    _cleanup_tables()
    response = client.get("/v1/ops/monitoring/conversation-kpis")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_access_token"


def test_ops_monitoring_forbidden_for_non_ops_role() -> None:
    _cleanup_tables()
    support_token = _register_user_with_role_and_token("monitoring-support@example.com", "support")
    response = client.get(
        "/v1/ops/monitoring/conversation-kpis",
        headers={"Authorization": f"Bearer {support_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"


def test_ops_monitoring_returns_kpis_for_ops_role() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("monitoring-ops@example.com", "ops")

    increment_counter("conversation_messages_total", 20)
    increment_counter("conversation_chat_messages_total", 20)
    increment_counter("conversation_out_of_scope_total", 3)
    increment_counter("conversation_llm_errors_total", 2)
    observe_duration("conversation_latency_seconds", 0.1)
    observe_duration("conversation_latency_seconds", 0.4)
    observe_duration("guidance_latency_seconds", 0.2)

    response = client.get(
        "/v1/ops/monitoring/conversation-kpis",
        params={"window": "24h"},
        headers={
            "Authorization": f"Bearer {ops_token}",
            "X-Request-Id": "rid-monitoring-ok",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["request_id"] == "rid-monitoring-ok"
    assert payload["data"]["window"] == "24h"
    assert payload["data"]["aggregation_scope"] == "instance_local"
    assert payload["data"]["messages_total"] == 20
    assert payload["data"]["out_of_scope_count"] == 3
    assert payload["data"]["llm_error_count"] == 2
    assert payload["data"]["p95_latency_ms"] == 380.0


def test_ops_monitoring_invalid_window_returns_422() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("monitoring-invalid@example.com", "ops")
    response = client.get(
        "/v1/ops/monitoring/conversation-kpis",
        params={"window": "3h"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_monitoring_window"


def test_ops_monitoring_returns_429_when_rate_limited(monkeypatch: object) -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("monitoring-429@example.com", "ops")
    headers = {"Authorization": f"Bearer {ops_token}", "X-Request-Id": "rid-monitoring-429"}

    def _always_rate_limited(*args: object, **kwargs: object) -> None:
        from app.core.rate_limit import RateLimitError

        raise RateLimitError(
            code="rate_limit_exceeded",
            message="rate limit exceeded",
            details={"retry_after": "7"},
            status_code=429,
        )

    monkeypatch.setattr("app.api.v1.routers.ops_monitoring.check_rate_limit", _always_rate_limited)

    response = client.get("/v1/ops/monitoring/conversation-kpis", headers=headers)
    assert response.status_code == 429
    payload = response.json()["error"]
    assert payload["code"] == "rate_limit_exceeded"
    assert payload["request_id"] == "rid-monitoring-429"


def test_ops_monitoring_operational_summary_returns_data_for_ops_role() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("monitoring-summary@example.com", "ops")

    increment_counter("http_requests_total|method=GET|route=/health|status_class=2xx", 40)
    increment_counter(
        "http_requests_server_errors_total|method=GET|route=/health|status_class=5xx", 1
    )
    observe_duration(
        "http_request_duration_seconds|method=GET|route=/health|status_class=2xx", 0.15
    )
    observe_duration("http_request_duration_seconds|method=GET|route=/health|status_class=2xx", 0.5)
    increment_counter("quota_exceeded_total", 3)

    response = client.get(
        "/v1/ops/monitoring/operational-summary",
        params={"window": "24h"},
        headers={
            "Authorization": f"Bearer {ops_token}",
            "X-Request-Id": "rid-monitoring-summary",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["request_id"] == "rid-monitoring-summary"
    assert payload["data"]["window"] == "24h"
    assert payload["data"]["requests_total"] == 40
    assert payload["data"]["errors_5xx_total"] == 1
    assert payload["data"]["quota_exceeded_total"] == 3
    assert len(payload["data"]["alerts"]) >= 1


def test_ops_monitoring_persona_kpis_returns_data_for_ops_role() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("monitoring-persona@example.com", "ops")

    increment_counter("conversation_messages_total|persona_profile=legacy-default", 7)
    increment_counter("conversation_guidance_messages_total|persona_profile=legacy-default", 3)
    increment_counter("conversation_llm_errors_total|persona_profile=legacy-default", 1)
    increment_counter("conversation_out_of_scope_total|persona_profile=legacy-default", 2)
    increment_counter("guidance_out_of_scope_total|persona_profile=legacy-default", 1)
    increment_counter("conversation_recovery_success_total|persona_profile=legacy-default", 2)
    increment_counter("guidance_recovery_success_total|persona_profile=legacy-default", 1)
    observe_duration("conversation_latency_seconds|persona_profile=legacy-default", 0.1)
    observe_duration("guidance_latency_seconds|persona_profile=legacy-default", 0.4)

    response = client.get(
        "/v1/ops/monitoring/persona-kpis",
        params={"window": "24h"},
        headers={
            "Authorization": f"Bearer {ops_token}",
            "X-Request-Id": "rid-monitoring-persona",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["request_id"] == "rid-monitoring-persona"
    assert payload["data"]["window"] == "24h"
    assert payload["data"]["aggregation_scope"] == "instance_local"
    personas = payload["data"]["personas"]
    assert len(personas) == 1
    assert personas[0]["persona_profile_code"] == "legacy-default"
    assert personas[0]["messages_total"] == 7
    assert personas[0]["guidance_messages_total"] == 3
    assert personas[0]["out_of_scope_count"] == 3
    assert personas[0]["recovery_success_count"] == 3
    assert personas[0]["recovery_success_rate"] == 1.0
    assert personas[0]["llm_error_count"] == 1
    assert personas[0]["llm_error_rate"] == (1 / 7)


def test_ops_monitoring_persona_kpis_invalid_window_returns_422() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("monitoring-persona-invalid@example.com", "ops")

    response = client.get(
        "/v1/ops/monitoring/persona-kpis",
        params={"window": "3h"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_monitoring_window"


def test_ops_monitoring_persona_kpis_reflect_live_chat_and_guidance_flows() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("monitoring-persona-live-ops@example.com", "ops")
    user_token = _register_user_with_role_and_token(
        "monitoring-persona-live-user@example.com",
        "user",
    )

    _activate_entry_plan(user_token, "monitoring-persona-live-checkout-1")
    _seed_birth_profile(user_token)

    chat_response = client.post(
        "/v1/chat/messages",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"message": "Bonjour, quelle tendance du jour ?"},
    )
    assert chat_response.status_code == 200

    guidance_response = client.post(
        "/v1/guidance",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"period": "daily"},
    )
    assert guidance_response.status_code == 200

    monitoring_response = client.get(
        "/v1/ops/monitoring/persona-kpis",
        params={"window": "24h"},
        headers={
            "Authorization": f"Bearer {ops_token}",
            "X-Request-Id": "rid-monitoring-persona-live",
        },
    )
    assert monitoring_response.status_code == 200
    payload = monitoring_response.json()
    assert payload["meta"]["request_id"] == "rid-monitoring-persona-live"

    by_code = {item["persona_profile_code"]: item for item in payload["data"]["personas"]}
    assert "legacy-default" in by_code
    persona = by_code["legacy-default"]
    assert persona["messages_total"] >= 2
    assert persona["guidance_messages_total"] >= 1
    assert "out_of_scope_count" in persona
    assert "recovery_success_count" in persona
    assert "recovery_success_rate" in persona


def test_ops_monitoring_pricing_experiment_kpis_returns_data_for_ops_role() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token("monitoring-pricing@example.com", "ops")
    user_token = _register_user_with_role_and_token("monitoring-pricing-user@example.com", "user")

    checkout_response = client.post(
        "/v1/billing/checkout",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "plan_code": "basic-entry",
            "payment_method_token": "pm_card_ok",
            "idempotency_key": "monitoring-pricing-checkout-1",
        },
    )
    assert checkout_response.status_code == 200

    subscription_response = client.get(
        "/v1/billing/subscription",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert subscription_response.status_code == 200

    response = client.get(
        "/v1/ops/monitoring/pricing-experiments-kpis",
        params={"window": "24h"},
        headers={
            "Authorization": f"Bearer {ops_token}",
            "X-Request-Id": "rid-monitoring-pricing",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["request_id"] == "rid-monitoring-pricing"
    assert payload["data"]["window"] == "24h"
    assert payload["data"]["aggregation_scope"] == "database_persistent"
    assert len(payload["data"]["variants"]) == 1
    variant = payload["data"]["variants"][0]
    assert variant["variant_id"] in {"control", "value_plus"}
    assert variant["exposures_total"] == 1
    assert variant["conversions_total"] == 1
    assert variant["revenue_cents_total"] == 500
    assert variant["retention_events_total"] >= 1


def test_ops_monitoring_pricing_experiment_kpis_invalid_window_returns_422() -> None:
    _cleanup_tables()
    ops_token = _register_user_with_role_and_token(
        "monitoring-pricing-invalid@example.com",
        "ops",
    )

    response = client.get(
        "/v1/ops/monitoring/pricing-experiments-kpis",
        params={"window": "3h"},
        headers={"Authorization": f"Bearer {ops_token}"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_monitoring_window"
