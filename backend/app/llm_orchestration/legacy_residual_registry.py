"""Compatibility shim vers le registre residual canonique."""

from app.domain.llm.governance.legacy_residual_registry import (
    DeprecatedUseCaseRecord,
    GovernedAliasRecord,
    LegacyFallbackPathRecord,
    LegacyResidualRegistryRoot,
    assert_deprecated_use_case_registered,
    build_governance_matrix_projection,
    effective_progressive_blocklist,
    extract_doc_registry_version,
    get_fallback_path_record,
    get_registry_schema_version,
    load_legacy_residual_registry,
    parse_progressive_blocklist_env,
    render_maintenance_report,
    validate_doc_registry_version,
    validate_registry_integrity,
)

__all__ = [
    "DeprecatedUseCaseRecord",
    "GovernedAliasRecord",
    "LegacyFallbackPathRecord",
    "LegacyResidualRegistryRoot",
    "assert_deprecated_use_case_registered",
    "build_governance_matrix_projection",
    "effective_progressive_blocklist",
    "extract_doc_registry_version",
    "get_fallback_path_record",
    "get_registry_schema_version",
    "load_legacy_residual_registry",
    "parse_progressive_blocklist_env",
    "render_maintenance_report",
    "validate_doc_registry_version",
    "validate_registry_integrity",
]
