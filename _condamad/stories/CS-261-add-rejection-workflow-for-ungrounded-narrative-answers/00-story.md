# Story CS-261 add-rejection-workflow-for-ungrounded-narrative-answers: Add Rejection Workflow For Ungrounded Narrative Answers
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-261-add-rejection-workflow-for-ungrounded-narrative-answers.md`.
- Related dependency: CS-259 defines `narrative_answer_audit_v1` as the answer audit contract.
- Related dependency: CS-260 defines `evidence_refs` as the proof reference contract.
- Existing owner found: `backend/app/domain/llm/runtime/observability_service.py` owns LLM runtime rejection observability events.
- Existing owner found: `backend/app/domain/llm/runtime/gateway.py` emits `runtime_rejected` events in the LLM runtime.
- Existing owner found: `backend/app/services/llm_generation/chat/chat_guidance_service.py` prevents raw structured JSON reaching the UI.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: ungrounded narrative answers need one auditable rejection workflow that protects clients and keeps diagnostic traces.
- Source-alignment evidence: PASS; ACs cover terminal status, retained rejected content, client masking, reasons, logs, no retry and debug separation.

## Objective

Define one canonical backend-domain contract document for rejecting ungrounded narrative answers.

The implementation must specify the `rejected` terminal status, transition rules, stored diagnostic data, controlled client response, internal
logs, alert semantics, privacy minimums and no-retry boundary without implementing the admin review UI, changing the LLM provider, creating a
retry queue, deciding final GDPR retention, or coupling the workflow to calculation debug.

## Target State

- `rejected` is documented as a terminal auditable state for narrative answers that fail grounding.
- Transition conditions from `ungrounded` or invalid `evidence_refs` to `rejected` are explicit.
- Rejected answer content is retained for internal analysis with source, prompt, provider, model and proof metadata.
- Rejection reasons are structured and searchable for admin analysis.
- The client receives controlled support wording and never receives the raw rejected AI answer.
- Internal logs and alert payloads identify the rejection without exposing unnecessary client-sensitive data.
- Privacy minimums define masking, access scope and unresolved final retention as a product decision.
- Retry remains outside this story and must not be implemented.
- The workflow remains separate from calculation debug data and astrology runtime traces.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-261-add-rejection-workflow-for-ungrounded-narrative-answers.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-261`.
- Evidence 3: `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md` - narrative audit dependency read.
- Evidence 4: `_condamad/stories/CS-260-evidence-refs-contract-validation/00-story.md` - evidence refs dependency read.
- Evidence 5: `backend/app/domain/llm/runtime/observability_service.py` - existing LLM rejection observability owner found.
- Evidence 6: `backend/app/domain/llm/runtime/gateway.py` - existing LLM runtime rejection event emitter found.
- Evidence 7: `backend/app/services/llm_generation/chat/chat_guidance_service.py` - existing raw-output client masking pattern found.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Evidence 9: `resolve_guardrails.py` - scoped resolver run for backend-domain rejection workflow, audit, privacy and no-retry surfaces.
- Source-alignment evidence: PASS; no brief concern was dropped or replaced by technical cleanup.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Canonical contract documentation for the ungrounded narrative answer rejection workflow.
  - `rejected` terminal state, transition conditions and audit status rules.
  - Stored diagnostic data for rejected raw answer content and grounding evidence.
  - Structured `rejection_reason` taxonomy and admin-analysis fields.
  - Controlled client response rule that masks the rejected AI answer.
  - Internal log and alert requirements for rejection events.
  - Minimal privacy rules for masking, access control and unresolved final retention.
  - Negative checks for retry, debug calculation, API route, DB, provider and frontend drift.
- Out of scope:
  - Frontend UI, public API exposure, DB schema, migrations, auth, i18n, styling, build tooling and generated clients.
  - Admin review back-office, final GDPR retention decision, LLM provider change, retry queue and calculation debug.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No public endpoint, OpenAPI schema, response serializer or API contract for rejection review.
  - No database table, migration, repository, final retention policy, admin route or admin screen.
  - No prompt template change, LLM provider implementation, retry mechanism or calculation debug workflow change.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain workflow contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the rejection workflow contract documentation and story evidence artifacts.
  - Reuse CS-259 `narrative_answer_audit_v1` and CS-260 `evidence_refs` terminology.
  - Reuse existing LLM runtime observability and raw-output masking concepts instead of creating parallel ownership.
  - Keep backend runtime code, API routes, frontend, DB, migrations, auth, i18n, style and build tooling unchanged.
  - Keep calculation debug data outside the rejection workflow.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks to implement retry, admin review UI, final GDPR retention or provider changes in this story.
- Additional validation rules:
  - The contract must name `rejected` as a terminal auditable state.
  - The contract must define transition conditions from `ungrounded` and invalid proof references.
  - The contract must require storing rejected raw answer content for internal analysis only.
  - The contract must define structured `rejection_reason` values.
  - The contract must require a controlled client response that excludes the raw rejected AI answer.
  - The contract must define internal log and alert fields for rejection events.
  - The contract must define privacy minimums for masking, access scope and undecided final retention.
  - The contract must state retry is a future-story decision and is not implemented here.
  - The contract must keep rejection workflow separate from calculation debug data.
  - `app.routes`, `app.openapi()`, `pytest` and scoped `git status` prove no public API or application surface drift.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Existing LLM owners, `app.routes`, `app.openapi()` and `pytest` prove source boundaries. |
| Baseline Snapshot | yes | Before and after evidence must prove one contract document and no application surface drift. |
| Ownership Routing | yes | Audit workflow, observability, client response, privacy and future retry need separate owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this workflow contract story. |
| Contract Shape | yes | The workflow has exact states, reasons, retained data, logs, alerts and privacy rules. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Raw client leakage, retry, debug coupling and route drift must stay out. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `rejected` is terminal. | Evidence profile: json_contract_shape; `rg` checks terminal auditable state. |
| AC2 | Transition conditions are explicit. | Evidence profile: json_contract_shape; `rg` checks ungrounded and invalid evidence_refs. |
| AC3 | Rejected raw answer is retained. | Evidence profile: json_contract_shape; `rg` checks raw answer storage and internal analysis. |
| AC4 | Client response is controlled. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks controlled message and raw answer masking. |
| AC5 | Rejection reasons are structured. | Evidence profile: json_contract_shape; `rg` checks rejection_reason values. |
| AC6 | Internal log is required. | Evidence profile: json_contract_shape; `rg` checks log event and alert fields. |
| AC7 | Privacy minimums are defined. | Evidence profile: json_contract_shape; `rg` checks masking, access scope and retention decision. |
| AC8 | Retry stays outside scope. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks future story decision and no retry queue. |
| AC9 | Calculation debug stays separate. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks workflow and debug separation. |
| AC10 | Public API surface stays unchanged. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`. |
| AC11 | Application source surfaces remain unchanged. | Evidence profile: repo_wide_negative_scan; `python` records scoped `git status --short` output. |
| AC12 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-261 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-259, CS-260, LLM observability and raw-output masking owners before writing the contract. (AC: AC1, AC4)
- [ ] Task 2: Create `docs/architecture/ungrounded-narrative-rejection-workflow.md` with a French global file comment. (AC: AC1)
- [ ] Task 3: Define `rejected` as a terminal auditable state and document allowed transitions. (AC: AC1, AC2)
- [ ] Task 4: Document retained rejected answer data for internal analysis only. (AC: AC3)
- [ ] Task 5: Define the controlled client response and the raw answer masking rule. (AC: AC4)
- [ ] Task 6: Define structured `rejection_reason` values and required admin-analysis fields. (AC: AC5)
- [ ] Task 7: Define internal log fields and alert semantics for rejection events. (AC: AC6)
- [ ] Task 8: Define privacy minimums for masking, access scope and unresolved final retention. (AC: AC7)
- [ ] Task 9: Document that retry is future-story work and no retry queue is created. (AC: AC8)
- [ ] Task 10: Document the separation from calculation debug data and runtime astrology traces. (AC: AC9)
- [ ] Task 11: Persist validation, scoped status and source checklist evidence under the CS-261 evidence folder. (AC: AC10, AC11, AC12)

## Files to Inspect First

- `_story_briefs/cs-261-add-rejection-workflow-for-ungrounded-narrative-answers.md` - source contract.
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md` - upstream audit contract dependency.
- `_condamad/stories/CS-260-evidence-refs-contract-validation/00-story.md` - upstream evidence reference dependency.
- `docs/architecture/narrative-answer-audit-v1-contract.md` - expected audit contract after CS-259 implementation.
- `docs/architecture/evidence-refs-contract.md` - expected evidence reference contract after CS-260 implementation.
- `backend/app/domain/llm/runtime/observability_service.py` - existing LLM rejection observability owner.
- `backend/app/domain/llm/runtime/gateway.py` - existing runtime rejection event emitter.
- `backend/app/services/llm_generation/chat/chat_guidance_service.py` - existing controlled-output pattern.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - CS-259 `narrative_answer_audit_v1` story for answer audit status and rejected answer metadata.
  - CS-260 `evidence_refs` story for proof reference validity and ungrounded status.
  - `backend/app/domain/llm/runtime/observability_service.py` for current LLM rejection observability events.
  - `backend/app/domain/llm/runtime/gateway.py` for current runtime rejection emission.
  - `backend/app/services/llm_generation/chat/chat_guidance_service.py` for current raw-output masking pattern.
  - `app.routes`, `app.openapi()`, scoped `git status`, `pytest` and targeted `rg` scans for no public API or app-source drift.
- Secondary evidence:
  - Targeted `rg` scans over `docs/architecture/ungrounded-narrative-rejection-workflow.md`.
- Static scans alone are not sufficient because:
  - public API neutrality and application-source non-change must be proven from the loaded app and scoped status.

## Contract Shape

- Contract type:
  - Markdown backend-domain workflow contract for rejected ungrounded narrative answers.
- Fields:
  - `workflow_id`: exact value `ungrounded_narrative_rejection_workflow`.
  - `answer_id`: unique generated narrative answer identifier.
  - `answer_type`: narrative answer category inherited from `narrative_answer_audit_v1`.
  - `grounding_status`: source audit value before rejection, usually `ungrounded`.
  - `status`: exact terminal value `rejected`.
  - `rejection_reason`: one structured value from the documented reason taxonomy.
  - `rejection_detail`: internal diagnostic detail, masked for client-facing surfaces.
  - `raw_answer_storage`: retained rejected AI answer content for internal analysis.
  - `evidence_refs`: proof references checked before rejection.
  - `audit_metadata`: source, prompt, provider, model, projection and hash metadata.
  - `client_message`: controlled support wording that contains no raw rejected answer.
  - `log_event`: internal event name and fields emitted during rejection.
  - `alert_event`: internal alert fields for analysis and monitoring.
  - `privacy_controls`: masking, access scope and final-retention decision status.
  - `retry_policy`: exact value `future_story_decision`.
  - `debug_boundary`: rule separating rejection workflow from calculation debug data.
- Required fields:
  - `workflow_id`
  - `answer_id`
  - `answer_type`
  - `grounding_status`
  - `status`
  - `rejection_reason`
  - `raw_answer_storage`
  - `evidence_refs`
  - `audit_metadata`
  - `client_message`
  - `log_event`
  - `privacy_controls`
  - `retry_policy`
  - `debug_boundary`
- Optional fields:
  - `rejection_detail` for internal protected analysis.
  - `alert_event` for internal monitoring channels.
- Status codes:
  - none; no HTTP endpoint implementation is authorized.
- Serialization names:
  - documentation only; no runtime JSON serializer is added.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must not expose this workflow from this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-261-add-rejection-workflow-for-ungrounded-narrative-answers.md`
  - `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md`
  - `_condamad/stories/CS-260-evidence-refs-contract-validation/00-story.md`
  - `backend/app/domain/llm/runtime/observability_service.py`
  - `backend/app/domain/llm/runtime/gateway.py`
  - `backend/app/services/llm_generation/chat/chat_guidance_service.py`
- Comparison after implementation:
  - `docs/architecture/ungrounded-narrative-rejection-workflow.md`
  - `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/evidence/validation.txt`
  - `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended repository delta is one architecture workflow document plus CONDAMAD story and evidence artifacts.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Rejection workflow contract | `docs/architecture/ungrounded-narrative-rejection-workflow.md` | API routers, frontend, DB models |
| Narrative answer audit status | `docs/architecture/narrative-answer-audit-v1-contract.md` | duplicated status taxonomy |
| Evidence proof validity | `docs/architecture/evidence-refs-contract.md` | rejection workflow as proof owner |
| LLM rejection observability | `backend/app/domain/llm/runtime/observability_service.py` | frontend or calculation debug code |
| Runtime rejection emission | `backend/app/domain/llm/runtime/gateway.py` | provider-specific client code |
| Controlled client response | future public projection story | raw rejected answer storage |
| Future retry decision | later dedicated story | this workflow contract story |
| Evidence artifacts | `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse CS-259 `narrative_answer_audit_v1` status and audit metadata language.
- Reuse CS-260 `evidence_refs` validity and source-hash language for grounding decisions.
- Reuse existing LLM runtime observability terminology for internal rejection events.
- Reuse existing controlled-output masking patterns instead of creating a second client exposure policy.
- Keep one canonical workflow document and one workflow identifier.
- Do not duplicate persistence, prompt, provider, public API, frontend, debug calculation or retry ownership inside this story.
- Do not add external packages, scripts, API schemas, frontend helpers, builders, services, prompts, migrations or generated clients.

## No Legacy / Forbidden Paths

- No legacy public route path may be added for this workflow.
- No compatibility workflow may bypass `narrative_answer_audit_v1` or `evidence_refs`.
- No fallback branch may send the rejected raw AI answer to clients.
- Do not create aliases, shims, wrappers or parallel documents for the same rejection workflow.
- Do not store unstructured rejection reasons as the only diagnostic signal.
- Do not couple rejection workflow data to calculation debug payloads or astrology runtime traces.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/**`
  - `backend/app/infra/db/**`
  - `backend/migrations/**`
  - generated OpenAPI clients
  - prompt template files as workflow owners
  - calculation debug modules as rejection workflow owners

## Reintroduction Guard

- Guard target:
  - ungrounded narrative answers cannot be treated as client-deliverable prose;
  - `rejected` cannot be reopened or treated as a non-terminal status in this contract;
  - rejected raw answer content cannot be sent to client-facing payloads;
  - `rejection_reason` cannot become an unstructured free-text-only field;
  - retry and calculation debug cannot be introduced by this story;
  - public API routes, database migrations and frontend files cannot be introduced by this story.
- Guard mechanism:
  - targeted `rg` checks for required workflow terms and forbidden client exposure terms;
  - `app.routes` and `app.openapi()` neutrality checks;
  - scoped `git status --short` for application roots;
  - persisted evidence under the CS-261 evidence folder.
- Guard owner:
  - `docs/architecture/ungrounded-narrative-rejection-workflow.md`;
  - `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/evidence/validation.txt`;
  - `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/evidence/app-surface-status.txt`.
- Guard evidence:
  - `rg -n "rejected|ungrounded|rejection_reason|controlled client|future_story_decision" docs _story_briefs`;
  - `python -c "from app.main import app; assert 'ungrounded_narrative_rejection_workflow' not in str(app.openapi())"`;
  - `python -c "from app.main import app; assert all('rejection' not in getattr(r, 'path', '') for r in app.routes)"`;
  - `git status --short -- backend/app frontend/src backend/tests backend/migrations`.

## Regression Guardrails

Scope vector:

- backend-domain workflow contract documentation: yes;
- docs architecture contract: yes;
- backend LLM observability references: yes;
- narrative audit and evidence reference dependencies: yes;
- API route change: no;
- frontend implementation: no;
- DB, auth, i18n, style, build and migration: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | Backend app paths are referenced only as source owners, not modified. | `git status`; `python` loaded app checks. |
| RG-022 | Prompt-generation validation discipline applies to LLM workflow evidence. | `rg`; `pytest`; persisted validation. |
| Registry gap | No exact ungrounded rejection workflow guardrail exists in resolver output. | Story-local scans and loaded app checks. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because this workflow concerns narrative rejection, not access rights.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Contract document | `docs/architecture/ungrounded-narrative-rejection-workflow.md` | Keep the canonical rejection workflow contract. |
| Validation output | `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/evidence/validation.txt` | Keep content scans and validation. |
| App surface status | `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/evidence/app-surface-status.txt` | Prove app roots. |
| Source checklist | `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/evidence/source-checklist.md` | Record mandatory source coverage. |
| Review output | `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/generated/11-code-review.md` | Keep review handoff. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this workflow contract story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `docs/architecture/ungrounded-narrative-rejection-workflow.md` - new canonical workflow contract document.
- `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/evidence/app-surface-status.txt` - application non-change proof.
- `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/evidence/source-checklist.md` - source coverage evidence.

Likely tests:

- `docs/architecture/ungrounded-narrative-rejection-workflow.md` - checked by `rg` and `python` validation commands.
- `backend/tests/architecture/test_api_contract_neutrality.py` - targeted architecture regression check for no public route drift.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/**` - out of scope; no backend application source is touched.
- `backend/tests/**` - out of scope; existing architecture tests may be executed as evidence.
- `backend/migrations/**` - out of scope; no database migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `python -c "from pathlib import Path; assert Path('docs/architecture/ungrounded-narrative-rejection-workflow.md').exists()"`
- VC3: `rg -n "rejected|terminal auditable state|status" docs/architecture/ungrounded-narrative-rejection-workflow.md`
- VC4: `rg -n "ungrounded|invalid evidence_refs|transition" docs/architecture/ungrounded-narrative-rejection-workflow.md`
- VC5: `rg -n "raw answer storage|internal analysis|audit_metadata" docs/architecture/ungrounded-narrative-rejection-workflow.md`
- VC6: `rg -n "controlled client|client_message|raw rejected answer" docs/architecture/ungrounded-narrative-rejection-workflow.md`
- VC7: `rg -n "rejection_reason|missing_evidence|unsupported_source|hash_mismatch" docs/architecture/ungrounded-narrative-rejection-workflow.md`
- VC8: `rg -n "log_event|alert_event|request_id|answer_id" docs/architecture/ungrounded-narrative-rejection-workflow.md`
- VC9: `rg -n "masking|access scope|retention decision|privacy_controls" docs/architecture/ungrounded-narrative-rejection-workflow.md`
- VC10: `rg -n "future_story_decision|retry queue|not implemented" docs/architecture/ungrounded-narrative-rejection-workflow.md`
- VC11: `rg -n "calculation debug|debug_boundary|astrology runtime traces" docs/architecture/ungrounded-narrative-rejection-workflow.md`
- VC12: `python -c "from app.main import app; assert 'ungrounded_narrative_rejection_workflow' not in str(app.openapi())"`
- VC13: `python -c "from app.main import app; assert all('rejection' not in getattr(r, 'path', '') for r in app.routes)"`
- VC14: `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`
- VC15: `git status --short -- backend/app frontend/src backend/tests backend/migrations`
- VC16: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/evidence/validation.txt').exists()"`
- VC17: `ruff format .`
- VC18: `ruff check .`
- VC19: `pytest -q`
- VC20: `rg -n "rejected|ungrounded|rejection_reason|reponse rejetee|message controle|retry|audit" .\docs .\_story_briefs`
- VC21: `git status --short -- backend/app frontend/src`

Before VC2, VC12, VC13 and VC16, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- Rejected ungrounded answers could be hidden from clients but also discarded, making analysis impossible.
- Raw rejected answer content could leak into client-facing payloads instead of controlled support wording.
- Rejection reasons could become unstructured text that admins cannot filter or analyze.
- Internal logs could omit answer identifiers, source hashes or correlation IDs needed for diagnosis.
- Retry could be introduced without a dedicated product and reliability decision.
- Calculation debug traces could become mixed with narrative rejection data and blur ownership boundaries.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Keep the implementation documentation-only unless a separate user decision authorizes code, DB, route, prompt, provider, retry or frontend work.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-261-add-rejection-workflow-for-ungrounded-narrative-answers.md`
- `_condamad/stories/CS-259-narrative-answer-audit-v1-contract/00-story.md`
- `_condamad/stories/CS-260-evidence-refs-contract-validation/00-story.md`
- `docs/architecture/narrative-answer-audit-v1-contract.md`
- `docs/architecture/evidence-refs-contract.md`
- `backend/app/domain/llm/runtime/observability_service.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/services/llm_generation/chat/chat_guidance_service.py`
- `_condamad/stories/regression-guardrails.md`
