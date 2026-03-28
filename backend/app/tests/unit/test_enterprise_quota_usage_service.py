from datetime import datetime, timezone

import pytest
from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_feature_usage_counters import (
    EnterpriseFeatureUsageCounterModel,
)
from app.infra.db.models.product_entitlements import (
    FeatureUsageCounterModel,
    PeriodUnit,
    ResetMode,
)
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService
from app.services.enterprise_quota_usage_service import EnterpriseQuotaUsageService
from app.services.entitlement_types import QuotaDefinition
from app.services.feature_scope_registry import (
    InvalidQuotaScopeError,
    UnknownFeatureCodeError,
)
from app.services.quota_usage_service import QuotaExhaustedError


def _cleanup_tables() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for model in (
            EnterpriseFeatureUsageCounterModel,
            FeatureUsageCounterModel,
            EnterpriseAccountModel,
            UserModel,
        ):
            db.execute(delete(model))
        db.commit()


def _create_enterprise_account(email: str) -> int:
    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email=email,
            password="strong-pass-123",
            role="enterprise_admin",
        )
        account = EnterpriseAccountModel(
            admin_user_id=auth.user.id,
            company_name="Test Enterprise",
            status="active",
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        return account.id


def test_enterprise_quota_usage_service_rejects_b2c_feature_on_get_usage() -> None:
    _cleanup_tables()
    account_id = _create_enterprise_account("reject-get@example.com")
    quota = QuotaDefinition(
        quota_key="monthly",
        quota_limit=1000,
        period_unit=PeriodUnit.MONTH,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    )
    with SessionLocal() as db:
        with pytest.raises(InvalidQuotaScopeError) as exc_info:
            EnterpriseQuotaUsageService.get_usage(
                db,
                account_id=account_id,
                feature_code="astrologer_chat",
                quota=quota,
            )
    assert "QuotaUsageService" in str(exc_info.value)


def test_enterprise_quota_usage_service_rejects_b2c_feature_on_consume() -> None:
    _cleanup_tables()
    account_id = _create_enterprise_account("reject-consume@example.com")
    quota = QuotaDefinition(
        quota_key="monthly",
        quota_limit=1000,
        period_unit=PeriodUnit.MONTH,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    )
    with SessionLocal() as db:
        with pytest.raises(InvalidQuotaScopeError) as exc_info:
            EnterpriseQuotaUsageService.consume(
                db,
                account_id=account_id,
                feature_code="thematic_consultation",
                quota=quota,
            )
    assert "QuotaUsageService" in str(exc_info.value)


def test_enterprise_quota_usage_service_rejects_unknown_feature_code() -> None:
    _cleanup_tables()
    account_id = _create_enterprise_account("reject-unknown@example.com")
    quota = QuotaDefinition(
        quota_key="monthly",
        quota_limit=1000,
        period_unit=PeriodUnit.MONTH,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    )
    with SessionLocal() as db:
        with pytest.raises(UnknownFeatureCodeError):
            EnterpriseQuotaUsageService.get_usage(
                db,
                account_id=account_id,
                feature_code="unregistered_feature",
                quota=quota,
            )


def test_enterprise_quota_get_usage_empty() -> None:
    _cleanup_tables()
    account_id = _create_enterprise_account("empty@example.com")
    quota = QuotaDefinition(
        quota_key="test_calls",
        quota_limit=100,
        period_unit=PeriodUnit.MONTH,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    )

    with SessionLocal() as db:
        state = EnterpriseQuotaUsageService.get_usage(
            db, account_id=account_id, feature_code="b2b_api_access", quota=quota
        )

    assert state.used == 0
    assert state.remaining == 100
    assert state.exhausted is False


def test_enterprise_quota_consume_initial_creates_counter() -> None:
    _cleanup_tables()
    account_id = _create_enterprise_account("consume@example.com")
    quota = QuotaDefinition(
        quota_key="test_calls",
        quota_limit=10,
        period_unit=PeriodUnit.MONTH,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    )

    with SessionLocal() as db:
        state = EnterpriseQuotaUsageService.consume(
            db, account_id=account_id, feature_code="b2b_api_access", quota=quota, amount=2
        )
        db.commit()

    assert state.used == 2
    assert state.remaining == 8
    assert state.exhausted is False

    with SessionLocal() as db:
        from sqlalchemy import select

        counter = db.scalar(
            select(EnterpriseFeatureUsageCounterModel).where(
                EnterpriseFeatureUsageCounterModel.enterprise_account_id == account_id
            )
        )
        assert counter is not None
        assert counter.used_count == 2


def test_enterprise_quota_consume_until_exhausted() -> None:
    _cleanup_tables()
    account_id = _create_enterprise_account("exhaust@example.com")
    quota = QuotaDefinition(
        quota_key="test_calls",
        quota_limit=5,
        period_unit=PeriodUnit.MONTH,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    )

    with SessionLocal() as db:
        # First consume OK
        EnterpriseQuotaUsageService.consume(
            db, account_id=account_id, feature_code="b2b_api_access", quota=quota, amount=3
        )
        # Second consume OK (edge)
        EnterpriseQuotaUsageService.consume(
            db, account_id=account_id, feature_code="b2b_api_access", quota=quota, amount=2
        )
        db.commit()

    with SessionLocal() as db:
        try:
            EnterpriseQuotaUsageService.consume(
                db, account_id=account_id, feature_code="b2b_api_access", quota=quota, amount=1
            )
            assert False, "Should have raised QuotaExhaustedError"
        except QuotaExhaustedError as exc:
            assert exc.quota_key == "test_calls"
            assert exc.used == 5
            assert exc.limit == 5


def test_enterprise_quota_window_isolation_by_month() -> None:
    _cleanup_tables()
    account_id = _create_enterprise_account("window@example.com")
    quota = QuotaDefinition(
        quota_key="test_calls",
        quota_limit=100,
        period_unit=PeriodUnit.MONTH,
        period_value=1,
        reset_mode=ResetMode.CALENDAR,
    )

    # Usage in February
    dt_feb = datetime(2026, 2, 15, tzinfo=timezone.utc)
    # Usage in March
    dt_march = datetime(2026, 3, 5, tzinfo=timezone.utc)

    with SessionLocal() as db:
        EnterpriseQuotaUsageService.consume(
            db,
            account_id=account_id,
            feature_code="b2b_api_access",
            quota=quota,
            amount=10,
            ref_dt=dt_feb,
        )
        EnterpriseQuotaUsageService.consume(
            db,
            account_id=account_id,
            feature_code="b2b_api_access",
            quota=quota,
            amount=25,
            ref_dt=dt_march,
        )
        db.commit()

    with SessionLocal() as db:
        state_feb = EnterpriseQuotaUsageService.get_usage(
            db, account_id=account_id, feature_code="b2b_api_access", quota=quota, ref_dt=dt_feb
        )
        state_march = EnterpriseQuotaUsageService.get_usage(
            db, account_id=account_id, feature_code="b2b_api_access", quota=quota, ref_dt=dt_march
        )

    assert state_feb.used == 10
    assert state_march.used == 25
