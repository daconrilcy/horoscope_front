# Readiness - CS-327

## Overall

- `llm_astrology_input` readiness: `bloquant`
- Main `configuration-blocker`: active natal use-case contracts and prompt placeholders are `chart_json`-centric.
- Main `data-blocker`: runtime currently assembles `chart_json`, `natal_data`, `evidence_catalog` and `astro_context`, while modern projection/narrative contracts remain not injected into the scoped LLM path.

## Readiness Table

| use case | prompt config | input schema | placeholders | readiness injection | blocker type |
|---|---|---|---|---|---|
| `natal_interpretation` | registry + v3 prompt/assembly | `chart_json` required | `chart_json`, `persona_name`, `locale`, `use_case` | `bloquant` | `configuration-blocker` |
| `natal_interpretation_short` | registry + legacy seed prompt | `chart_json` required | `chart_json`, `locale`, `use_case` | `bloquant` | `configuration-blocker` |
| thematic natal modules | registry + thematic v3 prompt builder | `chart_json` required | `chart_json`, `persona_name`, `locale`, `use_case` | `bloquant` | `configuration-blocker` |
| `natal_long_free` | catalog + runtime free-short branch | no canonical registry `input_schema` observed | runtime carrier `chart_json` | `legacy fallback` | `data-blocker` |
| target facts/signals/limits/proofs | none | none | none | `bloquant` | `configuration-blocker` |

## Target Contract Placement

Recommended next decision: choose whether `llm_astrology_input` is:

- a first-class field in `NatalExecutionInput`;
- a schema field declared per use case in `canonical_use_case_registry.py`;
- a wrapper around `AINarrativeInputContract`;
- or a smaller derived payload from `structured_facts_v1`.

The audit does not implement that decision. It only records that current configuration is not closure-ready for modern structured injection.

## Guard Requirements For Future Story

- No wildcard placeholder allowlist.
- No new `chart_json` alias, shim, fallback, or second runtime carrier.
- Scans must include `required_prompt_placeholders`, `input_schema`, `chart_json`, `natal_data`, `astro_context`, `llm_astrology_input`, `facts`, `signals`, `limits`, `proofs`.
- Existing orchestration tests should prove unchanged behavior before any prompt/schema migration.
