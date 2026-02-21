from datetime import UTC, datetime, timedelta

from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.billing import (
    BillingPlanModel,
    PaymentAttemptModel,
    UserDailyQuotaUsageModel,
    UserSubscriptionModel,
)
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService
from app.services.billing_service import BillingService, CheckoutPayload
from app.services.quota_service import QuotaService, QuotaServiceError


def _cleanup_tables() -> None:
    BillingService.reset_subscription_status_cache()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(UserDailyQuotaUsageModel))
        db.execute(delete(PaymentAttemptModel))
        db.execute(delete(UserSubscriptionModel))
        db.execute(delete(BillingPlanModel))
        db.execute(delete(UserModel))
        db.commit()


def _create_user_id() -> int:
    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email="quota-user@example.com",
            password="strong-pass-123",
            role="user",
        )
        db.commit()
        return auth.user.id


def _activate_basic_subscription(user_id: int) -> None:
    with SessionLocal() as db:
        BillingService.create_checkout(
            db,
            user_id=user_id,
            payload=CheckoutPayload(
                plan_code="basic-entry",
                payment_method_token="pm_card_ok",
                idempotency_key="quota-activate-1",
            ),
            request_id="quota-activate-1",
        )
        db.commit()


def test_get_quota_status_starts_with_full_remaining() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _activate_basic_subscription(user_id)
    with SessionLocal() as db:
        status = QuotaService.get_quota_status(db, user_id=user_id)
    assert status.limit == 5
    assert status.consumed == 0
    assert status.remaining == 5
    assert status.blocked is False


def test_consume_quota_increments_and_blocks_at_limit() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _activate_basic_subscription(user_id)
    with SessionLocal() as db:
        for _ in range(5):
            status = QuotaService.consume_quota_or_raise(
                db,
                user_id=user_id,
                request_id="quota-consume-ok",
            )
        assert status.consumed == 5
        assert status.remaining == 0
        assert status.blocked is True
        try:
            QuotaService.consume_quota_or_raise(
                db,
                user_id=user_id,
                request_id="quota-consume-over",
            )
        except QuotaServiceError as error:
            assert error.code == "quota_exceeded"
            assert error.details["limit"] == "5"
            assert error.details["remaining"] == "0"
        else:
            raise AssertionError("Expected QuotaServiceError")


def test_get_quota_status_requires_active_subscription() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        try:
            QuotaService.get_quota_status(db, user_id=user_id)
        except QuotaServiceError as error:
            assert error.code == "no_active_subscription"
        else:
            raise AssertionError("Expected QuotaServiceError")


def test_get_quota_status_reuses_preloaded_subscription(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _cleanup_tables()
    user_id = _create_user_id()
    _activate_basic_subscription(user_id)
    with SessionLocal() as db:
        preloaded = BillingService.get_subscription_status(db, user_id=user_id)

        def _forbid_status_fetch(*args: object, **kwargs: object) -> object:
            raise AssertionError("BillingService.get_subscription_status should not be called")

        monkeypatch.setattr(BillingService, "get_subscription_status", _forbid_status_fetch)
        status = QuotaService.get_quota_status(db, user_id=user_id, subscription=preloaded)

    assert status.limit == 5
    assert status.remaining == 5


def test_quota_reset_uses_utc_day_boundary() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    _activate_basic_subscription(user_id)
    with SessionLocal() as db:
        yesterday = (datetime.now(UTC) - timedelta(days=1)).date()
        db.add(
            UserDailyQuotaUsageModel(
                user_id=user_id,
                quota_date=yesterday,
                used_count=5,
            )
        )
        db.commit()
        status = QuotaService.get_quota_status(db, user_id=user_id)
    assert status.quota_date != yesterday
    assert status.consumed == 0
    assert status.remaining == 5
