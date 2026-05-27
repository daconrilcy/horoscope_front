<!-- Commentaire global: livrable story CS-345 sur le handoff runtime gateway vers provider LLM. -->

# runtime-gateway-handoff-audit - CS-345

This is the story-specific report. The full CONDAMAD companion report is in `00-audit-report.md` in the same folder.

## Executive Summary

The executed handoff is source-proven as:

`LLMGateway.execute_request` -> `_resolve_plan` -> `_validate_input` -> `_build_messages` -> `_call_provider` -> `ProviderRuntimeManager.execute_with_resilience` -> `ResponsesClient.execute`.

The last gateway-owned payload before provider is `messages`, passed unchanged to the runtime manager. The final adapter payload is `input=effective_input`, derived from those messages by `ResponsesClient.execute`, plus runtime-only provider parameters.

## Sequenced Runtime Trace

| step | owner | symbol or function | input | output | provider visibility | evidence | gap or next story marker |
|---|---|---|---|---|---|---|---|
| 1 | runtime gateway | `LLMGateway.execute_request` | `LLMExecutionRequest` | normalized request and context | runtime-only | E-005, E-011 | no gap |
| 2 | runtime gateway | `_resolve_plan` | request, DB, context | `ResolvedExecutionPlan` | runtime-only config carrier | E-005, E-011 | CS-344 owns configuration map |
| 3 | runtime gateway | `_validate_input` | input schema and request/context payload | pass or `InputValidationError` | validation-only | E-016 | no CS-345 gap |
| 4 | runtime gateway | `_build_messages` | request, plan, qualified context | `messages` | prompt-visible | E-007, E-011 | no gap |
| 5 | runtime gateway | `_call_provider` | `messages`, plan, request | `GatewayResult` | provider handoff | E-008, E-011 | no gap |
| 6 | provider runtime manager | `execute_with_resilience` | messages, model, family, kwargs | provider result or upstream error | provider handoff | E-009 | no real provider call |
| 7 | OpenAI adapter | `ResponsesClient.execute` | messages and params | OpenAI Responses API params | provider handoff | E-010 | no real provider call |
| 8 | runtime gateway | `_validate_and_normalize` | raw output and output schema | `ValidationResult` | validation-only | E-016 | CS-347 |
| 9 | runtime gateway | `_handle_repair_or_fallback` | invalid validation result | repair or fallback result | non nominal | E-016 | CS-347 if behavior changes |
| 10 | runtime gateway and observability | `_build_result`, `log_call` | plan, recovery, result | metadata, call log, snapshot | audit-only | E-016 | CS-347 |

## Last payload before provider

The last payload before provider is the `messages` list returned by `_build_messages`.

`_call_provider(messages, plan, request)` passes:

- `messages=messages`
- `model=plan.model_id`
- `family=plan.feature`
- `temperature=plan.temperature`
- `max_output_tokens=plan.max_output_tokens`
- `request_id=request.request_id`
- `trace_id=request.trace_id`
- `use_case=request.user_input.use_case`
- `reasoning_effort=plan.reasoning_effort`
- `verbosity=plan.verbosity`
- `response_format=response_format`

`ProviderRuntimeManager.execute_with_resilience` forwards `messages` and kwargs to `ResponsesClient.execute`. The OpenAI adapter sends `input=effective_input`, where `effective_input` is either typed content blocks for GPT-5 models or the original message dictionaries for other models.

## Structured message shape

`compose_structured_messages` produces this exact order:

1. system: `system_core`
2. developer: `dev_prompt`
3. developer: optional `persona_block`
4. user: `user_payload`

Structured mode does not include chat history.

## Chat message shape

`compose_chat_messages` produces this exact order:

1. system: `system_core`
2. developer: `dev_prompt`
3. developer: optional `persona_block`
4. history: every valid `{role, content}` item from `request.context.history`
5. user: `user_payload` or locale fallback message

Malformed history items are logged and skipped.

## Provider parameter derivation

| Parameter | Owner | Source | Provider visibility | Evidence |
|---|---|---|---|---|
| `model` | gateway plan | assembly/profile or fallback resolver | provider parameter | E-008, E-010 |
| `temperature` | gateway plan | `UseCaseConfig.temperature`; omitted by adapter for reasoning models | provider parameter | E-008, E-010 |
| `max_output_tokens` | gateway plan | length budget, profile, or verbosity fallback | provider parameter | E-008, E-010 |
| `response_format` | gateway call boundary | output schema preferred over translated provider params | provider parameter | E-008, E-010 |
| `reasoning_effort` | mapper and plan | profile mapping or reasoning adjustment | provider parameter | E-008, E-010 |
| `verbosity` | plan and adapter | profile verbosity for GPT-5 text config | provider parameter | E-008, E-010 |
| `request_id`, `trace_id`, `use_case` | request | execution identifiers | adapter metadata | E-008, E-010 |

## `llm_astrology_input_v1` include and exclude matrix

| Field | Classification | Provider prompt handling | Evidence |
|---|---|---|---|
| `facts` | prompt-visible | included | E-006, E-015 |
| `signals` | prompt-visible | included | E-006, E-015 |
| `limits` | prompt-visible | included | E-006, E-015 |
| `shaping` | prompt-visible | included | E-006, E-015 |
| `request_id` | runtime-only | excluded | E-015 |
| `trace_id` | runtime-only | excluded | E-015 |
| `chart_json` | runtime-only and legacy raw carrier | excluded when rich natal input exists | E-006, E-012, E-013 |
| `natal_data` | runtime-only and legacy raw carrier | excluded when rich natal input exists | E-006, E-012, E-013 |
| `evidence` | validation-only | excluded recursively | E-006, E-013, E-015 |
| `grounding_status` | validation-only | excluded recursively | E-006, E-013, E-015 |
| `validation_owner` | validation-only | excluded recursively | E-006, E-013, E-015 |
| `provenance` | audit-only container | excluded recursively | E-006, E-013 |
| `evidence_refs` | validation-only detail | excluded recursively | E-006, E-013 |
| `llm_input_version` | validation-only detail | excluded recursively | E-006, E-013 |
| `projection_hash` | audit-only | excluded | E-006, E-013, E-015 |
| `llm_input_hash` | audit-only | excluded | E-006, E-013, E-015 |
| `provider_response` | audit-only | excluded | E-006, E-013, E-015 |
| `persisted_answer` | audit-only | excluded | E-006, E-013, E-015 |

## Input validation, output validation, repair, and fallback classification

| Path | Owner | Classification | Provider prompt relation | Evidence |
|---|---|---|---|---|
| Input validation | `gateway._validate_input`, `input_validation.validate_input` | validation-only pre-handoff | blocks invalid inputs before messages | E-016 |
| Output validation | `gateway._validate_and_normalize`, `output_validator.validate_output` | validation-only post-provider | not provider prompt material | E-016 |
| Repair | `gateway._handle_repair_or_fallback`, `repair.build_repair_prompt`, `repair_prompter.build_repair_prompt` | non nominal recovery | creates a new repair request only after invalid output | E-016 |
| Legacy use-case fallback | `gateway._handle_repair_or_fallback` | non nominal recovery | forbidden on supported features | E-016 |
| Test fallback | gateway flags and metadata | non nominal test path | never nominal provider handoff | E-016 |
| Provider fallback | provider support and mapper branches | non nominal tolerated path outside nominal supported provider | not normal handoff | E-016 |

## Observability metadata, call logs, snapshots, and usage

Observability is populated after provider return and recovery classification:

- `GatewayMeta`: validation status, repair and fallback booleans, execution path, model, schema, prompt version, provider and translated params.
- `ExecutionObservabilitySnapshot`: pipeline kind, execution path kind, fallback kind, requested/resolved/executed provider, context quality, token source, active snapshot metadata and provider hardening metadata.
- `observability.log_call` / `observability_service.log_call`: call log row, operational metadata row, input hash, token usage, estimated cost, evidence warning count and replay snapshot.

These are audit/observability fields, not provider prompt material.

## Existing tests and gaps

| Test or scan | Result | Coverage | Gap |
|---|---|---|---|
| `pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py` | PASS | prompt-visible boundary and local provider double handoff | no real provider call by design |
| `pytest -q tests/architecture/test_llm_astrology_input_payload_boundaries.py` | PASS | AST exclusion of audit-only and validation-only fields | output validation persistence belongs to CS-347 |
| custom AST handoff guard | PASS | `_build_messages`, `_call_provider`, and `messages=messages` path | not persisted as reusable test |
| API/FastAPI import scan | PASS | dependency direction in audited runtime/domain files | only scoped to audited files |

## Conclusion

CS-345 is satisfied as an audit deliverable. The current nominal handoff is source-proven, structured and chat modes are separated, audit-only and validation-only fields are excluded from provider prompt material, and recovery paths are classified as non nominal.
