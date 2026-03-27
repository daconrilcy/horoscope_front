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
    PlanCatalogModel,
    PlanFeatureBindingModel,
    PlanFeatureQuotaModel,
    PeriodUnit,
    ResetMode,
)
from app.services.b2b_audit_service import B2BAuditEntry, B2BAuditService
from app.services.entitlement_types import UsageState


@pytest.fixture
def db_session():
    return MagicMock(spec=Session)


def test_audit_admin_user_id_missing(db_session):
    account = EnterpriseAccountModel(id=1, company_name="No Admin Co", admin_user_id=None)

    entry = B2BAuditService._audit_account(db_session, account)

    assert entry.account_id == 1
    assert entry.resolution_source == "settings_fallback"
    assert entry.reason == "admin_user_id_missing"
    assert entry.admin_user_id_present is False


@patch("app.services.b2b_audit_service.resolve_b2b_canonical_plan")
def test_audit_no_canonical_plan(mock_resolve, db_session):
    account = EnterpriseAccountModel(id=1, company_name="No Plan Co", admin_user_id=10)
    mock_resolve.return_value = None

    # Mock enterprise plan search - first for billing plan, then for the plan itself
    db_session.scalar.return_value = None 

    entry = B2BAuditService._audit_account(db_session, account)

    assert entry.resolution_source == "settings_fallback"
    assert entry.reason == "no_canonical_plan"
    assert entry.manual_review_required is False


@patch("app.services.b2b_audit_service.resolve_b2b_canonical_plan")
def test_audit_manual_review_required(mock_resolve, db_session):
    account = EnterpriseAccountModel(id=1, company_name="Review Co", admin_user_id=10)
    mock_resolve.return_value = None

    # Mock enterprise plan with 0 units
    acc_plan = EnterpriseAccountBillingPlanModel(enterprise_account_id=1, plan_id=100)
    ent_plan = EnterpriseBillingPlanModel(id=100, code="legacy", included_monthly_units=0)

    db_session.scalar.side_effect = [acc_plan, ent_plan]

    entry = B2BAuditService._audit_account(db_session, account)

    assert entry.resolution_source == "settings_fallback"
    assert entry.reason == "manual_review_required"
    assert entry.manual_review_required is True


@patch("app.services.b2b_audit_service.resolve_b2b_canonical_plan")
def test_audit_canonical_disabled(mock_resolve, db_session):
    account = EnterpriseAccountModel(id=1, company_name="Disabled Co", admin_user_id=10)
    plan = PlanCatalogModel(id=1, plan_code="b2b_plan")
    mock_resolve.return_value = plan
    
    # Mock sequence: 
    # 1. account_plan_model = db.scalar(...) -> returns None
    # 2. enterprise_plan = db.scalar(...) -> skipped because account_plan_model is None
    # 3. binding = db.scalar(...) -> returns binding
    binding = PlanFeatureBindingModel(id=1, access_mode=AccessMode.DISABLED, is_enabled=True)
    db_session.scalar.side_effect = [None, binding]
    
    entry = B2BAuditService._audit_account(db_session, account)
    
    assert entry.resolution_source == "canonical_disabled"
    assert entry.reason == "disabled_by_plan"
    assert entry.binding_status == "disabled"


@patch("app.services.b2b_audit_service.resolve_b2b_canonical_plan")
def test_audit_canonical_unlimited(mock_resolve, db_session):
    account = EnterpriseAccountModel(id=1, company_name="Unlimited Co", admin_user_id=10)
    plan = PlanCatalogModel(id=1, plan_code="b2b_plan")
    mock_resolve.return_value = plan
    
    # Mock sequence: account_plan (None), binding (unlimited)
    binding = PlanFeatureBindingModel(id=1, access_mode=AccessMode.UNLIMITED, is_enabled=True)
    db_session.scalar.side_effect = [None, binding]
    
    entry = B2BAuditService._audit_account(db_session, account)
    
    assert entry.resolution_source == "canonical_unlimited"
    assert entry.reason == "unlimited_access"
    assert entry.binding_status == "unlimited"


@patch("app.services.b2b_audit_service.QuotaUsageService.get_usage")
@patch("app.services.b2b_audit_service.resolve_b2b_canonical_plan")
def test_audit_canonical_quota(mock_resolve, mock_get_usage, db_session):
    account = EnterpriseAccountModel(id=1, company_name="Quota Co", admin_user_id=10)
    plan = PlanCatalogModel(id=1, plan_code="b2b_plan")
    mock_resolve.return_value = plan
    
    # Mock sequence: account_plan (None), binding (quota)
    binding = PlanFeatureBindingModel(id=1, access_mode=AccessMode.QUOTA, is_enabled=True)
    db_session.scalar.side_effect = [None, binding]
    
    quota = PlanFeatureQuotaModel(
        quota_key="calls",
        quota_limit=1000, 
        period_unit=PeriodUnit.MONTH,
        period_value=1,
        reset_mode=ResetMode.CALENDAR
    )
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
        window_end=None
    )
    
    entry = B2BAuditService._audit_account(db_session, account)
    
    assert entry.resolution_source == "canonical_quota"
    assert entry.reason == "quota_binding_active"
    assert entry.quota_limit == 1000
    assert entry.remaining == 900


def test_list_audit_pagination_and_filtering(db_session):
    # Mock accounts
    acc1 = EnterpriseAccountModel(id=1, company_name="A", admin_user_id=10, status="active")
    acc2 = EnterpriseAccountModel(id=2, company_name="B", admin_user_id=20, status="active")
    
    # Mock for pre-fetching logic:
    # 1. db.scalars(stmt_accounts).all()
    # 2. db.scalars(stmt_acc_plans).all()
    # 3. db.scalars(stmt_ent_plans).all()
    
    # We need to return different things for different calls to db.scalars().all()
    # But db_session.scalars.return_value.all is shared.
    # We use side_effect on scalars() instead.
    
    m_acc = MagicMock()
    m_acc.all.return_value = [acc1, acc2]
    
    m_plans = MagicMock()
    # EnterpriseAccountBillingPlanModel has enterprise_account_id
    ap1 = EnterpriseAccountBillingPlanModel(enterprise_account_id=1, plan_id=100)
    ap2 = EnterpriseAccountBillingPlanModel(enterprise_account_id=2, plan_id=200)
    m_plans.all.return_value = [ap1, ap2]
    
    m_ent = MagicMock()
    m_ent.all.return_value = [] # no enterprise plans needed for this mock test
    
    db_session.scalars.side_effect = [m_acc, m_plans, m_ent] * 4 # for each list_b2b_entitlement_audit call
    
    # Mock _audit_account to return different sources
    with patch.object(B2BAuditService, "_audit_account") as mock_audit:
        # Define the objects to return
        e1 = B2BAuditEntry(1, "A", None, None, None, None, "b2b", "canonical_quota", "quota_binding_active", "quota", 10, 5, None, True, False)
        e2 = B2BAuditEntry(2, "B", None, None, None, None, "b2b", "settings_fallback", "no_canonical_plan", None, None, None, None, True, False)
        
        mock_audit.side_effect = [e1, e2, e1, e2, e1, e2, e1, e2]
        
        # 1. No filter
        items, total = B2BAuditService.list_b2b_entitlement_audit(db_session)
        assert total == 2
        assert len(items) == 2
        
        # 2. Source filter
        items, total = B2BAuditService.list_b2b_entitlement_audit(db_session, resolution_source_filter="settings_fallback")
        assert total == 1
        assert items[0].account_id == 2
        
        # 3. Blocker only
        items, total = B2BAuditService.list_b2b_entitlement_audit(db_session, blocker_only=True)
        assert total == 1
        assert items[0].account_id == 2
        
        # 4. Pagination
        items, total = B2BAuditService.list_b2b_entitlement_audit(db_session, page=2, page_size=1)
        assert total == 2
        assert len(items) == 1
        assert items[0].account_id == 2

