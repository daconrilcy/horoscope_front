"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter

router = APIRouter()
logger = logging.getLogger(__name__)
from app.api.v1.schemas.routers.admin.llm.releases import *


def _validate_timezone_aware_timestamp(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("generated_at must include an explicit timezone offset.")
    return value
