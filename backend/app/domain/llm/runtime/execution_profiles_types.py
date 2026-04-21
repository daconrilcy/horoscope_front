"""Canonical runtime execution profile type definitions."""

from __future__ import annotations

from typing import Literal

# AC4: Stable internal profile abstractions (Story 66.11)
ReasoningProfile = Literal["off", "light", "medium", "deep"]
VerbosityProfile = Literal["concise", "balanced", "detailed"]
OutputMode = Literal["free_text", "structured_json"]
ToolMode = Literal["none", "optional", "required"]

__all__ = ["OutputMode", "ReasoningProfile", "ToolMode", "VerbosityProfile"]
