# Audit - Pipeline Prompt LLM Natal

This story-specific synthesis is backed by the CONDAMAD standard report files in the same folder.

## Runtime Flow

1. `NatalInterpretationService.interpret_chart` preserves the historical `/users` contract by calling `interpret(... level="complete", variant_code="free_short")` (E-005).
2. `NatalInterpretationService.interpret` builds `chart_json_dict`, `evidence_catalog` and `astro_context`; then selects `natal_long_free`, a thematic module use case, `natal_interpretation`, or `natal_interpretation_short` (E-006, E-007).
3. `NatalExecutionInput` carries `chart_json`, `natal_data`, `evidence_catalog`, `plan`, `level`, `question`, `astro_context`, `module`, `variant_code`, user and trace IDs (E-006, E-009).
4. `AIEngineAdapter.generate_natal_interpretation` maps that input to `LLMExecutionRequest`: `natal_data`, `chart_json`, `astro_context` in context; `module`, `variant_code`, `level` in `extra_context`; `evidence_catalog` in flags (E-008).
5. `assembly_resolver` composes the developer prompt, and `PromptRenderer` governs placeholder substitution such as `{{chart_json}}` (E-023, E-024).
6. `LLMGateway._build_messages` flattens `extra_context`, detects `{{chart_json}}` in the rendered developer prompt and calls `build_user_payload` (E-011).
7. `build_user_payload` appends `Technical Data: {chart_json}` only when `chart_json` exists and `chart_json_in_prompt` is false (E-010).
8. `validate_output` later consumes `evidence_catalog` for evidence normalization/sanitization (E-017).

## Answers To Required Questions

- Data entering gateway: `chart_json`, `natal_data`, `astro_context`, `plan`, `level`, `module`, `variant_code`, `question`, `persona_id`, locale and IDs; `evidence_catalog` enters as validation flags.
- Prompt-visible data: `chart_json` only, either via `{{chart_json}}` rendered in the developer prompt or `Technical Data`.
- `chart_json_in_prompt`: yes, it suppresses fallback `Technical Data` injection when the rendered developer prompt already contains `{{chart_json}}`.
- Branch data: `free_short`, `short`, `complete` and thematic modules share the same chart/evidence/astro-context producers; branch differences are use case, validation strictness, question, module, variant and schema behavior.
- `evidence_catalog`: validation-only under current evidence.
- Lost-or-flattened data: recent-refonte owners `structured_facts_v1`, `AINarrativeInput`, `ChartInterpretationInputBuilder`, `ChartObjectRuntimeData` are not in the scoped prompt path; chart details are flattened into public `chart_json` and labels, while `astro_context` is serialized astral-point context.
- Legacy behavior: `/users`, `free_short`, schema v1/v2/v3 compatibility and assembly/prompt fallback governance remain active compatibility surfaces.

## Findings

See `02-finding-register.md`: F-001 High, F-002 Medium, F-003 Medium, F-004 Medium.
