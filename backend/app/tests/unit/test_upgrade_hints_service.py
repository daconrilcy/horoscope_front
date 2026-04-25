from unittest.mock import MagicMock, patch

from app.infra.db.models.billing import BillingPlanModel
from app.infra.db.models.product_entitlements import Audience, PlanCatalogModel
from app.services.entitlement.effective_entitlement_resolver_service import (
    EffectiveEntitlementResolverService,
)
from app.services.entitlement.entitlement_types import (
    EffectiveEntitlementsSnapshot,
    EffectiveFeatureAccess,
)


def _make_snapshot(plan_code="free", entitlements=None):
    return EffectiveEntitlementsSnapshot(
        subject_type="b2c_user",
        subject_id=42,
        plan_code=plan_code,
        billing_status="active",
        entitlements=entitlements or {},
    )


def _make_access(granted=True, variant_code=None):
    return EffectiveFeatureAccess(
        granted=granted,
        reason_code="granted" if granted else "feature_not_in_plan",
        access_mode="unlimited",
        variant_code=variant_code,
        quota_limit=None,
        quota_used=None,
        quota_remaining=None,
        period_unit=None,
        period_value=None,
        reset_mode=None,
        usage_states=[],
    )


def test_is_restricted_variant():
    assert EffectiveEntitlementResolverService._is_restricted_variant("summary_only") is True
    assert EffectiveEntitlementResolverService._is_restricted_variant("free_short") is True
    assert EffectiveEntitlementResolverService._is_restricted_variant("full") is False
    assert EffectiveEntitlementResolverService._is_restricted_variant(None) is False


@patch(
    "app.services.entitlement.effective_entitlement_resolver_service."
    "EffectiveEntitlementResolverService._get_next_plan"
)
def test_compute_upgrade_hints_free_user(mock_next_plan, db_session):
    next_plan = MagicMock(spec=PlanCatalogModel)
    next_plan.plan_code = "basic"
    mock_next_plan.return_value = next_plan

    snapshot = _make_snapshot(
        plan_code="free",
        entitlements={
            "horoscope_daily": _make_access(granted=True, variant_code="summary_only"),
            "astrologer_chat": _make_access(granted=False),
            "natal_chart_long": _make_access(granted=True, variant_code="free_short"),
            "natal_chart_short": _make_access(granted=True),
        },
    )

    hints = EffectiveEntitlementResolverService.compute_upgrade_hints(snapshot, db_session)

    assert len(hints) == 3
    codes = [h.feature_code for h in hints]
    assert "astrologer_chat" in codes
    assert "horoscope_daily" in codes
    assert "natal_chart_long" in codes
    assert "natal_chart_short" not in codes

    chat_hint = next(h for h in hints if h.feature_code == "astrologer_chat")
    assert chat_hint.current_plan_code == "free"
    assert chat_hint.target_plan_code == "basic"
    assert chat_hint.benefit_key == "upgrade.astrologer_chat.unlimited_messages"
    assert chat_hint.cta_variant == "banner"
    assert chat_hint.priority == 10


def test_compute_upgrade_hints_no_next_plan(db_session):
    with patch(
        "app.services.entitlement.effective_entitlement_resolver_service."
        "EffectiveEntitlementResolverService._get_next_plan"
    ) as mock_next:
        mock_next.return_value = None

        snapshot = _make_snapshot(plan_code="premium")
        hints = EffectiveEntitlementResolverService.compute_upgrade_hints(snapshot, db_session)
        assert hints == []


def test_get_next_plan_logic(db_session):
    p1 = BillingPlanModel(
        code="free",
        display_name="Free",
        monthly_price_cents=0,
        daily_message_limit=0,
    )
    p2 = BillingPlanModel(
        code="basic",
        display_name="Basic",
        monthly_price_cents=900,
        daily_message_limit=0,
    )
    p3 = BillingPlanModel(
        code="premium",
        display_name="Premium",
        monthly_price_cents=2900,
        daily_message_limit=0,
    )
    db_session.add_all([p1, p2, p3])
    db_session.flush()

    c1 = PlanCatalogModel(plan_code="free", plan_name="Free", audience=Audience.B2C)
    c2 = PlanCatalogModel(plan_code="basic", plan_name="Basic", audience=Audience.B2C)
    c3 = PlanCatalogModel(plan_code="premium", plan_name="Premium", audience=Audience.B2C)
    db_session.add_all([c1, c2, c3])
    db_session.commit()

    res = EffectiveEntitlementResolverService._get_next_plan("free", db_session)
    assert res.plan_code == "basic"

    res = EffectiveEntitlementResolverService._get_next_plan("basic", db_session)
    assert res.plan_code == "premium"

    res = EffectiveEntitlementResolverService._get_next_plan("premium", db_session)
    assert res is None

    res = EffectiveEntitlementResolverService._get_next_plan("none", db_session)
    assert res.plan_code == "free"
