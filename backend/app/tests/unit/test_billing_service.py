from sqlalchemy import delete

from app.infra.db.base import Base
from app.infra.db.models.billing import (
    BillingPlanModel,
    UserSubscriptionModel,
)
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal, engine
from app.services.auth_service import AuthService
from app.services.billing.service import (
    BillingService,
)


def _cleanup_tables() -> None:
    BillingService.reset_subscription_status_cache()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.execute(delete(UserSubscriptionModel))
        db.execute(delete(BillingPlanModel))
        db.execute(delete(StripeBillingProfileModel))
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


def test_get_subscription_status_exposes_stripe_subscription_status() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        BillingService.ensure_default_plans(db)
        db.add(
            StripeBillingProfileModel(
                user_id=user_id,
                subscription_status="trialing",
                entitlement_plan="basic",
            )
        )
        db.commit()

        status = BillingService.get_subscription_status(db, user_id=user_id)

    assert status.status == "active"
    assert status.subscription_status == "trialing"
    assert status.plan is not None
    assert status.plan.code == "basic"


def test_get_subscription_status_fallback_to_legacy_when_no_stripe_profile() -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        plans = BillingService.ensure_default_plans(db)
        plan = plans["basic"]
        db.add(
            UserSubscriptionModel(
                user_id=user_id,
                plan_id=plan.id,
                status="active",
            )
        )
        db.commit()

        status = BillingService.get_subscription_status(db, user_id=user_id)

    assert status.status == "active"
    assert status.subscription_status is None
    assert status.plan is not None
    assert status.plan.code == "basic"


def test_readonly_status_ignores_non_usable_stripe_profile_when_legacy_subscription_exists() -> (
    None
):
    _cleanup_tables()
    user_id = _create_user_id()
    with SessionLocal() as db:
        plans = BillingService.ensure_default_plans(db)
        plan = plans["basic"]
        db.add(
            UserSubscriptionModel(
                user_id=user_id,
                plan_id=plan.id,
                status="active",
                failure_reason=None,
            )
        )
        db.add(
            StripeBillingProfileModel(
                user_id=user_id,
                stripe_customer_id="cus_empty_profile",
                subscription_status=None,
                entitlement_plan="free",
            )
        )
        db.commit()

        status = BillingService.get_subscription_status_readonly(db, user_id=user_id)

    assert status.status == "active"
    assert status.subscription_status is None
    assert status.plan is not None
    assert status.plan.code == "basic"


def test_get_subscription_status_defaults_to_free_in_local_runtime(monkeypatch) -> None:
    _cleanup_tables()
    user_id = _create_user_id()
    monkeypatch.setattr("app.services.billing.service.settings.app_env", "development")
    monkeypatch.setattr("app.services.billing.subscription_status.is_pytest_runtime", lambda: False)

    with SessionLocal() as db:
        status = BillingService.get_subscription_status(db, user_id=user_id)

    assert status.status == "active"
    assert status.subscription_status is None
    assert status.plan is not None
    assert status.plan.code == "free"
