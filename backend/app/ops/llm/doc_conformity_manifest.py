from __future__ import annotations

from typing import Final

# Story 66.38 : source unique pour la gouvernance documentaire (canonique sous app.ops.llm).

STRUCTURAL_FILES: Final[set[str]] = {
    "backend/app/domain/llm/governance/data/prompt_governance_registry.json",
    "backend/app/domain/llm/governance/prompt_governance_registry.py",
    "docs/llm-prompt-generation-by-feature.md",
    ".github/pull_request_template.md",
    ".github/workflows/llm-doc-conformity.yml",
    "backend/app/domain/llm/runtime/gateway.py",
    "backend/app/domain/llm/runtime/contracts.py",
    "backend/app/ops/llm/doc_conformity_manifest.py",
    "backend/app/domain/llm/governance/feature_taxonomy.py",
    "backend/app/ops/llm/doc_conformity_validator.py",
    "backend/app/ops/llm/semantic_invariants_registry.py",
    "backend/app/ops/llm/semantic_conformity_validator.py",
    "backend/app/domain/llm/runtime/fallback_governance.py",
    "backend/app/domain/llm/governance/legacy_residual_registry.py",
    "backend/app/domain/llm/governance/data/legacy_residual_registry.json",
    "backend/app/domain/llm/runtime/provider_parameter_mapper.py",
    "backend/app/domain/llm/configuration/config_coherence_validator.py",
    "backend/app/ops/llm/golden_regression_registry.py",
    "backend/app/domain/llm/runtime/supported_providers.py",
    "backend/scripts/check_doc_conformity.py",
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
