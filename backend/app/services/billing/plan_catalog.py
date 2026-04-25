"""Centralise le catalogue de plans billing et sa projection runtime."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infra.db.models.billing import BillingPlanModel
from app.services.billing.models import PLAN_DEFAULTS, BillingPlanData


def to_plan_data(model: BillingPlanModel) -> BillingPlanData:
    """Convertit un modele de plan en DTO runtime."""
    defaults = PLAN_DEFAULTS.get(model.code)
    monthly_price_cents = model.monthly_price_cents
    currency = model.currency
    daily_message_limit = model.daily_message_limit
    display_name = model.display_name

    if defaults is not None:
        if monthly_price_cents <= 0:
            monthly_price_cents = int(defaults["monthly_price_cents"])
        if not currency:
            currency = str(defaults["currency"])
        if daily_message_limit <= 0:
            daily_message_limit = int(defaults["daily_message_limit"])
        if not display_name:
            display_name = str(defaults["display_name"])

    return BillingPlanData(
        code=model.code,
        display_name=display_name,
        monthly_price_cents=monthly_price_cents,
        currency=currency,
        daily_message_limit=daily_message_limit,
        is_visible_to_users=model.is_visible_to_users,
        is_available_to_users=model.is_available_to_users,
        is_active=model.is_active,
    )


def get_default_plan_data_by_code(code: str | None) -> BillingPlanData | None:
    """Construit un DTO a partir des constantes applicatives par defaut."""
    defaults = PLAN_DEFAULTS.get(code or "")
    if defaults is None:
        return None
    return BillingPlanData(
        code=code or "",
        display_name=str(defaults["display_name"]),
        monthly_price_cents=int(defaults["monthly_price_cents"]),
        currency=str(defaults["currency"]),
        daily_message_limit=int(defaults["daily_message_limit"]),
        is_visible_to_users=True,
        is_available_to_users=True,
        is_active=True,
    )


def get_plan_by_code(db: Session, code: str) -> BillingPlanModel | None:
    """Recupere un plan par son code."""
    return db.scalar(select(BillingPlanModel).where(BillingPlanModel.code == code).limit(1))


def ensure_default_plans(db: Session) -> dict[str, BillingPlanModel]:
    """Garantit la presence des plans par defaut en base."""
    plans: dict[str, BillingPlanModel] = {}
    for code, data in PLAN_DEFAULTS.items():
        existing = get_plan_by_code(db, code)
        if existing is None:
            existing = BillingPlanModel(
                code=code,
                display_name=str(data["display_name"]),
                monthly_price_cents=int(data["monthly_price_cents"]),
                currency=str(data["currency"]),
                daily_message_limit=int(data["daily_message_limit"]),
                is_visible_to_users=True,
                is_available_to_users=True,
                is_active=True,
            )
            db.add(existing)
            db.flush()
        else:
            changed = False
            if existing.monthly_price_cents <= 0:
                existing.monthly_price_cents = int(data["monthly_price_cents"])
                changed = True
            if not existing.currency:
                existing.currency = str(data["currency"])
                changed = True
            if existing.daily_message_limit <= 0:
                existing.daily_message_limit = int(data["daily_message_limit"])
                changed = True
            if not existing.display_name:
                existing.display_name = str(data["display_name"])
                changed = True
            if changed:
                db.flush()
        plans[code] = existing
    return plans
