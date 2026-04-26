"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

import logging
from typing import Any

from fastapi.responses import JSONResponse

from app.api.v1.errors import api_error_response
from app.api.v1.schemas.routers.public.natal_interpretation import (
    NatalChartLongEntitlementInfo,
)
from app.services.entitlement.natal_chart_long_entitlement_gate import (
    NatalChartLongEntitlementResult,
)

logger = logging.getLogger(__name__)


def _create_error_response(
    status_code: int,
    code: str,
    message: str,
    request_id: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    return api_error_response(
        status_code=status_code,
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
