<!-- Commentaire global: rapport d'architecture produit CS-348 pour la generation des prompts LLM. -->

# Architecture Prompt Generation LLM - CS-348

## Executive architecture decision summary

- observed: CS-343 to CS-347 provide the source-of-truth audit bundle for prompt generation architecture; no new code audit is performed here.
- inferred: the architecture can safely standardize the four boundary labels because all five audits classify prompt generation through prompt-visible, runtime-only, validation-only or audit-only surfaces. Sources: CS-343 boundary summary, CS-345 include/exclude matrix, CS-346 prompt/backend classification, CS-347 pipeline.
- decision: use `llm_astrology_input_v1` as the modern natal prompt input contract, with `facts`, `signals`, `limits`, and `shaping` as prompt-visible blocks. Sources: CS-343 E-005/E-007, CS-346 F-001/F-002.
- decision: keep `evidence`, `grounding_status`, `validation_owner`, `provenance`, hashes, provider responses and persisted answers outside provider prompt material. Sources: CS-345 F-002, CS-346 F-002/F-004, CS-347 F-002.
- decision: treat seeds and bootstrap files as provisioning inputs, not runtime truth. Sources: CS-344 F-001/F-004, CS-343 surface table.
- blocker: output schema ownership is split across canonical contracts, assembly rows, fallback catalog, bootstrap schemas and tests; a product/architecture decision is required before convergence. Sources: CS-344 F-002, SC-001.
- blocker: semantic grounding is bounded by evidence refs and policy checks, not a full semantic verifier. Sources: CS-347 F-004, SC-001.
- decision: classify repair, use-case fallback, test fallback and provider fallback as non-nominal recovery, not nominal provider handoff. Sources: CS-345 F-003, CS-347 pipeline.
- decision: replay and observability are audit-only investigation surfaces; they do not prove prompt correctness. Sources: CS-347 F-003/F-004.
- highest-risk dependency: canonical schema ownership must be settled before API, automation, cache/replay or report claims rely on output shape as a stable product contract. Sources: CS-344 F-002, CS-347 F-004.

## Audit source map

| Audit | Scope | Closure status | Key architecture inputs | Evidence IDs | Findings used | Blockers | Deferred context | Used for |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CS-343 Surface Inventory | Inventory backend LLM prompt-generation surfaces | Closed as read-only inventory | Surface owners, status taxonomy, boundary taxonomy, debt carriers | E-003, E-004, E-005, E-006, E-007, E-010, E-011, E-012 | F-001, F-002, F-003 | Legacy/debt text hits must stay classified until routed | CS-344 to CS-350 detailed closure | Surface matrix, boundary vocabulary |
| CS-344 Configuration Assembly Placeholder | Configuration, assembly, renderer, placeholders, schemas, seeds | Closed with schema and guard gaps | Nominal configuration chain, placeholder families, output schema owner split, seed classification | E-005, E-006, E-007, E-010, E-011, E-012, E-013, E-014, E-017, E-018 | F-001, F-002, F-003, F-004 | Output schema ownership split; mutating prompt-resolution test | Provider handoff in CS-345; natal input in CS-346; persistence in CS-347 | Registries, roadmap stories SC-001 and SC-002 |
| CS-345 Runtime Gateway Handoff | Gateway-to-provider runtime handoff | Closed with no implementation story | Last payload is `messages`; provider params are runtime-only; recovery is non-nominal | E-004, E-005, E-006, E-007, E-008, E-009, E-010, E-011, E-012, E-013, E-015, E-016, E-017 | F-001, F-002, F-003, F-004 | Exact runtime handoff guardrail absent from registry | CS-346 input production; CS-347 output validation | Provider handoff contract, surface matrix |
| CS-346 Natal Astrology Input | Block-by-block source of modern natal input | Closed for audited domain | Canonical builders, prompt-visible blocks, evidence/provenance exclusion, hash policy | E-004, E-005, E-006, E-007, E-008, E-009, E-010, E-011, E-012, E-013, E-014 | F-001, F-002, F-003, F-004 | Integration legacy guards require `--long` | CS-347 post-provider persistence | Object/entity decisions, cache/hash rules |
| CS-347 Output Validation Persistence | Post-provider validation, rejection, audit persistence, observability, replay | Closed with semantic limit routed to CS-348/CS-350 | Validation pipeline, rejection workflow, persisted anchors, logs, replay, admin audit | E-006, E-007, E-008, E-009, E-010, E-011, E-012, E-013, E-015, E-016, E-017, E-018, E-019, E-020, E-021 | F-001, F-002, F-003, F-004, F-005 | Semantic grounding is bounded; exact post-provider guardrail absent | CS-350 final cartography report | Operational rules, blockers, roadmap SC-001 |

Story label caveats: audit story candidates `SC-001` and `SC-002` are provenance labels only. This report does not assign final tracker IDs; roadmap stories use `next-available-id` or `needs-tracker-remap` where implementation is later authorized.

## Capability matrix

| Capability / family | Inputs | Objects required | Canonical contracts required | Surfaces required | Status | Blockers | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Modern natal prompt input | `NatalResult`, structured facts, narrative contract, client projection, plan | `llm_astrology_input_v1`, `facts`, `signals`, `limits`, `shaping` | `llm_astrology_input_v1`, `LLM_ASTROLOGY_INPUT_DATA_ROLES`, hash material contract | internal, automation_or_llm, data_storage, observability | implemented | none | CS-343, CS-346 F-001/F-004 |
| Configuration and assembly resolution | use case, feature, subfeature, plan, locale, active assembly, profile | canonical use case, assembly, prompt template, execution profile | use-case contract, assembly contract, placeholder family contract, profile contract | internal, admin_debug, data_storage | partial | output schema owner split | CS-344 F-001/F-002 |
| Placeholder rendering | developer prompt, render vars, placeholder governance registry | placeholder family, rendered developer prompt | `prompt_governance_registry`, renderer required/allowed placeholder contract | internal, admin_debug, automation_or_llm | implemented | non-mutating guard gap | CS-344 F-003 |
| Provider handoff | execution request, resolved plan, messages, provider params | `messages`, `GatewayResult`, provider metadata | gateway handoff contract, provider parameter contract | internal, automation_or_llm, observability | implemented | exact registry guardrail missing | CS-345 F-001/F-004 |
| Input/output validation | input schema, raw provider output, output schema | `ValidationResult`, rejected answer outcome | input schema contract, output schema contract, rejection policy contract | internal, validation-only, data_storage | partial | output schema owner split; semantic grounding limit | CS-344 F-002, CS-347 F-001/F-004 |
| Audit persistence and observability | gateway result, rich input provenance, validation result, usage | persisted interpretation audit, `llm_call_logs`, replay snapshot | audit anchor contract, observability snapshot contract, replay snapshot contract | data_storage, admin_debug, observability | implemented | not proof of correctness | CS-347 F-002/F-003/F-004 |
| Non-nominal recovery | invalid output, repair prompts, fallback config, test flags | repair attempt, fallback metadata | recovery classification contract | internal, observability | implicit | must remain non-nominal unless product decides otherwise | CS-345 F-003, CS-347 |
| Final report / documentation | audit bundle, architecture decisions, bounded blockers | architecture report, future Mermaid report | product architecture contract | audit-only | partial | CS-350 owns final Mermaid documentation | CS-348 story, CS-347 SC-001 |

## Surface matrix

| Surface | Current contract | Expected contract | Capabilities exposed | Consumers | Risks | Blockers | Required changes | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| internal | Gateway, services, builders, validators and registries own runtime composition | Owner-routed internal contracts with no API/FastAPI dependency in domain/service prompt code | configuration, rich input, validation, handoff, recovery | backend domain/services | implicit coupling if schema ownership remains split | schema owner split | converge schema ownership before broad runtime changes | CS-343 F-003, CS-344 F-002 |
| public_api | Public routes trigger natal, guidance, chat, consultations, predictions | Runtime-only trigger surface; no prompt/audit internals leak | generation trigger | frontend or API clients | treating route payload as prompt truth | none observed in audits | keep prompt-visible classification inside runtime/gateway | CS-343 surface table |
| admin_debug | Admin LLM, sample payload, observability, replay endpoints | Admin-only audit/debug contracts, redacted where replay is exposed | preview, audit, replay, observability | operators/admin users | admin data mistaken for product proof | semantic proof limit | document that replay/admin are investigation surfaces | CS-343, CS-347 F-003/F-004 |
| automation_or_llm | Provider receives `messages` and provider params | Prompt-visible payload only; params runtime/provider-only | prompt execution, provider handoff | provider runtime manager, OpenAI adapter | audit-only or validation-only fields entering prompt | none observed; keep guard tests | preserve boundary tests and role constants | CS-345 F-001/F-002, CS-346 F-002 |
| frontend | No frontend edit in scope; frontend consumes public behavior only | No direct prompt registry or audit carrier dependency | user workflows after public API | users | future UI may display audit fields as correctness proof | no evidence for new frontend contract | defer frontend stories until contracts are stable | CS-348 non-goals |
| data_storage | DB models store prompts, use cases, assemblies, audit fields, logs, replay snapshots | Runtime truth must be separated from provisioning and audit anchors | config storage, persisted audit, observability, replay | backend services, admin | seed/bootstrap treated as runtime truth; audit anchors treated as prompt correctness | schema owner split; semantic proof limit | registry decisions for schema, audit anchors and replay | CS-344 F-004, CS-347 F-002/F-003/F-004 |
| observability | `log_call`, metadata, usage, replay snapshot, validation counters | Traceable audit-only investigation surface | debugging, replay, cost/usage, validation status | operators, developers | observability data overclaimed as semantic proof | semantic proof limit | add explicit trace and proof wording in docs/stories | CS-347 F-003/F-004 |

## Canonical registry decisions

### capability_registry

Decision: adopt
Owner: architecture owner

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| prompt_generation_capabilities | v1 | CS-343 to CS-347 audit bundle | Capability names and boundaries used by future stories | Additive capability rows are allowed; boundary changes require architecture decision | Deprecated capability labels must remain mapped to source audit IDs | story ID, audit path, finding IDs | CS-343 F-001, CS-348 story |

### prompt_input_registry

Decision: adopt
Owner: domain architecture owner

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| llm_astrology_input | v1 | structured facts, narrative input, client projection, limits | `llm_astrology_input_v1` with prompt-visible, validation-only and audit-only blocks | Prompt-visible block changes require version and hash policy review | `chart_json` and `natal_data` remain forbidden legacy carriers for modern natal prompt | request_id, trace_id, projection_hash, llm_input_hash, evidence_refs | CS-346 F-001/F-003/F-004 |

### configuration_registry

Decision: adopt with blocker
Owner: architecture owner plus product owner for fallback policy

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| use_case_contract | v1 | feature, subfeature, plan, locale, required placeholders, schemas | canonical use-case contract and seed parity | Contract changes require seed/config coherence validation | seed-only fields must not become runtime truth | use_case, prompt_version, schema_name, assembly_id | CS-344 F-001/F-004 |
| output_schema_resolution | needs-owner-decision | canonical contract, assembly row, fallback catalog, bootstrap schema | one nominal runtime schema owner, fallback/provisioning demoted | Breaking schema ownership changes require product/architecture approval | fallback and bootstrap schemas must be explicitly non-nominal or intentionally supported | schema_id, schema_version, use_case, assembly_id | CS-344 F-002, SC-001 |

### provider_handoff_registry

Decision: adopt
Owner: runtime gateway owner

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| provider_messages | v1 | resolved plan, developer prompt, persona block, user payload, optional chat history | ordered `messages` list and provider kwargs | Message ordering changes require gateway contract tests | recovery/fallback paths remain non-nominal and separately classified | request_id, trace_id, use_case, model, response_format | CS-345 F-001/F-003 |

### validation_audit_registry

Decision: adopt with semantic-limit blocker
Owner: data owner plus architecture owner

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| output_validation | v1 | raw provider output, output schema | `ValidationResult` with parsed/normalized/sanitized output | Schema shape changes require versioned tests | invalid or repaired outputs must keep recovery metadata | schema_version, validation_status, repair_attempted | CS-347 F-001 |
| narrative_grounding | v1-bounded | output evidence refs, backend evidence block, policy checks | accepted/rejected/controlled outcome | Cannot be marketed as full semantic verifier without new evidence | unsupported semantic-proof claims must be deprecated from docs | evidence_refs, grounding_status, projection_hash, llm_input_hash | CS-347 F-002/F-004 |

### replay_observability_registry

Decision: adopt
Owner: operations/data owner

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| llm_observability | v1 | gateway result, validation, usage, provider metadata | call logs, operational metadata, replay metadata | Additive metadata is compatible if redaction holds | raw or public replay exposure is forbidden without security decision | trace_id, request_id, input_hash, snapshot_id | CS-347 F-003/F-005 |

## Entity/object decisions

| Object | Kind | Lifecycle owner | Persistence | Serialization | Versioning | Surfaces | Decision | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `llm_astrology_input_v1` | value_object | natal interpretation domain owner | Full object may feed audit persistence; prompt projection is filtered | Canonical JSON for hash material; prompt-visible projection only for provider | `v1`; bump if prompt-visible blocks or hash semantics change | internal, automation_or_llm, data_storage, observability | adopt canonical modern natal input | CS-346 F-001/F-004 |
| `facts`, `signals`, `limits`, `shaping` | value_object | respective builders plus `LLMAstrologyInputV1Builder` | included in hash material | prompt-visible serialization | version with input contract | automation_or_llm | prompt-visible only blocks | CS-346 F-001/F-004 |
| `evidence`, `grounding_status`, `validation_owner` | value_object | validation owner | persisted/audit as needed | excluded from provider prompt | version with evidence contract | validation-only, data_storage | validation-only, not prompt-visible | CS-345 F-002, CS-346 F-002 |
| `provenance`, `projection_hash`, `llm_input_hash` | debug_artifact | data/audit owner | persisted as audit anchors | excluded from provider prompt | version with hash policy | audit-only, data_storage, observability | audit-only anchors | CS-346 F-004, CS-347 F-002 |
| `messages` | derived_object | runtime gateway owner | logged only through audit/observability policies | ordered provider message list | version on ordering/content contract changes | automation_or_llm, observability | last gateway-owned provider payload | CS-345 F-001 |
| `CanonicalUseCaseContract` | core_entity | LLM configuration owner | seed/provisioning and registry source | Pydantic contract | version on placeholder/schema semantics | internal, admin_debug, data_storage | runtime configuration input, not final schema owner until blocker resolved | CS-344 F-001/F-002 |
| assembly/config snapshot | core_entity | configuration owner | DB/snapshot | resolved plan/config serialization | version on selection semantics | internal, admin_debug, data_storage | nominal assembly selector | CS-344 registry matrix |
| output schema | value_object | needs owner decision | DB/snapshot/fallback/seed currently split | JSON schema | version every shape/semantic contract change | internal, validation-only, data_storage | defer final owner decision | CS-344 F-002 |
| `ValidationResult` | derived_object | output validation owner | audit/log metadata | parsed normalized output | schema-versioned | validation-only, data_storage, observability | adopt post-provider validation object | CS-347 F-001 |
| replay snapshot | debug_artifact | operations/data owner | encrypted/redacted storage | admin-only metadata | `replay_snapshot_v1` | admin_debug, data_storage, observability | audit-only investigation artifact | CS-347 F-003 |

## Operational rules

| Rule area | Rule | Applies to | Invalidated by | Trace requirement | Owner | Sources |
| --- | --- | --- | --- | --- | --- | --- |
| Versioning | Version prompt input contracts when required inputs, prompt-visible blocks, output shape, ordering, determinism, cache identity or replay compatibility changes. | `llm_astrology_input_v1`, output schemas, messages, replay snapshots | adding/removing blocks, schema shape changes, message order changes | version, source audit/story, contract ID | architecture owner | decision-rules, CS-346 F-004, CS-345 F-001 |
| Trace | Carry request, trace, use case, prompt/schema and hash anchors without making them prompt-visible. | gateway, persistence, observability, replay | missing trace_id/request_id/hash anchors | request_id, trace_id, prompt_ref, schema_version, projection_hash, llm_input_hash | runtime/data owner | CS-345 F-001, CS-347 F-002/F-003 |
| Cache | Cache keys for prompt-affecting natal input must include prompt-visible hash material only, not audit-only fields. | prompt input, output generation cache if introduced | facts/signals/limits/shaping or prompt/schema version changes | llm_input_hash plus version identity | architecture/data owner | CS-346 hash policy |
| Replay | Replay is audit-bound and redacted; it supports investigation, not public proof of correctness. | replay snapshots, admin replay | input contract version, schema version, provider params, redaction policy | snapshot_id, version_identity, provenance, audit_event_id | operations/security owner | CS-347 F-003/F-004 |
| Invalidation | Invalidate generated output when prompt-visible input, developer prompt, persona, plan rules, output schema or provider handoff contract changes. | generated interpretations, call logs, replay metadata | prompt version, schema version, model/profile, message order, `llm_input_hash` | prompt_ref, schema_version, model, provider, hash anchors | data/runtime owner | CS-344, CS-345, CS-346, CS-347 |
| Migration | Treat seeds/bootstrap as provisioning. Any promotion to runtime truth requires explicit migration and owner decision. | seed files, DB rows, fallback catalog, schema records | owner decision, seed/runtime contract mismatch | migration/story ID, before/after owner matrix | architecture owner | CS-344 F-004 |
| Observability | Observability fields must describe execution status, recovery, validation and usage without becoming prompt material or semantic proof. | `llm_call_logs`, metadata, admin audit | new public consumer, raw payload exposure, missing redaction | trace_id, input_hash, validation_status, fallback_kind, usage | operations/data owner | CS-347 F-003/F-004 |

## Blockers and decision owners

Contradictions and owner decisions are kept in this section instead of being smoothed into ordinary backlog items.

| Type | Blocker / decision | Owner | Blocks | Required owner decision | Sources |
| --- | --- | --- | --- | --- | --- |
| blocker | Output schema ownership is split across canonical contracts, assembly IDs, fallback catalog entries, bootstrap schemas and tests. | product owner + architecture owner | stable schema registry, contract tests, cache/replay schema identity | choose one nominal runtime schema owner and classify fallback/seed roles | CS-344 F-002, SC-001 |
| blocker | Product may expect stronger semantic verification than audits prove. | product owner + data owner | final report wording, validation claims, future user-facing correctness claims | accept bounded grounding or authorize a new semantic verifier story | CS-347 F-004, SC-001 |
| decision | Recovery/fallback behavior remains non-nominal. | runtime owner + product owner | any implementation that changes fallback behavior | confirm whether existing fallbacks are tolerated, deprecated or product-supported | CS-345 F-003, CS-344 F-004 |
| decision | Exact guardrail registry gaps are recorded but not edited in CS-348. | architecture owner | governance hardening roadmap | decide whether to create separate guardrail registry story | CS-345 F-004, CS-347 F-005 |
| blocker | Mutating prompt-resolution evaluation is not suitable as a no-delta audit guard. | test owner | reusable read-only validation | split or parameterize report generation | CS-344 F-003, SC-002 |

## Ordered implementation roadmap

### Story 1: Converge output schema configuration ownership

Story ID: next-available-id
Source label: CS-344 SC-001
Goal: Select and enforce one nominal runtime owner for output schema resolution while demoting catalog and seeds to explicit fallback/provisioning roles.
Source audits: CS-344
Source findings: F-002
Scope: schema owner matrix, canonical runtime resolver, fallback/seed classification, coherence tests.
Out of scope: provider calls, prompt wording, frontend UI.
Dependencies: product decision on whether catalog fallback schemas are supported public behavior.
Acceptance criteria:
- One nominal schema owner is documented and enforced.
- Fallback and bootstrap schema paths are explicitly non-nominal or product-supported.
- Contract tests cover schema resolution for modern natal and configured use cases.
Validation evidence:
- targeted scans for `output_schema_name`, `output_schema_id`, `get_output_schema`, `ASTRO_RESPONSE_V3_JSON_SCHEMA`.
- `pytest -q backend/tests/evaluation/test_output_contract.py` after venv activation.
Blockers / decisions:
- Product/architecture owner must resolve fallback schema status.
Stop condition: no competing nominal schema owner remains.

### Story 2: Make prompt-resolution evaluation non-mutating

Story ID: next-available-id
Source label: CS-344 SC-002
Goal: Make prompt-resolution validation runnable without modifying `backend/tests`.
Source audits: CS-344
Source findings: F-003
Scope: split or parameterize report generation in evaluation tests.
Out of scope: runtime prompt changes and provider calls.
Dependencies: none after Story 1, but can run independently if scoped to tests.
Acceptance criteria:
- Default pytest path leaves evaluation artifacts unchanged.
- Report generation is opt-in.
Validation evidence:
- `pytest -q backend/tests/evaluation/test_prompt_resolution.py` after venv activation.
- `git diff --quiet -- backend/tests/evaluation`.
Blockers / decisions:
- Test owner decision if report regeneration is intentionally default behavior.
Stop condition: validation passes with no `backend/tests` delta.

### Story 3: Freeze prompt input and boundary contract tests as product architecture guards

Story ID: next-available-id
Source label: derived from CS-343 F-002, CS-345 F-002, CS-346 F-001/F-002/F-004
Goal: Preserve the canonical `prompt-visible`, `runtime-only`, `validation-only`, and `audit-only` contract in reusable tests and docs.
Source audits: CS-343, CS-345, CS-346
Source findings: CS-343 F-002, CS-345 F-002, CS-346 F-001/F-002/F-004
Scope: boundary contract tests and architecture evidence references; no behavior change unless a failing guard exposes drift.
Out of scope: new prompt fields, schema owner convergence, frontend.
Dependencies: none.
Acceptance criteria:
- Modern natal prompt excludes `chart_json`, `natal_data`, validation and audit-only fields.
- Hash material includes only `facts`, `signals`, `limits`, `shaping`.
Validation evidence:
- existing unit, architecture and orchestration tests named in CS-346 and CS-345.
Blockers / decisions:
- none observed.
Stop condition: guards fail or require runtime behavior changes not authorized by story.

### Story 4: Document and guard bounded semantic grounding claims

Story ID: needs-tracker-remap
Source label: CS-347 SC-001
Goal: Ensure architecture and final reporting distinguish schema-valid, evidence-ref-grounded, audit-only, replayable and not semantically proven claims.
Source audits: CS-347, CS-348, future CS-350
Source findings: CS-347 F-004
Scope: report wording, validation scans, future CS-350 documentation closure.
Out of scope: building a semantic verifier.
Dependencies: product/data owner acceptance of bounded grounding language.
Acceptance criteria:
- Reports state that evidence refs and policy checks are bounded controls.
- Observability and replay are not described as correctness proof.
Validation evidence:
- report scans for `semantic grounding`, `bounded`, `observability`, `replay`, `not a full semantic verifier`.
Blockers / decisions:
- Product owner must authorize any stronger verifier as separate scope.
Stop condition: product requires complete semantic proof from current architecture.

### Story 5: Decide guardrail registry enrichment for runtime handoff and post-provider audit

Story ID: next-available-id
Source label: derived from CS-345 F-004 and CS-347 F-005
Goal: Decide whether exact registry guardrails are needed for provider handoff and output validation persistence cartography.
Source audits: CS-345, CS-347
Source findings: CS-345 F-004, CS-347 F-005
Scope: governance decision and potential guardrail registry update in a dedicated story.
Out of scope: CS-348 architecture artifacts and runtime code.
Dependencies: architecture owner decision.
Acceptance criteria:
- Decision recorded: adopt, defer or reject exact guardrails.
- If adopted, guardrail entries cite CS-345 and CS-347 evidence.
Validation evidence:
- guardrail registry scans and story validation output.
Blockers / decisions:
- architecture owner approval required.
Stop condition: registry edits are requested without a dedicated authorized story.

## Open questions and validation plan

| Question | Why it matters | Owner | Blocks | Suggested default | Sources |
| --- | --- | --- | --- | --- | --- |
| Which component is the sole nominal runtime output schema owner? | Required for stable contracts, cache identity, replay compatibility and API/admin claims | product owner + architecture owner | Story 1 and downstream schema consumers | assembly/runtime schema resolver as nominal, seeds provisioning-only, catalog fallback-only | CS-344 F-002 |
| Are catalog fallback schemas product-supported behavior or tolerated non-nominal recovery? | Changes deprecation and compatibility posture | product owner | Story 1 | classify as bounded non-nominal unless product says supported | CS-344 SC-001 |
| Is bounded evidence-ref grounding enough for product claims? | Prevents overclaiming semantic correctness | product owner + data owner | Story 4, CS-350 wording | accept bounded grounding and avoid full-verifier claims | CS-347 F-004 |
| Should exact runtime/post-provider guardrails be added to the registry? | Current evidence notes missing exact guardrails but forbids registry edits in audits | architecture owner | Story 5 | defer to dedicated governance story | CS-345 F-004, CS-347 F-005 |
| Should legacy integration guards requiring `--long` be part of mandatory prompt generation validation? | Affects regression confidence and CI cost | test owner | validation policy | keep as long-run regression unless CI policy changes | CS-346 gap classification |

Validation plan:

- `rg -n "Executive architecture|Capability|Surface|Canonical registry|Operational rules|Blockers" _condamad/architecture/prompt-generation-cartography`
- `rg -n "CS-343|CS-344|CS-345|CS-346|CS-347" _condamad/architecture/prompt-generation-cartography`
- `rg -n "prompt-visible|runtime-only|validation-only|audit-only" _condamad/architecture/prompt-generation-cartography`
- `rg -n "owner|versioning|trace|cache|replay|invalidation|deprecation" _condamad/architecture/prompt-generation-cartography`
- `rg -n "Ordered implementation roadmap|Open questions and validation plan" _condamad/architecture/prompt-generation-cartography`
- after venv activation: `python -c "from pathlib import Path; ..."` existence checks for architecture, source map and validation output.
- after venv activation: `python -c "import subprocess; assert not subprocess.check_output(['git','status','--short','--','backend/app','backend/tests','frontend/src','backend/migrations']).strip()"`
