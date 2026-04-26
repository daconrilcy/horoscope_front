"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import or_

from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.user import UserModel

logger = logging.getLogger(__name__)


def _apply_user_plan_filter(stmt: Any, plan_filter: str | None) -> Any:
    if not plan_filter:
        return stmt

    if plan_filter == "free":
        return stmt.outerjoin(
            StripeBillingProfileModel,
            StripeBillingProfileModel.user_id == UserModel.id,
        ).where(
            or_(
                StripeBillingProfileModel.user_id.is_(None),
                StripeBillingProfileModel.entitlement_plan == "free",
            )
        )

    return stmt.join(
        StripeBillingProfileModel,
        StripeBillingProfileModel.user_id == UserModel.id,
    ).where(StripeBillingProfileModel.entitlement_plan == plan_filter)
