from app.infra.observability.metrics import get_metrics_snapshot, reset_metrics
from app.services.pricing_experiment_service import (
    EVENT_VERSION,
    PricingExperimentEvent,
    PricingExperimentService,
)


def test_assign_variant_is_stable_for_same_user() -> None:
    first = PricingExperimentService.assign_variant(12345)
    second = PricingExperimentService.assign_variant(12345)
    assert first == second


def test_record_events_emit_metrics() -> None:
    reset_metrics()
    PricingExperimentService.record_offer_exposure(
        user_id=101,
        user_role="user",
        plan_code="basic-entry",
        request_id="rid-expo",
    )
    PricingExperimentService.record_offer_conversion(
        user_id=101,
        user_role="user",
        plan_code="basic-entry",
        conversion_type="checkout",
        conversion_status="success",
        request_id="rid-conv",
    )
    PricingExperimentService.record_offer_revenue(
        user_id=101,
        user_role="user",
        plan_code="basic-entry",
        revenue_cents=500,
        request_id="rid-rev",
    )
    PricingExperimentService.record_retention_usage(
        user_id=101,
        user_role="user",
        plan_code="basic-entry",
        retention_event="quota_status_view",
        request_id="rid-ret",
    )

    snapshot = get_metrics_snapshot()
    counters = snapshot["counters"]
    assert any(
        name.startswith("pricing_experiment_exposure_total|") and "|variant_id=" in name
        for name in counters
    )
    assert any(
        name.startswith("pricing_experiment_conversion_total|") and "|variant_id=" in name
        for name in counters
    )
    assert any(
        name.startswith("pricing_experiment_revenue_cents_total|") and "|variant_id=" in name
        for name in counters
    )
    assert any(
        name.startswith("pricing_experiment_retention_usage_total|") and "|variant_id=" in name
        for name in counters
    )


def test_event_schema_rejects_invalid_revenue_payload() -> None:
    try:
        PricingExperimentEvent(
            event_name="offer_revenue",
            event_version=EVENT_VERSION,
            variant_id="control",
            user_segment="user",
            revenue_cents=0,
        )
    except Exception:
        assert True
    else:
        raise AssertionError("expected invalid revenue payload to fail validation")
