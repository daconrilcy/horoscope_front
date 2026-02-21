from sqlalchemy import delete

from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.session import SessionLocal
from app.infra.observability.metrics import increment_counter, observe_duration, reset_metrics
from app.services.audit_service import AuditEventCreatePayload, AuditService
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


def test_get_pricing_experiment_kpis_returns_variant_aggregates() -> None:
    reset_metrics()
    increment_counter(
        "pricing_experiment_exposure_total|plan_code=basic-entry|user_segment=user|variant_id=control",
        40,
    )
    increment_counter(
        "pricing_experiment_exposure_total|plan_code=basic-entry|user_segment=user|variant_id=value_plus",
        20,
    )
    increment_counter(
        (
            "pricing_experiment_conversion_total|conversion_type=checkout|plan_code=basic-entry|"
            "status=success|user_segment=user|variant_id=control"
        ),
        8,
    )
    increment_counter(
        (
            "pricing_experiment_conversion_total|conversion_type=checkout|plan_code=basic-entry|"
            "status=failed|user_segment=user|variant_id=control"
        ),
        2,
    )
    increment_counter(
        (
            "pricing_experiment_conversion_total|conversion_type=checkout|plan_code=basic-entry|"
            "status=success|user_segment=user|variant_id=value_plus"
        ),
        3,
    )
    increment_counter(
        (
            "pricing_experiment_revenue_cents_total|plan_code=basic-entry|user_segment=user|"
            "variant_id=control"
        ),
        4000,
    )
    increment_counter(
        (
            "pricing_experiment_revenue_cents_total|plan_code=basic-entry|user_segment=user|"
            "variant_id=value_plus"
        ),
        1500,
    )
    increment_counter(
        (
            "pricing_experiment_retention_usage_total|plan_code=basic-entry|"
            "retention_event=quota_status_view|user_segment=user|variant_id=control"
        ),
        12,
    )

    data = OpsMonitoringService.get_pricing_experiment_kpis(window="24h")
    assert data.window == "24h"
    assert data.aggregation_scope == "instance_local"
    assert len(data.variants) == 2
    by_variant = {item.variant_id: item for item in data.variants}
    assert by_variant["control"].exposures_total == 40
    assert by_variant["control"].conversions_total == 8
    assert by_variant["control"].conversion_rate == 0.2
    assert by_variant["control"].retention_events_total == 12
    assert by_variant["control"].revenue_cents_total == 4000
    assert by_variant["control"].avg_revenue_per_conversion_cents == 500.0
    assert by_variant["control"].sample_size_is_low is True

    assert by_variant["value_plus"].exposures_total == 20
    assert by_variant["value_plus"].conversions_total == 3
    assert by_variant["value_plus"].conversion_rate == 0.15


def test_get_pricing_experiment_kpis_rounds_metric_values_before_aggregation() -> None:
    reset_metrics()
    increment_counter(
        "pricing_experiment_exposure_total|plan_code=basic-entry|user_segment=user|variant_id=control",
        10.6,
    )
    increment_counter(
        (
            "pricing_experiment_conversion_total|conversion_type=checkout|plan_code=basic-entry|"
            "status=success|user_segment=user|variant_id=control"
        ),
        2.4,
    )

    data = OpsMonitoringService.get_pricing_experiment_kpis(window="24h")
    control = next(item for item in data.variants if item.variant_id == "control")
    assert control.exposures_total == 11
    assert control.conversions_total == 2


def test_get_pricing_experiment_kpis_uses_database_persistent_events() -> None:
    reset_metrics()
    with SessionLocal() as db:
        db.execute(
            delete(AuditEventModel).where(
                AuditEventModel.action == "pricing_experiment_event"
            )
        )
        AuditService.record_event(
            db,
            payload=AuditEventCreatePayload(
                request_id="rid-pricing-1",
                actor_user_id=1,
                actor_role="user",
                action="pricing_experiment_event",
                target_type="pricing_experiment",
                target_id="control",
                status="success",
                details={
                    "event_name": "offer_exposure",
                    "variant_id": "control",
                    "user_segment": "user",
                    "plan_code": "basic-entry",
                    "event_version": "1.0",
                },
            ),
        )
        AuditService.record_event(
            db,
            payload=AuditEventCreatePayload(
                request_id="rid-pricing-2",
                actor_user_id=1,
                actor_role="user",
                action="pricing_experiment_event",
                target_type="pricing_experiment",
                target_id="control",
                status="success",
                details={
                    "event_name": "offer_conversion",
                    "variant_id": "control",
                    "conversion_status": "success",
                    "user_segment": "user",
                    "plan_code": "basic-entry",
                    "event_version": "1.0",
                },
            ),
        )
        db.commit()

        data = OpsMonitoringService.get_pricing_experiment_kpis(window="24h", db=db)

    assert data.aggregation_scope == "database_persistent"
    assert len(data.variants) == 1
    variant = data.variants[0]
    assert variant.variant_id == "control"
    assert variant.exposures_total == 1
    assert variant.conversions_total == 1


def test_get_pricing_experiment_kpis_falls_back_when_db_has_no_events() -> None:
    reset_metrics()
    increment_counter(
        "pricing_experiment_exposure_total|plan_code=basic-entry|user_segment=user|variant_id=control",
        3,
    )
    with SessionLocal() as db:
        db.execute(
            delete(AuditEventModel).where(
                AuditEventModel.action == "pricing_experiment_event"
            )
        )
        db.commit()
        data = OpsMonitoringService.get_pricing_experiment_kpis(window="24h", db=db)

    assert data.aggregation_scope == "instance_local_fallback"
    assert len(data.variants) == 1
    assert data.variants[0].variant_id == "control"
    assert data.variants[0].exposures_total == 3
