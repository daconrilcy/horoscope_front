# Placeholder Schema Matrix - CS-327

| use case | prompt config | input schema | placeholders | readiness injection | blocker type |
|---|---|---|---|---|---|
| Natal full and thematic modules | `canonical_use_case_registry.py`, `seed_30_8_v3_prompts.py`, `assembly_resolver.py` | `chart_json` object required; `locale` optional pattern | `chart_json`, `persona_name`, `locale`, `use_case` | `bloquant` | `configuration-blocker` |
| Natal short | `canonical_use_case_registry.py`, `seed_29_prompts.py` | `chart_json` object required; `locale` optional pattern | `chart_json`, `locale`, `use_case` | `bloquant` | `configuration-blocker` |
| Free long runtime | `catalog.py`, `_generate_free_short`, `NatalExecutionInput` | runtime carrier has `chart_json`, `natal_data`, `evidence_catalog`, `astro_context`; no registry `input_schema` owner observed | carrier `chart_json`, context `natal_data`, `astro_context` | `legacy fallback` | `data-blocker` |
| Target `llm_astrology_input` | none found by scoped scan | none | none | `bloquant` | `configuration-blocker` |
| Facts/signals/limits/proofs blocks | none found by scoped scan | none | none | `bloquant` | `configuration-blocker` |

## Renderer And Validation Constraints

- `PromptRenderer` extracts and renders flat `{{snake_case}}` placeholders; required variables are checked only when their placeholder appears in the template.
- Gateway render variables merge `ExecutionUserInput` and context, so a future `llm_astrology_input` could be technically carried only after schema/placeholder governance declares it.
- `validate_input` is generic JSON Schema Draft 7 and is compatible with richer schemas, but current natal schemas declare only `chart_json`.
- `_build_validation_payload` contains special logic for `chart_json`, filling it from `natal_data`, raw dict `chart_json`, or parsed string `chart_json`.

Evidence: E-007, E-008, E-014, E-016, E-017, E-018, E-019, E-020.
