# Input Field Matrix - Pipeline Prompt LLM Natal

| input field | producer | consumer | injection effective | statut |
|---|---|---|---|---|
| `chart_json` | `NatalInterpretationService.interpret` / `_generate_free_short` from `build_chart_json` | `AIEngineAdapter`, `LLMGateway.build_user_payload`, `PromptRenderer` placeholder path, input-schema payload mapping | prompt-visible | historical |
| `natal_data` | same `chart_json_dict` as `chart_json` | `ExecutionContext.natal_data`; schema payload mapping prefers it for `chart_json` object | runtime-only | historical |
| `evidence_catalog` | `build_enriched_evidence_catalog(chart_json_dict)` | `ExecutionFlags.evidence_catalog`; `validate_output` | validation-only | historical |
| `astro_context` | `build_astral_point_interpretation_context` serialized by service | `ExecutionContext.astro_context`; extra allowed context | runtime-only | transition |
| `plan` | entitlement resolver snapshot | `ExecutionUserInput.plan`, execution profile resolution | runtime-only | canonical-target |
| `level` | API/service call argument | `extra_context["level"]`, persistence/schema branch logic | runtime-only | transition |
| `variant_code` | API/service call argument or `free_short` branch | `extra_context["variant_code"]`, cache/persistence logic | runtime-only | transition |
| `module` | API/service call argument | `extra_context["module"]`, thematic use-case selection | runtime-only | transition |
| `question` | API/service call argument; default for `short` | `ExecutionUserInput.question`; visible only if question policy permits | prompt-visible | canonical-target |
| `persona_id` | API/service call argument | user input override/persona strategy | runtime-only | canonical-target |
| `structured_facts_v1` | domain astrology interpretation owner | no consumer in scoped natal LLM path | not-used | lost-or-flattened |
| `AINarrativeInput` | domain astrology interpretation owner | no consumer in scoped natal LLM path | not-used | lost-or-flattened |
| `ChartInterpretationInputBuilder` | domain astrology interpretation owner | no consumer in scoped natal LLM path | not-used | lost-or-flattened |
| `ChartObjectRuntimeData` | domain astrology runtime owner | no direct consumer in scoped natal LLM path | not-used | lost-or-flattened |
