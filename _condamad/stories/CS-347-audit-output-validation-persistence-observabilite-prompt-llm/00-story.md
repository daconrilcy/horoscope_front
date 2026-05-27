# Story CS-347 audit-output-validation-persistence-observabilite-prompt-llm: Audit Validation Output Persistence Observabilite Prompt LLM
Status: ready-to-dev

## Trigger / Source

- Mode: Audit-to-story with repo-informed evidence.
- Source brief: `_story_briefs/cs-347-audit-validation-output-persistence-observabilite-prompt-llm.md`.
- Source problem: the prompt cartography must continue after provider handoff and map output validation, rejection, audit persistence, observability, and replay.
- Source stakes:
  - The LLM response must not be treated as trusted because prompt handoff succeeded.
  - Validation runtime, repair, rejection, audit persistence, observability, and replay must be separated.
  - Prompt anchors, input hashes, projection hashes, evidence refs, grounding status, and provider usage must be traced.
  - Existing tests must show what is proven and which gaps feed CS-348 and CS-350.
  - The output audit must not modify schemas, add replay UI, call providers, or fix validation gaps.
- Source-alignment review: PASS. Objective, target state, ACs, tasks, evidence, non-goals, and guardrails map to the source stakes.

## Objective

Produce the fifth timestamped prompt-generation cartography audit focused on post-provider output validation, rejection workflow,
audit persistence, observability, replay metadata, and admin audit surfaces. The story creates documentation and evidence artifacts only;
it does not modify runtime code, output schemas, tests, persistence models, admin APIs, prompts, provider clients, or public behavior.

## Target State

- A report exists at `_condamad/audits/prompt-generation-cartography/YYYY-MM-DD-HHMM/05-output-validation-persistence-audit.md`.
- The report contains a post-provider pipeline from raw provider result to validation, repair, rejection, persistence, observability, and replay.
- The report maps output schemas by use case and distinguishes shape validation from semantic grounding validation.
- The report explains statuses for validation, recovery, rejection, grounding, persisted audit, observability, and replay readiness.
- The report traces `prompt_version`, `prompt_ref`, `projection_hash`, `llm_input_hash`, `evidence_refs`, and `grounding_status`.
- The report maps `llm_call_logs`, replay snapshots, gateway metadata, usage tokens, and admin audit or replay services.
- The report evaluates integration, unit, and workflow tests that prove rejection, audit persistence, evidence refs, and replay behavior.
- The report includes a prompt-to-output-to-audit matrix and records residual risks for CS-348 and CS-350.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-347-audit-validation-output-persistence-observabilite-prompt-llm.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-347`.
- Evidence 3: `_story_briefs/cs-288-implement-narrative-answer-audit-v1-persistence.md` - audit persistence source brief read.
- Evidence 4: `_story_briefs/cs-289-implement-evidence-refs-validation.md` - evidence refs validation source brief read.
- Evidence 5: `_story_briefs/cs-290-implement-rejected-narrative-answer-workflow.md` - rejection workflow source brief read.
- Evidence 6: `_story_briefs/cs-298-implement-replay-snapshot-v1-execution-audit.md` - replay audit source brief read.
- Evidence 7: `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md` - validation boundary source brief read.
- Evidence 8: `_story_briefs/cs-342-cloturer-process-evidence-hors-prompt-validation-redaction-llm-natale.md` - closure source brief read.
- Evidence 9: `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/00-story.md` - provider handoff context read.
- Evidence 10: `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/00-story.md` - input source audit context read.
- Evidence 11: `_condamad/stories/regression-guardrails.md` - guardrail registry consulted through scoped resolver output only.
- Evidence 12: `resolve_guardrails.py` returned RG-002 and RG-022 for the backend output validation persistence audit scope.
- Evidence 13: targeted path checks confirmed all priority backend files and tests named by the source brief exist in this workspace.
- Evidence 14: targeted `rg` found validation, rejection, hash, evidence refs, call log, and replay symbols in `backend/app` and `backend/tests`.
- Repository structure alert: `_condamad/audits/prompt-generation-cartography` is absent; implementation must create the audit folder.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Audit of output validation runtime, schema validation, repair, and validation status classification.
  - Audit of rejected narrative answer workflow and controlled client response behavior.
  - Audit of natal interpretation persistence and narrative answer audit fields.
  - Audit of `llm_call_logs`, replay snapshots, gateway metadata, token usage, and observability services.
  - Audit of admin audit, replay, and observability services that expose or consume persisted traces.
  - Audit of integration, unit, and workflow tests for persistence, rejection, evidence refs, observability, and replay.
  - Creation of the timestamped audit report and story evidence artifacts only.
- Out of scope:
  - Frontend UI, public API route changes, database schema changes, auth, i18n, styling, build tooling, migrations, and provider calls.
  - Output schema changes, replay or admin UI additions, real provider calls, and implementation fixes for discovered gaps.
  - Guardrail registry maintenance or enrichment.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No runtime code change, schema migration, model change, prompt rewrite, provider integration, or test source change.
  - No correction of validation, rejection, persistence, observability, or replay gaps found by the audit.
  - No claim that persisted audit data proves the original prompt was correct.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend post-provider validation and audit cartography contract.
- Behavior change allowed: no
- Behavior change constraints:
  - Create only audit, evidence, validation, and generated review artifacts.
  - Do not change application code, output schemas, database models, migrations, admin APIs, tests, provider clients, prompts, or runtime behavior.
  - Preserve the distinction between provider handoff, output validation, semantic grounding, audit persistence, observability, and replay.
  - Classify repair, rejected answer handling, and replay as post-provider controls, not prompt provider proof.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the post-provider pipeline cannot be traced from source, tests, or deterministic scan evidence.
- Additional validation rules:
  - The audit must cite concrete file paths and symbol names for every post-provider step it classifies.
  - Runtime claims must use `AST guard`, targeted `rg`, full backend `pytest` paths, loaded DB schema checks, or bounded source-trace evidence.
  - Persistence claims must name the model, table, service, field, or test that proves the stored audit anchor.
  - Observability and replay claims must name the call log, snapshot, metadata, usage, service, or admin surface owner.
  - Residual validation risks must be marked for CS-348 or CS-350 instead of being fixed inside this story.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `AST guard`, source traces, targeted `rg`, loaded DB schema checks, and backend `pytest` paths prove post-provider behavior. |
| Baseline Snapshot | yes | Scan outputs and symbol maps create a reproducible before-state for later validation and observability stories. |
| Ownership Routing | yes | Validation, repair, rejection, persistence, observability, replay, admin audit, and tests must keep canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this audit story. |
| Contract Shape | yes | The audit report has required pipeline, schema, status, field, observability, replay, test, matrix, and gap sections. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Prompt handoff evidence must not be reclassified as output validation or persisted audit proof. |
| Persistent Evidence | yes | Report, scan output, validation output, final evidence, and review handoff must be kept. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The output validation persistence audit report exists. | Evidence profile: baseline_before_after_diff; `python` checks the report path under `_condamad/audits`. |
| AC2 | The post-provider pipeline is sequenced. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks pipeline labels. |
| AC3 | Output schema validation is classified. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/llm_orchestration/test_output_validator_pipeline.py`. |
| AC4 | Semantic grounding limits are explicit. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_rejected_narrative_answer_workflow.py`. |
| AC5 | Rejected narrative workflow is mapped. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/unit/test_rejected_narrative_answer_workflow.py`. |
| AC6 | Audit persistence anchors are mapped. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py`. |
| AC7 | Evidence refs status flow is mapped. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/unit/test_evidence_refs_validation.py`. |
| AC8 | `llm_call_logs` observability is mapped. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/integration/test_llm_db_invariants.py`. |
| AC9 | Replay snapshot audit flow is mapped. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/unit/test_replay_snapshot_v1_service_audit.py`. |
| AC10 | Admin trace surfaces are evaluated. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/unit/test_admin_endpoint_segmentation_contract.py`. |
| AC11 | Prompt-output-audit matrix is produced. | Evidence profile: json_contract_shape; `rg` checks required anchor labels. |
| AC12 | Follow-up risks are recorded. | Evidence profile: baseline_before_after_diff; `rg` checks `CS-348` and `CS-350` in the audit report. |
| AC13 | Backend source files are unchanged. | Evidence profile: ast_architecture_guard; `python` checks git status for backend app and backend tests. |
| AC14 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence and generated paths. |

## Implementation Tasks

- [ ] Task 1: Create the timestamped audit folder and story evidence artifact set. (AC: AC1, AC14)
- [ ] Task 2: Trace raw provider result through validation, repair, rejection, persistence, observability, and replay. (AC: AC2)
- [ ] Task 3: Map output schema validation and distinguish shape validation from semantic grounding validation. (AC: AC3, AC4)
- [ ] Task 4: Map `RejectedNarrativeAnswer` workflow and controlled response behavior. (AC: AC5)
- [ ] Task 5: Map natal interpretation persistence fields and audit anchors. (AC: AC6, AC11)
- [ ] Task 6: Map `evidence_refs`, `grounding_status`, validation status, and recovery status transitions. (AC: AC4, AC7)
- [ ] Task 7: Map `llm_call_logs`, gateway metadata, usage tokens, and observability services. (AC: AC8)
- [ ] Task 8: Map replay snapshots, replay metadata, and safe audit events. (AC: AC9)
- [ ] Task 9: Evaluate admin audit, replay, and observability service exposure. (AC: AC10)
- [ ] Task 10: Produce the prompt-to-output-to-audit matrix with required anchors. (AC: AC11)
- [ ] Task 11: Evaluate existing integration, unit, rejection, audit, observability, and replay tests, then record gaps. (AC: AC4, AC5, AC6, AC7, AC8, AC9)
- [ ] Task 12: Record residual risks for CS-348 and CS-350, persist validation output, and prove backend files remain unchanged. (AC: AC12, AC13, AC14)

## Files to Inspect First

- `_story_briefs/cs-347-audit-validation-output-persistence-observabilite-prompt-llm.md` - source scope and acceptance criteria.
- `_story_briefs/cs-288-implement-narrative-answer-audit-v1-persistence.md` - persistence context.
- `_story_briefs/cs-289-implement-evidence-refs-validation.md` - evidence refs validation context.
- `_story_briefs/cs-290-implement-rejected-narrative-answer-workflow.md` - rejection workflow context.
- `_story_briefs/cs-298-implement-replay-snapshot-v1-execution-audit.md` - replay audit context.
- `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md` - post-generation validation context.
- `_story_briefs/cs-342-cloturer-process-evidence-hors-prompt-validation-redaction-llm-natale.md` - final validation boundary context.
- `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/00-story.md` - provider handoff context.
- `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/00-story.md` - input and evidence source context.
- `backend/app/domain/llm/runtime/output_validator.py` - output schema validation owner.
- `backend/app/domain/llm/runtime/repair.py` - repair behavior owner.
- `backend/app/domain/llm/runtime/observability.py` - call log, metadata, usage, and observability owner.
- `backend/app/domain/llm/runtime/observability_service.py` - observability persistence or service owner.
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` - rejected narrative workflow owner.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - natal persistence and gateway result handling owner.
- `backend/app/infra/db/models/user_natal_interpretation.py` - narrative answer audit persistence model.
- `backend/app/infra/db/models/llm/**` - LLM call log and replay persistence models.
- `backend/app/services/api_contracts/admin/audit.py` - admin audit contract owner.
- `backend/tests/unit/test_rejected_narrative_answer_workflow.py` - rejection workflow test evidence.
- `backend/tests/llm_orchestration/test_output_validator_pipeline.py` - output validation pipeline test evidence.
- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py` - natal audit persistence test evidence.
- `backend/tests/unit/test_evidence_refs_validation.py` - evidence refs validation test evidence.
- `backend/tests/integration/test_llm_db_invariants.py` - call log and replay schema evidence.
- `backend/tests/unit/test_replay_snapshot_v1_service_audit.py` - replay audit service evidence.
- `backend/tests/unit/test_admin_endpoint_segmentation_contract.py` - admin audit and replay surface evidence.

## Runtime Source of Truth

- Primary source of truth:
  - Source traces from backend output validator, repair, observability, rejected answer workflow, natal interpretation service, DB models, and admin audit files.
  - `AST guard` checks for validation, repair, rejection, persistence, observability, replay, and admin surface ownership.
- `pytest -q backend/tests/unit/test_rejected_narrative_answer_workflow.py` for rejection and grounding behavior.
- `pytest -q backend/tests/llm_orchestration/test_output_validator_pipeline.py` for output validation behavior.
- `pytest -q backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py` for persisted hashes and evidence refs.
  - `pytest -q backend/tests/integration/test_llm_db_invariants.py` for `llm_call_logs` and replay schema evidence.
- Secondary evidence:
  - Targeted `rg` scans for validation, rejection, audit fields, observability, call logs, replay, and admin symbols.
- Static scans alone are not sufficient for this story because:
  - The audit must distinguish symbol presence from runtime validation, persisted audit anchoring, observability emission, and replay readiness.

## Contract Shape

- Contract type:
  - Timestamped backend post-provider output validation and persistence audit report with persistent evidence bundle.
- Fields:
  - `pipeline step`: raw provider result, schema validation, repair, semantic validation, rejection, persistence, observability, replay, or admin audit.
  - `owner`: canonical source module, service, model, contract, test, or report owner.
  - `symbol or field`: concrete class, function, table, field, route, test, or artifact symbol.
  - `input`: runtime value, provider result, validated answer, audit object, log payload, snapshot, or admin query entering the step.
  - `output`: accepted response, rejected response, persisted row, log entry, replay snapshot, metadata, usage record, or gap classification.
  - `validation status`: shape-valid, repaired, rejected, grounded, partial, ungrounded, not checked, audit-only, replayable, or needs-investigation.
  - `persistent anchors`: prompt version, prompt ref, projection hash, LLM input hash, evidence refs, grounding status, trace id, usage, or none.
  - `evidence`: short source, scan, `AST guard`, loaded DB schema check, or `pytest` evidence.
  - `gap or next story marker`: no gap, CS-348, CS-350, needs-investigation, test gap, semantic gap, or observability gap.
- Required report sections:
  - Executive summary.
  - Post-provider pipeline.
  - Output schemas by use case.
  - Validation, recovery, rejection, and grounding statuses.
  - Persistent prompt, input, audit, and evidence anchors.
  - Evidence refs relation.
  - Observability, usage, call logs, and replay.
  - Admin audit and replay service surfaces.
  - Prompt-to-output-to-audit matrix.
  - Existing tests and gaps.
  - Residual risks for CS-348 and CS-350.
- Required fields:
  - pipeline step
  - owner
  - symbol or field
  - input
  - output
  - validation status
  - persistent anchors
  - evidence
  - gap or next story marker
- Optional fields:
  - none for required matrix rows; unknown anchors must use `needs-investigation`.
- Status codes:
  - none; this story does not change a public API route.
- Serialization names:
  - Report column names must use the exact field names listed above.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-347-audit-output-validation-persistence-observabilite-prompt-llm/evidence/output-validation-scan-baseline.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-347-audit-output-validation-persistence-observabilite-prompt-llm/evidence/output-validation-scan-after.txt`
- Expected invariant:
  - The only intended repository delta is the audit report, story evidence artifacts, generated review handoff, validation output, and tracker entry.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Output schema validation | `backend/app/domain/llm/runtime/output_validator.py` | prompt renderer or audit report prose |
| Output repair | `backend/app/domain/llm/runtime/repair.py` | persistence model or admin API |
| Rejected narrative workflow | `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` | provider adapter |
| Evidence refs validation | `backend/app/domain/astrology/interpretation/evidence_refs_validation.py` | prompt-visible payload |
| Natal audit persistence | `backend/app/services/llm_generation/natal/interpretation_service.py` | frontend or provider client |
| Narrative answer model | `backend/app/infra/db/models/user_natal_interpretation.py` | audit report-only schema |
| LLM observability | `backend/app/domain/llm/runtime/observability.py` | prompt composer |
| Observability service | `backend/app/domain/llm/runtime/observability_service.py` | replay service |
| LLM persistence models | `backend/app/infra/db/models/llm/**` | service-local ad hoc objects |
| Admin audit contract | `backend/app/services/api_contracts/admin/audit.py` | client prompt contract |
| Audit report | `_condamad/audits/prompt-generation-cartography/*/05-output-validation-persistence-audit.md` | transient chat notes |

## Mandatory Reuse / DRY Constraints

- Reuse the timestamped audit folder pattern from CS-343, CS-344, CS-345, and CS-346.
- Reuse the existing evidence artifact pattern under the story folder.
- Reuse CS-288, CS-289, CS-290, CS-298, CS-341, and CS-342 terms for audit anchors, evidence refs, grounding, rejection, and replay.
- Reuse existing source symbols and tests as evidence instead of copying implementation code into the report.
- Do not duplicate CS-345 provider handoff tracing or CS-346 input source mapping; reference them and focus on post-provider output and persistence.
- Do not introduce new dependencies.

## No Legacy / Forbidden Paths

- No legacy validation path may be accepted as a target implementation path.
- No compatibility validation or audit path may be added for this audit.
- No fallback persistence or replay path may be added for this audit.
- Do not edit validators, repair code, services, DB models, admin contracts, tests, migrations, prompts, provider clients, or frontend files.
- Do not describe prompt provider handoff as proof that output validation, semantic grounding, or persistence succeeded.
- Do not treat persisted audit anchors as prompt-visible material.

## Reintroduction Guard

- Exact forbidden implementation surfaces:
  - `backend/app/domain/llm/runtime/**` code edits.
  - `backend/app/services/llm_generation/natal/**` code edits.
  - `backend/app/infra/db/models/**` code edits.
  - `backend/app/services/api_contracts/admin/**` code edits.
  - `backend/tests/**` edits outside persisted validation evidence.
  - `frontend/src/**` edits.
  - `_condamad/stories/regression-guardrails.md` edits.
- Required deterministic guards:
  - `python` checks `git status --short -- backend/app backend/tests frontend/src`.
  - `rg` verifies the audit report contains validation, rejection, persistence, observability, replay, admin, and residual risk sections.
  - `AST guard` verifies the audit evidence references existing source symbols rather than new implementation changes.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Applicable only as backend boundary control; no API routing logic may move during audit. | `python` git-status guard; targeted `rg`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Applicable; validation plans must use collected backend pytest paths. | `pytest` paths in VC6 through VC11. |
| Registry gap | No exact guardrail exists for post-provider output validation persistence cartography. | Resolver output recorded in evidence. |

Non-applicable examples: RG-047, RG-052, and RG-041 are frontend or entitlement-documentation guardrails and remain out of scope.

## Persistent Evidence Artifacts

Story evidence paths below are under
`_condamad/stories/CS-347-audit-output-validation-persistence-observabilite-prompt-llm/`.

| Artifact | Path | Purpose |
|---|---|---|
| Baseline scan | `evidence/output-validation-scan-baseline.txt` | Keep pre-audit source scan evidence. |
| After scan | `evidence/output-validation-scan-after.txt` | Keep post-audit source scan evidence. |
| Symbol map | `evidence/output-validation-symbol-map.md` | Keep owner evidence. |
| Audit report | `_condamad/audits/prompt-generation-cartography/YYYY-MM-DD-HHMM/05-output-validation-persistence-audit.md` | Deliver the audit. |
| Validation output | `evidence/validation.txt` | Keep validation command output. |
| Final evidence | `evidence/final-evidence.md` | Summarize final proof and residual gaps. |
| Review output | `generated/11-code-review.md` | Keep review handoff. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this output validation persistence audit story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/audits/prompt-generation-cartography/YYYY-MM-DD-HHMM/05-output-validation-persistence-audit.md` - audit deliverable.
- `_condamad/stories/CS-347-audit-output-validation-persistence-observabilite-prompt-llm/evidence/output-validation-scan-baseline.txt` - baseline scan artifact.
- `_condamad/stories/CS-347-audit-output-validation-persistence-observabilite-prompt-llm/evidence/output-validation-scan-after.txt` - after scan artifact.
- `_condamad/stories/CS-347-audit-output-validation-persistence-observabilite-prompt-llm/evidence/output-validation-symbol-map.md` - source symbol map.
- `_condamad/stories/CS-347-audit-output-validation-persistence-observabilite-prompt-llm/evidence/validation.txt` - validation output artifact.
- `_condamad/stories/CS-347-audit-output-validation-persistence-observabilite-prompt-llm/evidence/final-evidence.md` - final evidence summary.
- `_condamad/stories/CS-347-audit-output-validation-persistence-observabilite-prompt-llm/generated/11-code-review.md` - generated review handoff.

Likely tests:

- `backend/tests/unit/test_rejected_narrative_answer_workflow.py` - proves rejection and grounding workflow behavior.
- `backend/tests/llm_orchestration/test_output_validator_pipeline.py` - proves output validation pipeline behavior.
- `backend/tests/unit/test_rejected_narrative_answer_logging.py` - proves rejected narrative answer logging behavior.
- `backend/tests/unit/test_evidence_refs_validation.py` - proves evidence refs validation behavior.
- `backend/tests/unit/test_evidence_refs_section_status.py` - proves section-level grounding status behavior.
- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py` - proves persisted natal audit anchors.
- `backend/tests/integration/test_llm_db_invariants.py` - proves `llm_call_logs` and replay schema invariants.
- `backend/tests/unit/test_replay_snapshot_v1_service_audit.py` - proves replay audit events.
- `backend/tests/unit/test_admin_endpoint_segmentation_contract.py` - proves admin audit and replay surface segmentation.

Files not expected to change:

- `backend/app/**` - out of scope; no runtime, validation, repair, persistence, observability, replay, admin, or provider code is edited.
- `backend/tests/**` - out of scope; existing tests may be executed or cited but not edited.
- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no migration is touched.
- `_condamad/stories/regression-guardrails.md` - out of scope; registry enrichment is not authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

All Python commands must run after `.\.venv\Scripts\Activate.ps1`.
Run VC1 through VC5, VC12, VC13, and VC14 from the repository root.
Run VC6 through VC11, VC15, and VC16 from `backend`.

- VC1 report path:
  `python -c "from pathlib import Path; root=Path('_condamad/audits/prompt-generation-cartography'); assert any(root.glob('*/05-output-validation-persistence-audit.md'))"`
- VC2 source scan:
  `rg -n "validate_output|RejectedNarrativeAnswer|grounding_status|evidence_refs|prompt_version|llm_input_hash|projection_hash|llm_call_logs|replay" backend/app backend/tests`
- VC3 report coverage:
  `rg -n "Post-provider pipeline|Output schemas by use case|Validation, recovery, rejection|Prompt-to-output-to-audit matrix" _condamad`
- VC4 anchor coverage:
  `rg -n "prompt_version|prompt_ref|projection_hash|llm_input_hash|evidence_refs|grounding_status" _condamad/audits/prompt-generation-cartography`
- VC5 residual risk coverage:
  `rg -n "CS-348|CS-350|semantic gap|observability gap|replay gap" _condamad/audits/prompt-generation-cartography`
- VC6 output validation tests:
  `pytest -q tests/llm_orchestration/test_output_validator_pipeline.py --tb=short`
- VC7 rejected workflow tests:
  `pytest -q tests/unit/test_rejected_narrative_answer_workflow.py tests/unit/test_rejected_narrative_answer_logging.py --tb=short`
- VC8 evidence refs tests:
  `pytest -q tests/unit/test_evidence_refs_validation.py tests/unit/test_evidence_refs_section_status.py --tb=short`
- VC9 natal audit persistence tests:
  `pytest -q tests/integration/llm/test_natal_llm_astrology_input_audit.py --tb=short`
- VC10 LLM DB invariant tests:
  `pytest -q tests/integration/test_llm_db_invariants.py --tb=short`
- VC11 replay audit tests:
  `pytest -q tests/unit/test_replay_snapshot_v1_service_audit.py tests/unit/test_replay_snapshot_v1_service_manual_purge.py --tb=short`
- VC12 admin audit surface tests:
  `pytest -q tests/unit/test_admin_endpoint_segmentation_contract.py --tb=short`
- VC13 no runtime source delta:
  `python -c "import subprocess; subprocess.run(['git','diff','--quiet','--','backend/app','backend/tests','frontend/src'], check=True)"`
- VC14 artifact paths:
  `python -c "from pathlib import Path; r=Path('_condamad/stories/CS-347-audit-output-validation-persistence-observabilite-prompt-llm'); assert (r/'evidence').exists()"`
  Run `python` with the same `r` value to assert `(r/'generated').exists()`.
- VC15 format: `ruff format .`
- VC16 lint: `ruff check .`
- VC17 full backend tests: `pytest -q tests --tb=short`

## Regression Risks

- Risk: the audit could imply that provider handoff success proves output validity.
  - Mitigation: AC2, AC3, AC4, and the Runtime Source of Truth require a post-provider control sequence.
- Risk: persistence could be described as proof of prompt correctness.
  - Mitigation: AC6 and AC11 require persistent anchors to be classified as audit data, not prompt proof.
- Risk: shape validation could be confused with semantic grounding validation.
  - Mitigation: AC3 and AC4 require separate schema validation and semantic grounding limit sections.
- Risk: replay or admin audit surfaces could be documented without safe metadata boundaries.
  - Mitigation: AC8, AC9, and AC10 require call log, replay, usage, metadata, and admin surface evidence.
- Risk: the report could duplicate CS-345 or CS-346 instead of focusing on post-provider output handling.
  - Mitigation: DRY constraints require using prior audits as context while focusing this story on output validation and persistence.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command.
- Keep the audit as documentation plus evidence only; application files remain unchanged.
- Create `_condamad/audits/prompt-generation-cartography/YYYY-MM-DD-HHMM/` before writing the audit report.
- Keep markdown table lines under 180 characters in generated evidence and final report.
- Record any missing post-provider-output guardrail as `Registry gap` in story evidence, not in the registry.

## References

- `_story_briefs/cs-347-audit-validation-output-persistence-observabilite-prompt-llm.md`
- `_story_briefs/cs-288-implement-narrative-answer-audit-v1-persistence.md`
- `_story_briefs/cs-289-implement-evidence-refs-validation.md`
- `_story_briefs/cs-290-implement-rejected-narrative-answer-workflow.md`
- `_story_briefs/cs-298-implement-replay-snapshot-v1-execution-audit.md`
- `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md`
- `_story_briefs/cs-342-cloturer-process-evidence-hors-prompt-validation-redaction-llm-natale.md`
- `_condamad/stories/CS-345-audit-runtime-gateway-handoff-provider-prompt-llm/00-story.md`
- `_condamad/stories/CS-346-audit-natal-astrology-llm-input-sources/00-story.md`
- `_condamad/stories/regression-guardrails.md`
