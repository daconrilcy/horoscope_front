from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.observability.metrics import (
    get_counter_sum_in_window,
    get_counter_sums_by_prefix_in_window,
    get_duration_values_by_prefix_in_window,
    get_duration_values_in_window,
)

WINDOWS: dict[str, timedelta] = {
    "1h": timedelta(hours=1),
    "24h": timedelta(hours=24),
    "7d": timedelta(days=7),
}


class OpsMonitoringServiceError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class OpsMonitoringKpisData(BaseModel):
    window: str
    aggregation_scope: str
    messages_total: int
    out_of_scope_count: int
    out_of_scope_rate: float
    llm_error_count: int
    llm_error_rate: float
    p95_latency_ms: float


class OpsMonitoringAlertData(BaseModel):
    code: str
    severity: str
    status: str
    message: str
    context: dict[str, float | str]


class OpsMonitoringOperationalSummaryData(BaseModel):
    window: str
    aggregation_scope: str
    requests_total: int
    errors_4xx_total: int
    errors_5xx_total: int
    error_5xx_rate: float
    availability_percent: float
    p95_latency_ms: float
    quota_exceeded_total: int
    privacy_failures_total: int
    b2b_auth_failures_total: int
    alerts: list[OpsMonitoringAlertData]


class OpsMonitoringPersonaKpisItem(BaseModel):
    persona_profile_code: str
    messages_total: int
    guidance_messages_total: int
    out_of_scope_count: int
    recovery_success_count: int
    recovery_success_rate: float
    llm_error_count: int
    llm_error_rate: float
    p95_latency_ms: float


class OpsMonitoringPersonaKpisData(BaseModel):
    window: str
    aggregation_scope: str
    personas: list[OpsMonitoringPersonaKpisItem]


class OpsMonitoringPricingKpisVariantItem(BaseModel):
    variant_id: str
    exposures_total: int
    conversions_total: int
    conversion_rate: float
    retention_events_total: int
    revenue_cents_total: int
    avg_revenue_per_conversion_cents: float
    sample_size_is_low: bool


class OpsMonitoringPricingKpisData(BaseModel):
    window: str
    aggregation_scope: str
    min_sample_size: int
    variants: list[OpsMonitoringPricingKpisVariantItem]


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return float(values[0])
    normalized = sorted(values)
    position = (len(normalized) - 1) * max(0.0, min(1.0, q))
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(normalized) - 1)
    if lower_index == upper_index:
        return float(normalized[lower_index])
    fraction = position - lower_index
    lower = normalized[lower_index]
    upper = normalized[upper_index]
    return float(lower + (upper - lower) * fraction)


class OpsMonitoringService:
    @staticmethod
    def _variant_from_metric_name(metric_name: str) -> str | None:
        marker = "variant_id="
        if marker not in metric_name:
            return None
        return metric_name.split(marker, 1)[1].split("|", 1)[0]

    @staticmethod
    def _aggregate_by_variant(
        metric_values: dict[str, float],
        *,
        success_only: bool = False,
    ) -> dict[str, int]:
        totals: dict[str, int] = {}
        for metric_name, value in metric_values.items():
            variant = OpsMonitoringService._variant_from_metric_name(metric_name)
            if variant is None:
                continue
            if success_only and "|status=success" not in metric_name:
                continue
            normalized_value = max(0, int(round(value)))
            totals[variant] = totals.get(variant, 0) + normalized_value
        return totals

    @staticmethod
    def get_conversation_kpis(*, window: str) -> OpsMonitoringKpisData:
        selected_window = window.strip().lower()
        if selected_window not in WINDOWS:
            raise OpsMonitoringServiceError(
                code="invalid_monitoring_window",
                message="monitoring window is invalid",
                details={"supported_windows": "1h,24h,7d"},
            )

        duration = WINDOWS[selected_window]
        messages_total = int(get_counter_sum_in_window("conversation_messages_total", duration))
        chat_messages_total = int(
            get_counter_sum_in_window("conversation_chat_messages_total", duration)
        )
        out_of_scope_count = int(
            get_counter_sum_in_window("conversation_out_of_scope_total", duration)
        )
        llm_error_count = int(get_counter_sum_in_window("conversation_llm_errors_total", duration))

        out_of_scope_rate = (
            out_of_scope_count / chat_messages_total if chat_messages_total > 0 else 0.0
        )
        llm_error_rate = (llm_error_count / messages_total) if messages_total > 0 else 0.0

        chat_latency = get_duration_values_in_window("conversation_latency_seconds", duration)
        guidance_latency = get_duration_values_in_window("guidance_latency_seconds", duration)
        all_latency = chat_latency + guidance_latency
        p95_latency_ms = _percentile(all_latency, 0.95) * 1000.0

        return OpsMonitoringKpisData(
            window=selected_window,
            aggregation_scope="instance_local",
            messages_total=messages_total,
            out_of_scope_count=out_of_scope_count,
            out_of_scope_rate=out_of_scope_rate,
            llm_error_count=llm_error_count,
            llm_error_rate=llm_error_rate,
            p95_latency_ms=p95_latency_ms,
        )

    @staticmethod
    def get_operational_summary(*, window: str) -> OpsMonitoringOperationalSummaryData:
        selected_window = window.strip().lower()
        if selected_window not in WINDOWS:
            raise OpsMonitoringServiceError(
                code="invalid_monitoring_window",
                message="monitoring window is invalid",
                details={"supported_windows": "1h,24h,7d"},
            )

        duration = WINDOWS[selected_window]
        request_counts = get_counter_sums_by_prefix_in_window("http_requests_total|", duration)
        error_4xx_counts = get_counter_sums_by_prefix_in_window(
            "http_requests_client_errors_total|", duration
        )
        error_5xx_counts = get_counter_sums_by_prefix_in_window(
            "http_requests_server_errors_total|", duration
        )

        latency_map = get_duration_values_by_prefix_in_window(
            "http_request_duration_seconds|", duration
        )
        latency_values = [value for values in latency_map.values() for value in values]

        requests_total = int(sum(request_counts.values()))
        errors_4xx_total = int(sum(error_4xx_counts.values()))
        errors_5xx_total = int(sum(error_5xx_counts.values()))
        error_5xx_rate = (errors_5xx_total / requests_total) if requests_total > 0 else 0.0
        availability_percent = (
            ((requests_total - errors_5xx_total) / requests_total) * 100.0
            if requests_total > 0
            else 100.0
        )
        p95_latency_ms = _percentile(latency_values, 0.95) * 1000.0

        quota_exceeded_total = int(
            get_counter_sum_in_window("quota_exceeded_total", duration)
            + get_counter_sum_in_window("b2b_quota_exceeded_total", duration)
        )
        privacy_failures_total = int(
            get_counter_sum_in_window("privacy_request_failures_total", duration)
        )
        b2b_auth_failures_total = int(
            get_counter_sum_in_window("b2b_api_auth_failures_total", duration)
        )

        alerts = OpsMonitoringService._build_alerts(
            window=selected_window,
            availability_percent=availability_percent,
            error_5xx_rate=error_5xx_rate,
            p95_latency_ms=p95_latency_ms,
            quota_exceeded_total=quota_exceeded_total,
            privacy_failures_total=privacy_failures_total,
            b2b_auth_failures_total=b2b_auth_failures_total,
        )

        return OpsMonitoringOperationalSummaryData(
            window=selected_window,
            aggregation_scope="instance_local",
            requests_total=requests_total,
            errors_4xx_total=errors_4xx_total,
            errors_5xx_total=errors_5xx_total,
            error_5xx_rate=error_5xx_rate,
            availability_percent=availability_percent,
            p95_latency_ms=p95_latency_ms,
            quota_exceeded_total=quota_exceeded_total,
            privacy_failures_total=privacy_failures_total,
            b2b_auth_failures_total=b2b_auth_failures_total,
            alerts=alerts,
        )

    @staticmethod
    def get_persona_kpis(*, window: str) -> OpsMonitoringPersonaKpisData:
        selected_window = window.strip().lower()
        if selected_window not in WINDOWS:
            raise OpsMonitoringServiceError(
                code="invalid_monitoring_window",
                message="monitoring window is invalid",
                details={"supported_windows": "1h,24h,7d"},
            )
        duration = WINDOWS[selected_window]
        messages_by_persona = get_counter_sums_by_prefix_in_window(
            "conversation_messages_total|persona_profile=",
            duration,
        )
        guidance_messages_by_persona = get_counter_sums_by_prefix_in_window(
            "conversation_guidance_messages_total|persona_profile=",
            duration,
        )
        llm_errors_by_persona = get_counter_sums_by_prefix_in_window(
            "conversation_llm_errors_total|persona_profile=",
            duration,
        )
        chat_out_of_scope_by_persona = get_counter_sums_by_prefix_in_window(
            "conversation_out_of_scope_total|persona_profile=",
            duration,
        )
        guidance_out_of_scope_by_persona = get_counter_sums_by_prefix_in_window(
            "guidance_out_of_scope_total|persona_profile=",
            duration,
        )
        chat_recovery_success_by_persona = get_counter_sums_by_prefix_in_window(
            "conversation_recovery_success_total|persona_profile=",
            duration,
        )
        guidance_recovery_success_by_persona = get_counter_sums_by_prefix_in_window(
            "guidance_recovery_success_total|persona_profile=",
            duration,
        )
        chat_latency_by_persona = get_duration_values_by_prefix_in_window(
            "conversation_latency_seconds|persona_profile=",
            duration,
        )
        guidance_latency_by_persona = get_duration_values_by_prefix_in_window(
            "guidance_latency_seconds|persona_profile=",
            duration,
        )

        persona_codes = set()
        for metric_name in messages_by_persona:
            persona_codes.add(metric_name.split("persona_profile=", 1)[1])
        for metric_name in guidance_messages_by_persona:
            persona_codes.add(metric_name.split("persona_profile=", 1)[1])
        for metric_name in llm_errors_by_persona:
            persona_codes.add(metric_name.split("persona_profile=", 1)[1])
        for metric_name in chat_out_of_scope_by_persona:
            persona_codes.add(metric_name.split("persona_profile=", 1)[1])
        for metric_name in guidance_out_of_scope_by_persona:
            persona_codes.add(metric_name.split("persona_profile=", 1)[1])
        for metric_name in chat_recovery_success_by_persona:
            persona_codes.add(metric_name.split("persona_profile=", 1)[1])
        for metric_name in guidance_recovery_success_by_persona:
            persona_codes.add(metric_name.split("persona_profile=", 1)[1])
        for metric_name in chat_latency_by_persona:
            persona_codes.add(metric_name.split("persona_profile=", 1)[1])
        for metric_name in guidance_latency_by_persona:
            persona_codes.add(metric_name.split("persona_profile=", 1)[1])

        items: list[OpsMonitoringPersonaKpisItem] = []
        for persona_code in sorted(persona_codes):
            messages_metric = f"conversation_messages_total|persona_profile={persona_code}"
            guidance_metric = f"conversation_guidance_messages_total|persona_profile={persona_code}"
            errors_metric = f"conversation_llm_errors_total|persona_profile={persona_code}"
            chat_out_scope_metric = (
                f"conversation_out_of_scope_total|persona_profile={persona_code}"
            )
            guidance_out_scope_metric = (
                f"guidance_out_of_scope_total|persona_profile={persona_code}"
            )
            chat_recovery_success_metric = (
                f"conversation_recovery_success_total|persona_profile={persona_code}"
            )
            guidance_recovery_success_metric = (
                f"guidance_recovery_success_total|persona_profile={persona_code}"
            )
            chat_latency_metric = f"conversation_latency_seconds|persona_profile={persona_code}"
            guidance_latency_metric = f"guidance_latency_seconds|persona_profile={persona_code}"
            messages_total = int(messages_by_persona.get(messages_metric, 0.0))
            guidance_messages_total = int(guidance_messages_by_persona.get(guidance_metric, 0.0))
            llm_error_count = int(llm_errors_by_persona.get(errors_metric, 0.0))
            out_of_scope_count = int(
                chat_out_of_scope_by_persona.get(chat_out_scope_metric, 0.0)
                + guidance_out_of_scope_by_persona.get(guidance_out_scope_metric, 0.0)
            )
            recovery_success_count = int(
                chat_recovery_success_by_persona.get(chat_recovery_success_metric, 0.0)
                + guidance_recovery_success_by_persona.get(guidance_recovery_success_metric, 0.0)
            )
            all_latency_values = chat_latency_by_persona.get(
                chat_latency_metric, []
            ) + guidance_latency_by_persona.get(guidance_latency_metric, [])
            llm_error_rate = (llm_error_count / messages_total) if messages_total > 0 else 0.0
            recovery_success_rate = (
                recovery_success_count / out_of_scope_count if out_of_scope_count > 0 else 0.0
            )
            items.append(
                OpsMonitoringPersonaKpisItem(
                    persona_profile_code=persona_code,
                    messages_total=messages_total,
                    guidance_messages_total=guidance_messages_total,
                    out_of_scope_count=out_of_scope_count,
                    recovery_success_count=recovery_success_count,
                    recovery_success_rate=recovery_success_rate,
                    llm_error_count=llm_error_count,
                    llm_error_rate=llm_error_rate,
                    p95_latency_ms=_percentile(all_latency_values, 0.95) * 1000.0,
                )
            )

        return OpsMonitoringPersonaKpisData(
            window=selected_window,
            aggregation_scope="instance_local",
            personas=items,
        )

    @staticmethod
    def get_pricing_experiment_kpis(
        *,
        window: str,
        db: Session | None = None,
    ) -> OpsMonitoringPricingKpisData:
        selected_window = window.strip().lower()
        if selected_window not in WINDOWS:
            raise OpsMonitoringServiceError(
                code="invalid_monitoring_window",
                message="monitoring window is invalid",
                details={"supported_windows": "1h,24h,7d"},
            )

        duration = WINDOWS[selected_window]
        min_sample_size = max(1, settings.pricing_experiment_min_sample_size)

        if db is not None:
            since = datetime.now(timezone.utc) - duration
            rows = db.scalars(
                select(AuditEventModel).where(
                    AuditEventModel.action == "pricing_experiment_event",
                    AuditEventModel.status == "success",
                    AuditEventModel.created_at >= since,
                )
            ).all()
            variant_totals: dict[str, dict[str, int]] = {}
            for row in rows:
                details = row.details if isinstance(row.details, dict) else {}
                variant = str(details.get("variant_id", "")).strip()
                if not variant:
                    continue
                bucket = variant_totals.setdefault(
                    variant,
                    {
                        "exposures_total": 0,
                        "conversions_total": 0,
                        "retention_events_total": 0,
                        "revenue_cents_total": 0,
                    },
                )
                event_name = str(details.get("event_name", "")).strip()
                if event_name == "offer_exposure":
                    bucket["exposures_total"] += 1
                elif event_name == "offer_conversion":
                    if str(details.get("conversion_status", "")).strip() == "success":
                        bucket["conversions_total"] += 1
                elif event_name == "offer_retention":
                    bucket["retention_events_total"] += 1
                elif event_name == "offer_revenue":
                    revenue_cents = details.get("revenue_cents", 0)
                    try:
                        bucket["revenue_cents_total"] += max(0, int(revenue_cents))
                    except (TypeError, ValueError):
                        continue

            if variant_totals:
                variants = []
                for variant in sorted(variant_totals):
                    totals = variant_totals[variant]
                    exposures_total = totals["exposures_total"]
                    conversions_total = totals["conversions_total"]
                    revenue_cents_total = totals["revenue_cents_total"]
                    variants.append(
                        OpsMonitoringPricingKpisVariantItem(
                            variant_id=variant,
                            exposures_total=exposures_total,
                            conversions_total=conversions_total,
                            conversion_rate=(
                                conversions_total / exposures_total
                                if exposures_total > 0
                                else 0.0
                            ),
                            retention_events_total=totals["retention_events_total"],
                            revenue_cents_total=revenue_cents_total,
                            avg_revenue_per_conversion_cents=(
                                revenue_cents_total / conversions_total
                                if conversions_total > 0
                                else 0.0
                            ),
                            sample_size_is_low=exposures_total < min_sample_size,
                        )
                    )

                return OpsMonitoringPricingKpisData(
                    window=selected_window,
                    aggregation_scope="database_persistent",
                    min_sample_size=min_sample_size,
                    variants=variants,
                )

        exposures_map = get_counter_sums_by_prefix_in_window(
            "pricing_experiment_exposure_total|",
            duration,
        )
        conversions_map = get_counter_sums_by_prefix_in_window(
            "pricing_experiment_conversion_total|",
            duration,
        )
        retention_map = get_counter_sums_by_prefix_in_window(
            "pricing_experiment_retention_usage_total|",
            duration,
        )
        revenue_map = get_counter_sums_by_prefix_in_window(
            "pricing_experiment_revenue_cents_total|",
            duration,
        )

        exposures_by_variant = OpsMonitoringService._aggregate_by_variant(exposures_map)
        conversions_by_variant = OpsMonitoringService._aggregate_by_variant(
            conversions_map,
            success_only=True,
        )
        retention_by_variant = OpsMonitoringService._aggregate_by_variant(retention_map)
        revenue_by_variant = OpsMonitoringService._aggregate_by_variant(revenue_map)

        variant_codes = (
            set(exposures_by_variant)
            | set(conversions_by_variant)
            | set(retention_by_variant)
            | set(revenue_by_variant)
        )

        variant_items: list[OpsMonitoringPricingKpisVariantItem] = []
        for variant in sorted(variant_codes):
            exposures_total = exposures_by_variant.get(variant, 0)
            conversions_total = conversions_by_variant.get(variant, 0)
            retention_events_total = retention_by_variant.get(variant, 0)
            revenue_cents_total = revenue_by_variant.get(variant, 0)
            conversion_rate = (conversions_total / exposures_total) if exposures_total > 0 else 0.0
            avg_revenue_per_conversion = (
                revenue_cents_total / conversions_total if conversions_total > 0 else 0.0
            )
            variant_items.append(
                OpsMonitoringPricingKpisVariantItem(
                    variant_id=variant,
                    exposures_total=exposures_total,
                    conversions_total=conversions_total,
                    conversion_rate=conversion_rate,
                    retention_events_total=retention_events_total,
                    revenue_cents_total=revenue_cents_total,
                    avg_revenue_per_conversion_cents=avg_revenue_per_conversion,
                    sample_size_is_low=exposures_total < min_sample_size,
                )
            )

        scope = "instance_local_fallback" if db is not None else "instance_local"
        return OpsMonitoringPricingKpisData(
            window=selected_window,
            aggregation_scope=scope,
            min_sample_size=min_sample_size,
            variants=variant_items,
        )

    @staticmethod
    def _build_alerts(
        *,
        window: str,
        availability_percent: float,
        error_5xx_rate: float,
        p95_latency_ms: float,
        quota_exceeded_total: int,
        privacy_failures_total: int,
        b2b_auth_failures_total: int,
    ) -> list[OpsMonitoringAlertData]:
        alerts: list[OpsMonitoringAlertData] = []

        def _build_alert(
            *,
            code: str,
            severity: str,
            firing: bool,
            message: str,
            context: dict[str, float | str],
        ) -> OpsMonitoringAlertData:
            return OpsMonitoringAlertData(
                code=code,
                severity=severity,
                status="firing" if firing else "ok",
                message=message,
                context={"window": window, **context},
            )

        alerts.append(
            _build_alert(
                code="availability_degraded",
                severity="critical",
                firing=availability_percent < 99.0,
                message="API availability dropped below 99%.",
                context={
                    "value_percent": round(availability_percent, 4),
                    "threshold_percent": 99.0,
                },
            )
        )
        alerts.append(
            _build_alert(
                code="error_rate_5xx_high",
                severity="high",
                firing=error_5xx_rate > 0.02,
                message="5xx error rate exceeded threshold.",
                context={"value_rate": round(error_5xx_rate, 6), "threshold_rate": 0.02},
            )
        )
        alerts.append(
            _build_alert(
                code="latency_p95_high",
                severity="medium",
                firing=p95_latency_ms > 1200.0,
                message="p95 latency exceeded threshold on monitored endpoints.",
                context={"value_ms": round(p95_latency_ms, 2), "threshold_ms": 1200.0},
            )
        )
        alerts.append(
            _build_alert(
                code="quota_exceeded_spike",
                severity="medium",
                firing=quota_exceeded_total >= 25,
                message="Quota exceeded events are above baseline.",
                context={"value_count": quota_exceeded_total, "threshold_count": 25.0},
            )
        )
        alerts.append(
            _build_alert(
                code="privacy_failures_detected",
                severity="high",
                firing=privacy_failures_total > 0,
                message="Privacy workflow failures detected.",
                context={"value_count": privacy_failures_total, "threshold_count": 0.0},
            )
        )
        alerts.append(
            _build_alert(
                code="b2b_auth_failures_spike",
                severity="medium",
                firing=b2b_auth_failures_total >= 10,
                message="B2B API authentication failures exceeded threshold.",
                context={"value_count": b2b_auth_failures_total, "threshold_count": 10.0},
            )
        )
        return alerts
