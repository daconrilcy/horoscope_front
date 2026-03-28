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
    PeriodUnit,
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    ResetMode,
)
from app.services.b2b_audit_service import B2BAuditEntry, B2BAuditService
from app.services.entitlement_types import UsageState


@pytest.fixture
def db_session() -> MagicMock:
    return MagicMock(spec=Session)


@patch("app.services.b2b_audit_service.resolve_b2b_canonical_plan")
def test_audit_admin_user_id_absent_does_not_block_canonical_resolution(
    mock_resolve: MagicMock,
    db_session: MagicMock,
) -> None:
    # AC 1: admin_user_id=None + plan canonique + binding valide -> resolution_source canonique
    account = EnterpriseAccountModel(id=1, company_name="No Admin Co", admin_user_id=None)
    canonical_plan = PlanCatalogModel(id=1, plan_code="b2b_plan")
    mock_resolve.return_value = canonical_plan

    binding = PlanFeatureBindingModel(
        id=10, plan_id=1, feature_id=100, access_mode=AccessMode.UNLIMITED, is_enabled=True
    )
    # 1. acc_plan -> None, 2. binding -> binding
    db_session.scalar.side_effect = [None, binding]

    entry = B2BAuditService._audit_account(db_session, account)

    assert entry.account_id == 1
    assert entry.resolution_source == "canonical_unlimited"
    assert entry.reason == "unlimited_access"
    assert entry.admin_user_id_present is False


@patch("app.services.b2b_audit_service.resolve_b2b_canonical_plan")
def test_audit_no_canonical_plan(
    mock_resolve: MagicMock,
    db_session: MagicMock,
) -> None:
    account = EnterpriseAccountModel(id=1, company_name="No Plan Co", admin_user_id=10)
    mock_resolve.return_value = None
    db_session.scalar.return_value = None

    entry = B2BAuditService._audit_account(db_session, account)

    assert entry.resolution_source == "settings_fallback"
    assert entry.reason == "no_canonical_plan"
    assert entry.binding_status is None
    assert entry.manual_review_required is False


@patch("app.services.b2b_audit_service.resolve_b2b_canonical_plan")
def test_audit_manual_review_required_without_canonical_plan(
    mock_resolve: MagicMock,
    db_session: MagicMock,
) -> None:
    account = EnterpriseAccountModel(id=1, company_name="Review Co", admin_user_id=10)
    mock_resolve.return_value = None
    account_plan = EnterpriseAccountBillingPlanModel(enterprise_account_id=1, plan_id=100)
    enterprise_plan = EnterpriseBillingPlanModel(id=100, code="legacy", included_monthly_units=0)
    db_session.scalar.side_effect = [account_plan, enterprise_plan]

    entry = B2BAuditService._audit_account(db_session, account)

    assert entry.resolution_source == "settings_fallback"
    assert entry.reason == "manual_review_required"
    assert entry.binding_status is None
    assert entry.manual_review_required is True


@patch("app.services.b2b_audit_service.resolve_b2b_canonical_plan")
def test_audit_missing_binding_uses_settings_fallback(
    mock_resolve: MagicMock,
    db_session: MagicMock,
) -> None:
    account = EnterpriseAccountModel(id=1, company_name="Missing Binding Co", admin_user_id=10)
    canonical_plan = PlanCatalogModel(id=1, plan_code="b2b_plan")
    mock_resolve.return_value = canonical_plan
    db_session.scalar.side_effect = [None, None]

    entry = B2BAuditService._audit_account(db_session, account)

    assert entry.resolution_source == "settings_fallback"
    assert entry.reason == "no_binding"
    assert entry.binding_status == "missing"


@patch("app.services.b2b_audit_service.resolve_b2b_canonical_plan")
def test_audit_canonical_disabled(
    mock_resolve: MagicMock,
    db_session: MagicMock,
) -> None:
    account = EnterpriseAccountModel(id=1, company_name="Disabled Co", admin_user_id=10)
    canonical_plan = PlanCatalogModel(id=1, plan_code="b2b_plan")
    mock_resolve.return_value = canonical_plan
    binding = PlanFeatureBindingModel(id=1, access_mode=AccessMode.DISABLED, is_enabled=True)
    db_session.scalar.side_effect = [None, binding]

    entry = B2BAuditService._audit_account(db_session, account)

    assert entry.resolution_source == "canonical_disabled"
    assert entry.reason == "disabled_by_plan"
    assert entry.binding_status == "disabled"


@patch("app.services.b2b_audit_service.resolve_b2b_canonical_plan")
def test_audit_canonical_unlimited(
    mock_resolve: MagicMock,
    db_session: MagicMock,
) -> None:
    account = EnterpriseAccountModel(id=1, company_name="Unlimited Co", admin_user_id=10)
    canonical_plan = PlanCatalogModel(id=1, plan_code="b2b_plan")
    mock_resolve.return_value = canonical_plan
    binding = PlanFeatureBindingModel(id=1, access_mode=AccessMode.UNLIMITED, is_enabled=True)
    db_session.scalar.side_effect = [None, binding]

    entry = B2BAuditService._audit_account(db_session, account)

    assert entry.resolution_source == "canonical_unlimited"
    assert entry.reason == "unlimited_access"
    assert entry.binding_status == "unlimited"


@patch("app.services.b2b_audit_service.EnterpriseQuotaUsageService.get_usage")
@patch("app.services.b2b_audit_service.resolve_b2b_canonical_plan")
def test_audit_canonical_quota(
    mock_resolve: MagicMock,
    mock_get_usage: MagicMock,
    db_session: MagicMock,
) -> None:
    account = EnterpriseAccountModel(id=1, company_name="Quota Co", admin_user_id=10)
    canonical_plan = PlanCatalogModel(id=1, plan_code="b2b_plan")
    mock_resolve.return_value = canonical_plan
    binding = PlanFeatureBindingModel(id=1, access_mode=AccessMode.QUOTA, is_enabled=True)
    quota = PlanFeatureQuotaModel(
        quota_key="calls",
        quota_limit=1000,
        period_unit=PeriodUnit.MONTH,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    )
    db_session.scalar.side_effect = [None, binding]
    db_session.scalars.return_value.all.return_value = [quota]
    mock_get_usage.return_value = UsageState(
        feature_code="b2b_api_access",
        quota_key="calls",
        used=100,
        quota_limit=1000,
        remaining=900,
        exhausted=False,
        period_unit="month",
        period_value=1,
        reset_mode="calendar",
        window_start=datetime.now(timezone.utc),
        window_end=None,
    )

    entry = B2BAuditService._audit_account(db_session, account)

    assert entry.resolution_source == "canonical_quota"
    assert entry.reason == "quota_binding_active"
    assert entry.binding_status == "quota"
    assert entry.quota_limit == 1000
    assert entry.remaining == 900


@patch("app.services.b2b_audit_service.resolve_b2b_canonical_plan")
def test_audit_zero_quota_falls_back_to_manual_review(
    mock_resolve: MagicMock,
    db_session: MagicMock,
) -> None:
    account = EnterpriseAccountModel(id=1, company_name="Zero Quota Co", admin_user_id=10)
    account_plan = EnterpriseAccountBillingPlanModel(enterprise_account_id=1, plan_id=100)
    enterprise_plan = EnterpriseBillingPlanModel(id=100, code="legacy", included_monthly_units=0)
    canonical_plan = PlanCatalogModel(id=1, plan_code="b2b_plan")
    binding = PlanFeatureBindingModel(id=1, access_mode=AccessMode.QUOTA, is_enabled=True)
    zero_quota = PlanFeatureQuotaModel(
        quota_key="calls",
        quota_limit=0,
        period_unit=PeriodUnit.MONTH,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    )
    mock_resolve.return_value = canonical_plan
    db_session.scalar.side_effect = [account_plan, enterprise_plan, binding]
    db_session.scalars.return_value.all.return_value = [zero_quota]

    entry = B2BAuditService._audit_account(db_session, account)

    assert entry.resolution_source == "settings_fallback"
    assert entry.reason == "manual_review_required"
    assert entry.binding_status == "quota"
    assert entry.manual_review_required is True


def test_list_audit_pagination_and_filtering(db_session: MagicMock) -> None:
    account_a = EnterpriseAccountModel(id=1, company_name="A", admin_user_id=10, status="active")
    account_b = EnterpriseAccountModel(id=2, company_name="B", admin_user_id=20, status="active")

    accounts_result = MagicMock()
    accounts_result.all.return_value = [account_a, account_b]

    account_plans_result = MagicMock()
    account_plans_result.all.return_value = [
        EnterpriseAccountBillingPlanModel(enterprise_account_id=1, plan_id=100),
        EnterpriseAccountBillingPlanModel(enterprise_account_id=2, plan_id=200),
    ]

    enterprise_plans_result = MagicMock()
    enterprise_plans_result.all.return_value = []

    canonical_plans_result = MagicMock()
    canonical_plans_result.all.return_value = []

    db_session.scalars.side_effect = [
        accounts_result,
        account_plans_result,
        enterprise_plans_result,
        canonical_plans_result,
    ] * 4

    with patch.object(B2BAuditService, "_audit_account") as mock_audit:
        canonical_entry = B2BAuditEntry(
            account_id=1,
            company_name="A",
            enterprise_plan_id=None,
            enterprise_plan_code=None,
            canonical_plan_id=None,
            canonical_plan_code=None,
            feature_code="b2b_api_access",
            resolution_source="canonical_quota",
            reason="quota_binding_active",
            binding_status="quota",
            quota_limit=10,
            remaining=5,
            window_end=None,
            admin_user_id_present=True,
            manual_review_required=False,
        )
        fallback_entry = B2BAuditEntry(
            account_id=2,
            company_name="B",
            enterprise_plan_id=None,
            enterprise_plan_code=None,
            canonical_plan_id=None,
            canonical_plan_code=None,
            feature_code="b2b_api_access",
            resolution_source="settings_fallback",
            reason="no_canonical_plan",
            binding_status=None,
            quota_limit=None,
            remaining=None,
            window_end=None,
            admin_user_id_present=True,
            manual_review_required=False,
        )
        mock_audit.side_effect = [canonical_entry, fallback_entry] * 4

        items, total = B2BAuditService.list_b2b_entitlement_audit(db_session)
        assert total == 2
        assert len(items) == 2

        items, total = B2BAuditService.list_b2b_entitlement_audit(
            db_session,
            resolution_source_filter="settings_fallback",
        )
        assert total == 1
        assert items[0].account_id == 2

        items, total = B2BAuditService.list_b2b_entitlement_audit(
            db_session,
            blocker_only=True,
        )
        assert total == 1
        assert items[0].account_id == 2

        items, total = B2BAuditService.list_b2b_entitlement_audit(
            db_session,
            page=2,
            page_size=1,
        )
        assert total == 2
        assert len(items) == 1
        assert items[0].account_id == 2


def test_list_audit_blocker_only_excludes_canonical_disabled(db_session: MagicMock) -> None:
    account = EnterpriseAccountModel(
        id=1, company_name="Disabled", admin_user_id=10, status="active"
    )

    accounts_result = MagicMock()
    accounts_result.all.return_value = [account]

    account_plans_result = MagicMock()
    account_plans_result.all.return_value = []

    enterprise_plans_result = MagicMock()
    enterprise_plans_result.all.return_value = []

    db_session.scalars.side_effect = [
        accounts_result,
        account_plans_result,
        enterprise_plans_result,
    ]

    with (
        patch.object(B2BAuditService, "_prefetch_canonical_plans", return_value={}),
        patch.object(B2BAuditService, "_prefetch_bindings", return_value={}),
        patch.object(B2BAuditService, "_prefetch_quotas", return_value={}),
        patch.object(B2BAuditService, "_audit_account") as mock_audit,
    ):
        mock_audit.return_value = B2BAuditEntry(
            account_id=1,
            company_name="Disabled",
            enterprise_plan_id=None,
            enterprise_plan_code=None,
            canonical_plan_id=10,
            canonical_plan_code="disabled-plan",
            feature_code="b2b_api_access",
            resolution_source="canonical_disabled",
            reason="disabled_by_plan",
            binding_status="disabled",
            quota_limit=None,
            remaining=None,
            window_end=None,
            admin_user_id_present=True,
            manual_review_required=False,
        )

        items, total = B2BAuditService.list_b2b_entitlement_audit(
            db_session,
            blocker_only=True,
        )

    assert total == 0
    assert items == []
