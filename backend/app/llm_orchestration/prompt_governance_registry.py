"""Compatibility shim vers le registre de gouvernance canonique."""

from app.domain.llm.governance.prompt_governance_registry import (
    DEPRECATED_USE_CASE_MAPPING,
    LEGACY_DAILY_FEATURE,
    LEGACY_NATAL_FEATURE,
    NATAL_CANONICAL_FEATURE,
    PLACEHOLDER_ALLOWLIST,
    SUPPORTED_EXCEPTION_RULE_IDS,
    PlaceholderEntry,
    PlaceholderGovernanceViolation,
    PromptGovernanceRegistry,
    PromptGovernanceRegistryData,
    UseCaseDeprecationTarget,
    format_placeholder_violation_report,
    get_deprecated_use_case_mapping,
    get_prompt_governance_registry,
)

__all__ = [
    "DEPRECATED_USE_CASE_MAPPING",
    "LEGACY_DAILY_FEATURE",
    "LEGACY_NATAL_FEATURE",
    "NATAL_CANONICAL_FEATURE",
    "PLACEHOLDER_ALLOWLIST",
    "PromptGovernanceRegistry",
    "PromptGovernanceRegistryData",
    "PlaceholderEntry",
    "PlaceholderGovernanceViolation",
    "SUPPORTED_EXCEPTION_RULE_IDS",
    "UseCaseDeprecationTarget",
    "format_placeholder_violation_report",
    "get_deprecated_use_case_mapping",
    "get_prompt_governance_registry",
]
