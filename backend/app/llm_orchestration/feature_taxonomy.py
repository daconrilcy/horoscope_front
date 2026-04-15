from __future__ import annotations

from typing import Literal

from app.llm_orchestration.prompt_governance_registry import (
    LEGACY_DAILY_FEATURE,
    LEGACY_NATAL_FEATURE,
    NATAL_CANONICAL_FEATURE,
    get_prompt_governance_registry,
)

# AC1: Canonical feature identifier for the natal domain (stable API).
# Valeurs nominales / sous-familles : registre central JSON (Story 66.42).

_reg = get_prompt_governance_registry()

NATAL_SUBFEATURES = _reg.natal_subfeatures_canonical_list()

NATAL_SUBFEATURE_MAPPING = _reg.natal_subfeature_legacy_mapping()

SUPPORTED_FAMILIES = set(_reg.canonical_families)


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
    Source de vérité : prompt_governance_registry.json (Story 66.42).
    """
    return _reg.normalize_feature(feature)


def normalize_subfeature(feature: str, subfeature: str | None) -> str | None:
    """
    Normalize a subfeature identifier within a domain (Task 4).
    """
    return _reg.normalize_subfeature(feature, subfeature)


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
