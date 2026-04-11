from __future__ import annotations

from typing import Literal

# AC1: Canonical feature identifier for the natal domain.
NATAL_CANONICAL_FEATURE = "natal"

# AC2: Forbidden nominal feature identifier (historical drift).
# This must never be used as a nominal feature key in registries, publication or runtime.
LEGACY_NATAL_FEATURE = "natal_interpretation"

# AC1, AC3: Canonical subfeatures for the natal domain (Task 4).
# We prefer non-prefixed names for subfeatures to avoid redundancy.
# Example: feature=natal, subfeature=interpretation instead of natal_interpretation.
NATAL_SUBFEATURES = [
    "interpretation",  # Deep dive / standard
    "short",  # Concise version
    "full",  # Exhaustive version
    "psy_profile",
    "shadow_integration",
    "leadership_workstyle",
    "creativity_joy",
    "relationship_style",
    "community_networks",
    "values_security",
    "evolution_path",
]

# Mapping for legacy subfeatures within the natal domain to their canonical counterparts.
NATAL_SUBFEATURE_MAPPING = {
    "natal_interpretation": "interpretation",
}

# Type for static analysis
NatalSubfeature = Literal[
    "interpretation",
    "short",
    "full",
    "psy_profile",
    "shadow_integration",
    "leadership_workstyle",
    "creativity_joy",
    "relationship_style",
    "community_networks",
    "values_security",
    "evolution_path",
]


# Story 66.28: Forbidden nominal feature identifier (historical drift).
# This key was previously used for the daily domain before absorption.
LEGACY_DAILY_FEATURE = "daily_prediction"


# Story 66.29: Centralized rule for supported families.
# Any feature in this set MUST use canonical assembly resolution and execution.
SUPPORTED_FAMILIES = {"chat", "guidance", "natal", "horoscope_daily"}


def is_supported_feature(feature: str | None) -> bool:
    """
    Checks if a feature belongs to the supported perimeter where
    canonical assembly is mandatory. (Story 66.29 AC6)
    """
    if not feature:
        return False
    return normalize_feature(feature) in SUPPORTED_FAMILIES


def normalize_feature(feature: str) -> str:
    """
    Normalize a feature identifier to its canonical form (AC1, AC4).
    If it's the legacy natal feature, it returns 'natal'.
    Story 66.28: daily_prediction is now an alias for horoscope_daily.
    """
    if not feature:
        return feature
    feature = feature.strip()
    if feature == LEGACY_NATAL_FEATURE:
        return NATAL_CANONICAL_FEATURE
    if feature == LEGACY_DAILY_FEATURE:
        return "horoscope_daily"
    return feature


def normalize_subfeature(feature: str, subfeature: str | None) -> str | None:
    """
    Normalize a subfeature identifier within a domain (Task 4).
    """
    if feature == NATAL_CANONICAL_FEATURE and subfeature in NATAL_SUBFEATURE_MAPPING:
        return NATAL_SUBFEATURE_MAPPING[subfeature]
    return subfeature


def is_nominal_feature_allowed(feature: str) -> bool:
    """
    Check if a feature identifier is allowed for nominal use (AC2, AC5).
    'natal_interpretation' and 'daily_prediction' are strictly forbidden as nominal features.
    """
    if not feature:
        return True
    feature = feature.strip()
    return feature not in {LEGACY_NATAL_FEATURE, LEGACY_DAILY_FEATURE}


def assert_nominal_feature_allowed(feature: str) -> None:
    """
    Raise ValueError if the feature is not allowed for nominal use (AC5).
    """
    if not is_nominal_feature_allowed(feature):
        msg = f"Feature identifier '{feature}' is forbidden for nominal use."
        if feature == LEGACY_NATAL_FEATURE:
            msg += f" Use feature='{NATAL_CANONICAL_FEATURE}' instead."
        elif feature == LEGACY_DAILY_FEATURE:
            msg += " Use feature='horoscope_daily' instead."
        raise ValueError(msg)

def is_natal_subfeature_canonical(subfeature: str) -> bool:
    """Check if a subfeature is part of the canonical natal taxonomy."""
    return subfeature in NATAL_SUBFEATURES
