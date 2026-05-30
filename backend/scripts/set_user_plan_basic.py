"""Script local : bascule un utilisateur B2C vers le plan basic."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.config import settings
from app.infra.db.models.billing import BillingPlanModel, UserSubscriptionModel
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal
from app.services.billing.service import BillingService


def set_user_plan_basic(email: str) -> None:
    """Met à jour entitlement_plan et l'abonnement actif pour l'email donné."""
    with SessionLocal() as db:
        user = db.scalar(select(UserModel).where(UserModel.email == email))
        if user is None:
            raise SystemExit(f"Utilisateur introuvable: {email}")

        BillingService.ensure_default_plans(db)
        basic_plan = db.scalar(select(BillingPlanModel).where(BillingPlanModel.code == "basic"))
        if basic_plan is None:
            raise SystemExit("Plan billing 'basic' introuvable après ensure_default_plans")

        now = datetime.now(timezone.utc)
        period_end = now + timedelta(days=30)

        profile = db.scalar(
            select(StripeBillingProfileModel).where(StripeBillingProfileModel.user_id == user.id)
        )
        if profile is None:
            profile = StripeBillingProfileModel(
                user_id=user.id,
                stripe_customer_id=f"cus_local_{user.id}",
                stripe_subscription_id=f"sub_local_{user.id}",
                subscription_status="active",
                entitlement_plan="basic",
                current_period_start=now,
                current_period_end=period_end,
            )
            db.add(profile)
        else:
            profile.subscription_status = "active"
            profile.entitlement_plan = "basic"
            profile.current_period_start = now
            profile.current_period_end = period_end
            profile.scheduled_plan_code = None
            profile.scheduled_change_effective_at = None
            profile.pending_cancellation_effective_at = None

        subscription = db.scalar(
            select(UserSubscriptionModel).where(UserSubscriptionModel.user_id == user.id)
        )
        if subscription is None:
            subscription = UserSubscriptionModel(
                user_id=user.id,
                plan_id=basic_plan.id,
                status="active",
                started_at=now,
            )
            db.add(subscription)
        else:
            subscription.plan_id = basic_plan.id
            subscription.status = "active"

        db.commit()
        print(
            f"OK user_id={user.id} email={email} entitlement_plan=basic "
            f"database={settings.database_url}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--email",
        default="daconrilcy@hotmail.com",
        help="Email de l'utilisateur à passer en basic",
    )
    args = parser.parse_args()
    set_user_plan_basic(args.email)


if __name__ == "__main__":
    main()
