"""Canonical governance registries entrypoint."""

from app.domain.llm.governance.legacy_residual_registry import (
    LegacyResidualRegistryRoot,
    build_governance_matrix_projection,
    get_fallback_path_record,
    get_registry_schema_version,
    load_legacy_residual_registry,
)
from app.domain.llm.governance.prompt_governance_registry import (
    PromptGovernanceRegistry,
    get_prompt_governance_registry,
)

__all__ = [
    "LegacyResidualRegistryRoot",
    "PromptGovernanceRegistry",
    "build_governance_matrix_projection",
    "get_fallback_path_record",
    "get_prompt_governance_registry",
    "get_registry_schema_version",
    "load_legacy_residual_registry",
]
