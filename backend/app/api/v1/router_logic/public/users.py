"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

import logging
import random
from threading import Lock
from time import monotonic

from fastapi import APIRouter

VALID_ASTROLOGER_PROFILES = {"standard", "vedique", "humaniste", "karmique", "psychologique"}
router = APIRouter(prefix="/v1/users", tags=["users"])
logger = logging.getLogger(__name__)
_INCONSISTENT_LOG_WINDOW_SECONDS = 60.0
_INCONSISTENT_LOG_ALWAYS_PER_WINDOW = 10
_INCONSISTENT_LOG_SAMPLING_RATIO = 0.01
_inconsistent_log_sampling_lock = Lock()
_inconsistent_log_sampling_state = {"window_start": monotonic(), "count": 0}
from app.api.v1.schemas.routers.public.users import *


def _normalize_metric_label(value: str | None) -> str:
    if value is None:
        return "unknown"
    normalized = value.strip().lower()
    if not normalized:
        return "unknown"
    return normalized.replace("|", "_").replace("=", "_")


def _natal_inconsistent_metric_name(
    *,
    reference_version: str | None,
    house_system: str | None,
    planet_code: str | None,
) -> str:
    return (
        "natal_inconsistent_result_total"
        f"|reference_version={_normalize_metric_label(reference_version)}"
        f"|house_system={_normalize_metric_label(house_system)}"
        f"|planet_code={_normalize_metric_label(planet_code)}"
    )


def _should_log_inconsistent_result_event() -> bool:
    with _inconsistent_log_sampling_lock:
        now = monotonic()
        window_start = _inconsistent_log_sampling_state["window_start"]
        if (now - window_start) >= _INCONSISTENT_LOG_WINDOW_SECONDS:
            _inconsistent_log_sampling_state["window_start"] = now
            _inconsistent_log_sampling_state["count"] = 0
        _inconsistent_log_sampling_state["count"] += 1
        count = _inconsistent_log_sampling_state["count"]
    if count <= _INCONSISTENT_LOG_ALWAYS_PER_WINDOW:
        return True
    return random.random() < _INCONSISTENT_LOG_SAMPLING_RATIO
