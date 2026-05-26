# Audit Report - Configuration Prompts Placeholders Input Schema

## Scope

- Domain key: `configuration-prompts-placeholders-input-schema`
- Domain closure status: `blocked`
- Audit archetype: `custom` with contract-shape, legacy-surface and test-guard dimensions.
- Read-only scope: LLM configuration, prompt placeholder rendering, input validation, natal runtime input carriers, bootstrap prompts and orchestration tests.
- Output folder: `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/`

## Executive Conclusion

The current natal LLM configuration is `bloquant` for first-class structured injection. It can pass JSON-like astrology data through current context and placeholders, but the explicit configuration contract is still `chart_json`-centric.

The blocking configuration issue is that active natal use cases declare `input_schema.required = ["chart_json"]` and required prompt placeholders based on `chart_json`, while scoped scans show no `llm_astrology_input` or equivalent facts/signals/limits/proofs contract (E-007, E-008, E-019, E-020). The data blocker is separate: current runtime assembles `chart_json`, `natal_data`, `evidence_catalog` and `astro_context`, but recent projection/narrative owners remain available-not-injected according to prior audits and current scans (E-004, E-005, E-006, E-012, E-020).

## Required Questions

1. Current astrology placeholders: `chart_json`, `persona_name`, `locale`, `use_case`; `natal_data` appears in preview/runtime context but is not the nominal prompt placeholder in current natal prompt seeds (E-007, E-010, E-011, E-023).
2. Natal input schemas: active natal schemas describe only `chart_json` plus `locale`; they do not describe structured facts, signals, limits or proofs (E-007, E-008, E-019).
3. New `llm_astrology_input`: not currently declared; adding it without hack requires a target schema owner and placeholder governance update (E-019, E-020).
4. `chart_json` dependencies: canonical natal use cases, thematic modules, bootstrap prompts, validation payload builder and runtime contracts all depend on `chart_json` directly or by compatibility substitution (E-007 to E-016).
5. Legacy fallback: supported feature output fallback is blocked, but configuration fallback targets to `natal_interpretation_short` remain and input readiness still uses legacy `chart_json` carriers (E-007, E-008, E-021, E-022).
6. Target declaration owner: likely `backend/app/domain/llm/configuration/canonical_use_case_registry.py` for schema declaration, with runtime contract support in `backend/app/domain/llm/runtime/contracts.py` if the payload becomes first-class (E-007, E-013).
7. Renderer constraints: `PromptRenderer` handles flat `{{snake_case}}` placeholders and context-quality blocks; multiple structured blocks need declared variables/allowlist or one typed placeholder, not implicit nested rendering (E-014, E-017, E-023).

## Findings Summary

See `02-finding-register.md`: F-001 High; F-002, F-003 and F-004 Medium.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/stories/CS-327-audit-configuration-prompts-placeholders-input-schema/00-story.md` | used | E-001 | Source contract for scope, ACs and explicit output shape. | None. |
| `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md` | used | E-002 | Source brief for mandatory audit questions and source list. | None. |
| `_condamad/stories/regression-guardrails.md` | used | E-003 | Guardrail registry consulted before findings. | No exact guardrail for this target contract. |
| `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/00-audit.md` | out-of-domain | E-004 | Adjacent prior audit for LLM input lineage. | Context only. |
| `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/00-audit.md` | out-of-domain | E-005 | Adjacent prior audit for runtime prompt pipeline. | Context only. |
| `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/00-audit.md` | out-of-domain | E-006 | Adjacent prior audit for candidate target contracts. | Context only. |
| `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | used | E-007, E-008 | Canonical owner of use-case input schemas and required placeholders. | Runtime DB state not dumped. |
| `backend/app/domain/llm/configuration/assemblies.py` | intentional-public-export | E-024 | Canonical entrypoint re-exporting assembly admin, registry and resolver APIs. | Entry point surface only. |
| `backend/app/domain/llm/configuration/assembly_registry.py` | used | E-024 | Resolves active assembly configs from release snapshot/DB. | Detailed DB state not audited. |
| `backend/app/domain/llm/configuration/assembly_resolver.py` | used | E-023 | Resolves assemblies, previews placeholders and natal mock variables. | Preview path only partially proves runtime behavior. |
| `backend/app/domain/llm/configuration/prompt_versions.py` | intentional-public-export | E-024 | Canonical prompt version lookup entrypoint. | Facade by design. |
| `backend/app/domain/llm/configuration/prompt_version_lookup.py` | used | E-024 | Underlying active prompt version lookup owner. | No DB query executed. |
| `backend/app/domain/llm/prompting/prompt_renderer.py` / `PromptRenderer` | used | E-014, E-017 | Runtime placeholder rendering owner. | No behavior changed. |
| `backend/app/domain/llm/prompting/catalog.py` | used | E-021 | Runtime catalog and bounded fallback config owner. | Catalog fallback differs from DB assembly path. |
| `backend/app/domain/llm/runtime/input_validation.py` | intentional-public-export | E-024 | Canonical validation entrypoint re-exporting `validate_input`. | Facade by design. |
| `backend/app/domain/llm/runtime/input_validator.py` | used | E-018 | JSON Schema validation owner. | Generic validation only. |
| `backend/app/domain/llm/runtime/gateway.py` | used | E-014, E-015, E-016, E-022 | Runtime plan, rendering, payload and validation orchestration. | Runtime execution not mocked beyond tests. |
| `backend/app/domain/llm/runtime/contracts.py` | used | E-013 | Defines current `ExecutionContext`, `NatalExecutionInput` and plan contracts. | No target contract exists. |
| `backend/app/ops/llm/bootstrap/use_cases_seed.py` | used | E-009 | Seeds canonical use-case contracts into persistence. | Specific contract values sourced from registry. |
| `backend/app/ops/llm/bootstrap/seed_29_prompts.py` | used | E-010 | Historical/current seed prompts with `chart_json` placeholders. | Bootstrap artifact, not necessarily active DB row. |
| `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py` | used | E-011 | GPT-5 v3 natal and thematic prompts with `chart_json`. | Prompt text not modified. |
| `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py` | used | E-009 | Active natal feature/subfeature/plan mapping source. | Bootstrap taxonomy, not DB dump. |
| `backend/tests/llm_orchestration/**` | test-only | E-019, E-020 | Orchestration tests provide scan/guard context for current LLM paths. | Full tests recorded in validation output. |
| `backend/app/services/llm_generation/natal/interpretation_service.py` | out-of-domain | E-012 | Runtime data assembly inspected to bound data blockers; owner is service layer adjacent to config audit. | No service modification proposed here. |
| `frontend/**`, `backend/app/api/**`, DB migrations | out-of-domain | E-001, E-002 | Explicitly outside story scope. | Not audited in depth. |

## DRY No Legacy Mono-Domain And Dependency Direction

- DRY: The audit did not introduce a second schema path. Existing duplication/aliasing between `chart_json` and `natal_data` is captured in F-002.
- No Legacy: Existing `chart_json` and fallback behavior is classified; no legacy prompt, route, provider or payload path was added.
- Mono-domain: Findings stay in LLM configuration/prompt/runtime readiness. Service-layer evidence is used only to separate data blockers.
- Dependency direction: Future implementation should let LLM configuration/runtime consume a declared astrology input contract; astrology domain should not import LLM provider/runtime code.

## Closure Analysis

- Prior same-domain audit folders consulted: none found for `configuration-prompts-placeholders-input-schema`.
- Adjacent audit folders consulted: `calculs-interpretations-vers-llm`, `pipeline-prompt-llm-natal`, `projections-interpretatives-llm-input-readiness`.
- Story keys consulted: CS-324, CS-325, CS-326, CS-327 and guardrail registry entries RG-018, RG-021, RG-022.
- Active findings: F-001, F-002, F-003, F-004.
- Closed prior findings: none for same domain.
- Implementation files in audited domain changed by this audit: none.
- Governance/test files changed by this audit: audit artifacts only.
- Deferred non-domain concerns: prompt copy, provider behavior, frontend, DB schema, auth, migrations, release governance.

## Exhaustive Active Finding Surface

- F-001: `backend/app/domain/llm/configuration/canonical_use_case_registry.py`, `backend/app/ops/llm/bootstrap/use_cases_seed.py`, `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py`, `backend/app/domain/llm/runtime/contracts.py`.
- F-002: `backend/app/domain/llm/runtime/gateway.py`, `backend/app/domain/llm/runtime/contracts.py`, `backend/app/services/llm_generation/natal/interpretation_service.py`.
- F-003: `backend/app/domain/llm/prompting/prompt_renderer.py`, `backend/app/domain/llm/configuration/assembly_resolver.py`, prompt governance owners, and `backend/tests/llm_orchestration/test_placeholder_validation.py`.
- F-004: `backend/app/domain/llm/configuration/canonical_use_case_registry.py`, `backend/app/domain/llm/prompting/catalog.py`, `backend/app/domain/llm/runtime/gateway.py`.
