import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.services.b2b_entitlement_repair_service import (
    B2BEntitlementRepairService,
    RepairValidationError,
    RepairRunReport
)
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
    SourceOrigin,
)
from app.infra.db.models.user import UserModel
from app.services.b2b_audit_service import B2BAuditEntry

@pytest.fixture
def db():
    return MagicMock(spec=Session)

@pytest.fixture
def feature():
    f = MagicMock(spec=FeatureCatalogModel)
    f.id = 1
    f.feature_code = "b2b_api_access"
    return f

def test_run_auto_repair_dry_run_no_mutation(db, feature):
    # Setup
    account = EnterpriseAccountModel(id=1, company_name="Test Co", status="active", admin_user_id=10)
    acc_plan = EnterpriseAccountBillingPlanModel(enterprise_account_id=1, plan_id=100)
    ent_plan = EnterpriseBillingPlanModel(id=100, code="PLAN1", display_name="Plan 1", included_monthly_units=10, is_active=True)
    
    db.scalars.return_value.all.side_effect = [
        [account], # all_accounts
        [acc_plan], # account_plans
        [ent_plan], # enterprise_plans
    ]
    # db.scalar calls in order:
    # 1. feature lookup
    # 2. existing plan check in _backfill_canonical_plan
    # 3. existing binding check in run_auto_repair
    db.scalar.side_effect = [feature, None, None]
    
    # Mock audit to return no_canonical_plan
    with patch("app.services.b2b_audit_service.B2BAuditService._audit_account") as mock_audit, \
         patch("app.services.b2b_audit_service.B2BAuditService._prefetch_canonical_plans", return_value={}), \
         patch("app.services.b2b_audit_service.B2BAuditService._prefetch_bindings", return_value={}), \
         patch("app.services.b2b_audit_service.B2BAuditService._prefetch_quotas", return_value={}):
        
        mock_audit.return_value = B2BAuditEntry(
            account_id=1, company_name="Test Co", enterprise_plan_id=100, enterprise_plan_code="PLAN1",
            canonical_plan_id=None, canonical_plan_code=None, feature_code="b2b_api_access",
            resolution_source="settings_fallback", reason="no_canonical_plan",
            binding_status=None, quota_limit=None, remaining=None, window_end=None,
            admin_user_id_present=True, manual_review_required=False
        )
        
        # Action
        report = B2BEntitlementRepairService.run_auto_repair(db, dry_run=True)
        
        # Assert
        assert report.dry_run is True
        assert report.plans_created == 1
        assert report.bindings_created == 1
        assert report.quotas_created == 1
        db.add.assert_not_called()
        db.commit.assert_not_called()

def test_run_auto_repair_full_backfill(db, feature):
    # Setup
    account = EnterpriseAccountModel(id=1, company_name="Test Co", status="active", admin_user_id=10)
    acc_plan = EnterpriseAccountBillingPlanModel(enterprise_account_id=1, plan_id=100)
    ent_plan = EnterpriseBillingPlanModel(id=100, code="PLAN1", display_name="Plan 1", included_monthly_units=10, is_active=True)
    
    db.scalars.return_value.all.side_effect = [
        [account], [acc_plan], [ent_plan]
    ]
    # db.scalar calls in order:
    # 1. feature lookup
    # 2. existing plan check in _backfill_canonical_plan
    # 3. existing binding check in run_auto_repair
    db.scalar.side_effect = [feature, None, None]
    
    with patch("app.services.b2b_audit_service.B2BAuditService._audit_account") as mock_audit, \
         patch("app.services.b2b_audit_service.B2BAuditService._prefetch_canonical_plans", return_value={}), \
         patch("app.services.b2b_audit_service.B2BAuditService._prefetch_bindings", return_value={}), \
         patch("app.services.b2b_audit_service.B2BAuditService._prefetch_quotas", return_value={}):
        
        mock_audit.return_value = B2BAuditEntry(
            account_id=1, company_name="Test Co", enterprise_plan_id=100, enterprise_plan_code="PLAN1",
            canonical_plan_id=None, canonical_plan_code=None, feature_code="b2b_api_access",
            resolution_source="settings_fallback", reason="no_canonical_plan",
            binding_status=None, quota_limit=None, remaining=None, window_end=None,
            admin_user_id_present=True, manual_review_required=False
        )
        
        # Action
        report = B2BEntitlementRepairService.run_auto_repair(db, dry_run=False)
        
        # Assert
        assert report.plans_created == 1
        assert report.bindings_created == 1
        assert report.quotas_created == 1
        assert db.add.call_count == 3 # Plan, Binding, Quota
        db.commit.assert_called_once()


def test_run_auto_repair_already_canonical_skipped(db, feature):
    # Setup
    account = EnterpriseAccountModel(id=1, company_name="Test Co", status="active", admin_user_id=10)
    acc_plan = EnterpriseAccountBillingPlanModel(enterprise_account_id=1, plan_id=100)
    ent_plan = EnterpriseBillingPlanModel(id=100, code="PLAN1", display_name="Plan 1", included_monthly_units=10, is_active=True)
    
    db.scalars.return_value.all.side_effect = [
        [account], [acc_plan], [ent_plan]
    ]
    db.scalar.side_effect = [feature]
    
    with patch("app.services.b2b_audit_service.B2BAuditService._audit_account") as mock_audit, \
         patch("app.services.b2b_audit_service.B2BAuditService._prefetch_canonical_plans", return_value={}), \
         patch("app.services.b2b_audit_service.B2BAuditService._prefetch_bindings", return_value={}), \
         patch("app.services.b2b_audit_service.B2BAuditService._prefetch_quotas", return_value={}):
        
        mock_audit.return_value = B2BAuditEntry(
            account_id=1, company_name="Test Co", enterprise_plan_id=100, enterprise_plan_code="PLAN1",
            canonical_plan_id=200, canonical_plan_code="PLAN1", feature_code="b2b_api_access",
            resolution_source="canonical_quota", reason="quota_binding_active",
            binding_status="quota", quota_limit=10, remaining=10, window_end=None,
            admin_user_id_present=True, manual_review_required=False
        )
        
        # Action
        report = B2BEntitlementRepairService.run_auto_repair(db, dry_run=False)
        
        # Assert
        assert report.skipped_already_canonical == 1
        assert report.plans_created == 0
        db.add.assert_not_called()

def test_run_auto_repair_admin_missing_blocker(db, feature):
    # Setup
    account = EnterpriseAccountModel(id=1, company_name="Test Co", status="active", admin_user_id=None)
    
    db.scalars.return_value.all.side_effect = [
        [account], {}, {}
    ]
    db.scalar.side_effect = [feature]
    
    with patch("app.services.b2b_audit_service.B2BAuditService._audit_account") as mock_audit, \
         patch("app.services.b2b_audit_service.B2BAuditService._prefetch_canonical_plans", return_value={}), \
         patch("app.services.b2b_audit_service.B2BAuditService._prefetch_bindings", return_value={}), \
         patch("app.services.b2b_audit_service.B2BAuditService._prefetch_quotas", return_value={}):
        
        mock_audit.return_value = B2BAuditEntry(
            account_id=1, company_name="Test Co", enterprise_plan_id=None, enterprise_plan_code=None,
            canonical_plan_id=None, canonical_plan_code=None, feature_code="b2b_api_access",
            resolution_source="settings_fallback", reason="admin_user_id_missing",
            binding_status=None, quota_limit=None, remaining=None, window_end=None,
            admin_user_id_present=False, manual_review_required=False
        )
        
        # Action
        report = B2BEntitlementRepairService.run_auto_repair(db, dry_run=False)
        
        # Assert
        assert len(report.remaining_blockers) == 1
        assert report.remaining_blockers[0].recommended_action == "set_admin_user"

def test_set_admin_user_valid(db):
    account = EnterpriseAccountModel(id=1, status="active", admin_user_id=None)
    user = UserModel(id=10)
    db.get.side_effect = [account, user]
    db.scalar.side_effect = [None] # No other account
    
    result = B2BEntitlementRepairService.set_admin_user(db, account_id=1, user_id=10)
    
    assert result["status"] == "ok"
    assert account.admin_user_id == 10
    db.commit.assert_called_once()

def test_set_admin_user_already_set(db):
    account = EnterpriseAccountModel(id=1, status="active", admin_user_id=9)
    db.get.return_value = account
    
    with pytest.raises(RepairValidationError) as excinfo:
        B2BEntitlementRepairService.set_admin_user(db, account_id=1, user_id=10)
    assert excinfo.value.code == "admin_user_already_set"

def test_classify_zero_units_quota_valid(db, feature):
    plan = PlanCatalogModel(id=200, audience=Audience.B2B, is_active=True, source_type=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value, source_id=100)
    ent_plan = EnterpriseBillingPlanModel(id=100, included_monthly_units=0)
    db.get.side_effect = [plan, ent_plan]
    # db.scalar calls: 1. feature, 2. binding, 3. quota check
    db.scalar.side_effect = [feature, None, None] 
    
    result = B2BEntitlementRepairService.classify_zero_units(db, canonical_plan_id=200, access_mode="quota", quota_limit=50)
    
    assert result["status"] == "created"
    assert result["access_mode"] == "quota"
    assert result["quota_limit"] == 50
    db.commit.assert_called_once()

def test_classify_zero_units_not_eligible(db):
    plan = PlanCatalogModel(id=200, audience=Audience.B2B, is_active=True, source_type=SourceOrigin.MIGRATED_FROM_ENTERPRISE_PLAN.value, source_id=100)
    ent_plan = EnterpriseBillingPlanModel(id=100, included_monthly_units=10) # Not zero
    db.get.side_effect = [plan, ent_plan]
    
    with pytest.raises(RepairValidationError) as excinfo:
        B2BEntitlementRepairService.classify_zero_units(db, canonical_plan_id=200, access_mode="unlimited", quota_limit=None)
    assert excinfo.value.code == "canonical_plan_not_zero_units_eligible"
