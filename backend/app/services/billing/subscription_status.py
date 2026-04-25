"""Construit le statut d abonnement a partir du catalogue, du quota et du snapshot Stripe."""

from __future__ import annotations

import logging
import sys

from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models.billing import BillingPlanModel
from app.services.billing.models import FREE_PLAN_CODE, SubscriptionStatusData
from app.services.billing.plan_catalog import (
    ensure_default_plans,
    get_default_plan_data_by_code,
    get_plan_by_code,
    to_plan_data,
)
from app.services.billing.quota_runtime import resolve_current_quota
from app.services.billing.stripe_provider import (
    get_latest_subscription,
    get_stripe_billing_profile,
    has_usable_stripe_snapshot,
)
from app.services.billing.subscription_cache import (
    get_cached_subscription_status,
    set_cached_subscription_status,
)

logger = logging.getLogger(__name__)


def is_pytest_runtime() -> bool:
    """Indique si le runtime courant est pilote par pytest."""
    return "pytest" in sys.modules


def should_default_missing_subscription_to_free() -> bool:
    """Autorise le plan free implicite en environnement local hors pytest."""
    return not is_pytest_runtime() and settings.app_env in {"development", "dev", "local"}


def to_stripe_subscription_data(
    db: Session,
    *,
    user_id: int,
    feature_code: str,
    profile,
) -> SubscriptionStatusData:
    """Convertit un snapshot Stripe en statut runtime exploitable."""
    is_active = profile.subscription_status in {"active", "trialing"}
    exposed_status = "active" if is_active else "inactive"
    app_plan_code = profile.entitlement_plan

    show_plan = app_plan_code and (is_active or app_plan_code not in {"", "free"})
    plan_data = None
    if show_plan:
        plan_model = get_plan_by_code(db, app_plan_code)
        plan_data = (
            to_plan_data(plan_model)
            if plan_model is not None
            else get_default_plan_data_by_code(app_plan_code)
        )

    scheduled_plan_data = None
    if profile.scheduled_plan_code:
        scheduled_model = get_plan_by_code(db, profile.scheduled_plan_code)
        scheduled_plan_data = (
            to_plan_data(scheduled_model)
            if scheduled_model is not None
            else get_default_plan_data_by_code(profile.scheduled_plan_code)
        )

    current_quota = None
    if is_active and app_plan_code:
        try:
            current_quota = resolve_current_quota(
                db,
                user_id=user_id,
                feature_code=feature_code,
                plan_code=app_plan_code,
            )
        except Exception:
            logger.warning("Failed to resolve current_quota for user=%s", user_id)

    return SubscriptionStatusData(
        status=exposed_status,
        subscription_status=profile.subscription_status,
        plan=plan_data,
        scheduled_plan=scheduled_plan_data,
        change_effective_at=profile.scheduled_change_effective_at,
        cancel_at_period_end=profile.cancel_at_period_end,
        current_period_end=profile.current_period_end,
        failure_reason=None,
        current_quota=current_quota,
        updated_at=profile.updated_at,
    )


def get_subscription_status(
    db: Session,
    *,
    user_id: int,
    feature_code: str,
) -> SubscriptionStatusData:
    """Retourne le statut d abonnement canonique avec priorite Stripe."""
    cached = get_cached_subscription_status(user_id)
    if cached is not None:
        return cached

    ensure_default_plans(db)
    stripe_profile = get_stripe_billing_profile(db, user_id=user_id)
    if has_usable_stripe_snapshot(stripe_profile):
        payload = to_stripe_subscription_data(
            db,
            user_id=user_id,
            feature_code=feature_code,
            profile=stripe_profile,
        )
        set_cached_subscription_status(user_id, payload)
        return payload

    latest = get_latest_subscription(db, user_id=user_id)
    if latest is not None:
        plan_model = db.get(BillingPlanModel, latest.plan_id)
        payload = SubscriptionStatusData(
            status="active" if latest.status == "active" else "inactive",
            subscription_status=None,
            plan=to_plan_data(plan_model) if plan_model is not None else None,
            failure_reason=latest.failure_reason,
            updated_at=latest.updated_at,
        )
        set_cached_subscription_status(user_id, payload)
        return payload

    if should_default_missing_subscription_to_free():
        payload = SubscriptionStatusData(
            status="active",
            subscription_status=None,
            plan=get_default_plan_data_by_code(FREE_PLAN_CODE),
            failure_reason=None,
            updated_at=None,
        )
        set_cached_subscription_status(user_id, payload)
        return payload

    payload = SubscriptionStatusData(
        status="inactive",
        subscription_status=None,
        plan=None,
        failure_reason=None,
        updated_at=None,
    )
    set_cached_subscription_status(user_id, payload)
    return payload


def resolve_runtime_billing_status(subscription: SubscriptionStatusData) -> str:
    """Retourne le statut billing canonique expose au runtime."""
    if subscription.subscription_status is not None:
        return subscription.subscription_status
    if subscription.plan is None:
        return "none"
    return subscription.status


def resolve_runtime_plan_code(subscription: SubscriptionStatusData) -> str:
    """Retourne le plan canonique utilise cote runtime."""
    if subscription.plan is None:
        return "none"
    return subscription.plan.code
