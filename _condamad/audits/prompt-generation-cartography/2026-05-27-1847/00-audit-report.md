<!-- Commentaire global: rapport CONDAMAD de l'audit CS-347 post-provider LLM. -->

# CS-347 Domain Audit Report

## Domain Closure Status

Status: `closed`

Reason: no application implementation gap remains inside the CS-347 audit scope. F-004 is a deferred reporting and architecture risk for CS-348 and CS-350, not an open CS-347 implementation gap.

## Audit Target

- Domain key: `prompt-generation-cartography`
- Domain: backend-domain
- Archetype: custom post-provider output validation, persistence, observability, and replay audit
- Read-only mode: application code, tests, migrations, frontend, provider clients, and guardrail registry remain unchanged.
- Story-specific report: `05-output-validation-persistence-audit.md`

## Prior Audit And Story History Consulted

| Prior artifact | Classification | Current evidence |
|---|---|---|
| CS-345 runtime gateway handoff audit | still-active context | E-004 proves provider handoff ends before output validation. |
| CS-346 natal astrology input audit | still-active context | E-005 proves prompt-visible input and backend-only evidence roles. |
| RG-002 | applicable indirect guardrail | E-003; no API routing move is authorized. |
| RG-022 | applicable indirect guardrail | E-003; pytest paths used by this story are collected and current. |
| Exact post-provider guardrail | registry gap | E-003; CS-347 forbids registry edits. |

## Closure Analysis

Active findings:

- None inside the CS-347 audited domain.

Closed or observation-only findings:

- F-001 is observation-only; output validation is traceable and test-backed.
- F-002 is observation-only; rejection and audit persistence are separated.
- F-003 is observation-only; observability and replay metadata are mapped.
- F-005 is observation-only; registry enrichment is explicitly out of scope.

Deferred non-domain findings:

- F-004 is deferred to CS-348 and CS-350 as an architecture/reporting closure item. It does not require CS-347 code, test, schema, migration, or guardrail changes.

Implementation files remaining for active in-domain findings: none.

Governance/test files remaining for active in-domain findings: none.

Deferred non-domain concerns: frontend UI, DB migrations, provider calls, schema changes, and runtime fixes.

## Post-Provider Pipeline

| pipeline step | owner | symbol or field | input | output | validation status | persistent anchors | evidence | gap or next story marker |
|---|---|---|---|---|---|---|---|---|
| raw provider result | gateway | `GatewayResult.raw_output` | provider text | raw output string | not checked | request_id, trace_id | E-007 | no gap |
| schema validation | output validator | `validate_output` | raw output and JSON schema | `ValidationResult` | shape-valid or invalid | schema_version | E-006, E-015 | no gap |
| repair | gateway plus repair owner | `_handle_repair_or_fallback`, `build_repair_prompt` | invalid validation result | repaired result or error | repaired or error | repair_attempted | E-007 | no gap |
| semantic grounding | rejected workflow | `build_rejected_narrative_answer_outcome_from_payload` | structured output plus backend evidence refs | rejected outcome or none | grounded, partial, ungrounded, rejected | projection_hash, llm_input_hash, evidence_refs | E-008, E-017 | CS-348, CS-350 |
| rejection client response | natal service | `meta.validation_status = "rejected"` | rejected outcome | controlled client message | rejected | answer_id, grounding_status | E-008, E-009, E-016 | no gap |
| narrative audit persistence | natal service and model | `_apply_narrative_answer_audit`, `UserNatalInterpretationModel` | response and audit anchors | persisted narrative audit row | audit-only | prompt_version, prompt_ref, projection_hash, llm_input_hash | E-009, E-010, E-018 | no gap |
| observability | observability service | `log_call` | final gateway result | `llm_call_logs` and metadata | valid, repair_success, fallback, error | request_id, trace_id, input_hash, usage | E-011, E-012, E-019 | no gap |
| replay readiness | replay service | `ReplaySnapshotV1Service.create_snapshot` | sanitized user input and gateway result | encrypted snapshot and metadata | replayable or validation_failed | input_hash, version_identity, provenance | E-013, E-020 | no gap |
| admin audit surfaces | admin contracts/tests | `AdminReplaySnapshotV1*`, `RejectedAnswerReview*` | admin query/update | redacted metadata and review contracts | audit-only | snapshot_id, audit_event_id, replay_attempt_id | E-014, E-021 | no gap |

## Output Schemas By Use Case

| use case family | schema owner | runtime owner | status | evidence | gap |
|---|---|---|---|---|---|
| natal free short | `AstroFreeResponseV1` | gateway output schema and natal service | shape validation plus rejection workflow | E-006, E-009, E-015 | semantic proof bounded |
| natal complete v1/v2/v3 | `AstroResponseV1`, `AstroResponseV2`, `AstroResponseV3` | gateway output schema and natal service | shape validation plus evidence refs | E-006, E-009, E-015 | semantic proof bounded |
| natal error v3 | `AstroErrorResponseV3` | schema owner and gateway | shape validation | E-006 | no provider call made in audit |

## Validation, Recovery, Rejection, And Grounding Statuses

| status | owner | meaning | evidence |
|---|---|---|---|
| valid | gateway/meta and DB enum | schema validation passed or no schema was required | E-007, E-011 |
| repair_success | gateway/meta and DB enum | invalid output was repaired successfully | E-007, E-011 |
| fallback | gateway/meta and DB enum | non-supported feature fallback path was used | E-007, E-011 |
| error | gateway/meta and DB enum | validation or provider path failed | E-007, E-011 |
| grounded | evidence refs validation | evidence refs meet section requirements | E-008, E-017 |
| partial | evidence refs validation | some required evidence refs are missing or invalid | E-008, E-017 |
| ungrounded | evidence refs validation | generated content lacks accepted evidence | E-008, E-017 |
| rejected | natal persistence | client receives controlled rejection; internal audit stores context | E-009, E-010, E-016 |
| replayable | replay service | snapshot metadata and encrypted input are available and unexpired | E-013, E-020 |

## Persistent Prompt, Input, Audit, And Evidence Anchors

| anchor | owner | persisted location | role | evidence |
|---|---|---|---|---|
| `prompt_version` | natal service | `user_natal_interpretations.prompt_version` | audit-only | E-009, E-010 |
| `prompt_ref` | natal service | `user_natal_interpretations.prompt_ref` | audit-only | E-009, E-010 |
| `projection_hash` | natal service/model | `user_natal_interpretations.projection_hash` | audit-only | E-009, E-010 |
| `llm_input_hash` | natal service/model | `user_natal_interpretations.llm_input_hash` | audit-only | E-009, E-010 |
| `evidence_refs` | natal service/model | `user_natal_interpretations.evidence_refs` | validation/audit-only | E-009, E-010 |
| `grounding_status` | natal service/model | `user_natal_interpretations.grounding_status` | validation/audit-only | E-009, E-010 |
| usage tokens | observability service/model | `llm_call_logs.tokens_in`, `tokens_out` | observability | E-011, E-012 |
| replay metadata | replay service/model | `llm_replay_snapshots.version_identity`, `provenance` | replay/audit-only | E-011, E-013 |

## Evidence Refs Relation

Output `evidence` items are not trusted as semantic proof by shape alone. `rejected_answer_workflow.py` maps output evidence to backend-only `llm_astrology_input_v1.evidence.evidence_refs`, then validates section requirements against source proofs built from `projection_hash` and `llm_input_hash`. Evidence E-008 and E-017 prove this relation.

## Observability, Usage, Call Logs, And Replay

`observability_service.log_call` hashes sanitized user input, maps gateway validation status to `LlmValidationStatus`, records token usage and evidence warning counts, writes operational provider metadata, and creates `replay_snapshot_v1` when user input exists. Replay snapshots keep encrypted input and redacted metadata only. Evidence E-011, E-012, E-013, E-019, and E-020 prove these surfaces.

## Admin Audit And Replay Service Surfaces

Admin contracts expose redacted replay metadata and rejected-answer review objects through `admin/audit.py`. `test_admin_endpoint_segmentation_contract.py` proves admin audit and replay paths remain internal/admin surfaces and are not public OpenAPI tokens. Evidence E-014 and E-021 prove the contract and segmentation.

## Prompt-To-Output-To-Audit Matrix

| pipeline step | owner | symbol or field | input | output | validation status | persistent anchors | evidence | gap or next story marker |
|---|---|---|---|---|---|---|---|---|
| prompt input | CS-346 input audit | `llm_astrology_input_v1` | chart facts and signals | prompt-visible blocks plus backend-only evidence | input-ready | projection_hash, llm_input_hash | E-005 | no gap |
| provider output | gateway | `GatewayResult.raw_output` | provider response | raw JSON text | not checked | request_id, trace_id | E-004, E-007 | no gap |
| schema output | output validator | `ValidationResult.parsed` | raw output | normalized structured output | shape-valid or invalid | schema_version | E-006, E-015 | no gap |
| semantic output | rejected workflow | `RejectedNarrativeAnswerOutcome` | structured output and backend refs | accepted or rejected narrative | grounded, partial, ungrounded | evidence_refs, grounding_status | E-008, E-017 | CS-348, CS-350 |
| persisted audit | natal model | `UserNatalInterpretationModel` | accepted or rejected payload | audit row | audit-only | prompt_version, prompt_ref, projection_hash, llm_input_hash | E-009, E-010, E-018 | no gap |
| observability audit | LLM DB models | `llm_call_logs` | gateway result | log and operational metadata | valid, repair_success, fallback, error | input_hash, usage, provider metadata | E-011, E-012, E-019 | no gap |
| replay audit | replay service | `replay_snapshot_v1` | sanitized input and result | encrypted snapshot metadata | replayable | input_hash, version_identity, provenance | E-013, E-020 | no gap |

## Existing Tests And Gaps

| Test | Result | Proves | Gap |
|---|---|---|---|
| `tests/llm_orchestration/test_output_validator_pipeline.py` | PASS, 8 passed | parse, schema, normalization, evidence sanitization | no gap |
| `tests/unit/test_rejected_narrative_answer_workflow.py` and logging | PASS, 13 passed | controlled rejection payload and log behavior | no gap |
| `tests/unit/test_evidence_refs_validation.py` and section status | PASS, 10 passed | evidence refs status flow | no gap |
| `tests/integration/llm/test_natal_llm_astrology_input_audit.py --long` | PASS, 2 passed | audit persistence anchors | no gap |
| `tests/integration/test_llm_db_invariants.py --long` | PASS, 18 passed | call log and replay schema invariants | no gap |
| `tests/unit/test_replay_snapshot_v1_service_audit.py` and manual purge | PASS, 4 passed | replay audit events and purge audit | no gap |
| `tests/unit/test_admin_endpoint_segmentation_contract.py` | PASS, 5 passed | admin audit/replay segmentation | no gap |

## Residual Risks For CS-348 And CS-350

- CS-348: define the architecture closure map for semantic grounding limits, observability boundaries, and replay readiness.
- CS-350: report the final prompt-generation cartography without implying that persisted audit anchors prove prompt correctness.
- Semantic gap: schema validity and evidence refs reduce risk but do not prove every generated claim semantically.
- Observability gap: current logs are operational/audit evidence, not user-facing correctness proof.
- Replay gap: replay metadata enables controlled investigation, not public replay UI or provider proof.

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `backend/app/domain/llm/runtime/output_validator.py` | used | E-006, E-007, E-015 | Canonical schema validation owner called by gateway. | Static call trace plus tests. |
| `backend/app/domain/llm/runtime/repair.py` | intentional-public-export | E-007 | Canonical runtime repair entrypoint re-exporting repair prompt owner. | No deletion audit requested. |
| `backend/app/domain/llm/runtime/observability.py` | intentional-public-export | E-012 | Canonical runtime observability entrypoint. | No deletion audit requested. |
| `backend/app/domain/llm/runtime/observability_service.py` | used | E-012, E-019 | Persists call logs, metadata, usage, and replay snapshots. | Static source trace plus DB invariant tests. |
| `backend/app/domain/llm/runtime/gateway.py` | used | E-007, E-015 | Orchestrates post-provider validation, repair, result metadata, and log call. | Provider calls not executed. |
| `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` | used | E-008, E-016 | Canonical rejected narrative answer workflow. | No product decision on stronger semantic verifier. |
| `backend/app/services/llm_generation/natal/interpretation_service.py` | used | E-009, E-018 | Persists narrative answer audit anchors and rejected state. | Large service; audit inspected relevant symbols. |
| `backend/app/infra/db/models/user_natal_interpretation.py` | used | E-010, E-018 | Canonical narrative audit persistence model. | No migration generated. |
| `backend/app/infra/db/models/llm/llm_observability.py` | used | E-011, E-019 | Owns `llm_call_logs`, operational metadata, and replay snapshot models. | No live DB inspection beyond tests. |
| `backend/app/services/replay_snapshot_v1_service.py` | used | E-013, E-020 | Canonical replay snapshot lifecycle service. | Service is outside original priority list but required by replay mapping. |
| `backend/app/services/api_contracts/admin/audit.py` | used | E-014, E-021 | Admin audit, replay, and rejected answer review contracts. | Runtime route implementation was bounded by tests. |
| `backend/tests/llm_orchestration/test_output_validator_pipeline.py` | test-only | E-015 | Owns output validation test evidence. | None. |
| `backend/tests/unit/test_rejected_narrative_answer_workflow.py` | test-only | E-016 | Owns rejection workflow behavior evidence. | None. |
| `backend/tests/unit/test_rejected_narrative_answer_logging.py` | test-only | E-016 | Owns rejection logging evidence. | None. |
| `backend/tests/unit/test_evidence_refs_validation.py` | test-only | E-017 | Owns evidence refs validation evidence. | None. |
| `backend/tests/unit/test_evidence_refs_section_status.py` | test-only | E-017 | Owns section grounding status evidence. | None. |
| `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py` | test-only | E-018 | Owns persisted natal audit anchor evidence. | Requires `--long`. |
| `backend/tests/integration/test_llm_db_invariants.py` | test-only | E-019 | Owns call log and replay schema invariant evidence. | Requires `--long`. |
| `backend/tests/unit/test_replay_snapshot_v1_service_audit.py` | test-only | E-020 | Owns replay audit event evidence. | None. |
| `backend/tests/unit/test_replay_snapshot_v1_service_manual_purge.py` | test-only | E-020 | Owns manual purge audit evidence. | None. |
| `backend/tests/unit/test_admin_endpoint_segmentation_contract.py` | test-only | E-021 | Owns admin segmentation evidence. | None. |

## DRY, No Legacy, Mono-Domain, Dependency Direction

- DRY: no new implementation path was created; evidence reuses existing validators, services, models, and tests.
- No Legacy: fallback and repair remain classified as recovery paths, not nominal provider proof.
- Mono-domain: audit stays in backend post-provider output validation/persistence/observability/replay.
- Dependency direction: no application imports or runtime files were changed; no API or frontend ownership was moved.
