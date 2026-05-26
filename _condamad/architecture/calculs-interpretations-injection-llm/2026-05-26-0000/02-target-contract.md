# Target Contract Conceptuel

Decision: define `llm_astrology_input_v1` as the LLM-runtime schema wrapper around `AINarrativeInputContract`. The wrapper is internal and versioned; it is not a public API projection and not a prompt text.

## Contract Identity

| Field | Decision | Sources |
| --- | --- | --- |
| Canonical owner | `AINarrativeInputContract` owns internal narrative readiness | CS-326 F-001 E-009/E-010/E-020 |
| LLM schema name | `llm_astrology_input_v1` | CS-327 F-001 E-019/E-020 |
| Fact source | `structured_facts_v1` | CS-326 F-002 E-006/E-017 |
| Product shaping source | `client_interpretation_projection_v1` metadata only | CS-326 F-002 E-008/E-019 |
| Audit target | `narrative_answer_audit_v1` stores `projection_hash`, `llm_input_hash`, `evidence_refs` | CS-326 F-003 E-011/E-012/E-015/E-022 |
| Forbidden source | prompt prose, provider output, public `chart_json` compatibility payload | CS-324 F-001/F-002; CS-325 F-001; CS-327 F-001 |

## Target Injection Block Matrix

| Bloc | Contenu | Source canonique | Source interdite | Hashable | Prompt-visible | Audit-visible | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| faits structurels | positions, maisons, aspects principaux, dominantes, donnees manquantes factuelles, versions source | `structured_facts_v1` from `ChartInterpretationInputRuntimeData` | `chart_json`, prompt text, provider output, raw `ChartObjectRuntimeData` | yes | yes | yes | fact projection owner; sources CS-326 F-002 E-006/E-017 |
| signaux interpretatifs | signals pre-narratifs, readiness flags, masking policy, interpretive indicators | `AINarrativeInputContract` | final LLM answer, client wording, frontend labels | yes, when deterministic | yes | yes | interpretation/narrative owner; sources CS-326 F-001 E-009/E-020 |
| limites et donnees manquantes | missing data, excluded surfaces, confidence/readiness flags | `structured_facts_v1` + `AINarrativeInputContract` | prompt disclaimers as source of truth | yes | yes | yes | interpretation owner; sources CS-326 E-006/E-009 |
| preuves / evidence refs | `evidence_refs`, allowed evidence source IDs, hash references, validation role | evidence refs validator + narrative audit workflow | public `chart_json` labels as canonical owner, prompt prose | yes | open question: refs visible, detailed catalog validation-only | yes | observability/data owner; sources CS-324 F-003, CS-325 F-003, CS-326 F-003 |
| shaping editorial par plan | plan, depth profile, allowed client sections, visibility policy | `client_interpretation_projection_v1` metadata only | treating B2C labels as facts | yes if deterministic inputs included in `llm_input_hash` | yes, as instructions/context not facts | yes | product projection owner; sources CS-326 F-002 E-008/E-019 |
| provenance et versions | contract versions, `projection_hash`, `llm_input_hash`, source versions, prompt ref/version | `narrative_answer_audit_v1`, input registry | runtime-only object dumps, provider response as provenance | yes | no, except compact prompt ref/version if required | yes | observability/data owner; sources CS-326 F-003 E-012/E-015/E-022 |
| exclusions explicites | no raw runtime, no client projection as facts, no prompt/provider as source of truth, no hidden fallback | architecture registry and guards | wildcard placeholder allowlist, hidden compatibility alias | yes, as policy version | optional summary | yes | architecture owner; sources CS-324 F-001/F-002, CS-327 F-003 |

## Conceptual Shape

```text
llm_astrology_input_v1
  contract_version
  facts: structured_facts_v1 subset + hash identity
  signals: AINarrativeInputContract interpretive_signals/readiness_flags
  limits: missing_data + excluded_surfaces + masking_policy
  evidence: evidence_refs + validation role
  shaping: plan/depth/allowed section metadata, not factual owner
  provenance: source_versions + projection_hash + llm_input_hash + prompt_ref
  exclusions: forbidden source list and compatibility transition-condition
```

## Hash Rules

- `projection_hash` is derived from stable projection/fact material, primarily `structured_facts_v1`. Sources: CS-326 F-002/F-003.
- `llm_input_hash` is derived from all prompt-influencing target blocks: facts, signals, limits, evidence refs, shaping, provenance version IDs and exclusions policy. Sources: CS-326 F-003, CS-327 F-001/F-003.
- `evidence_refs` must reference allowed evidence sources and SHA-256-compatible hash material. Sources: CS-326 E-011/E-013.
- Any change to facts, signals, missing data, plan shaping, evidence refs, source versions, masking policy or prompt input schema invalidates `llm_input_hash`.

## Forbidden Shortcuts

- `chart_json` must not be promoted as `llm_astrology_input_v1`; it is transition-condition compatibility only. Sources: CS-324 F-002, CS-327 F-001.
- `natal_data` must not silently satisfy a modern structured input after migration. Sources: CS-327 F-002 E-016.
- `client_interpretation_projection_v1` must not be used as factual prompt source. Sources: CS-326 F-002.
- `narrative_answer_audit_v1` must not be injected as context. Sources: CS-326 F-003.
- Prompt copy and provider output are never sources of truth. Sources: CS-254, CS-325 F-002.
