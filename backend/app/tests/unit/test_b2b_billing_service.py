from datetime import date

from sqlalchemy import delete

from app.core.config import settings
from app.infra.db.base import Base
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
from app.services.b2b_billing_service import B2BBillingService, B2BBillingServiceError
from app.services.enterprise_credentials_service import EnterpriseCredentialsService


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
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


def _create_enterprise_context() -> tuple[int, int]:
    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email="b2b-billing-service@example.com",
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
        created = EnterpriseCredentialsService.create_credential(db, admin_user_id=auth.user.id)
        db.commit()
        return account.id, created.credential_id


def _seed_usage(account_id: int, credential_id: int, usage_date: date, used_count: int) -> None:
    with SessionLocal() as db:
        db.add(
            EnterpriseDailyUsageModel(
                enterprise_account_id=account_id,
                credential_id=credential_id,
                usage_date=usage_date,
                used_count=used_count,
            )
        )
        db.commit()


def test_b2b_billing_close_cycle_calculates_fixed_and_variable(monkeypatch: object) -> None:
    _cleanup_tables()
    account_id, credential_id = _create_enterprise_context()
    usage_day = date(2026, 2, 15)
    _seed_usage(account_id, credential_id, usage_day, used_count=5)
    monkeypatch.setattr(settings, "b2b_monthly_usage_limit", 2)
    monkeypatch.setattr(settings, "b2b_usage_limit_mode", "overage")

    with SessionLocal() as db:
        cycle = B2BBillingService.close_cycle(
            db,
            account_id=account_id,
            period_start=date(2026, 2, 1),
            period_end=date(2026, 2, 28),
            closed_by_user_id=None,
        )
        db.commit()

    assert cycle.fixed_amount_cents == 5000
    assert cycle.consumed_units == 5
    assert cycle.billable_units == 3
    assert cycle.variable_amount_cents == 6
    assert cycle.total_amount_cents == 5006
    assert cycle.overage_applied is True


def test_b2b_billing_close_cycle_is_idempotent() -> None:
    _cleanup_tables()
    account_id, credential_id = _create_enterprise_context()
    _seed_usage(account_id, credential_id, date(2026, 2, 10), used_count=1)

    with SessionLocal() as db:
        first = B2BBillingService.close_cycle(
            db,
            account_id=account_id,
            period_start=date(2026, 2, 1),
            period_end=date(2026, 2, 28),
            closed_by_user_id=None,
        )
        second = B2BBillingService.close_cycle(
            db,
            account_id=account_id,
            period_start=date(2026, 2, 1),
            period_end=date(2026, 2, 28),
            closed_by_user_id=None,
        )
        db.commit()

    assert first.cycle_id == second.cycle_id


def test_b2b_billing_list_and_latest_return_persisted_cycles() -> None:
    _cleanup_tables()
    account_id, credential_id = _create_enterprise_context()
    _seed_usage(account_id, credential_id, date(2026, 1, 20), used_count=2)
    _seed_usage(account_id, credential_id, date(2026, 2, 20), used_count=3)

    with SessionLocal() as db:
        january = B2BBillingService.close_cycle(
            db,
            account_id=account_id,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31),
            closed_by_user_id=None,
        )
        february = B2BBillingService.close_cycle(
            db,
            account_id=account_id,
            period_start=date(2026, 2, 1),
            period_end=date(2026, 2, 28),
            closed_by_user_id=None,
        )
        db.commit()

    with SessionLocal() as db:
        latest = B2BBillingService.get_latest_cycle(db, account_id=account_id)
        listing = B2BBillingService.list_cycles(db, account_id=account_id, limit=10, offset=0)

    assert latest is not None
    assert latest.cycle_id == february.cycle_id
    assert listing.total == 2
    assert [item.cycle_id for item in listing.items] == [february.cycle_id, january.cycle_id]


def test_b2b_billing_rejects_invalid_period() -> None:
    _cleanup_tables()
    account_id, _ = _create_enterprise_context()
    with SessionLocal() as db:
        try:
            B2BBillingService.close_cycle(
                db,
                account_id=account_id,
                period_start=date(2026, 3, 1),
                period_end=date(2026, 2, 28),
                closed_by_user_id=None,
            )
            assert False, "expected B2BBillingServiceError"
        except B2BBillingServiceError as error:
            assert error.code == "invalid_billing_period"


def test_b2b_billing_uses_account_specific_plan_mapping() -> None:
    _cleanup_tables()
    account_id, credential_id = _create_enterprise_context()
    _seed_usage(account_id, credential_id, date(2026, 2, 20), used_count=1)

    with SessionLocal() as db:
        default_plan = EnterpriseBillingPlanModel(
            code="b2b_default",
            display_name="B2B Default",
            monthly_fixed_cents=5000,
            included_monthly_units=100,
            overage_unit_price_cents=2,
            currency="EUR",
            is_active=True,
        )
        premium_plan = EnterpriseBillingPlanModel(
            code="b2b_premium",
            display_name="B2B Premium",
            monthly_fixed_cents=9000,
            included_monthly_units=500,
            overage_unit_price_cents=1,
            currency="EUR",
            is_active=True,
        )
        db.add(default_plan)
        db.add(premium_plan)
        db.flush()
        db.add(
            EnterpriseAccountBillingPlanModel(
                enterprise_account_id=account_id,
                plan_id=premium_plan.id,
            )
        )
        db.commit()

    with SessionLocal() as db:
        cycle = B2BBillingService.close_cycle(
            db,
            account_id=account_id,
            period_start=date(2026, 2, 1),
            period_end=date(2026, 2, 28),
            closed_by_user_id=None,
        )
        db.commit()

    assert cycle.plan_code == "b2b_premium"
    assert cycle.fixed_amount_cents == 9000
