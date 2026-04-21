from __future__ import annotations

from typing import Literal

# AC1: Canonical registry of providers supported nominally by the platform.
# At this date, only 'openai' is supported for nominal production execution (Story 66.22).
NOMINAL_SUPPORTED_PROVIDERS = ["openai"]

# Literal type for static analysis
SupportedProvider = Literal["openai"]


def is_provider_supported(provider: str) -> bool:
    """
    Check if a provider is nominally supported by the platform (AC9).
    This function is the unique source of truth for the admin, validation, and gateway.
    """
    return provider in NOMINAL_SUPPORTED_PROVIDERS
