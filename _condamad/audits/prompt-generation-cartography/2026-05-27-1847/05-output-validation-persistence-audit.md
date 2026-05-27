<!-- Commentaire global: livrable story CS-347 sur la validation de sortie, persistance, observabilite et replay LLM. -->

# output-validation-persistence-audit - CS-347

This is the story-specific report. The full CONDAMAD companion report is in `00-audit-report.md` in the same folder.

## Executive Summary

The audited post-provider flow is:

`raw provider result -> validate_output -> repair or rejection -> UserNatalInterpretationModel audit -> llm_call_logs -> replay_snapshot_v1 -> admin audit contracts`.

No runtime code, schemas, tests, migrations, provider clients, frontend files, or guardrails were changed.

## Post-provider pipeline

| pipeline step | owner | symbol or field | input | output | validation status | persistent anchors | evidence | gap or next story marker |
|---|---|---|---|---|---|---|---|---|
| raw provider result | `backend/app/domain/llm/runtime/gateway.py` | `GatewayResult.raw_output` | provider text | raw JSON text | not checked | request_id, trace_id | E-007 | no gap |
| schema validation | `backend/app/domain/llm/runtime/output_validator.py` | `validate_output` | raw output and schema | `ValidationResult` | shape-valid or invalid | schema_version | E-006, E-015 | no gap |
| repair | `backend/app/domain/llm/runtime/gateway.py` | `_handle_repair_or_fallback` | invalid `ValidationResult` | repaired result or error | repaired or error | repair_attempted | E-007 | no gap |
| rejection | `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` | `RejectedNarrativeAnswerOutcome` | structured output plus backend refs | controlled rejection | partial, ungrounded, rejected | evidence_refs, grounding_status | E-008, E-016, E-017 | no gap |
| audit persistence | `backend/app/services/llm_generation/natal/interpretation_service.py` | `_apply_narrative_answer_audit` | output and audit anchors | persisted row | audit-only | prompt_version, prompt_ref, projection_hash, llm_input_hash | E-009, E-010, E-018 | no gap |
| observability | `backend/app/domain/llm/runtime/observability_service.py` | `log_call` | final result | `llm_call_logs` | valid, repair_success, fallback, error | input_hash, usage, trace_id | E-011, E-012, E-019 | no gap |
| replay | `backend/app/services/replay_snapshot_v1_service.py` | `create_snapshot` | sanitized input and result | encrypted snapshot metadata | replayable | version_identity, provenance | E-013, E-020 | no gap |
| admin audit | `backend/app/services/api_contracts/admin/audit.py` | admin replay and rejected answer contracts | admin-only access | redacted audit data | audit-only | snapshot_id, audit_event_id | E-014, E-021 | no gap |

## Output schemas by use case

| Use case | Schema family | Shape validation | Semantic grounding | Evidence |
|---|---|---|---|---|
| `natal_long_free` / free short | `AstroFreeResponseV1` | `validate_output` and gateway schema version | rejected workflow when evidence/policy requires it | E-006, E-009, E-015 |
| premium/basic natal narratives | `AstroResponseV1`, `AstroResponseV2`, `AstroResponseV3` | `validate_output` and output schema | evidence refs by section plus unsupported claim and limit checks | E-006, E-008, E-017 |
| v3 error response | `AstroErrorResponseV3` | JSON/schema validation | not a semantic proof surface | E-006 |

## Validation, recovery, rejection

- Shape validation: parse JSON, validate JSON Schema, normalize evidence aliases, sanitize evidence.
- Recovery: repair is invoked after invalid output; supported features do not fall back to legacy use cases.
- Rejection: ungrounded or partial evidence refs produce `RejectedNarrativeAnswerOutcome`.
- Client behavior: rejected answers expose only controlled wording.
- Persistence behavior: internal audit context keeps rejection reason, validation context, raw structured output storage, anchors, provider, model, and grounding status.

## Persistent prompt, input, audit fields

| Field | Persisted owner | Source | Role | Evidence |
|---|---|---|---|---|
| `prompt_version` | `UserNatalInterpretationModel` | `gateway_result.meta.prompt_version_id` | audit-only | E-009, E-010 |
| `prompt_ref` | `UserNatalInterpretationModel` | `llm_prompt_versions:<id>` | audit-only | E-009, E-010 |
| `projection_hash` | `UserNatalInterpretationModel` | `llm_astrology_input_v1.provenance` | audit-only | E-009, E-010 |
| `llm_input_hash` | `UserNatalInterpretationModel` | `llm_astrology_input_v1.provenance` | audit-only | E-009, E-010 |
| `evidence_refs` | `UserNatalInterpretationModel` | backend evidence block or rejection validation context | validation/audit-only | E-009, E-010 |
| `grounding_status` | `UserNatalInterpretationModel` | evidence block or rejected outcome | validation/audit-only | E-009, E-010 |

## Evidence refs relation

The current output validation separates schema shape from semantic grounding. Output evidence labels are mapped back to backend-only evidence refs from `llm_astrology_input_v1.evidence`. The rejected-answer workflow validates section requirements with `build_audit_source_proofs`, `projection_hash`, and `llm_input_hash`. This supports rejection decisions, but it does not prove every possible semantic claim; CS-348 and CS-350 must keep that limitation visible.

## Observability and replay

`log_call` records validation status, repair/fallback flags, usage tokens, evidence warning counts, provider metadata, and input hash. It also creates `replay_snapshot_v1` metadata when user input exists. Replay stores encrypted input plus redacted `input_ref`, `version_identity`, and `provenance`, then admin reads and replay attempts are audit-bound.

## Admin audit and replay service surfaces

`AdminReplaySnapshotV1MetadataResponse`, `AdminReplaySnapshotV1ReplayAttemptResponse`, and rejected-answer review contracts expose admin-only metadata. `test_admin_endpoint_segmentation_contract.py` proves admin audit/replay paths are segmented and not public projection tokens.

## Prompt-to-output-to-audit matrix

| pipeline step | owner | symbol or field | input | output | validation status | persistent anchors | evidence | gap or next story marker |
|---|---|---|---|---|---|---|---|---|
| prompt material | CS-346 audit | `llm_astrology_input_v1` | facts, signals, limits, shaping | provider prompt-visible payload | input-ready | projection_hash, llm_input_hash | E-005 | no gap |
| provider response | CS-345 audit and gateway | `raw_output` | provider result | raw JSON text | not checked | request_id, trace_id | E-004, E-007 | no gap |
| validated output | output validator | `ValidationResult.parsed` | raw output | normalized payload | shape-valid | schema_version | E-006, E-015 | no gap |
| grounded or rejected answer | rejected workflow | `RejectedNarrativeAnswerOutcome` | output evidence and backend refs | accepted or controlled rejection | grounded, partial, ungrounded, rejected | evidence_refs, grounding_status | E-008, E-017 | CS-348, CS-350 |
| persisted answer audit | natal service/model | `UserNatalInterpretationModel` | accepted/rejected payload | audit row | audit-only | prompt_version, prompt_ref, projection_hash, llm_input_hash | E-009, E-010, E-018 | no gap |
| operational audit | observability model | `llm_call_logs` | gateway result | log and metadata | valid, repair_success, fallback, error | input_hash, token usage | E-011, E-012, E-019 | no gap |
| replay audit | replay service/model | `llm_replay_snapshots` | sanitized input | encrypted replay snapshot | replayable | version_identity, provenance | E-013, E-020 | no gap |

## Existing tests and gaps

| Test | Result | Proves | Gap |
|---|---|---|---|
| `tests/llm_orchestration/test_output_validator_pipeline.py` | PASS, 8 passed | output parsing, schema validation, normalization, sanitization | no gap |
| `tests/unit/test_rejected_narrative_answer_workflow.py` plus logging | PASS, 13 passed | rejection workflow and safe log event | no gap |
| `tests/unit/test_evidence_refs_validation.py` plus section status | PASS, 10 passed | evidence refs and grounding status flow | no gap |
| `tests/integration/llm/test_natal_llm_astrology_input_audit.py --long` | PASS, 2 passed | persisted prompt/input/evidence anchors | no gap |
| `tests/integration/test_llm_db_invariants.py --long` | PASS, 18 passed | `llm_call_logs` and replay DB invariants | no gap |
| `tests/unit/test_replay_snapshot_v1_service_audit.py` plus manual purge | PASS, 4 passed | replay audit events and purge behavior | no gap |
| `tests/unit/test_admin_endpoint_segmentation_contract.py` | PASS, 5 passed | admin audit/replay surface segmentation | no gap |

## Residual risks for CS-348 and CS-350

- CS-348: close the architecture map for semantic grounding, observability, replay readiness, and admin audit boundaries.
- CS-350: produce the final cartography report without treating persisted audit anchors as prompt correctness proof.
- Semantic gap: evidence refs and policy checks are bounded controls, not a full semantic verifier.
- Observability gap: `llm_call_logs` support investigation, not correctness proof.
- Replay gap: replay snapshots support controlled investigation, not public replay UI or provider proof.
