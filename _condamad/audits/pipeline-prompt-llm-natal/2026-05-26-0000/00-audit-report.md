# Audit Report - Pipeline Prompt LLM Natal

## Domain Closure Status

Status: `phased-with-map`.

Audited domain: backend natal LLM prompt-injection pipeline, from `NatalInterpretationService` through `NatalExecutionInput`, `AIEngineAdapter.generate_natal_interpretation`, `LLMExecutionRequest`, `LLMGateway._build_messages` and `build_user_payload`.

This run is read-only for application code. It creates audit artifacts only.

## Mandatory Answers

1. Donnees qui entrent dans `LLMGateway`: `chart_json`, `natal_data`, `astro_context`, `plan`, `level`, `module`, `variant_code`, `question`, `persona_id`, `locale`, IDs de requete et `evidence_catalog` via flags (E-006, E-008, E-009).
2. Donnees visibles dans le message utilisateur: `chart_json` only, either through prompt placeholder `{{chart_json}}` rendered by `PromptRenderer` or through `Technical Data: {chart_json}`. `natal_data`, `astro_context`, `plan`, `level`, `module`, `variant_code` and `evidence_catalog` are runtime-only, validation-only or input-schema material unless a template explicitly references an allowed placeholder (E-010, E-011, E-012, E-013, E-023).
3. `chart_json_in_prompt`: `_build_messages` sets it to true when `{{chart_json}}` exists in the rendered developer prompt assembled by the prompt assembly path. In that case `build_user_payload` suppresses the fallback `Technical Data` append, so injection strategy switches from user-data block append to template placeholder rendering (E-010, E-011, E-023, E-024).
4. Branches: `short`, `complete`, `free_short` and thematic modules all originate from the same `chart_json_dict`, `evidence_catalog` and `astro_context` assembly; they differ by `use_case_key`, `level`, `validation_strict`, `question`, `module`, `variant_code`, prompt assembly/fallback context and schema fallback behavior (E-006, E-007, E-013, E-020, E-024).
5. `evidence_catalog`: it is passed into `ExecutionFlags` and consumed by output validation normalization/sanitization. Evidence found no source path where it constrains prompt composition or provider input text (E-008, E-011, E-017).
6. Donnees refondues perdues/aplaties: the audited pipeline does not consume `structured_facts_v1`, `AINarrativeInput`, `ChartInterpretationInputBuilder` or `ChartObjectRuntimeData`; current prompt-visible data is the `build_chart_json` projection serialized as `chart_json`, with astral-point context serialized separately but not prompt-visible by default (E-006, E-015, E-019).
7. Explicit legacy behavior: `/users` routes are maintained through `interpret_chart` mapped to `variant_code="free_short"`; schema v3/v2/v1 compatibility and fallback branches remain in deserialization; prompt fallback/legacy residuals are separately guarded by RG-018/RG-021 (E-003, E-005, E-006).

## Findings Summary

| ID | Severity | Summary | Evidence | Story candidate |
|---|---|---|---|---|
| F-001 | High | Rich natal facts are carried to the gateway mainly through legacy/public `chart_json`, while recent canonical interpretation owners are absent from the scoped LLM prompt path. | E-006, E-008, E-013, E-019 | yes |
| F-002 | Medium | `natal_data`, `astro_context`, `plan`, `level`, `module` and `variant_code` enter runtime context but are not prompt-visible in `build_user_payload`. | E-008, E-009, E-010, E-011, E-023 | yes |
| F-003 | Medium | `evidence_catalog` validates/sanitizes output evidence but does not constrain message composition. | E-008, E-011, E-017 | yes |
| F-004 | Medium | Historical branch compatibility remains active for `/users`, `free_short`, schema v1/v2/v3 and prompt fallback/governance surfaces. | E-003, E-005, E-006, E-020, E-024, E-025 | yes |

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/stories/CS-325-audit-pipeline-prompt-llm-natal/00-story.md` | used | E-001 | Source contract for scope, target files, ACs and no-app-change rule. | None. |
| `_story_briefs/cs-325-audit-pipeline-prompt-llm-natal-legacy-vs-canonique.md` | used | E-002 | Source brief for mandatory questions and audit deliverables. | None. |
| `_condamad/stories/regression-guardrails.md` / RG-018, RG-021, RG-022 | used | E-003 | Existing LLM prompt/fallback/orchestration invariants bound this audit. | No exact CS-325 guardrail exists. |
| `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000` | out-of-domain | E-004 | Prior adjacent audit used for closure context. | Adjacent domain only. |
| `backend/app/services/llm_generation/natal/interpretation_service.py` / `interpret_chart` | used | E-005 | Public historical `/users` entry delegates to canonical `free_short`. | No runtime request executed. |
| `backend/app/services/llm_generation/natal/interpretation_service.py` / `interpret` | used | E-006 | Current producer of `chart_json`, `natal_data`, `evidence_catalog`, `astro_context`, branch routing and `NatalExecutionInput`. | Source inspection only. |
| `backend/app/services/llm_generation/natal/interpretation_service.py` / `_generate_free_short` | used | E-007 | Dedicated free-short producer using the same chart data surfaces. | Source inspection only. |
| `backend/app/domain/llm/runtime/adapter.py` / `AIEngineAdapter.generate_natal_interpretation` | used | E-008 | Maps `NatalExecutionInput` to `LLMExecutionRequest`. | Source inspection only. |
| `backend/app/domain/llm/runtime/contracts.py` / `NatalExecutionInput` and `LLMExecutionRequest` | intentional-public-export | E-009 | Runtime contract consumed by service, adapter and tests. | Shape unchanged. |
| `backend/app/domain/llm/runtime/gateway.py` / `build_user_payload` | used | E-010 | Determines user-message visible data and `Technical Data` append. | Source inspection only. |
| `backend/app/domain/llm/runtime/gateway.py` / `_build_messages` | used | E-011 | Calls `build_user_payload` and detects `{{chart_json}}`. | Source inspection only. |
| `backend/app/domain/llm/runtime/gateway.py` / input-schema payload mapping | used | E-012 | Maps schema `chart_json` from `natal_data` first, then `chart_json`. | Source inspection only. |
| `backend/app/domain/llm/configuration/canonical_use_case_registry.py` / natal contracts | intentional-public-export | E-013 | Canonical LLM use-case contracts require `chart_json` for natal and module prompts. | Contract source only. |
| `backend/app/services/llm_generation/natal/prompt_context.py` | used | E-014 | Canonical import facade for shared natal prompt helpers. | No deletion recommendation. |
| `backend/app/services/llm_generation/shared/natal_context.py` / `build_astral_point_interpretation_context` | used | E-015 | Producer of `astro_context` content used by the service. | Source inspection only. |
| `backend/app/domain/llm/prompting/prompt_renderer.py` / `PromptRenderer.render` | used | E-023 | Renders allowed placeholders such as `{{chart_json}}` and governs unresolved or unauthorized placeholders. | Source inspection only. |
| `backend/app/domain/llm/prompting/context.py` / common context builder | out-of-domain | E-016 | Separate prompt common context path inspected to avoid confusing it with the natal gateway path. | Not the CS-325 runtime path. |
| `backend/app/domain/llm/configuration/assembly_resolver.py` / `resolve_assembly`, `assemble_developer_prompt` | used | E-024 | Composes the rendered developer prompt inspected by `_build_messages` for `{{chart_json}}`; also documents fallback/default template source behavior. | Source inspection only. |
| `backend/app/domain/llm/runtime/output_validator.py` / evidence validation | used | E-017 | Consumer of `evidence_catalog` during output validation. | Source inspection only. |
| `backend/tests/llm_orchestration/**` | test-only | E-018, E-025 | Existing LLM orchestration tests cover gateway/request/prompt behavior, prompt renderer governance, assembly resolution and fallback guards. | Execution recorded in validation output. |
| `backend/app/tests/integration/test_llm_qa_runtime_contracts.py` | test-only | E-018, E-025 | Integration evidence for placeholder-based `chart_json` prompt rendering in developer messages. | Execution recorded in validation output. |

## Prior Audit And Story Closure

- Prior folders consulted: `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000` (E-004).
- Prior story consulted: `CS-324-audit-calculs-interpretations-llm` through story and audit artifacts (E-004).
- Prior active context still-active: CS-324 F-001/F-002/F-003 remain relevant because current CS-325 evidence still shows no recent canonical owner in the scoped prompt-injection path (E-004, E-019).
- Closed findings: none closed by this read-only audit.
- Superseded findings: none; CS-325 narrows CS-324 to message visibility and branch behavior.
- Non-domain/deferred: frontend, DB migrations, auth/security, provider cost, prompt rewrite and schema changes.

## Mandatory Dimensions

- DRY: `chart_json` and `natal_data` duplicate one chart projection in two shapes; no new runtime path is added by this audit.
- No Legacy: existing `/users`, `free_short`, fallback and schema compatibility are classified; no shim, alias, prompt, route or fallback is created.
- Mono-domain: findings stay within backend natal LLM prompt injection.
- Dependency direction: future work should keep astrology/domain facts upstream of LLM service/runtime, without making domain astrology depend on gateway/provider code.

## Exhaustive Active Finding Surface

- F-001: `backend/app/services/llm_generation/natal/interpretation_service.py`, `backend/app/domain/llm/runtime/contracts.py`, `backend/app/domain/llm/runtime/adapter.py`, selected canonical owner under `backend/app/domain/astrology/interpretation/**` if a future implementation chooses one.
- F-002: `backend/app/domain/llm/runtime/gateway.py`, `backend/app/domain/llm/prompting/prompt_renderer.py`, `backend/app/domain/llm/configuration/canonical_use_case_registry.py`, `backend/app/domain/llm/runtime/contracts.py`, `backend/app/services/llm_generation/natal/interpretation_service.py`.
- F-003: `backend/app/domain/llm/runtime/output_validator.py`, `backend/app/domain/llm/runtime/gateway.py`, `backend/app/services/llm_generation/natal/interpretation_service.py`.
- F-004: `backend/app/services/llm_generation/natal/interpretation_service.py`, `backend/app/domain/llm/configuration/canonical_use_case_registry.py`, `backend/app/domain/llm/configuration/assembly_resolver.py`, prompt fallback/governance tests under `backend/tests/llm_orchestration/**`.

## Deferred Non-Domain Context

No application implementation is performed here. Prompt text changes, provider settings, output schema changes, frontend display, DB changes, auth/security and CI are deferred non-domain concerns for this audit.
