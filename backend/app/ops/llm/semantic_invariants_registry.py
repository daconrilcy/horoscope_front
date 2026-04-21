"""
Registre d'invariants sémantiques bornés — Story 66.41.

Séparé du manifeste structurel (`app.ops.llm.doc_conformity_manifest`) : celui-ci décrit
ce qui doit rester vrai dans l'architecture runtime du pipeline, pas le
périmètre de fichiers PR.
"""

from __future__ import annotations

from typing import Final

from app.domain.llm.governance.prompt_governance_registry import get_prompt_governance_registry

# Version du contrat sémantique (incrémenter si les invariants évoluent volontairement).
SEMANTIC_INVARIANTS_VERSION: Final[str] = "1.0.0"

_gov = get_prompt_governance_registry()

# Ordre doctrinal des transformations majeures du developer prompt (après résolution assembly
# des blocs texte). Doit rester aligné avec docs/llm-prompt-generation-by-feature.md.
# — Phase assemble_developer_prompt : budget de longueur puis compensation context_quality.
# — Phase gateway (_resolve_plan) : context_quality runtime, verbosité, rendu placeholders.
ASSEMBLE_DEVELOPER_PROMPT_TRANSFORM_ORDER: Final[tuple[str, ...]] = (
    "length_budget_inject",
    "context_quality_inject",
)

GATEWAY_PROMPT_TRANSFORM_ORDER: Final[tuple[str, ...]] = (
    "context_quality_inject",
    "verbosity_instruction",
    "prompt_render",
)

# Règle runtime : le snapshot de release actif prime sur les tables publiées « live »
# lorsqu'il est présent (AssemblyRegistry + ExecutionProfileRegistry).
RUNTIME_SNAPSHOT_PRIORITY_RULE_ID: Final[str] = "runtime.snapshot_active_before_live_tables"

# Familles et providers nominaux — alignés sur le registre central JSON (Story 66.42).
GOVERNED_NOMINAL_FAMILIES: Final[frozenset[str]] = frozenset(_gov.canonical_families)
GOVERNED_NOMINAL_PROVIDERS: Final[frozenset[str]] = frozenset({"openai"})

# Aliases de features legacy → canonique (même source que normalize_feature / registre 66.42).
GOVERNED_LEGACY_FEATURE_ALIASES_TO_CANONICAL: Final[dict[str, str]] = dict(
    _gov.legacy_nominal_feature_aliases_map()
)

# Noms d'enum FallbackType autorisés (contrat gouvernance ; nouveau membre = mise à jour registre).
GOVERNED_FALLBACK_TYPE_NAMES: Final[frozenset[str]] = frozenset(
    {
        "LEGACY_WRAPPER",
        "DEPRECATED_USE_CASE",
        "USE_CASE_FIRST",
        "RESOLVE_MODEL",
        "EXECUTION_CONFIG_ADMIN",
        "PROVIDER_OPENAI",
        "NARRATOR_LEGACY",
        "TEST_LOCAL",
        "NATAL_NO_DB",
        "DEPRECATED_FEATURE_ALIAS",
    }
)

# Discriminants devant rester présents sur les modèles de plan / observabilité (contrat review).
CRITICAL_RESOLVED_EXECUTION_PLAN_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "assembly_id",
        "feature",
        "subfeature",
        "plan",
        "requested_provider",
        "provider",
        "context_quality",
        "context_quality_instruction_injected",
        "context_quality_handled_by_template",
        "active_snapshot_id",
        "active_snapshot_version",
        "manifest_entry_id",
    }
)

CRITICAL_EXECUTION_OBS_SNAPSHOT_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "requested_provider",
        "resolved_provider",
        "executed_provider",
        "context_quality",
        "max_output_tokens_source",
        "active_snapshot_id",
        "active_snapshot_version",
        "manifest_entry_id",
    }
)

# Marqueurs stables pour la persistance d'observabilité (llm_call_logs).
OBSERVABILITY_LOG_SNAPSHOT_MARKERS: Final[tuple[str, ...]] = (
    "active_snapshot_id",
    "active_snapshot_version",
)
