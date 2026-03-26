from __future__ import annotations

import logging
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_billing import (
    EnterpriseAccountBillingPlanModel,
    EnterpriseBillingPlanModel,
)
from app.infra.db.models.product_entitlements import (
    AccessMode,
    Audience,
    FeatureCatalogModel,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    PeriodUnit,
    ResetMode,
    SourceOrigin,
)
from app.services.b2b_api_entitlement_gate import (
    B2BApiAccessDeniedError,
    B2BApiEntitlementGate,
    B2BApiQuotaExceededError,
)

logger = logging.getLogger(__name__)


def seed_b2b_data(
    db: Session,
    *,
    account_id: int = 1,
    admin_user_id: int | None = 10,
    has_canonical: bool = True,
    access_mode: AccessMode = AccessMode.QUOTA,
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
    acc_plan = EnterpriseAccountBillingPlanModel(enterprise_account_id=account_id, plan_id=ent_plan.id)
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
    binding = PlanFeatureBindingModel(
        plan_id=plan_catalog.id,
        feature_id=feature.id,
        access_mode=access_mode,
        is_enabled=True,
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


def test_check_and_consume_quota_exhausted(db_session):
    seed_b2b_data(db_session, account_id=1, admin_user_id=10, access_mode=AccessMode.QUOTA)

    # Consommer tout le quota (quota_limit=1000)
    # On peut simuler l'épuisement en créant un compteur déjà plein
    from app.infra.db.models.product_entitlements import FeatureUsageCounterModel
    from app.services.quota_window_resolver import QuotaWindowResolver

    now = datetime.now(timezone.utc)
    window = QuotaWindowResolver.compute_window(
        PeriodUnit.MONTH.value, 1, ResetMode.CALENDAR.value, now
    )

    counter = FeatureUsageCounterModel(
        user_id=10,
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

    result = B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)

    assert result.path == "settings_fallback"


def test_check_and_consume_admin_user_missing(db_session):
    # On mock le retour de db.scalar pour simuler un compte avec admin_user_id à None
    mock_account = MagicMock(spec=EnterpriseAccountModel)
    mock_account.admin_user_id = None

    with patch.object(Session, "scalar", return_value=mock_account):
        result = B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)

    assert result.path == "settings_fallback"


def test_check_and_consume_window_end_is_next_month(db_session):
    # On mock datetime.now(timezone.utc) via patch dans quota_usage_service
    fixed_now = datetime(2026, 3, 15, 12, 0, 0, tzinfo=timezone.utc)
    seed_b2b_data(db_session, account_id=1, admin_user_id=10, access_mode=AccessMode.QUOTA)

    with patch("app.services.quota_usage_service.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_now
        # window end should be 2026-04-01 00:00:00
        result = B2BApiEntitlementGate.check_and_consume(db_session, account_id=1)

    assert result.path == "canonical_quota"
    state = result.usage_states[0]
    assert state.window_end == datetime(2026, 4, 1, 0, 0, 0, tzinfo=timezone.utc)
