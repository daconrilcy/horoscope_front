"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

import logging
from typing import Any

from app.api.v1.schemas.routers.public.natal_interpretation import (
    NatalChartLongEntitlementInfo,
)
from app.core.exceptions import ApplicationError
from app.services.entitlement.natal_chart_long_entitlement_gate import (
    NatalChartLongEntitlementResult,
)

logger = logging.getLogger(__name__)


def _raise_error(*args: Any, details: dict[str, Any] | None = None, **_: Any) -> Any:
    """Lève une erreur applicative en acceptant l'ancien appel routeur avec statut."""
    values = list(args)
    if values and isinstance(values[0], int):
        values.pop(0)
    code = values[0] if len(values) > 0 else _["code"]
    message = values[1] if len(values) > 1 else _["message"]
    request_id = values[2] if len(values) > 2 else _["request_id"]
    raise ApplicationError(
        request_id=request_id,
        code=code,
        message=message,
        details=details,
    )


def _build_natal_entitlement_info(
    result: NatalChartLongEntitlementResult,
) -> NatalChartLongEntitlementInfo:
    if result.usage_states:
        state = result.usage_states[0]
        return NatalChartLongEntitlementInfo(
            remaining=state.remaining,
            limit=state.quota_limit,
            window_end=state.window_end,  # None pour lifetime
            variant_code=result.variant_code,
        )
    return NatalChartLongEntitlementInfo(variant_code=result.variant_code)
