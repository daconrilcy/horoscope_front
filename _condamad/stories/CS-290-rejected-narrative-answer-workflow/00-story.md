# Story CS-290 rejected-narrative-answer-workflow: Implement Rejected Narrative Answer Workflow
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-290-implement-rejected-narrative-answer-workflow.md`.
- Related dependency: CS-261 defines the rejected ungrounded narrative answer workflow contract.
- Related dependency: CS-288 defines the expected `narrative_answer_audit_v1` persistence owner.
- Related dependency: CS-289 defines section-level `evidence_refs` validation.
- Existing owner found: `backend/app/services/llm_generation/natal/interpretation_service.py` owns natal narrative response creation.
- Existing owner found: `backend/app/infra/db/models/user_natal_interpretation.py` owns persisted natal interpretation rows.
- Existing owner found: `backend/app/infra/db/models/llm/llm_observability.py` owns LLM call logs and validation status.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: ungrounded narrative answers must be rejected, audited, logged and masked before any client response is returned.
- Source-alignment evidence: PASS; ACs cover rejection, storage, client masking, logs, no retry and tests.

## Objective

Implement the backend application workflow that turns an ungrounded narrative answer into a rejected audited outcome.

The implementation must reuse the existing audit persistence path, store `rejection_reason` and validation context, return only controlled
client wording, emit internal logs and keep retry, manual publication, UI review and LLM provider changes outside this story.

## Target State

- Narrative answers classified as ungrounded by the CS-289 validation result are not delivered as raw client content.
- The canonical audit persistence stores `status="rejected"` for the rejected narrative answer.
- The audit record stores a structured `rejection_reason` and validation context from the evidence refs result.
- The client response contains controlled support wording and never contains the rejected raw AI answer.
- Internal logs include answer, request, use case and rejection diagnostic fields without exposing raw client payloads.
- The existing LLM provider and prompt execution path stay unchanged.
- No retry queue, manual publication path, admin review UI or public proof details are added.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-290-implement-rejected-narrative-answer-workflow.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-290`.
- Evidence 3: `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/00-story.md` - rejection contract read.
- Evidence 4: `_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/00-story.md` - audit persistence dependency read.
- Evidence 5: `_condamad/stories/CS-289-evidence-refs-section-validation/00-story.md` - validation dependency read.
- Evidence 6: `backend/app/services/llm_generation/natal/interpretation_service.py` - narrative response orchestration owner inspected.
- Evidence 7: `backend/app/infra/db/models/user_natal_interpretation.py` - persisted interpretation owner inspected.
- Evidence 8: `backend/app/infra/db/models/llm/llm_observability.py` - existing LLM call log owner inspected.
- Evidence 9: targeted `rg` found no complete `narrative_answer_audit` or `rejection_reason` application workflow in backend source.
- Evidence 10: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Evidence 11: `resolve_guardrails.py` - scoped resolver run for backend-domain, audit, validation and no-retry surfaces.
- Repository structure alert: no expected backend root is absent; implementation may create scoped files listed below.
- Source-alignment review result: PASS; no brief stake was narrowed into documentation-only, API-only, UI or provider work.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend workflow that consumes CS-289 validation output for narrative answers.
  - Reuse or extension of the canonical CS-288 audit persistence owner.
  - Marking ungrounded narrative answers with `status="rejected"`.
  - Storage of `rejection_reason`, validation context and raw rejected answer for internal audit use.
  - Controlled client response mapping that excludes the rejected raw AI answer.
  - Internal log event emitted for the rejection workflow.
  - Unit, integration and architecture tests for rejection, storage, response masking and no retry.
- Out of scope:
  - Frontend UI, admin review UI, public API contract changes, auth, i18n, styling, build tooling and generated clients.
  - Automatic retry, manual publication, LLM provider changes, prompt content rewrites and full admin review workflow.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No new public endpoint, admin endpoint, OpenAPI schema or response serializer for rejected answer review.
  - No retry queue, manual publish action, LLM provider adapter change or prompt template rewrite.
  - No duplicate persistence path beside the canonical narrative answer audit owner.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend workflow integration story.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only backend workflow behavior required to reject ungrounded narrative answers.
  - Reuse CS-261, CS-288 and CS-289 owners before creating new workflow helpers.
  - Keep public API routes, admin API routes, frontend, auth, i18n, style and build tooling unchanged.
  - Keep the LLM provider invocation unchanged and evaluate rejection after validation output is available.
  - Return controlled client wording instead of raw rejected AI answer content.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-288 or CS-289 implementation evidence is missing and no canonical audit or validation owner exists.
- Additional validation rules:
  - Ungrounded validation output must produce `status="rejected"` in the audit persistence path.
  - `rejection_reason` must be structured and must not be a free-text-only diagnostic.
  - Validation context must include enough evidence refs outcome data for admin analysis.
  - Raw rejected AI answer content must be retained for internal audit use only.
  - Client-facing payloads must contain controlled wording and no raw rejected AI answer.
  - Internal logs must include request, answer, use case and rejection reason fields.
  - Retry, manual publication and admin review UI must not be implemented by this story.
  - `pytest`, `TestClient`, `app.routes`, `app.openapi()` and AST guard prove the final runtime state.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, `TestClient`, `app.routes`, `app.openapi()` and DB checks prove workflow behavior. |
| Baseline Snapshot | yes | Before and after evidence proves the intended backend workflow and audit delta. |
| Ownership Routing | yes | Rejection workflow, audit persistence, validation and client response need canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this workflow story. |
| Contract Shape | yes | Rejection has exact status, reason, validation context, raw storage and client response rules. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Raw answer leakage, duplicate persistence and retry must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Ungrounded answers become rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_rejected_narrative_answer_workflow.py`. |
| AC2 | Rejected records are persisted. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_rejected_narrative_answer_audit.py`. |
| AC3 | `rejection_reason` is stored. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_rejected_narrative_answer_audit.py`. |
| AC4 | Validation context is stored. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_rejected_narrative_answer_audit.py`. |
| AC5 | Client response is controlled. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_rejected_narrative_answer_response.py`. |
| AC6 | Raw AI answer stays internal. | Evidence profile: targeted_forbidden_symbol_scan; `pytest -q backend/tests/integration/test_rejected_narrative_answer_response.py`. |
| AC7 | Internal log is emitted. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_rejected_narrative_answer_logging.py`. |
| AC8 | Retry is not introduced. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans retry symbols in backend workflow paths. |
| AC9 | Public API runtime surface is unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`. |
| AC10 | One workflow owner exists. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/architecture/test_rejected_narrative_answer_boundary.py`. |
| AC11 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-290 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-261, CS-288, CS-289 and existing narrative persistence owners before editing. (AC: AC1, AC2, AC10)
- [ ] Task 2: Record the reuse decision for audit persistence, validation input and response mapping. (AC: AC10, AC11)
- [ ] Task 3: Add a canonical workflow helper or service method for rejected narrative answers. (AC: AC1, AC5)
- [ ] Task 4: Persist `status="rejected"` through the canonical audit owner. (AC: AC2)
- [ ] Task 5: Persist structured `rejection_reason` and validation context. (AC: AC3, AC4)
- [ ] Task 6: Retain raw rejected AI answer content for internal audit storage only. (AC: AC2, AC6)
- [ ] Task 7: Map rejected output to controlled client wording before response serialization. (AC: AC5, AC6)
- [ ] Task 8: Add internal logging with request, answer, use case and reason fields. (AC: AC7)
- [ ] Task 9: Add architecture guards for one owner, no public API drift and no retry queue. (AC: AC8, AC9, AC10)
- [ ] Task 10: Add unit and integration tests for rejection, audit storage, response masking and logs. (AC: AC1, AC2, AC5, AC7)
- [ ] Task 11: Persist validation transcript, reuse decision and app surface evidence under the CS-290 evidence folder. (AC: AC9, AC11)

## Files to Inspect First

- `_story_briefs/cs-290-implement-rejected-narrative-answer-workflow.md` - source brief.
- `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/00-story.md` - workflow contract dependency.
- `_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/00-story.md` - audit persistence dependency.
- `_condamad/stories/CS-289-evidence-refs-section-validation/00-story.md` - validation dependency.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - current narrative answer orchestration owner.
- `backend/app/infra/db/models/user_natal_interpretation.py` - existing persisted interpretation owner.
- `backend/app/infra/db/models/llm/llm_observability.py` - LLM call log and validation status owner.
- `backend/app/infra/db/repositories/**` - expected repository owner for audit persistence reuse.
- `backend/app/domain/astrology/interpretation/**` - expected evidence refs validation owner.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - Unit tests for rejected workflow decision and log emission.
  - Integration tests proving audit persistence and controlled client response.
  - DB repository checks for stored `status`, `rejection_reason`, validation context and raw internal answer.
  - `TestClient`, `app.routes` and `app.openapi()` for public API neutrality.
  - AST guard for one canonical workflow owner and no retry queue.
- Secondary evidence:
  - Targeted `rg` scans for `status="rejected"`, `rejection_reason`, validation context and retry symbols.
  - Persisted source-decision evidence under `_condamad/stories/CS-290-rejected-narrative-answer-workflow/evidence/`.
- Static scans alone are not sufficient because:
  - rejection, persistence, response masking and logs must be proven by runtime tests and loaded app inspection.

## Contract Shape

- Contract type:
  - Backend workflow contract for rejected ungrounded narrative answers.
- Fields:
  - `answer_id`: stable narrative answer identifier.
  - `answer_type`: narrative answer category from `narrative_answer_audit_v1`.
  - `status`: exact value `rejected` for the rejected audit record.
  - `grounding_status`: source validation outcome that triggered rejection, usually `ungrounded`.
  - `rejection_reason`: structured reason code derived from validation result.
  - `validation_context`: section validation summary and evidence refs diagnostic context.
  - `raw_answer_storage`: retained rejected AI answer content for internal analysis.
  - `client_message`: controlled wording returned to the client instead of raw answer content.
  - `log_event`: internal log event and fields for operational analysis.
  - `retry_policy`: exact value `out_of_scope`.
- Required fields:
  - `answer_id`
  - `answer_type`
  - `status`
  - `grounding_status`
  - `rejection_reason`
  - `validation_context`
  - `raw_answer_storage`
  - `client_message`
  - `log_event`
  - `retry_policy`
- Optional fields:
  - none
- Status codes:
  - unchanged; this story does not add or alter HTTP route status codes.
- Serialization names:
  - persisted audit fields stay snake_case and align with CS-261, CS-288 and CS-289 terminology.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must stay unchanged for rejected narrative answer internals.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-290-implement-rejected-narrative-answer-workflow.md`
  - CS-261 rejection workflow contract story
  - CS-288 narrative answer audit persistence story
  - CS-289 evidence refs validation story
  - targeted scan of narrative service, audit persistence and LLM observability owners
- Comparison after implementation:
  - `_condamad/stories/CS-290-rejected-narrative-answer-workflow/evidence/validation.txt`
  - `_condamad/stories/CS-290-rejected-narrative-answer-workflow/evidence/reuse-decision.md`
  - `_condamad/stories/CS-290-rejected-narrative-answer-workflow/evidence/app-surface-status.txt`
  - `_condamad/stories/CS-290-rejected-narrative-answer-workflow/evidence/response-mask-scan.txt`
- Expected invariant:
  - The only intended application delta is backend workflow, audit integration, tests and CONDAMAD evidence for rejected answers.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Rejection workflow decision | backend narrative workflow helper or service owner | API router or frontend component |
| Evidence validation input | CS-289 evidence refs validation owner | narrative renderer text logic |
| Audit persistence | CS-288 canonical audit repository or model owner | duplicate audit table or UI state |
| Controlled client response | backend projection or response mapping owner | raw audit storage payload |
| Internal logging | backend workflow service logger | public API serializer |
| Retry decision | future dedicated story | CS-290 implementation |
| Evidence artifacts | `_condamad/stories/CS-290-rejected-narrative-answer-workflow/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse CS-261 rejection state, controlled response and no-retry language.
- Reuse CS-288 audit persistence owner and field names for narrative answer audit data.
- Reuse CS-289 validation output instead of creating a second evidence refs validator.
- Reuse current narrative answer orchestration before adding a new service boundary.
- Reuse existing LLM call logging terminology for request, trace, use case and validation status context.
- Keep one canonical rejected-answer workflow owner.
- Do not add external packages, generated clients, public routes, admin routes, prompt templates, provider adapters or retry workers.

## No Legacy / Forbidden Paths

- No legacy workflow path may deliver an ungrounded narrative answer to the client.
- No compatibility workflow path may bypass CS-289 validation output.
- No fallback branch may return the rejected raw AI answer to clients.
- Do not create aliases, shims, wrappers or parallel validators for the same rejected-answer decision.
- Do not create a second audit persistence path beside the CS-288 owner.
- Do not implement retry queue, manual publication, admin review UI or LLM provider changes.
- Forbidden surfaces:
  - `frontend/src/**`
  - public API routers
  - admin API routers
  - generated OpenAPI clients
  - prompt template files
  - LLM provider adapters
  - duplicate audit repositories
  - retry worker or queue modules

## Reintroduction Guard

- Guard target:
  - ungrounded narrative answers cannot be returned as raw client content;
  - rejected answers must persist `status="rejected"`;
  - `rejection_reason` cannot become unstructured free-text-only data;
  - validation context cannot be dropped from the audit record;
  - retry, manual publication, admin review UI and public route drift cannot be introduced by this story.
- Guard mechanism:
  - unit tests for workflow decision and log emission;
  - integration tests for audit persistence and controlled client response;
  - AST guard for canonical owner and no retry queue;
  - `app.routes` and `app.openapi()` neutrality checks;
  - targeted `rg` scans for raw answer leakage and duplicate workflow symbols.
- Guard owner:
  - backend rejected narrative answer workflow owner chosen during implementation;
  - backend audit persistence owner from CS-288;
  - backend tests listed in this story.
- Guard evidence:
  - `pytest -q backend/tests/unit/test_rejected_narrative_answer_workflow.py`;
  - `pytest -q backend/tests/integration/test_rejected_narrative_answer_audit.py`;
  - `pytest -q backend/tests/integration/test_rejected_narrative_answer_response.py`;
  - `pytest -q backend/tests/architecture/test_rejected_narrative_answer_boundary.py`;
  - `python -c "from app.main import app; assert 'rejected_narrative_answer' not in str(app.openapi())"`.

## Regression Guardrails

Scope vector:

- backend-domain workflow integration: yes;
- narrative answer audit persistence: yes;
- evidence refs validation output: yes;
- backend tests and architecture guard: yes;
- public API, admin API and frontend implementation: no;
- auth, i18n, style, build tooling and migration: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | Backend ownership stays in canonical app paths. | `rg`; targeted `pytest`. |
| RG-022 | Validation paths must remain executable for backend tests. | `pytest`; persisted validation. |
| Registry gap | No exact rejected narrative answer workflow guardrail exists in resolver output. | Story-local response and audit guards. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because this story targets rejected narrative answers.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Reuse decision | `_condamad/stories/CS-290-rejected-narrative-answer-workflow/evidence/reuse-decision.md` | Record reused owners. |
| Validation output | `_condamad/stories/CS-290-rejected-narrative-answer-workflow/evidence/validation.txt` | Keep lint, tests and scans. |
| Application surface status | `_condamad/stories/CS-290-rejected-narrative-answer-workflow/evidence/app-surface-status.txt` | Prove API neutrality. |
| Response mask scan | `_condamad/stories/CS-290-rejected-narrative-answer-workflow/evidence/response-mask-scan.txt` | Prove raw-answer masking. |
| Review output | `_condamad/stories/CS-290-rejected-narrative-answer-workflow/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this workflow story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/services/llm_generation/natal/interpretation_service.py` - likely workflow integration point.
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` - possible canonical workflow helper.
- `backend/app/infra/db/repositories/llm/narrative_answer_audit_repository.py` - expected audit persistence owner.
- `backend/app/infra/db/models/llm/narrative_answer_audit.py` - expected audit model owner from CS-288.
- `_condamad/stories/CS-290-rejected-narrative-answer-workflow/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-290-rejected-narrative-answer-workflow/evidence/reuse-decision.md` - owner reuse evidence.
- `_condamad/stories/CS-290-rejected-narrative-answer-workflow/evidence/app-surface-status.txt` - API neutrality proof.
- `_condamad/stories/CS-290-rejected-narrative-answer-workflow/evidence/response-mask-scan.txt` - masking proof.

Likely tests:

- `backend/tests/unit/test_rejected_narrative_answer_workflow.py` - workflow decision and controlled message behavior.
- `backend/tests/unit/test_rejected_narrative_answer_logging.py` - internal log event fields.
- `backend/tests/integration/test_rejected_narrative_answer_audit.py` - rejected audit persistence.
- `backend/tests/integration/test_rejected_narrative_answer_response.py` - client response masking.
- `backend/tests/architecture/test_rejected_narrative_answer_boundary.py` - owner, API neutrality and no-retry guard.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- public API routers - out of scope; no client route is touched.
- admin API routers - out of scope; no admin API is implemented.
- prompt template files - out of scope; prompt content is not changed.
- LLM provider adapters - out of scope; provider behavior is unchanged.
- generated OpenAPI clients - out of scope; no API contract is exposed.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `. .\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `pytest -q tests/unit/test_rejected_narrative_answer_workflow.py`
- VC6: `pytest -q tests/unit/test_rejected_narrative_answer_logging.py`
- VC7: `pytest -q tests/integration/test_rejected_narrative_answer_audit.py`
- VC8: `pytest -q tests/integration/test_rejected_narrative_answer_response.py`
- VC9: `pytest -q tests/architecture/test_rejected_narrative_answer_boundary.py`
- VC10: `pytest -q`
- VC11: `python -c "from app.main import app; assert 'rejected_narrative_answer' not in str(app.openapi())"`
- VC12: `python -c "from app.main import app; assert all('rejected-narrative' not in getattr(r, 'path', '') for r in app.routes)"`
- VC13: `rg -n "status.*rejected|rejection_reason|validation_context|client_message" app tests`
- VC14: `rg -n "retry|queue|manual publish|raw_answer" app tests`
- VC15: `python -c "from pathlib import Path; p=Path('../_condamad/stories/CS-290-rejected-narrative-answer-workflow/evidence/validation.txt'); assert p.exists()"`
- VC16: `python -c "from pathlib import Path; p=Path('../_condamad/stories/CS-290-rejected-narrative-answer-workflow/evidence/reuse-decision.md'); assert p.exists()"`
- VC17: `python -c "from pathlib import Path; p=Path('../_condamad/stories/CS-290-rejected-narrative-answer-workflow/evidence/app-surface-status.txt'); assert p.exists()"`
- VC18: `python -c "from pathlib import Path; p=Path('../_condamad/stories/CS-290-rejected-narrative-answer-workflow/evidence/response-mask-scan.txt'); assert p.exists()"`
- VC19: `git status --short -- app tests migrations ../frontend/src`

Before VC3 through VC18, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The workflow could mark the audit row as rejected while still returning raw rejected answer content to clients.
- Rejection diagnostics could be logged but not stored in the canonical audit record.
- `rejection_reason` could become free text that admin analysis cannot filter.
- A retry branch could be introduced without the future product and reliability decision required by CS-261.
- The implementation could create duplicate validation or persistence owners instead of reusing CS-288 and CS-289 surfaces.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Start by proving whether CS-288 and CS-289 have implemented their canonical owners.
- Record the owner reuse decision before adding workflow code.
- Persist required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-290-implement-rejected-narrative-answer-workflow.md`
- `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/00-story.md`
- `_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/00-story.md`
- `_condamad/stories/CS-289-evidence-refs-section-validation/00-story.md`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/infra/db/models/user_natal_interpretation.py`
- `backend/app/infra/db/models/llm/llm_observability.py`
- `_condamad/stories/regression-guardrails.md`
