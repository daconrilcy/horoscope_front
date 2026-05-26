# Story Candidates

All IDs below are candidate routing labels only. They must be remapped by the tracker before implementation.

## Story Candidate Matrix

| Priorite | Story candidate | But | Prerequis | Risque | Validation attendue |
| --- | --- | --- | --- | --- | --- |
| P1 | needs-tracker-remap: Formaliser `llm_astrology_input_v1` | Choose canonical LLM input owner and map fields from `AINarrativeInputContract` | Architecture owner decision | continuing `chart_json` as source of truth | contract shape tests, scans for selected owner, no raw runtime prompt/provider exposure |
| P2 | needs-tracker-remap: Aligner facts/hash/evidence refs | Make `projection_hash`, `llm_input_hash`, `evidence_refs` derive from target facts/input | P1, evidence owner decision | ungrounded or untraceable narrative audit | hash stability tests, evidence refs validation, rejected workflow tests |
| P3 | needs-tracker-remap: Declarer schema runtime/config LLM | Replace `chart_json`-only schema with structured astrology input | P1/P2 | modern payload exists but configs cannot validate it | LLM orchestration schema tests and zero new legacy alias scan |
| P4 | needs-tracker-remap: Garder prompt-visible/runtime-only | Guard what enters prompt versus runtime/validation/audit only | P3 | accidental prompt exposure or hidden non-grounding | gateway/renderer tests and field classification matrix |
| P5 | needs-tracker-remap: Confiner legacy branches | Classify `/users`, `free_short`, schema/fallback and duplicate carriers | P1-P4, product owner branch decisions | breaking compatibility or keeping hidden fallbacks | branch register, targeted service/gateway tests, scans for transition-condition |

## Candidate Cards

### P1 - Formaliser `llm_astrology_input_v1`

Source labels: CS-326 SC-001, CS-327 SC-001, CS-324 SC-001, CS-325 SC-001.
Source findings: CS-326 F-001; CS-327 F-001; CS-324 F-001/F-003; CS-325 F-001.
Scope: registry, field map, owner, exclusions, transition-condition.
Out of scope: prompt wording, provider, frontend, public endpoint, DB.
Acceptance criteria:
- `AINarrativeInputContract` is canonical internal owner or rejection is recorded as product/architecture decision.
- `llm_astrology_input_v1` has facts, signals, limits, evidence refs, shaping, provenance and exclusions.
- `ChartObjectRuntimeData` is not raw prompt/provider payload.
Stop condition: product requires `client_interpretation_projection_v1` or `chart_json` to remain factual prompt source.

### P2 - Aligner facts/hash/evidence refs

Source labels: CS-324 SC-003, CS-325 SC-003, CS-326 F-003.
Source findings: CS-324 F-003; CS-325 F-003; CS-326 F-002/F-003.
Scope: `structured_facts_v1`, `projection_hash`, `llm_input_hash`, `evidence_refs`, validation-only versus prompt-visible evidence.
Out of scope: prompt copy and provider.
Acceptance criteria:
- facts hash source is `structured_facts_v1`.
- `llm_input_hash` includes all prompt-influencing blocks.
- `evidence_refs` validate against allowed sources.
Stop condition: evidence owner cannot decide prompt-visible role.

### P3 - Declarer schema runtime/config LLM

Source labels: CS-327 SC-001, CS-327 SC-002.
Source findings: CS-327 F-001/F-002/F-003.
Scope: active natal use cases, validation payload ownership, structured placeholder/schema fields.
Out of scope: editorial prompt rewrite.
Acceptance criteria:
- active natal use cases declare `llm_astrology_input_v1` or explicit exception.
- `_build_validation_payload` has one modern owner and no silent `chart_json` substitution for modern input.
- no wildcard placeholder allowlist.
Stop condition: compatibility branch status is unknown.

### P4 - Garder prompt-visible/runtime-only

Source labels: CS-325 SC-002, CS-327 SC-003.
Source findings: CS-325 F-002; CS-327 F-003.
Scope: gateway message composition tests, renderer/placeholder governance, classification of facts/signals/limits/proofs.
Out of scope: prompt prose changes.
Acceptance criteria:
- tests prove `natal_data`, `astro_context`, `plan`, `level`, `module`, `variant_code` remain non-visible unless explicitly allowed.
- `chart_json` compatibility is limited by transition-condition.
Stop condition: prompt rewrite is requested without separate story.

### P5 - Confiner legacy branches

Source labels: CS-324 SC-002, CS-325 SC-004, CS-327 F-004.
Source findings: CS-324 F-002/F-004; CS-325 F-004; CS-327 F-002/F-004.
Scope: `/users`, `free_short`, `natal_long_free`, schema compatibility, fallback, `chart_json`, `natal_data`, `astro_context`.
Out of scope: public endpoint redesign.
Acceptance criteria:
- every compatibility branch is `intentional`, `delete-candidate` or `needs-user-decision`.
- no new `*_legacy` or duplicate factual carrier is introduced.
Stop condition: product owner cannot classify external compatibility.
