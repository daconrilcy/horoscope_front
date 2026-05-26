# Legacy Transition

This transition plan confines historical surfaces until the canonical `llm_astrology_input_v1` mapping, schema and guards exist. It does not authorize code changes.

## Transition Principles

- observed: `chart_json` is current prompt-visible material; `natal_data`, `astro_context`, `plan`, `level`, `module`, `variant_code` are runtime-only for the audited path. Sources: CS-325 F-002 E-008/E-009/E-010/E-011/E-023.
- observed: `evidence_catalog` is validation-only in the current pipeline. Sources: CS-325 F-003 E-008/E-011/E-017.
- decision: compatibility remains named and temporary; no new alias, fallback or wildcard placeholder is permitted. Sources: CS-327 F-002/F-003.
- blocker: product owner must classify externally visible `/users`, `free_short`, schema and fallback branches before removal. Sources: CS-325 F-004.

## Legacy Surface Register

| Surface | Current role | Target role | transition-condition | Owner | Risk | Required next action | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `chart_json` | public projection and current prompt carrier | compatibility only | allowed only until `llm_astrology_input_v1` schema, prompt-visible tests and hash audit pass | public projection owner + LLM runtime owner | source-of-truth drift | replace canonical prompt ownership | CS-324 F-001/F-002; CS-327 F-001 |
| `natal_data` | duplicate dict projection used by runtime/validation | compatibility only | allowed only while gateway validation still requires `chart_json` contracts | LLM runtime owner | duplicate responsibility | converge validation payload ownership | CS-324 F-002; CS-327 F-002 |
| `astro_context` | narrow astral-point context | scoped interpretive-signal input or removed | allowed only if labeled as astral-point context, not broad astrology context | interpretation owner | misleading broad name | rename/classify in migration story | CS-324 F-004 E-021 |
| `evidence_catalog` | validation-only output grounding aid | split: validation catalog plus `evidence_refs` in target contract | owner decision required before prompt visibility | observability owner | false belief that prompt is grounded | decide role and tests | CS-325 F-003; CS-326 F-003 |
| `/users` natal branch | compatibility entrypoint | classified keep/remove | no behavior change before external contract status known | product owner | breaking public behavior | branch decision register | CS-325 F-004 E-005/E-006 |
| `free_short` / `natal_long_free` mapping | compatibility plan/module branch | classified keep/remove | no migration until plan semantics are known | product owner + LLM owner | inconsistent prompt path | classify branch | CS-325 F-004 E-020 |
| schema v1/v2/v3 compatibility | output/input compatibility | bounded compatibility | allowed only with explicit tests and expiry | LLM runtime owner | hidden fallback | map each schema branch | CS-325 F-004 |
| prompt/assembly fallback | fallback guardrails and preview variables | structured schema registry | allowed only for existing supported behavior | LLM configuration owner | bypass structured input | align assembly preview variables | CS-325 F-004 E-024; CS-327 E-023 |

## Retirement Order

1. Decide and document `llm_astrology_input_v1` owner and block mapping.
2. Align `projection_hash`, `llm_input_hash` and `evidence_refs`.
3. Declare the modern runtime/configuration input schema.
4. Add prompt-visible versus runtime-only guards.
5. Classify external compatibility branches.
6. Remove or permanently document `chart_json`/`natal_data` compatibility.

## Non-Goals During Transition

- No prompt wording change.
- No provider change.
- No public endpoint change.
- No frontend change.
- No DB or migration change.
- No deletion of legacy code before owner decisions and validation evidence.
