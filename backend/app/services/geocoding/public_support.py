"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402
from __future__ import annotations

import logging
import math
import re
from typing import Any

from app.api.dependencies.auth import (
    AuthenticatedUser,
)
from app.core.config import settings
from app.core.exceptions import ApplicationError
from app.services.geocoding_service import (
    GeocodingSearchResult,
)

logger = logging.getLogger(__name__)


def _raise_error(
    *,
    request_id: str,
    code: str,
    message: str,
    details: dict[str, Any],
    **_: Any,
) -> Any:
    raise ApplicationError(
        request_id=request_id,
        code=code,
        message=message,
        details=details,
    )


def _normalize_query(q: str) -> str:
    """Trim et collapse des espaces multiples."""
    return re.sub(r"\s+", " ", q.strip())


def _result_to_dict(r: GeocodingSearchResult) -> dict[str, Any]:
    return r.model_dump(by_alias=True)


def _resolved_place_to_dict(model: Any) -> dict[str, Any]:
    return {
        "id": model.id,
        "provider": model.provider,
        "provider_place_id": model.provider_place_id,
        "osm_type": model.osm_type,
        "osm_id": model.osm_id,
        "display_name": model.display_name,
        "latitude": float(model.latitude),
        "longitude": float(model.longitude),
        "timezone_iana": model.timezone_iana,
        "timezone_source": model.timezone_source,
        "timezone_confidence": model.timezone_confidence,
    }


def _validate_resolve_snapshot(snapshot: GeocodingSearchResult) -> None:
    if snapshot.provider_place_id <= 0:
        raise ValueError("snapshot provider_place_id must be positive")
    if not snapshot.display_name.strip():
        raise ValueError("snapshot display_name must not be blank")
    if not snapshot.osm_type.strip():
        raise ValueError("snapshot osm_type must not be blank")
    if snapshot.osm_id <= 0:
        raise ValueError("snapshot osm_id must be positive")
    if not math.isfinite(snapshot.lat) or snapshot.lat < -90 or snapshot.lat > 90:
        raise ValueError("snapshot lat must be within [-90, 90]")
    if not math.isfinite(snapshot.lon) or snapshot.lon < -180 or snapshot.lon > 180:
        raise ValueError("snapshot lon must be within [-180, 180]")


def _can_use_seed_token() -> bool:
    return settings.app_env in {
        "development",
        "dev",
        "local",
        "test",
        "testing",
    }


def _validate_nocache_access(
    *,
    nocache: bool,
    x_admin_token: str | None,
    current_user: AuthenticatedUser | None,
) -> tuple[bool, str, str, dict[str, Any]]:
    if not nocache:
        return True, "", "", {}
    if current_user is not None and current_user.role in {"support", "ops", "admin"}:
        return True, "", "", {}
    if current_user is not None and current_user.role not in {"support", "ops", "admin"}:
        return (
            False,
            "insufficient_role",
            "role is not allowed",
            {"required_roles": "support,ops,admin", "actual_role": current_user.role},
        )
    if _can_use_seed_token() and x_admin_token == settings.reference_seed_admin_token:
        return True, "", "", {}
    return False, "unauthorized_nocache_access", "invalid admin token", {}
