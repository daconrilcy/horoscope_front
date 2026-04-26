"""Logique non HTTP extraite du routeur API v1 correspondant."""

# ruff: noqa: E402, F403, F405
from __future__ import annotations

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/admin/logs", tags=["admin-logs"])


def _mask_email(email: str) -> str:
    local_part, separator, domain = email.partition("@")
    if not separator:
        return email

    visible_prefix = local_part[:3]
    return f"{visible_prefix}***@{domain}"
