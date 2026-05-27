<!-- Commentaire global: rapport compagnon CONDAMAD pour l'audit CS-345 du handoff runtime provider LLM. -->

# Audit Report - CS-345 Runtime Gateway Handoff Provider Prompt LLM

## Domain Closure Status

Status: closed.

This is an audit-only run for `prompt-generation-cartography`. No in-domain implementation finding remains for CS-345. The story-specific deliverable is `03-runtime-gateway-handoff-audit.md` in this folder.

## Prior Audit And Story History Consulted

| Source | Classification | Current closure status | Evidence |
|---|---|---|---|
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1800` | prior same-domain audit | still-active as baseline only | E-002 |
| `_condamad/audits/prompt-generation-cartography/2026-05-27-1809` | prior same-domain audit | still-active as configuration baseline only | E-003 |
| `_condamad/stories/CS-343-prompt-generation-surface-inventory/00-story.md` | prior same-domain story | closed for inventory context, non-domain for handoff implementation | E-002 |
| `_condamad/stories/CS-344-audit-configuration-assembly-placeholder/00-story.md` | prior same-domain story | closed for configuration context, non-domain for runtime handoff | E-003 |
| `_condamad/stories/regression-guardrails.md` | guardrail registry | RG-002 and RG-022 applicable; exact handoff registry gap recorded | E-004 |

## Active Findings After Current Evidence

None requiring implementation. F-001 to F-004 are informational audit findings with no story candidate.

## Findings Now Closed

| Finding | Closure evidence | Guardrail IDs |
|---|---|---|
| CS-343 handoff dependency marker | Runtime handoff now mapped in this audit report. | RG-002, RG-022 |
| CS-344 configuration-versus-runtime risk | Final provider payload is traced from gateway and provider runtime source, not inferred from configuration. | RG-022 |

## Audited Domain Responsibility

The audited domain owns the runtime path that turns resolved prompt configuration and request context into provider-facing messages and provider parameters. It does not own frontend behavior, API routing, production of `llm_astrology_input_v1`, output persistence policy changes, schema migrations or real provider testing.

## Runtime Trace Summary

| step | owner | symbol or function | input | output | provider visibility | evidence | gap or next story marker |
|---|---|---|---|---|---|---|---|
| 1 | gateway | `execute_request` | `LLMExecutionRequest` | normalized request and context dict | runtime-only | E-005, E-011 | no gap |
| 2 | gateway | `_resolve_plan` | request, DB, context | `ResolvedExecutionPlan` and qualified context | runtime-only, prompt config resolved | E-005, E-011 | CS-344 remains configuration baseline |
| 3 | gateway | `_validate_input` | config input schema and request/context payload | pass or `InputValidationError` | validation-only | E-016 | no gap in CS-345 |
| 4 | gateway | `_build_messages` | request, plan, qualified context | `messages` list | prompt-visible | E-007, E-011 | no gap |
| 5 | gateway | `_call_provider` | `messages`, plan, request | `GatewayResult` from runtime manager | provider handoff | E-008, E-011 | no gap |
| 6 | provider runtime | `execute_with_resilience` | messages, model, family, kwargs | provider client result or classified upstream error | provider handoff | E-009 | no gap |
| 7 | provider adapter | `ResponsesClient.execute` | messages and provider params | OpenAI Responses API request | provider handoff | E-010 | no real provider call by design |
| 8 | gateway | `_validate_and_normalize` | provider raw output and output schema | `ValidationResult` | validation-only | E-016 | CS-347 owns completeness audit |
| 9 | gateway | `_handle_repair_or_fallback` | invalid validation result | repair result, fallback result or error | non-nominal | E-016 | CS-347 if behavior changes |
| 10 | gateway | `_build_result` and `log_call` | validation, plan, recovery, result | metadata, call log and snapshot | audit-only, observability | E-016 | CS-347 owns persistence audit |

## Last Payload Before Provider

The last gateway-owned provider payload is the `messages` list returned by `_build_messages` and passed unchanged as `messages=messages` into `ProviderRuntimeManager.execute_with_resilience` in `_call_provider`.

The last provider-adapter input is `effective_input`, built by `ResponsesClient.execute` from `messages`. For GPT-5 models, messages are converted to typed content blocks; otherwise the message dictionaries are used directly as `input`.

Provider parameters at the handoff are runtime-only: `model`, `family`, `temperature`, `max_output_tokens`, `request_id`, `trace_id`, `use_case`, `reasoning_effort`, `verbosity`, and `response_format`.

## Structured Message Shape

`compose_structured_messages` creates:

1. `{"role": "system", "content": system_core}`
2. `{"role": "developer", "content": dev_prompt}`
3. optional `{"role": "developer", "content": persona_block}`
4. `{"role": "user", "content": user_payload}`

No chat history is included in structured mode.

## Chat Message Shape

`compose_chat_messages` creates:

1. `{"role": "system", "content": system_core}`
2. `{"role": "developer", "content": dev_prompt}`
3. optional `{"role": "developer", "content": persona_block}`
4. every valid history item with its existing `role` and `content`
5. final `{"role": "user", "content": effective_user}`

Malformed history items are skipped with a warning and are not prompt material.

## Provider Parameter Derivation

| Parameter | Runtime owner | Source | Provider visibility | Evidence |
|---|---|---|---|---|
| `model` | gateway plan | assembly/profile or fallback resolver | provider parameter | E-008, E-010 |
| `temperature` | gateway plan | config unless reasoning model removes provider use | provider parameter | E-008, E-010 |
| `max_output_tokens` | gateway plan | length budget, execution profile, or verbosity fallback | provider parameter | E-008, E-010 |
| `reasoning_effort` | provider mapper and plan | profile mapping or reasoning adjustment | provider parameter | E-008, E-010 |
| `verbosity` | gateway plan | execution profile verbosity mapping | provider parameter | E-008, E-010 |
| `response_format` | gateway `_call_provider` | output schema preferred over translated params | provider parameter, not prompt text | E-008, E-010 |
| `request_id`, `trace_id`, `use_case` | request | execution request identifiers | runtime metadata to adapter | E-008, E-010 |

## `llm_astrology_input_v1` Include And Exclude Matrix

| Field or block | Classification | Provider prompt handling | Evidence |
|---|---|---|---|
| `facts` | prompt-visible | included when present | E-006, E-015 |
| `signals` | prompt-visible | included when present | E-006, E-015 |
| `limits` | prompt-visible | included when present | E-006, E-015 |
| `shaping` | prompt-visible | included when present | E-006, E-015 |
| `request_id`, `trace_id` | runtime-only | excluded from prompt projection | E-015 |
| `chart_json`, `natal_data` | runtime-only / legacy raw carriers | excluded from natal rich prompt path when `llm_astrology_input_v1` exists | E-006, E-012, E-013 |
| `evidence`, `grounding_status`, `validation_owner` | validation-only | recursively excluded from prompt projection | E-006, E-013, E-015 |
| `provenance`, `evidence_refs`, `llm_input_version` | audit or validation detail | recursively excluded by gateway prompt exclusion set | E-006, E-013 |
| `projection_hash`, `llm_input_hash`, `provider_response`, `persisted_answer` | audit-only | excluded from prompt projection | E-006, E-013, E-015 |
| `data_roles`, `exclusions` | contract metadata | not a prompt-visible block | E-015 |

## Validation, Repair, Fallback And Observability

Input validation runs before message construction. Output validation runs after provider return. Repair is invoked only when output validation fails and the current call is not already a repair call. Legacy use-case fallback is only attempted after invalid output and only outside supported feature paths. These are non nominal recovery paths, not the standard provider handoff.

Observability metadata is built after validation and recovery: execution path, repair/fallback booleans, validation status, model, prompt version, assembly, profile, provider parameters, operational snapshot, call log, replay snapshot and usage/cost fields. These fields are not prompt material.

## Existing Tests And Gaps

| Test or guard | Result | Proves | Gap |
|---|---|---|---|
| `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` | PASS | local provider double captures final messages and prompt boundary | no real provider call by design |
| `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` | PASS | AST boundary projection and audit-only exclusions | no output validation persistence audit |
| custom AST handoff guard | PASS | `_build_messages` and `_call_provider` handoff shape | not persisted as reusable guard |
| `git diff --quiet -- backend/app backend/tests frontend/src` | PASS | code/test/frontend read-only invariant | `_condamad` artifacts intentionally changed |

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `backend/app/domain/llm/runtime/gateway.py::LLMGateway.execute_request` | used | E-005, E-011 | Canonical runtime entrypoint for the handoff trace. | Source and tests only; no external provider call. |
| `backend/app/domain/llm/runtime/gateway.py::_resolve_plan` | used | E-005, E-011 | Produces `ResolvedExecutionPlan` consumed by message composition and provider call. | Configuration completeness is CS-344 context. |
| `backend/app/domain/llm/runtime/gateway.py::build_user_payload` | used | E-006, E-012 | Builds final user payload text for prompt-visible request data. | Production of rich input is CS-346. |
| `backend/app/domain/llm/runtime/gateway.py::_prompt_visible_llm_astrology_input` | used | E-006, E-013, E-015 | Projects canonical prompt-visible blocks before provider handoff. | None for CS-345. |
| `backend/app/domain/llm/runtime/gateway.py::compose_structured_messages` | used | E-007, E-011 | Owns structured mode message shape. | None. |
| `backend/app/domain/llm/runtime/gateway.py::compose_chat_messages` | used | E-007, E-011 | Owns chat mode message shape and history insertion. | None. |
| `backend/app/domain/llm/runtime/gateway.py::_build_messages` | used | E-007, E-011 | Selects structured or chat composer and returns the provider message list. | None. |
| `backend/app/domain/llm/runtime/gateway.py::_call_provider` | used | E-008, E-011 | Last gateway boundary before provider runtime manager. | Does not execute a real provider in audit. |
| `backend/app/domain/llm/runtime/provider_runtime_manager.py::ProviderRuntimeManager.execute_with_resilience` | used | E-009 | Runtime owner for provider retries, timeout and circuit breaker. | OpenAI-specific manager behavior only inspected. |
| `backend/app/domain/llm/runtime/provider_parameter_mapper.py::ProviderParameterMapper` | used | E-008 | Maps execution profiles to provider params consumed by plan and handoff. | Anthropic mapping inspected only as non-executed source context. |
| `backend/app/domain/llm/runtime/providers.py::is_provider_supported` | used | E-005, E-016 | Provider support gate participates in nominal versus non-nominal classification. | No provider policy change in audit. |
| `backend/app/domain/llm/runtime/input_validation.py::validate_input` | used | E-016 | Input validation entrypoint before provider messages. | Detailed schema correctness outside CS-345. |
| `backend/app/domain/llm/runtime/output_validator.py::validate_output` | used | E-016 | Output validation owner after provider return. | CS-347 owns deeper output audit. |
| `backend/app/domain/llm/runtime/repair.py::build_repair_prompt` | used | E-016 | Repair path owner for invalid provider output. | Non-nominal only. |
| `backend/app/domain/llm/runtime/observability.py::log_call` | used | E-016 | Observability entrypoint for call logs and snapshots. | Persistence completeness deferred to CS-347. |
| `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py::LLM_ASTROLOGY_INPUT_DATA_ROLES` | used | E-015 | Canonical role contract reused by gateway projection. | Production mapping deferred to CS-346. |
| `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` | test-only | E-012 | Test owner for local handoff and prompt-boundary proof. | None. |
| `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` | test-only | E-013 | Architecture guard for prompt role reuse and exclusions. | None. |
| `_condamad/stories/regression-guardrails.md::RG-002` | out-of-domain | E-004 | Consulted backend boundary invariant, not modified. | Not exact handoff guardrail. |
| `_condamad/stories/regression-guardrails.md::RG-022` | out-of-domain | E-004 | Consulted prompt-generation validation path invariant, not modified. | Not exact handoff guardrail. |

## DRY, No Legacy, Mono-Domain And Dependency Direction

- DRY: the audit does not duplicate CS-343 inventory or CS-344 configuration matrices; it references them and focuses on executed provider handoff.
- No Legacy: legacy use-case mapping, provider fallback, test fallback and repair are classified as non nominal recovery paths, not as the normal handoff.
- Mono-domain: runtime handoff ownership remains in `backend/app/domain/llm/runtime/**`; production of `llm_astrology_input_v1` and output persistence are deferred to CS-346 and CS-347.
- Dependency direction: targeted scan found no API/FastAPI imports in audited runtime/domain files.

## Deferred Non-Domain Concerns

- CS-346: source production and completeness of `llm_astrology_input_v1`.
- CS-347: output validation, persistence, repair outcomes and observability completeness.
- Guardrail registry enrichment: explicitly not authorized by CS-345.

