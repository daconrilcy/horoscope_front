from datetime import date, datetime, timezone

from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_api_credential import EnterpriseApiCredentialModel
from app.infra.db.models.enterprise_billing import (
    EnterpriseAccountBillingPlanModel,
    EnterpriseBillingCycleModel,
    EnterpriseBillingPlanModel,
)
from app.infra.db.models.enterprise_feature_usage_counters import (
    EnterpriseFeatureUsageCounterModel,
)
from app.infra.db.models.product_entitlements import (
    FeatureUsageCounterModel,
    PeriodUnit,
    ResetMode,
)
from app.infra.db.models.user import UserModel
from app.services.auth_service import AuthService
from app.services.b2b.billing_service import B2BBillingService
from app.services.b2b.enterprise_credentials_service import EnterpriseCredentialsService
from app.services.b2b.reconciliation_service import (
    B2BReconciliationService,
    ReconciliationActionCode,
    ReconciliationActionPayload,
    ReconciliationSeverity,
    ReconciliationStatus,
)
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())
    with open_app_test_db_session() as db:
        for model in (
            AuditEventModel,
            EnterpriseAccountBillingPlanModel,
            EnterpriseBillingCycleModel,
            EnterpriseBillingPlanModel,
            EnterpriseFeatureUsageCounterModel,
            FeatureUsageCounterModel,
            EnterpriseApiCredentialModel,
            EnterpriseAccountModel,
            UserModel,
        ):
            db.execute(delete(model))
        db.commit()


def _create_enterprise_context(email: str) -> tuple[int, int]:
    with open_app_test_db_session() as db:
        auth = AuthService.register(
            db,
            email=email,
            password="strong-pass-123",
            role="enterprise_admin",
        )
        account = EnterpriseAccountModel(
            admin_user_id=auth.user.id,
            company_name="Acme Media",
            status="active",
        )
        db.add(account)
        db.flush()
        credential = EnterpriseCredentialsService.create_credential(db, admin_user_id=auth.user.id)
        db.commit()
        return account.id, credential.credential_id


def _seed_usage(account_id: int, usage_date: date, used_count: int) -> None:
    with open_app_test_db_session() as db:
        # Fenêtre mensuelle UTC
        window_start = datetime(usage_date.year, usage_date.month, 1, tzinfo=timezone.utc)
        if usage_date.month == 12:
            window_end = datetime(usage_date.year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            window_end = datetime(usage_date.year, usage_date.month + 1, 1, tzinfo=timezone.utc)

        db.add(
            EnterpriseFeatureUsageCounterModel(
                enterprise_account_id=account_id,
                feature_code="b2b_api_access",
                quota_key="b2b_api_access_monthly",
                period_unit=PeriodUnit.MONTH,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
                window_start=window_start,
                window_end=window_end,
                used_count=used_count,
            )
        )
        db.commit()


def test_reconciliation_detects_missing_billing_cycle_as_major() -> None:
    _cleanup_tables()
    account_id, credential_id = _create_enterprise_context("reco-service-major@example.com")
    _seed_usage(account_id, date(2026, 2, 5), used_count=12)

    with open_app_test_db_session() as db:
        listed = B2BReconciliationService.list_issues(db, account_id=account_id, limit=20, offset=0)

    assert listed.total == 1
    issue = listed.items[0]
    assert issue.mismatch_type == "missing_billing_cycle"
    assert issue.severity == ReconciliationSeverity.MAJOR
    assert issue.status == ReconciliationStatus.OPEN
    assert issue.delta_units == 12


def test_reconciliation_is_resolved_when_usage_and_billing_match() -> None:
    _cleanup_tables()
    account_id, credential_id = _create_enterprise_context("reco-service-resolved@example.com")
    _seed_usage(account_id, date(2026, 3, 5), used_count=4)

    with open_app_test_db_session() as db:
        B2BBillingService.close_cycle(
            db,
            account_id=account_id,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
            closed_by_user_id=None,
        )
        db.commit()

    with open_app_test_db_session() as db:
        listed = B2BReconciliationService.list_issues(db, account_id=account_id, limit=20, offset=0)

    assert listed.total == 1
    issue = listed.items[0]
    assert issue.mismatch_type == "coherent"
    assert issue.severity == ReconciliationSeverity.NONE
    assert issue.status == ReconciliationStatus.RESOLVED


def test_reconciliation_action_recalculate_returns_action_state() -> None:
    _cleanup_tables()
    account_id, credential_id = _create_enterprise_context("reco-service-action@example.com")
    _seed_usage(account_id, date(2026, 4, 15), used_count=7)

    with open_app_test_db_session() as db:
        listed = B2BReconciliationService.list_issues(db, account_id=account_id, limit=20, offset=0)
        assert listed.total == 1
        issue_id = listed.items[0].issue_id
        result = B2BReconciliationService.execute_action(
            db,
            issue_id=issue_id,
            payload=ReconciliationActionPayload(action=ReconciliationActionCode.RECALCULATE),
        )
        db.commit()

    assert result.action == ReconciliationActionCode.RECALCULATE
    assert result.status == "accepted"
    assert result.correction_state in {
        ReconciliationStatus.RESOLVED,
        ReconciliationStatus.INVESTIGATING,
    }


def test_reconciliation_normalizes_period_filters_to_month_bounds() -> None:
    _cleanup_tables()
    account_id, credential_id = _create_enterprise_context("reco-service-period@example.com")
    _seed_usage(account_id, date(2026, 5, 2), used_count=3)
    # On ajoute au même compteur pour le même mois
    with open_app_test_db_session() as db:
        counter = db.scalar(
            select(EnterpriseFeatureUsageCounterModel).where(
                EnterpriseFeatureUsageCounterModel.enterprise_account_id == account_id,
                EnterpriseFeatureUsageCounterModel.feature_code == "b2b_api_access",
            )
        )
        counter.used_count += 4
        db.commit()

    with open_app_test_db_session() as db:
        listed = B2BReconciliationService.list_issues(
            db,
            account_id=account_id,
            period_start=date(2026, 5, 15),
            period_end=date(2026, 5, 20),
            limit=20,
            offset=0,
        )

    assert listed.total == 1
    issue = listed.items[0]
    assert issue.period_start == date(2026, 5, 1)
    assert issue.period_end == date(2026, 5, 31)
    assert issue.usage_measured_units == 7


def test_reconciliation_ignores_non_monthly_counters() -> None:
    _cleanup_tables()
    account_id, _ = _create_enterprise_context("reco-service-ignore-yearly@example.com")
    _seed_usage(account_id, date(2026, 6, 5), used_count=4)

    with open_app_test_db_session() as db:
        db.add(
            EnterpriseFeatureUsageCounterModel(
                enterprise_account_id=account_id,
                feature_code="b2b_api_access",
                quota_key="b2b_api_access_yearly",
                period_unit=PeriodUnit.YEAR,
                period_value=1,
                reset_mode=ResetMode.CALENDAR,
                window_start=datetime(2026, 1, 1, tzinfo=timezone.utc),
                window_end=datetime(2027, 1, 1, tzinfo=timezone.utc),
                used_count=50,
            )
        )
        db.commit()

    with open_app_test_db_session() as db:
        listed = B2BReconciliationService.list_issues(db, account_id=account_id, limit=20, offset=0)

    assert listed.total == 1
    assert listed.items[0].usage_measured_units == 4


def test_reconciliation_ignores_non_calendar_monthly_counters() -> None:
    _cleanup_tables()
    account_id, _ = _create_enterprise_context("reco-service-ignore-rolling@example.com")
    _seed_usage(account_id, date(2026, 6, 5), used_count=4)

    with open_app_test_db_session() as db:
        db.add(
            EnterpriseFeatureUsageCounterModel(
                enterprise_account_id=account_id,
                feature_code="b2b_api_access",
                quota_key="b2b_api_access_monthly_rolling",
                period_unit=PeriodUnit.MONTH,
                period_value=1,
                reset_mode=ResetMode.ROLLING,
                window_start=datetime(2026, 6, 1, tzinfo=timezone.utc),
                window_end=datetime(2026, 7, 1, tzinfo=timezone.utc),
                used_count=50,
            )
        )
        db.commit()

    with open_app_test_db_session() as db:
        listed = B2BReconciliationService.list_issues(db, account_id=account_id, limit=20, offset=0)

    assert listed.total == 1
    assert listed.items[0].usage_measured_units == 4
