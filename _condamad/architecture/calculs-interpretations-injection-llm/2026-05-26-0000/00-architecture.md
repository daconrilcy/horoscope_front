# Architecture Transition Calculs Interpretations Injection LLM

Source story: CS-328. Scope: architecture-only synthesis over CS-324, CS-325, CS-326 and CS-327. No application, prompt, provider, endpoint, DB, migration or frontend change is authorized.

## Executive Architecture Decision Summary

- observed: Current natal LLM assembly is still based on `chart_json`, `natal_data`, `evidence_catalog` and `astro_context`; recent interpretation owners are available but not injected. Sources: CS-324 F-001 E-008/E-009/E-010/E-011/E-013/E-016, CS-325 F-001 E-006/E-008/E-013/E-019.
- decision: The target flow is `CalculationGraph / ChartObjectRuntimeData -> ChartInterpretationInput -> contrat interne d'injection LLM -> prompt runtime -> audit narrative answer`. `ChartObjectRuntimeData` and `CalculationGraph` remain calculation/runtime sources, not prompt payloads. Sources: CS-324 E-005/E-006/E-008/E-020, brief CS-245, story CS-328.
- decision: Adopt `AINarrativeInputContract` as the target canonical internal LLM input owner, with an explicit LLM-facing wrapper/registry entry `llm_astrology_input_v1` only where LLM configuration needs a schema name. Sources: CS-326 F-001 E-009/E-010/E-016/E-020, CS-327 F-001 E-019/E-020.
- decision: `structured_facts_v1` owns hashable structural facts; it is an input block source, not the full LLM contract. Sources: CS-326 F-002 E-006/E-017, brief CS-256.
- decision: `client_interpretation_projection_v1` is product/editorial shaping by plan and must not become the canonical prompt input. Sources: CS-326 F-002 E-008/E-019, brief CS-258, brief CS-287.
- decision: `narrative_answer_audit_v1` remains audit storage for `projection_hash`, `llm_input_hash`, prompt/provider/model metadata and `evidence_refs`; it is never injected as prompt payload. Sources: CS-326 F-003 E-011/E-012/E-013/E-015/E-021/E-022, brief CS-259.
- blocker: Prompt configuration and runtime validation still declare/accept `chart_json` and do not expose `llm_astrology_input`, facts/signals/limits/proofs blocks. Sources: CS-327 F-001/F-003 E-007/E-008/E-013/E-017/E-019/E-020/E-023.
- blocker: `evidence_catalog` is validation-only in current prompt path, while future grounding may require prompt-visible evidence refs; owner decision is required before implementation. Sources: CS-325 F-003 E-008/E-011/E-017, CS-324 F-003 E-010/E-012/E-013.
- highest-risk dependency: Any prompt or runtime change before the canonical input/schema decision risks preserving public `chart_json` as source of truth. Sources: CS-324 F-001, CS-325 F-001, CS-327 F-001.

Target flow:

```text
CalculationGraph / ChartObjectRuntimeData
  -> ChartInterpretationInput
  -> AINarrativeInputContract
  -> llm_astrology_input_v1
  -> prompt runtime
  -> narrative_answer_audit_v1
```

## Audit Source Map

| Audit | Scope | Closure status | Key architecture inputs | Evidence IDs | Findings used | Blockers | Deferred context | Used for |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CS-324 `calculs-interpretations-vers-llm` | Calculation/interpretation surfaces versus current LLM input | closed with phased map | Current input uses `chart_json`, `natal_data`, `evidence_catalog`, `astro_context`; recent owners exist but are not in scoped path | E-005..E-016, E-020, E-021 | F-001, F-002, F-003, F-004; SC-001, SC-002, SC-003 | canonical input owner, duplicate `chart_json`/`natal_data`, evidence owner | prompt wording, provider, frontend, DB | source owner split and legacy transition |
| CS-325 `pipeline-prompt-llm-natal` | Natal prompt pipeline, message composition and branch behavior | closed with follow-up candidates | `chart_json` prompt-visible by default; runtime fields are not automatically prompt-visible; `evidence_catalog` validates output | E-006, E-008..E-013, E-017, E-019, E-023..E-025 | F-001, F-002, F-003, F-004; SC-001..SC-004 | prompt-visible/runtime-only distinction, evidence role, compatibility branches | prompt copy, provider, frontend | prompt runtime boundary and branch confinement |
| CS-326 `projections-interpretatives-llm-input-readiness` | Readiness of recent projections/contracts for LLM input | read-only; no app/test edit | `AINarrativeInputContract` best candidate; `structured_facts_v1` fact source; client projections are B2C shaping; audit storage is not injection | E-004..E-022 | F-001, F-002, F-003, F-004; SC-001, SC-002 | product may reject internal contract or use B2C shaping as prompt wording | provider, prompt rewrite, DB migration, frontend | target contract and object decisions |
| CS-327 `configuration-prompts-placeholders-input-schema` | Prompt configs, placeholders and input schema readiness | closed; full closure blocked by schema decision | Active configs still require `chart_json`; no `llm_astrology_input`; flat placeholders only | E-007, E-008, E-012..E-020, E-023 | F-001, F-002, F-003, F-004; SC-001..SC-003 | schema owner decision, validation payload ownership, structured placeholder governance | prompt copy, provider, frontend, DB | registry and roadmap sequencing |

Story label caveats: all `SC-*` values are audit provenance only. They are not definitive tracker IDs. CS-327 SC-001 is an architecture-transition candidate but remains `needs-tracker-remap` for implementation; no candidate here claims a final `CS-*` ID.

## Capability Matrix

| Capability / family | Inputs | Objects required | Canonical contracts required | Surfaces required | Status | Blockers | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| deterministic calculation facts | birth input, graph nodes, runtime references | `CalculationGraph`, `ChartObjectRuntimeData`, chart objects | graph/runtime registry, `structured_facts_v1` | internal, data_storage, observability | partial | raw runtime must not be prompt/public payload | CS-324 E-005/E-006/E-010; brief CS-245 |
| pre-narrative interpretation | calculation outputs, aspects, dignities, dominance, missing data | `ChartInterpretationInputRuntimeData`, `AINarrativeInputContract` | `chart_interpretation_input_v1`, `ai_narrative_input_v1` | internal, automation_or_llm | partial | not wired into natal LLM path | CS-324 F-001 E-008/E-009/E-016; CS-326 F-001 |
| hashable facts for audit | interpretation input | `structured_facts_v1` | `structured_facts_v1`, `projection_hash` | internal, data_storage, observability | implemented | not sufficient alone for narrative readiness | CS-326 F-002 E-006/E-017; brief CS-256 |
| LLM injection contract | facts, signals, limits, evidence refs, shaping, provenance | `AINarrativeInputContract`, `llm_astrology_input_v1` | `llm_astrology_input_v1`, `llm_input_hash`, `evidence_refs` | automation_or_llm, observability | missing | owner/schema decision and config readiness | CS-326 F-001; CS-327 F-001/F-003 |
| prompt runtime rendering | LLM input schema, prompt placeholders, plan/context | `ExecutionContext`, `NatalExecutionInput`, prompt config | structured placeholder contract | internal, automation_or_llm | conflicting | current prompt path uses `chart_json` flat placeholders | CS-325 F-002; CS-327 F-003 |
| narrative answer audit | LLM output, projection hash, input hash, evidence refs | `narrative_answer_audit_v1` | `narrative_answer_audit_v1` | data_storage, observability, admin_debug | partial | current hashes are not derived from target contract yet | CS-326 F-003 E-011/E-012/E-015; brief CS-259 |
| client projection by plan | facts, signals, entitlements, plan | `client_interpretation_projection_v1` | projection by plan contract | frontend, public_api | implemented | must remain B2C projection, not prompt source | CS-326 F-002 E-008/E-019; brief CS-258/CS-287 |

## Surface Matrix

| Surface | Statut actuel | Statut cible | Owner actuel | Owner cible | LLM input | Public | Legacy | Action recommandee |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `chart_json` | observed: public/historical projection and current prompt-visible carrier | confined compatibility only | chart JSON builder / public chart projection | public projection owner; not LLM owner | no, except bounded compatibility | yes | yes | Replace as canonical LLM input after `llm_astrology_input_v1`; guard no new alias. Sources: CS-324 F-002 E-012/E-013/E-014; CS-327 F-001 E-007/E-010/E-011 |
| `natal_data` | observed: same projection as `chart_json` in dict form | confined runtime compatibility only | natal LLM service | LLM runtime mapping owner | no, except transition-condition | no | yes | Remove or explicitly mark duplicate compatibility after target mapping. Sources: CS-324 F-002; CS-327 F-002 E-012/E-016 |
| `astro_context` | observed: narrow astral-point context | optional interpretive signal source if renamed/scoped | shared natal context | interpretation owner | only as scoped signal block | no | transition | Rename/classify before use as broad astrology context. Sources: CS-324 F-004 E-013/E-021 |
| `evidence_catalog` | observed: validation-only in current path | split into validation catalog plus `evidence_refs` in contract | chart JSON/evidence builder and output validator | evidence registry owner | blocker: decision required | no | transition | Decide prompt-visible vs validation-only; never prompt prose owner. Sources: CS-325 F-003 E-008/E-011/E-017; CS-324 F-003 |
| `ChartObjectRuntimeData` | observed: rich runtime internal payload | internal calculation primitive only | astrology runtime | runtime domain owner | no raw exposure | no | no | Feed interpretation input, never provider/public payload. Sources: CS-324 E-005; CS-245 |
| `ChartInterpretationInputRuntimeData` | observed: built from runtime outputs | canonical pre-narrative input | interpretation builder | interpretation domain owner | source to LLM contract | no | no | Use as bridge from runtime facts to narrative input. Sources: CS-324 E-008/E-020 |
| `structured_facts_v1` | observed: stable hashable fact projection | canonical facts block source | interpretation projection owner | fact registry owner | yes, facts block only | not direct B2C | no | Keep non-narrative and hashable; derive `projection_hash`. Sources: CS-326 F-002 E-006/E-017; brief CS-256 |
| `client_interpretation_projection_v1` | observed: plan-aware B2C projection | shaping source only, not canonical facts | client projection builder | product projection owner | only shaping metadata by plan | yes | no | Keep as product projection; prevent factual prompt ownership. Sources: CS-326 F-002 E-008/E-019; brief CS-258 |
| `AINarrativeInputContract` | observed: best candidate, available-not-injected | canonical internal LLM input owner | interpretation/narrative input builder | architecture + interpretation owners | yes | no | no | Adopt and wrap as `llm_astrology_input_v1` for LLM schema/config. Sources: CS-326 F-001 E-009/E-010/E-020 |
| `narrative_answer_audit_v1` | observed: stores hashes/provider/model/evidence refs | audit-only output trace | audit persistence/workflow | observability/data owner | no | no | no | Persist `projection_hash`, `llm_input_hash`, `evidence_refs`; never inject raw prompt payload. Sources: CS-326 F-003 E-011/E-012/E-013/E-015/E-022; brief CS-259 |

## Canonical Registry Decisions

### LLM Input Contract Registry

Decision: adopt.
Owner: architecture owner + backend astrology interpretation owner + LLM runtime owner.

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ai_narrative_input` | `v1` | `ChartInterpretationInputRuntimeData`, facts, signals, readiness, source versions, masking policy | immutable internal narrative input | additive only for optional fields; semantic changes require v2 | deprecate only after all prompt/runtime consumers migrate | `source_versions`, readiness flags, projection links | CS-326 F-001 E-009/E-010/E-020 |
| `llm_astrology_input` | `v1` | `ai_narrative_input_v1`, evidence refs, plan shaping, exclusions | structured facts/signals/limits/proofs/provenance/shaping blocks for runtime schema | may coexist with `chart_json` during transition-condition only | retire `chart_json` prompt ownership after schema and tests pass | `projection_hash`, `llm_input_hash`, `evidence_refs`, `prompt_ref` | CS-327 F-001/F-003 E-019/E-020; CS-325 F-002/F-003 |

### Projection And Evidence Registry

Decision: adopt.
Owner: backend interpretation projection owner + observability/data owner.

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `structured_facts` | `v1` | `ChartInterpretationInputRuntimeData` | non-narrative stable fact payload | hash identity must remain deterministic | v2 required for field meaning/order/hash changes | `hash_input`, `projection_hash`, excluded surfaces | CS-326 F-002 E-006/E-017; brief CS-256 |
| `client_interpretation_projection` | `v1` | `structured_facts_v1`, plan, entitlements/disclaimers | B2C projection by plan | public contract compatibility applies | do not deprecate into prompt payload; keep separate | `projection_version`, plan, audit input | CS-326 F-002 E-008/E-019; brief CS-258/CS-287 |
| `narrative_answer_audit` | `v1` | LLM output, prompt/model/provider, hashes and evidence refs | audit storage and rejection workflow evidence | persisted compatibility; additive metadata only | retention/deprecation needs data owner | `projection_hash`, `llm_input_hash`, `evidence_refs`, `grounding_status` | CS-326 F-003 E-011/E-012/E-013/E-015/E-022; brief CS-259 |

### Legacy Compatibility Registry

Decision: defer implementation; adopt classification requirement.
Owner: backend LLM runtime owner + product owner for externally contracted branches.

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `chart_json_prompt_compat` | transition | public chart projection | current prompt-compatible string/dict payload | allowed only under transition-condition | remove after `llm_astrology_input_v1` prompt/runtime schema validation | request/trace ID, prompt version | CS-324 F-002; CS-325 F-004; CS-327 F-001/F-002 |
| `natal_branch_compat` | transition | `/users`, `free_short`, schema v1/v2/v3, fallback configs | explicit keep/remove branch register | each branch requires owner decision | no unclassified branch may survive migration | branch key, use case key, plan/module | CS-325 F-004 E-003/E-005/E-006/E-020/E-024/E-025 |

## Object / Entity Decisions

| Object | Kind | Lifecycle owner | Persistence | Serialization | Versioning | Surfaces | Decision | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `CalculationGraph` | core_entity | astrology runtime owner | not persisted as LLM payload | graph definition/result contracts only | graph family/version registry | internal, observability | observed primitive; decision: calculation source only | CS-324 E-006; brief CS-245 |
| `ChartObjectRuntimeData` | value_object | astrology runtime owner | no public/prompt persistence | internal typed payload | runtime contract version if exposed to replay | internal, admin_debug only | decision: no raw LLM/provider/public exposure | CS-324 E-005; CS-245 |
| `ChartInterpretationInputRuntimeData` | derived_object | interpretation owner | optional replay/debug only | typed interpretation input | `chart_interpretation_input_v1` | internal, automation_or_llm | decision: bridge object from calculation to narrative input | CS-324 E-008/E-020 |
| `structured_facts_v1` | derived_object | fact projection owner | hashable projection/audit | stable JSON/hash input | explicit v1 hash compatibility | internal, data_storage, observability | decision: facts block source | CS-326 F-002 E-006/E-017 |
| `AINarrativeInputContract` | derived_object | interpretation/narrative owner | not public; may be audit-linked | immutable internal contract | v1; v2 for semantics/hash/readiness changes | internal, automation_or_llm | decision: canonical internal LLM input owner | CS-326 F-001 E-009/E-010/E-020 |
| `llm_astrology_input_v1` | presentation_model | LLM runtime/config owner | request/audit hash only, not raw long-term payload unless data owner approves | structured blocks | v1; schema changes require v2 | automation_or_llm, observability | decision: schema-facing wrapper around AINarrative input | CS-327 F-001/F-003 |
| `client_interpretation_projection_v1` | presentation_model | product projection owner | public/projection persistence as allowed | plan-aware public JSON | v1 public compatibility | public_api, frontend | decision: shaping/projection only, not fact source | CS-326 F-002 E-008/E-019 |
| `narrative_answer_audit_v1` | debug_artifact | observability/data owner | persisted audit rows | audit schema | v1 persisted compatibility | data_storage, admin_debug, observability | decision: audit-only, never prompt payload | CS-326 F-003 E-011/E-012/E-022 |
| `chart_json` | presentation_model | public chart projection owner | existing public/runtime compatibility | legacy JSON/string | transition only | public_api, automation_or_llm transition | decision: confined legacy carrier | CS-324 F-002 E-012/E-013/E-014; CS-327 F-002 |
| `evidence_refs` | value_object | evidence/audit owner | persisted with audit | reference list with SHA-256 hash requirement | evidence schema version | data_storage, observability, optional LLM input block | blocker: prompt-visible role needs owner decision | CS-326 E-011/E-012/E-013; CS-325 F-003 |

## Operational Rules

| Rule area | Rule | Applies to | Invalidated by | Trace requirement | Owner | Sources |
| --- | --- | --- | --- | --- | --- | --- |
| Versioning | Version every cross-surface contract as `_v1`; semantic/hash/input changes require v2 | `structured_facts_v1`, `ai_narrative_input_v1`, `llm_astrology_input_v1`, `narrative_answer_audit_v1` | required field, semantics, ordering, determinism, cache/replay identity changes | contract ID + version in request/audit | architecture owner | decision-rules.md; CS-326 F-001/F-003 |
| Trace | Every generated narrative must retain source projection and LLM input hashes | `prompt runtime`, `narrative_answer_audit_v1` | missing or mismatched source facts/evidence | `projection_hash`, `llm_input_hash`, `evidence_refs`, prompt/model/provider | observability/data owner | CS-326 F-003 E-011/E-012/E-015/E-022 |
| Cache | Cache identity must include contract version, input hash, plan and prompt/runtime version | LLM input, prompt runtime, validation | facts/signals/limits/evidence/shaping/provenance change | cache key material recorded in audit | LLM runtime owner | CS-324 F-003; CS-327 F-001 |
| Replay | Replay uses stored hashes, versions and evidence refs; raw `ChartObjectRuntimeData` replay is not required for prompt proof | narrative audit, rejected workflow | unavailable contract version or missing evidence refs | replay snapshot points to contract versions and hashes | observability owner | CS-326 E-012/E-013/E-021 |
| Invalidation | Invalidate `llm_input_hash` when facts, signals, missing data, evidence refs, plan shaping, masking policy or source versions change | `llm_astrology_input_v1` | any block content or version change | invalidation reason + old/new hash | LLM runtime owner | CS-326 F-001/F-002; CS-327 F-003 |
| Migration | `chart_json`/`natal_data` may exist only under named transition-condition until schema and prompt-visible tests pass | legacy carriers | target schema declared and tests green | branch status and transition condition | backend LLM owner | CS-324 F-002; CS-327 F-002 |
| Observability | Distinguish prompt-visible, runtime-only, validation-only and audit-only fields in tests/guards | gateway, renderer, validator, audit | new field without classification | field classification matrix in tests/docs | LLM runtime owner | CS-325 F-002/F-003; CS-327 F-003 |

## Blockers And Decision Owners

| Item | Type | Owner | Blocks | Required decision | Sources |
| --- | --- | --- | --- | --- | --- |
| Canonical schema name and owner | blocker | architecture owner + LLM runtime owner | all implementation stories | Confirm `AINarrativeInputContract` as target and `llm_astrology_input_v1` as schema wrapper | CS-326 F-001 SC-001; CS-327 F-001 SC-001 |
| Evidence role | blocker | observability/data owner + product owner | evidence mapping and prompt grounding | Keep `evidence_catalog` validation-only or include evidence refs in prompt-visible block | CS-325 F-003 SC-003; CS-324 F-003 |
| Legacy compatibility branch status | blocker | product owner + backend LLM owner | safe prompt/runtime refactor | Classify `/users`, `free_short`, schema compatibility and fallback branches | CS-325 F-004 SC-004 |
| Prompt placeholder shape | blocker | LLM configuration owner | structured prompt block implementation | Choose single structured placeholder vs multiple facts/signals/limits/proofs fields | CS-327 F-003 SC-003 |
| Public projection boundary | decision | product owner | client projection use in LLM | Confirm `client_interpretation_projection_v1` is not factual prompt source | CS-326 F-002; brief CS-258 |

## Ordered Implementation Roadmap

### Story 1: Formaliser le registre `llm_astrology_input_v1`

Story ID: needs-tracker-remap.
Source label: CS-326 SC-001, CS-327 SC-001, CS-324 SC-001, CS-325 SC-001.
Goal: define the canonical LLM input registry entry and field map without changing prompt copy.
Source audits: CS-324, CS-325, CS-326, CS-327.
Source findings: CS-324 F-001/F-003, CS-325 F-001, CS-326 F-001, CS-327 F-001.
Scope: contract/schema decision, ownership routing, `NatalExecutionInput` mapping, transition-condition for `chart_json`.
Out of scope: provider integration, prompt wording, frontend, public endpoint.
Dependencies: owner approval.
Acceptance criteria:
- `llm_astrology_input_v1` maps facts, signals, limits, evidence refs, shaping, provenance and exclusions.
- `AINarrativeInputContract` is invoked or explicitly rejected by owner decision.
- raw `ChartObjectRuntimeData` remains absent from prompt/provider payload.
Validation evidence:
- scans for selected owner in natal assembly and no raw runtime class in provider/prompt layers.
- contract tests for shape and version.
Blockers / decisions:
- architecture owner must approve target owner.
Stop condition: stop if product requires client projection to be prompt source.

### Story 2: Converger les faits hashables et `evidence_refs`

Story ID: needs-tracker-remap.
Source label: CS-324 SC-003, CS-325 SC-003, CS-326 F-003.
Goal: align evidence refs and `projection_hash`/`llm_input_hash` with the canonical fact/input source.
Source findings: CS-324 F-003, CS-325 F-003, CS-326 F-003.
Scope: evidence owner decision, hash inputs, validation role, rejected answer workflow compatibility.
Out of scope: prompt copy and provider changes.
Dependencies: Story 1.
Acceptance criteria:
- `structured_facts_v1` owns fact hash material.
- `llm_input_hash` changes when any target injection block changes.
- evidence refs validate against allowed sources.
Validation evidence:
- audit/rejection workflow tests and hash stability tests.
Blockers / decisions:
- decide whether evidence refs are prompt-visible or validation-only.
Stop condition: stop if evidence refs cannot be tied to canonical facts.

### Story 3: Déclarer le schéma runtime/configuration moderne

Story ID: needs-tracker-remap.
Source label: CS-327 SC-001, CS-327 SC-002.
Goal: make natal LLM configuration declare the canonical structured astrology input schema.
Source findings: CS-327 F-001/F-002/F-003.
Scope: use-case input schema, validation payload ownership, no wildcard placeholder.
Out of scope: prompt wording.
Dependencies: Story 1 and Story 2 role decisions.
Acceptance criteria:
- active natal use cases declare `llm_astrology_input_v1` or documented exceptions.
- validation no longer silently treats `natal_data`/parsed `chart_json` as canonical modern input.
- no new legacy aliases.
Validation evidence:
- LLM orchestration tests around schema validation and gateway payload.
Blockers / decisions:
- schema wrapper versus direct `AINarrativeInputContract`.
Stop condition: stop if compatibility requirements for public branches are unknown.

### Story 4: Garder la frontiere prompt-visible/runtime-only

Story ID: needs-tracker-remap.
Source label: CS-325 SC-002, CS-327 SC-003.
Goal: guard message composition so only intended blocks are prompt-visible.
Source findings: CS-325 F-002, CS-327 F-003.
Scope: gateway/renderer tests, placeholder governance, classification of facts/signals/limits/proofs.
Out of scope: editorial prompt copy.
Dependencies: Story 3.
Acceptance criteria:
- tests distinguish prompt-visible, runtime-only, validation-only and audit-only fields.
- `chart_json` compatibility is visible only under transition-condition.
Validation evidence:
- focused gateway and prompt renderer tests.
Blockers / decisions:
- structured placeholder shape owner decision.
Stop condition: stop if prompt copy changes are requested without separate story.

### Story 5: Confiner et retirer les surfaces legacy

Story ID: needs-tracker-remap.
Source label: CS-324 SC-002, CS-325 SC-004, CS-327 F-004.
Goal: classify and then remove or permanently document compatibility surfaces.
Source findings: CS-324 F-002/F-004, CS-325 F-004, CS-327 F-002/F-004.
Scope: `/users`, `free_short`, schema compatibility, fallback branches, `chart_json`/`natal_data`, `astro_context`.
Out of scope: public endpoint redesign and frontend.
Dependencies: Stories 1-4.
Acceptance criteria:
- every branch is `intentional`, `delete-candidate` or `needs-user-decision`.
- no unclassified fallback carries modern input.
Validation evidence:
- branch scans and targeted service/gateway tests.
Blockers / decisions:
- product owner must classify externally contracted compatibility branches.
Stop condition: stop if a branch has unknown external contract status.

## Open Questions And Validation Plan

| Question | Why it matters | Owner | Blocks | Suggested default | Sources |
| --- | --- | --- | --- | --- | --- |
| Should the schema be named `llm_astrology_input_v1` while using `AINarrativeInputContract` internally? | Separates internal owner from LLM runtime/config vocabulary | architecture owner | Story 1/3 | yes | CS-326 F-001, CS-327 F-001 |
| Are `evidence_refs` prompt-visible, validation-only, or both? | Determines grounding before generation vs after generation | observability/data owner | Story 2/4 | both: refs visible, detailed catalog validation/audit-only | CS-325 F-003, CS-326 F-003 |
| Which legacy natal branches are externally contracted? | Avoids accidental breaking changes during confinement | product owner | Story 5 | classify before code change | CS-325 F-004 |
| Can `astro_context` be renamed or scoped? | Current name overclaims broad astrology context | backend interpretation owner | Story 5 | keep transition-only until renamed | CS-324 F-004 |

Validation plan:

- `Test-Path` for the four source audit folders.
- `rg -n "CS-324|CS-325|CS-326|CS-327"` over the architecture folder.
- `rg -n "CalculationGraph|ChartObjectRuntimeData|ChartInterpretationInput|prompt runtime"` in `00-architecture.md`.
- `rg -n "chart_json|natal_data|astro_context|evidence_catalog|AINarrativeInputContract"` over the architecture folder.
- `rg -n "projection_hash|llm_input_hash|evidence_refs|transition-condition"` over the architecture folder.
- Python path check, after venv activation, for the six required files.
- `git status --short -- backend/app backend/tests frontend/src backend/migrations` must show no app surface modified.
