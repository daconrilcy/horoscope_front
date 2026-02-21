from app.infra.observability.metrics import increment_counter, observe_duration, reset_metrics
from app.services.ops_monitoring_service import OpsMonitoringService, OpsMonitoringServiceError


def test_get_conversation_kpis_returns_zeroes_when_no_metrics() -> None:
    reset_metrics()

    data = OpsMonitoringService.get_conversation_kpis(window="24h")

    assert data.window == "24h"
    assert data.aggregation_scope == "instance_local"
    assert data.messages_total == 0
    assert data.out_of_scope_count == 0
    assert data.out_of_scope_rate == 0.0
    assert data.llm_error_count == 0
    assert data.llm_error_rate == 0.0
    assert data.p95_latency_ms == 0.0


def test_get_conversation_kpis_aggregates_rates_and_p95() -> None:
    reset_metrics()
    increment_counter("conversation_messages_total", 10)
    increment_counter("conversation_chat_messages_total", 10)
    increment_counter("conversation_out_of_scope_total", 2)
    increment_counter("conversation_llm_errors_total", 1)

    observe_duration("conversation_latency_seconds", 0.1)
    observe_duration("conversation_latency_seconds", 0.2)
    observe_duration("guidance_latency_seconds", 0.3)
    observe_duration("guidance_latency_seconds", 0.5)

    data = OpsMonitoringService.get_conversation_kpis(window="24h")

    assert data.messages_total == 10
    assert data.out_of_scope_count == 2
    assert data.out_of_scope_rate == 0.2
    assert data.llm_error_count == 1
    assert data.llm_error_rate == 0.1
    assert abs(data.p95_latency_ms - 470.0) < 1e-6


def test_get_conversation_kpis_invalid_window_raises() -> None:
    reset_metrics()

    try:
        OpsMonitoringService.get_conversation_kpis(window="3h")
    except OpsMonitoringServiceError as error:
        assert error.code == "invalid_monitoring_window"
    else:
        raise AssertionError("expected OpsMonitoringServiceError")


def test_get_operational_summary_returns_alerts_and_kpis() -> None:
    reset_metrics()
    increment_counter("http_requests_total|method=GET|route=/health|status_class=2xx", 100)
    increment_counter(
        "http_requests_server_errors_total|method=GET|route=/health|status_class=5xx", 4
    )
    increment_counter(
        "http_requests_client_errors_total|method=GET|route=/health|status_class=4xx", 10
    )
    observe_duration("http_request_duration_seconds|method=GET|route=/health|status_class=2xx", 0.2)
    observe_duration("http_request_duration_seconds|method=GET|route=/health|status_class=2xx", 1.4)
    increment_counter("quota_exceeded_total", 30)
    increment_counter("privacy_request_failures_total", 1)
    increment_counter("b2b_api_auth_failures_total", 12)

    data = OpsMonitoringService.get_operational_summary(window="24h")

    assert data.requests_total == 100
    assert data.errors_4xx_total == 10
    assert data.errors_5xx_total == 4
    assert abs(data.error_5xx_rate - 0.04) < 1e-9
    assert abs(data.availability_percent - 96.0) < 1e-9
    assert abs(data.p95_latency_ms - 1340.0) < 1e-6
    assert data.quota_exceeded_total == 30
    assert data.privacy_failures_total == 1
    assert data.b2b_auth_failures_total == 12

    alert_status = {alert.code: alert.status for alert in data.alerts}
    assert alert_status["availability_degraded"] == "firing"
    assert alert_status["error_rate_5xx_high"] == "firing"
    assert alert_status["latency_p95_high"] == "firing"
    assert alert_status["quota_exceeded_spike"] == "firing"
    assert alert_status["privacy_failures_detected"] == "firing"
    assert alert_status["b2b_auth_failures_spike"] == "firing"


def test_get_persona_kpis_returns_grouped_metrics() -> None:
    reset_metrics()
    increment_counter("conversation_messages_total|persona_profile=legacy-default", 10)
    increment_counter("conversation_guidance_messages_total|persona_profile=legacy-default", 4)
    increment_counter("conversation_llm_errors_total|persona_profile=legacy-default", 1)
    increment_counter("conversation_out_of_scope_total|persona_profile=legacy-default", 3)
    increment_counter("guidance_out_of_scope_total|persona_profile=legacy-default", 1)
    increment_counter("conversation_recovery_success_total|persona_profile=legacy-default", 2)
    increment_counter("guidance_recovery_success_total|persona_profile=legacy-default", 1)
    observe_duration("conversation_latency_seconds|persona_profile=legacy-default", 0.1)
    observe_duration("guidance_latency_seconds|persona_profile=legacy-default", 0.4)

    increment_counter("conversation_messages_total|persona_profile=sage-astro", 5)
    increment_counter("conversation_guidance_messages_total|persona_profile=sage-astro", 2)
    increment_counter("conversation_llm_errors_total|persona_profile=sage-astro", 0)
    increment_counter("conversation_out_of_scope_total|persona_profile=sage-astro", 2)
    increment_counter("guidance_recovery_success_total|persona_profile=sage-astro", 1)
    observe_duration("conversation_latency_seconds|persona_profile=sage-astro", 0.2)
    observe_duration("guidance_latency_seconds|persona_profile=sage-astro", 0.3)

    data = OpsMonitoringService.get_persona_kpis(window="24h")
    assert data.window == "24h"
    assert data.aggregation_scope == "instance_local"
    assert len(data.personas) == 2
    by_code = {item.persona_profile_code: item for item in data.personas}
    assert by_code["legacy-default"].messages_total == 10
    assert by_code["legacy-default"].guidance_messages_total == 4
    assert by_code["legacy-default"].out_of_scope_count == 4
    assert by_code["legacy-default"].recovery_success_count == 3
    assert by_code["legacy-default"].recovery_success_rate == 0.75
    assert by_code["legacy-default"].llm_error_count == 1
    assert by_code["legacy-default"].llm_error_rate == 0.1
    assert by_code["sage-astro"].messages_total == 5
    assert by_code["sage-astro"].guidance_messages_total == 2
    assert by_code["sage-astro"].out_of_scope_count == 2
    assert by_code["sage-astro"].recovery_success_count == 1
    assert by_code["sage-astro"].recovery_success_rate == 0.5
    assert by_code["sage-astro"].llm_error_count == 0
