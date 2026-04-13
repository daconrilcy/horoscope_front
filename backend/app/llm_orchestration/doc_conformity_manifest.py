from __future__ import annotations

from typing import Final

# Story 66.38: single source of truth for documentation governance.

STRUCTURAL_FILES: Final[set[str]] = {
    "docs/llm-prompt-generation-by-feature.md",
    ".github/pull_request_template.md",
    "backend/app/llm_orchestration/gateway.py",
    "backend/app/llm_orchestration/feature_taxonomy.py",
    "backend/app/llm_orchestration/services/fallback_governance.py",
    "backend/app/llm_orchestration/services/provider_parameter_mapper.py",
    "backend/app/llm_orchestration/services/config_coherence_validator.py",
    "backend/app/llm_orchestration/golden_regression_registry.py",
    "backend/app/llm_orchestration/supported_providers.py",
    "backend/app/llm_orchestration/models.py",
}

DOC_PATH: Final[str] = "docs/llm-prompt-generation-by-feature.md"
PR_TEMPLATE_PATH: Final[str] = ".github/pull_request_template.md"
VERIFICATION_MARKER: Final[str] = (
    "Dernière vérification manuelle contre le pipeline réel du gateway"
)

AUTHORIZED_PR_REASONS: Final[tuple[str, ...]] = (
    "REF_ONLY",
    "FIX_TYPO",
    "TEST_ONLY",
    "DOC_ONLY",
    "NON_LLM",
)
