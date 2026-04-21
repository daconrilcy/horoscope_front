from __future__ import annotations

from typing import Literal

from app.domain.llm.governance.prompt_governance_registry import (
    LEGACY_DAILY_FEATURE,
    LEGACY_NATAL_FEATURE,
    NATAL_CANONICAL_FEATURE,
    get_prompt_governance_registry,
)

# AC1: Canonical feature identifier for the natal domain (stable API).
# Source of truth: prompt_governance_registry.json.
_reg = get_prompt_governance_registry()

NATAL_SUBFEATURES = _reg.natal_subfeatures_canonical_list()
NATAL_SUBFEATURE_MAPPING = _reg.natal_subfeature_legacy_mapping()
SUPPORTED_FAMILIES = set(_reg.canonical_families)


def is_supported_feature(feature: str | None) -> bool:
    if not feature:
        return False
    return normalize_feature(feature) in SUPPORTED_FAMILIES


def normalize_feature(feature: str) -> str:
    return _reg.normalize_feature(feature)


def normalize_subfeature(feature: str, subfeature: str | None) -> str | None:
    return _reg.normalize_subfeature(feature, subfeature)


def is_nominal_feature_allowed(feature: str) -> bool:
    if not feature:
        return True
    feature = feature.strip()
    return feature not in {LEGACY_NATAL_FEATURE, LEGACY_DAILY_FEATURE}


def assert_nominal_feature_allowed(feature: str) -> None:
    if not is_nominal_feature_allowed(feature):
        msg = f"Feature identifier '{feature}' is forbidden for nominal use."
        if feature == LEGACY_NATAL_FEATURE:
            msg += f" Use feature='{NATAL_CANONICAL_FEATURE}' instead."
        elif feature == LEGACY_DAILY_FEATURE:
            msg += " Use feature='horoscope_daily' instead."
        raise ValueError(msg)


def is_natal_subfeature_canonical(subfeature: str) -> bool:
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
