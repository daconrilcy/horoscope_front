from datetime import date

from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.audit_event import AuditEventModel
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_api_credential import EnterpriseApiCredentialModel
from app.infra.db.models.enterprise_billing import (
    EnterpriseAccountBillingPlanModel,
    EnterpriseBillingCycleModel,
    EnterpriseBillingPlanModel,
)
from app.infra.db.models.enterprise_usage import EnterpriseDailyUsageModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService
from app.services.b2b_billing_service import B2BBillingService
from app.services.b2b_reconciliation_service import (
    B2BReconciliationService,
    ReconciliationActionCode,
    ReconciliationActionPayload,
    ReconciliationSeverity,
    ReconciliationStatus,
)
from app.services.enterprise_credentials_service import EnterpriseCredentialsService


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            AuditEventModel,
            EnterpriseAccountBillingPlanModel,
            EnterpriseBillingCycleModel,
            EnterpriseBillingPlanModel,
            EnterpriseDailyUsageModel,
            EnterpriseApiCredentialModel,
            EnterpriseAccountModel,
            UserModel,
        ):
            db.execute(delete(model))
        db.commit()


def _create_enterprise_context(email: str) -> tuple[int, int]:
    with SessionLocal() as db:
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


def test_reconciliation_detects_missing_billing_cycle_as_major() -> None:
    _cleanup_tables()
    account_id, credential_id = _create_enterprise_context("reco-service-major@example.com")
    with SessionLocal() as db:
        db.add(
            EnterpriseDailyUsageModel(
                enterprise_account_id=account_id,
                credential_id=credential_id,
                usage_date=date(2026, 2, 5),
                used_count=12,
            )
        )
        db.commit()

    with SessionLocal() as db:
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
    with SessionLocal() as db:
        db.add(
            EnterpriseDailyUsageModel(
                enterprise_account_id=account_id,
                credential_id=credential_id,
                usage_date=date(2026, 3, 5),
                used_count=4,
            )
        )
        B2BBillingService.close_cycle(
            db,
            account_id=account_id,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
            closed_by_user_id=None,
        )
        db.commit()

    with SessionLocal() as db:
        listed = B2BReconciliationService.list_issues(db, account_id=account_id, limit=20, offset=0)

    assert listed.total == 1
    issue = listed.items[0]
    assert issue.mismatch_type == "coherent"
    assert issue.severity == ReconciliationSeverity.NONE
    assert issue.status == ReconciliationStatus.RESOLVED


def test_reconciliation_action_recalculate_returns_action_state() -> None:
    _cleanup_tables()
    account_id, credential_id = _create_enterprise_context("reco-service-action@example.com")
    with SessionLocal() as db:
        db.add(
            EnterpriseDailyUsageModel(
                enterprise_account_id=account_id,
                credential_id=credential_id,
                usage_date=date(2026, 4, 15),
                used_count=7,
            )
        )
        db.commit()

    with SessionLocal() as db:
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
    with SessionLocal() as db:
        db.add(
            EnterpriseDailyUsageModel(
                enterprise_account_id=account_id,
                credential_id=credential_id,
                usage_date=date(2026, 5, 2),
                used_count=3,
            )
        )
        db.add(
            EnterpriseDailyUsageModel(
                enterprise_account_id=account_id,
                credential_id=credential_id,
                usage_date=date(2026, 5, 28),
                used_count=4,
            )
        )
        db.commit()

    with SessionLocal() as db:
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
