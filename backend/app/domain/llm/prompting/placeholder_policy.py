"""Canonical placeholder policy definitions."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel


class PlaceholderDef(BaseModel):
    name: str
    classification: Literal["required", "optional", "optional_with_fallback"]
    fallback: Optional[str] = None


# AC11: Placeholder Policy (Story 66.13 D3)
class PlaceholderPolicy(BaseModel):
    blocking_features: list[str] = ["natal", "guidance_contextual"]


PLACEHOLDER_POLICY = PlaceholderPolicy()

__all__ = ["PLACEHOLDER_POLICY", "PlaceholderDef", "PlaceholderPolicy"]
