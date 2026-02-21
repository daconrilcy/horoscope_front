from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.billing import (
    BillingPlanModel,
    PaymentAttemptModel,
    SubscriptionPlanChangeModel,
    UserSubscriptionModel,
)
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService
from app.services.billing_service import (
    BillingService,
    BillingServiceError,
    CheckoutPayload,
    PlanChangePayload,
)


def _cleanup_tables() -> None:
    BillingService.reset_subscription_status_cache()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(SubscriptionPlanChangeModel))
        db.execute(delete(PaymentAttemptModel))
        db.execute(delete(UserSubscriptionModel))
        db.execute(delete(BillingPlanModel))
        db.execute(delete(UserModel))
        db.commit()


def _create_user_id() -> int:
    with SessionLocal() as db:
        auth = AuthService.register(
            db,
            email="billing-user@example.com",
            password="strong-pass-123",
            role="user",
        )
        db.commit()
        return auth.user.id


def test_checkout_success_activates_subscription() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        BillingService.ensure_entry_plan(db)
        result = BillingService.create_checkout(
            db,
            user_id=user_id,
            payload=CheckoutPayload(
                plan_code="basic-entry",
                payment_method_token="pm_card_ok",
                idempotency_key="checkout-success-1",
            ),
            request_id="test-checkout-success",
        )
        db.commit()

    assert result.subscription.status == "active"
    assert result.subscription.plan is not None
    assert result.subscription.plan.code == "basic-entry"
    assert result.payment_status == "succeeded"


def test_checkout_failure_keeps_inactive_with_reason() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        BillingService.ensure_entry_plan(db)
        result = BillingService.create_checkout(
            db,
            user_id=user_id,
            payload=CheckoutPayload(
                plan_code="basic-entry",
                payment_method_token="pm_fail",
                idempotency_key="checkout-fail-1",
            ),
            request_id="test-checkout-fail",
        )
        db.commit()

    assert result.subscription.status == "inactive"
    assert result.subscription.failure_reason is not None
    assert "declined" in result.subscription.failure_reason
    assert result.payment_status == "failed"


def test_checkout_is_idempotent_with_same_idempotency_key() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        BillingService.ensure_entry_plan(db)
        first = BillingService.create_checkout(
            db,
            user_id=user_id,
            payload=CheckoutPayload(
                plan_code="basic-entry",
                payment_method_token="pm_card_ok",
                idempotency_key="checkout-idempotent-1",
            ),
            request_id="test-checkout-idempotent-1",
        )
        second = BillingService.create_checkout(
            db,
            user_id=user_id,
            payload=CheckoutPayload(
                plan_code="basic-entry",
                payment_method_token="pm_fail",
                idempotency_key="checkout-idempotent-1",
            ),
            request_id="test-checkout-idempotent-2",
        )
        db.commit()

    assert first.payment_attempt_id == second.payment_attempt_id
    assert second.subscription.status == "active"
    assert second.payment_status == "succeeded"


def test_retry_checkout_activates_after_initial_failure() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        BillingService.ensure_entry_plan(db)
        first = BillingService.create_checkout(
            db,
            user_id=user_id,
            payload=CheckoutPayload(
                plan_code="basic-entry",
                payment_method_token="pm_fail",
                idempotency_key="checkout-retry-fail-1",
            ),
            request_id="test-retry-fail",
        )
        retried = BillingService.retry_checkout(
            db,
            user_id=user_id,
            payload=CheckoutPayload(
                plan_code="basic-entry",
                payment_method_token="pm_card_ok",
                idempotency_key="checkout-retry-ok-1",
            ),
            request_id="test-retry-ok",
        )
        db.commit()

    assert first.subscription.status == "inactive"
    assert retried.subscription.status == "active"
    assert retried.payment_status == "succeeded"


def test_checkout_rejects_when_already_active() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        BillingService.ensure_entry_plan(db)
        BillingService.create_checkout(
            db,
            user_id=user_id,
            payload=CheckoutPayload(
                plan_code="basic-entry",
                payment_method_token="pm_card_ok",
                idempotency_key="checkout-already-active-1",
            ),
            request_id="test-already-active-1",
        )
        try:
            BillingService.create_checkout(
                db,
                user_id=user_id,
                payload=CheckoutPayload(
                    plan_code="basic-entry",
                    payment_method_token="pm_card_ok",
                    idempotency_key="checkout-already-active-2",
                ),
                request_id="test-already-active-2",
            )
        except BillingServiceError as error:
            assert error.code == "subscription_already_active"
        else:
            raise AssertionError("Expected BillingServiceError")


def test_change_plan_updates_active_subscription_and_quota_limit() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        BillingService.create_checkout(
            db,
            user_id=user_id,
            payload=CheckoutPayload(
                plan_code="basic-entry",
                payment_method_token="pm_card_ok",
                idempotency_key="checkout-before-change-1",
            ),
            request_id="test-change-plan-checkout",
        )
        result = BillingService.change_subscription_plan(
            db,
            user_id=user_id,
            payload=PlanChangePayload(
                target_plan_code="premium-unlimited",
                idempotency_key="plan-change-1",
            ),
            request_id="test-change-plan",
        )
        db.commit()

    assert result.subscription.status == "active"
    assert result.subscription.plan is not None
    assert result.subscription.plan.code == "premium-unlimited"
    assert result.subscription.plan.daily_message_limit == 1000
    assert result.previous_plan_code == "basic-entry"
    assert result.target_plan_code == "premium-unlimited"
    assert result.plan_change_status == "succeeded"


def test_change_plan_is_idempotent_for_same_idempotency_key() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        BillingService.create_checkout(
            db,
            user_id=user_id,
            payload=CheckoutPayload(
                plan_code="basic-entry",
                payment_method_token="pm_card_ok",
                idempotency_key="checkout-before-change-idempotent",
            ),
            request_id="test-change-plan-idempotent-checkout",
        )
        first = BillingService.change_subscription_plan(
            db,
            user_id=user_id,
            payload=PlanChangePayload(
                target_plan_code="premium-unlimited",
                idempotency_key="plan-change-idempotent-1",
            ),
            request_id="test-change-plan-idempotent-1",
        )
        second = BillingService.change_subscription_plan(
            db,
            user_id=user_id,
            payload=PlanChangePayload(
                target_plan_code="basic-entry",
                idempotency_key="plan-change-idempotent-1",
            ),
            request_id="test-change-plan-idempotent-2",
        )
        db.commit()

    assert first.plan_change_id == second.plan_change_id
    assert second.target_plan_code == "premium-unlimited"
    assert second.subscription.plan is not None
    assert second.subscription.plan.code == "premium-unlimited"


def test_change_plan_rejects_invalid_target_plan() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        BillingService.create_checkout(
            db,
            user_id=user_id,
            payload=CheckoutPayload(
                plan_code="basic-entry",
                payment_method_token="pm_card_ok",
                idempotency_key="checkout-before-invalid-change",
            ),
            request_id="test-change-plan-invalid-checkout",
        )
        try:
            BillingService.change_subscription_plan(
                db,
                user_id=user_id,
                payload=PlanChangePayload(
                    target_plan_code="unknown-plan",
                    idempotency_key="plan-change-invalid-1",
                ),
                request_id="test-change-plan-invalid",
            )
        except BillingServiceError as error:
            assert error.code == "invalid_target_plan"
        else:
            raise AssertionError("Expected BillingServiceError")


def test_change_plan_rejects_when_no_active_subscription() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        try:
            BillingService.change_subscription_plan(
                db,
                user_id=user_id,
                payload=PlanChangePayload(
                    target_plan_code="premium-unlimited",
                    idempotency_key="plan-change-no-active-1",
                ),
                request_id="test-change-plan-no-active",
            )
        except BillingServiceError as error:
            assert error.code == "no_active_subscription"
        else:
            raise AssertionError("Expected BillingServiceError")


def test_change_plan_rejects_duplicate_target_plan() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        BillingService.create_checkout(
            db,
            user_id=user_id,
            payload=CheckoutPayload(
                plan_code="basic-entry",
                payment_method_token="pm_card_ok",
                idempotency_key="checkout-before-duplicate-change",
            ),
            request_id="test-change-plan-duplicate-checkout",
        )
        try:
            BillingService.change_subscription_plan(
                db,
                user_id=user_id,
                payload=PlanChangePayload(
                    target_plan_code="basic-entry",
                    idempotency_key="plan-change-duplicate-target-1",
                ),
                request_id="test-change-plan-duplicate-target",
            )
        except BillingServiceError as error:
            assert error.code == "duplicate_plan_change"
        else:
            raise AssertionError("Expected BillingServiceError")


def test_subscription_status_cache_is_refreshed_after_plan_change() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        BillingService.create_checkout(
            db,
            user_id=user_id,
            payload=CheckoutPayload(
                plan_code="basic-entry",
                payment_method_token="pm_card_ok",
                idempotency_key="checkout-cache-refresh-1",
            ),
            request_id="test-cache-refresh-checkout",
        )
        before = BillingService.get_subscription_status_readonly(db, user_id=user_id)
        assert before.plan is not None
        assert before.plan.code == "basic-entry"

        changed = BillingService.change_subscription_plan(
            db,
            user_id=user_id,
            payload=PlanChangePayload(
                target_plan_code="premium-unlimited",
                idempotency_key="plan-change-cache-refresh-1",
            ),
            request_id="test-cache-refresh-change",
        )
        after = BillingService.get_subscription_status_readonly(db, user_id=user_id)
        db.commit()

    assert changed.subscription.plan is not None
    assert changed.subscription.plan.code == "premium-unlimited"
    assert after.plan is not None
    assert after.plan.code == "premium-unlimited"
