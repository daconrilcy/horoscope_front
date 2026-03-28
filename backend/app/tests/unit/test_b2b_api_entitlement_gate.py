from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_billing import (
    EnterpriseAccountBillingPlanModel,
    EnterpriseBillingPlanModel,
)
from app.infra.db.models.enterprise_feature_usage_counters import (
    EnterpriseFeatureUsageCounterModel,
)
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PeriodUnit,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    ResetMode,
    SourceOrigin,
)
from app.services.b2b_api_entitlement_gate import (
    B2BApiAccessDeniedError,
    B2BApiEntitlementGate,
    B2BApiQuotaExceededError,
)


def seed_b2b_data(
    db: Session,
    *,
    account_id: int = 1,
    admin_user_id: int | None = 10,
    has_canonical: bool = True,
    access_mode: AccessMode = AccessMode.QUOTA,
    is_enabled: bool = True,
    with_binding: bool = True,
) -> EnterpriseAccountModel:
    # 1. Create account
    account = EnterpriseAccountModel(
        id=account_id,
        admin_user_id=admin_user_id,
        company_name="Test Co",
        status="active",
    )
    db.add(account)

    if not has_canonical:
        db.commit()
        return account

    # 2. Enterprise Plan
    ent_plan = EnterpriseBillingPlanModel(
        id=100,
        code="ent-test",
        display_name="Ent Test",
        monthly_fixed_cents=1000,
        included_monthly_units=1000,
    )
    db.add(ent_plan)

    # 3. Binding account to plan
    acc_plan = EnterpriseAccountBillingPlanModel(
        enterprise_account_id=account_id,
        plan_id=ent_plan.id,
    )
    db.add(acc_plan)

    # 4. Plan Catalog (Canonical)
    plan_catalog = PlanCatalogModel(
        plan_code="b2b-test",
        plan_name="B2B Test",
        audience=Audience.B2B,
        source_type=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value,
        source_id=ent_plan.id,
        is_active=True,
    )
    db.add(plan_catalog)
    db.flush()

    # 5. Feature Catalog
    feature = FeatureCatalogModel(
        feature_code=B2BApiEntitlementGate.FEATURE_CODE,
        feature_name="B2B API",
        is_metered=True,
    )
    db.add(feature)
    db.flush()

    # 6. Plan Feature Binding
    if not with_binding:
        db.commit()
        return account

    binding = PlanFeatureBindingModel(
        plan_id=plan_catalog.id,
        feature_id=feature.id,
        access_mode=access_mode,
        is_enabled=is_enabled,
    )
    db.add(binding)
    db.flush()

    # 7. Quota if needed
    if access_mode == AccessMode.QUOTA:
        quota = PlanFeatureQuotaModel(
            plan_feature_binding_id=binding.id,
            quota_key="calls",
            quota_limit=1000,
            period_unit=PeriodUnit.MONTH,
            period_value=1,
            reset_mode=ResetMode.CALENDAR,
        )
        db.add(quota)

    db.commit()
    return account


def test_check_and_consume_quota_success(db_session):
    seed_b2b_data(db_session, account_id=1, admin_user_id=10, access_mode=AccessMode.QUOTA)

    result = B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)

    assert result.path == "canonical_quota"
    assert len(result.usage_states) == 1
    state = result.usage_states[0]
    assert state.used == 1
    assert state.remaining == 999
    assert state.quota_limit == 1000


def test_check_and_consume_unlimited(db_session):
    seed_b2b_data(db_session, account_id=1, admin_user_id=10, access_mode=AccessMode.UNLIMITED)

    result = B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)

    assert result.path == "canonical_unlimited"
    assert len(result.usage_states) == 0


def test_check_and_consume_disabled(db_session):
    seed_b2b_data(db_session, account_id=1, admin_user_id=10, access_mode=AccessMode.DISABLED)

    with pytest.raises(B2BApiAccessDeniedError) as exc:
        B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)
    assert exc.value.code == "b2b_api_access_denied"
    assert exc.value.details["reason"] == "disabled_by_plan"


def test_check_and_consume_disabled_when_binding_not_enabled(db_session):
    seed_b2b_data(
        db_session,
        account_id=1,
        admin_user_id=10,
        access_mode=AccessMode.QUOTA,
        is_enabled=False,
    )

    with pytest.raises(B2BApiAccessDeniedError) as exc:
        B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)

    assert exc.value.code == "b2b_api_access_denied"
    assert exc.value.details["reason"] == "disabled_by_plan"


def test_check_and_consume_quota_exhausted(db_session):
    seed_b2b_data(db_session, account_id=1, admin_user_id=10, access_mode=AccessMode.QUOTA)

    # Consommer tout le quota (quota_limit=1000)
    # On peut simuler l'épuisement en créant un compteur déjà plein
    from app.services.quota_window_resolver import QuotaWindowResolver

    now = datetime.now(timezone.utc)
    window = QuotaWindowResolver.compute_window(
        PeriodUnit.MONTH.value, 1, ResetMode.CALENDAR.value, now
    )

    counter = EnterpriseFeatureUsageCounterModel(
        enterprise_account_id=1,
        feature_code=B2BApiEntitlementGate.FEATURE_CODE,
        quota_key="calls",
        period_unit=PeriodUnit.MONTH,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
        window_start=window.window_start,
        window_end=window.window_end,
        used_count=1000,
    )
    db_session.add(counter)
    db_session.commit()

    with pytest.raises(B2BApiQuotaExceededError) as exc:
        B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)
    assert exc.value.code == "b2b_api_quota_exceeded"


def test_check_and_consume_fallback_no_canonical(db_session):
    seed_b2b_data(db_session, account_id=1, admin_user_id=10, has_canonical=False)

    with pytest.raises(B2BApiAccessDeniedError) as exc:
        B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)

    assert exc.value.code == "b2b_no_canonical_plan"


def test_check_and_consume_fallback_no_binding(db_session):
    seed_b2b_data(
        db_session,
        account_id=1,
        admin_user_id=10,
        has_canonical=True,
        with_binding=False,
    )

    with pytest.raises(B2BApiAccessDeniedError) as exc:
        B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)

    assert exc.value.code == "b2b_no_binding"


def test_check_and_consume_quota_without_quota_rows(db_session):
    seed_b2b_data(
        db_session,
        account_id=1,
        admin_user_id=10,
        has_canonical=True,
        access_mode=AccessMode.UNLIMITED,
    )
    binding = db_session.scalar(select(PlanFeatureBindingModel).limit(1))
    assert binding is not None
    binding.access_mode = AccessMode.QUOTA
    db_session.commit()

    with pytest.raises(B2BApiAccessDeniedError) as exc:
        B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)

    assert exc.value.code == "b2b_no_quota_defined"


def test_check_and_consume_unknown_access_mode_logs_warning(db_session, caplog):
    account = EnterpriseAccountModel(
        id=1,
        company_name="Test Co",
        admin_user_id=10,
        status="active",
    )
    binding = MagicMock(spec=PlanFeatureBindingModel)
    binding.is_enabled = True
    binding.access_mode = "surprise-mode"

    caplog.set_level("WARNING", logger="app.services.b2b_api_entitlement_gate")
    with patch(
        "app.services.b2b_api_entitlement_gate.resolve_b2b_canonical_plan",
        return_value=PlanCatalogModel(id=1, plan_code="b2b-test"),
    ), patch.object(db_session, "scalar", side_effect=[account, binding]):

        with pytest.raises(B2BApiAccessDeniedError) as exc:
            B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)

    assert exc.value.code == "b2b_unknown_access_mode"
    assert "b2b_gate_blocked" in caplog.text


def test_check_and_consume_admin_user_missing_no_longer_blocks_quota(db_session):
    seed_b2b_data(db_session, account_id=1, admin_user_id=None, access_mode=AccessMode.QUOTA)

    result = B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)

    assert result.path == "canonical_quota"
    assert result.usage_states[0].used == 1


def test_check_and_consume_window_end_is_next_month(db_session):
    fixed_now = datetime(2026, 3, 15, 12, 0, 0, tzinfo=timezone.utc)
    seed_b2b_data(db_session, account_id=1, admin_user_id=10, access_mode=AccessMode.QUOTA)

    with patch("app.services.enterprise_quota_usage_service.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_now
        mock_dt.side_effect = datetime
        # window end should be 2026-04-01 00:00:00
        result = B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)

    assert result.path == "canonical_quota"
    state = result.usage_states[0]
    assert state.window_end == datetime(2026, 4, 1, 0, 0, 0, tzinfo=timezone.utc)
