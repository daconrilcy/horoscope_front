# Legacy Vs Canonical - Pipeline Prompt LLM Natal

| Surface | Classification | Evidence | Canonical target / replacement | Decision |
|---|---|---|---|---|
| `/users` route compatibility through `interpret_chart` | historical | E-005 | Public route contract or newer public natal interpretation endpoint decision | keep until product/API decision. |
| simplified legacy payload returned by `_to_legacy_payload` path | historical | E-005 | Public API contract layer, not prompt path | out-of-scope for prompt audit. |
| `free_short` / `natal_long_free` | historical | E-007, E-020 | Explicit free preview variant | keep but guard as intentional compatibility. |
| `schema v1` short fallback | historical | E-006 | Explicit output schema version policy | needs-user-decision before removal. |
| `schema v2` paid complete fallback | historical | E-006 | v3/v3_error target if rollout complete | needs-user-decision before removal. |
| `schema v3` / `v3_error` | canonical-target | E-006 | Current richer complete response shape | keep. |
| prompt fallback registry/governance | historical | E-003 | Governed assembly prompts for supported natal use cases | keep only exact audited exceptions. |
| developer prompt assembly and placeholder rendering | transition | E-023, E-024, E-025 | governed assembly + renderer path for allowed placeholders | keep as canonical prompt-composition path; do not add audit-specific placeholders. |
| `chart_json` public projection | historical | E-006, E-010, E-013 | selected canonical LLM factual/narrative owner | keep for compatibility until SC-001 decision. |
| `natal_data` duplicate object projection | historical | E-006, E-008 | same selected canonical owner as `chart_json` | duplicate-responsibility risk. |
| `evidence_catalog` from `chart_json` | historical | E-006, E-017 | validation-only catalog or future canonical evidence owner | needs-user-decision if generation grounding is desired. |
| `astro_context` astral-point JSON | transition | E-015 | named astral-point context or broader narrative owner | lost-or-flattened relative to newer full interpretation facts. |
| `structured_facts_v1` | canonical-target | E-019 | candidate factual owner | lost-or-flattened: absent from current prompt path. |
| `AINarrativeInput` | canonical-target | E-019 | candidate narrative owner | lost-or-flattened: absent from current prompt path. |
| `ChartInterpretationInputBuilder` | canonical-target | E-019 | candidate pre-narrative owner | lost-or-flattened: absent from current prompt path. |
| `ChartObjectRuntimeData` | canonical-target | E-019 | internal runtime facts, not raw prompt payload | lost-or-flattened: should not be exposed raw. |
