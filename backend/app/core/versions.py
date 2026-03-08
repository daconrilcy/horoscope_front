from __future__ import annotations
import re
from typing import Literal

# This is the central source of truth for active business versions.
# Story 39.2: These should ideally be moved to a dynamic configuration in DB,
# but for now, we centralize them here to avoid hardcoded strings.

# Reference version governs the semantic model (planets, houses, aspects, weights)
ACTIVE_REFERENCE_VERSION: str = "2.0.0"

# Ruleset version governs calculation parameters and event types
ACTIVE_RULESET_VERSION: str = "1.0.0"  # Currently using legacy, switch to 2.0.0 later

def validate_version_format(version: str) -> bool:
    """Validate that version follows X.Y.Z format."""
    return bool(re.match(r"^\d+\.\d+\.\d+$", version))

if not validate_version_format(ACTIVE_REFERENCE_VERSION):
    raise ValueError(f"Invalid ACTIVE_REFERENCE_VERSION format: {ACTIVE_REFERENCE_VERSION}")

if not validate_version_format(ACTIVE_RULESET_VERSION):
    raise ValueError(f"Invalid ACTIVE_RULESET_VERSION format: {ACTIVE_RULESET_VERSION}")

def get_active_reference_version() -> str:
    return ACTIVE_REFERENCE_VERSION

def get_active_ruleset_version() -> str:
    return ACTIVE_RULESET_VERSION
