# Story CS-269 add-rejected-answer-review-workflow: Add Rejected Answer Review Workflow
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-269-add-rejected-answer-review-workflow.md`.
- Related dependency: CS-261 defines rejected narrative answer handling.
- Related dependency: CS-267 defines the protected `admin_answer_audit_v1` admin API contract.
- Related dependency: CS-268 defines admin answer audit access logs.
- Related dependency: CS-288 provides persisted audit records for production reads.
- Related dependency: CS-289 provides proof validation for missing evidence analysis.
- Related dependency: CS-290 provides real rejected answer workflow data.
- Existing owner found: `backend/app/api/v1/routers/admin/audit.py` exposes protected admin audit consultation behavior.
- Existing owner found: `backend/app/services/ops/audit_service.py` records sanitized audit events.
- Existing owner found: `backend/app/infra/db/models/audit_event.py` owns the existing audit event persistence table.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: admins need a protected workflow to inspect rejected narrative answers without turning review into client delivery.
- Source-alignment evidence: PASS; ACs cover authorized admin consultation, structured reasons, review statuses, logs and client separation.

## Objective

Add one protected backend admin workflow for reviewing rejected narrative answers.

The implementation must let authorized admins list rejected answers, inspect `rejection_reason`, missing proof signals and version context,
set internal review statuses, and journalize review consultations or actions without delivering rejected content to clients or merging the
workflow with public support surfaces.

## Target State

- Authorized admins can list rejected narrative answers through the protected admin answer audit surface.
- Authorized admins can inspect one rejected answer with structured `rejection_reason`, missing proof indicators and version context.
- Internal review statuses are explicit and limited to the rejected answer review workflow.
- Review consultations and status changes are recorded through the existing audit event path.
- Client-facing routes never return rejected raw answer content.
- The workflow stays separate from public customer support, replay, prompt auto-correction and advanced annotation tools.
- The implementation reuses existing admin API, answer audit and access log ownership instead of creating parallel workflow surfaces.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-269-add-rejected-answer-review-workflow.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-269`.
- Evidence 3: `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/00-story.md` - rejection dependency read.
- Evidence 4: `_condamad/stories/CS-267-admin-answer-audit-api/00-story.md` - admin audit API dependency read.
- Evidence 5: `_condamad/stories/CS-268-answer-audit-access-logs/00-story.md` - access log dependency read.
- Evidence 6: `backend/app/api/v1/routers/admin/audit.py` - existing protected admin audit route owner found.
- Evidence 7: `backend/app/services/ops/audit_service.py` - existing sanitized audit event owner found.
- Evidence 8: `backend/app/infra/db/models/audit_event.py` - existing audit event model owner found.
- Evidence 9: targeted `rg` found existing `rejection`, `prompt_version_id` and admin audit surfaces under `backend`.
- Evidence 10: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Evidence 11: `resolve_guardrails.py` - scoped resolver run for backend API, admin review, JSON response and access-log scope.
- Repository structure alert: backend, backend app and backend tests roots exist in this workspace.
- Source-alignment evidence: PASS; no brief stake was replaced by a generic admin audit cleanup.

## Domain Boundary

- Domain: backend-api
- In scope:
  - Protected admin list workflow for rejected narrative answers.
  - Protected admin detail workflow for one rejected narrative answer.
  - Structured `rejection_reason`, missing proof indicators and version context in admin response payloads.
  - Internal review status values for rejected answer triage.
  - Audit events for review consultations and review actions through existing access logging ownership.
  - Tests using `TestClient`, `app.routes`, `app.openapi()` and DB-backed assertions for protected admin behavior.
- Out of scope:
  - Frontend UI, client API access, DB schema redesign, replay, prompt auto-correction, advanced annotation, i18n, styling and build tooling.
  - Manual delivery of a rejected answer to a client.
  - Global customer support workflow, public support ticketing and registry enrichment.
- Explicit non-goals:
  - No frontend route, screen, generated client, CSS or browser validation.
  - No public endpoint, replay endpoint, prompt mutation workflow or advanced annotation tool.
  - No manual reinjection of rejected narrative answers into client responses.
  - No new audit event table or parallel audit log store.

## Operation Contract

- Operation type: create
- Primary archetype: api-contract-change
- Archetype reason: the story adds protected admin API behavior with OpenAPI, JSON response and audit logging contracts.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the rejected answer review workflow under the protected admin answer audit boundary.
  - Reuse CS-261 rejected answer status and reason vocabulary.
  - Reuse CS-267 `admin_answer_audit_v1` route family and permission model.
  - Reuse CS-268 access log ownership through `AuditService.record_event` or one thin wrapper around it.
  - Keep frontend, public routes, replay, prompt mutation, advanced annotation, migrations and build tooling unchanged.
  - Keep rejected raw answer content internal and unavailable to client-facing routes.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks to publish rejected content, auto-correct prompts, replay answers or build an annotation UI.
- Additional validation rules:
  - The implementation must inspect existing backend owners before creating a route, service, model, builder or test helper.
  - `app.routes`, `app.openapi()`, `pytest` and `TestClient` must prove the review workflow is protected admin behavior.
  - `AST guard` or targeted `rg` must prove rejected raw content is not exposed through client routes.
  - DB-backed tests must prove review status changes and audit events persist through canonical owners.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `TestClient`, DB-backed `pytest` and `AuditService` prove runtime behavior. |
| Baseline Snapshot | yes | Before and after evidence prove the admin review delta and no client route drift. |
| Ownership Routing | yes | Admin API, rejected answer review, audit events and future persistence owners must stay separate. |
| Allowlist Exception | no | No allowlist handling is authorized for this protected admin workflow story. |
| Contract Shape | yes | The API has exact filters, fields, review statuses, permissions, errors and audit events. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Client delivery, replay, prompt mutation, annotation UI and parallel logs must stay out. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Admins can list rejected answers. | Evidence profile: json_contract_shape; `pytest -q backend/tests/api/admin/test_rejected_answer_review_workflow.py`. |
| AC2 | Admin detail shows rejection reason. | Evidence profile: json_contract_shape; `pytest` checks `rejection_reason` in detail payload. |
| AC3 | Missing proof indicators are visible. | Evidence profile: json_contract_shape; `pytest` checks missing evidence fields. |
| AC4 | Version context is visible. | Evidence profile: json_contract_shape; `pytest` checks prompt, projection and model fields. |
| AC5 | Review statuses are internal. | Evidence profile: json_contract_shape; `pytest` checks review status values. |
| AC6 | Review actions are logged. | Evidence profile: json_contract_shape; `pytest` checks persisted audit events. |
| AC7 | Public clients cannot read rejected content. | Evidence profile: route_absence_runtime; `python` checks `app.routes`; `app.openapi()` is checked. |
| AC8 | Support public surface stays separate. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks support and client route boundaries. |
| AC9 | Admin workflow remains protected. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/api/admin/test_rejected_answer_review_workflow.py`. |
| AC10 | No parallel audit store is added. | Evidence profile: no_legacy_contract; `rg` checks audit store symbols and `audit_events` reuse. |
| AC11 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-269 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-261, CS-267, CS-268 and existing admin audit owners before creating workflow code. (AC: AC1, AC10)
- [ ] Task 2: Add the protected admin list behavior for rejected narrative answers. (AC: AC1, AC9)
- [ ] Task 3: Add the protected admin detail behavior with `rejection_reason` and missing proof indicators. (AC: AC2, AC3)
- [ ] Task 4: Include prompt, projection, provider, model and audit version context in the admin detail payload. (AC: AC4)
- [ ] Task 5: Define internal review statuses and a protected status-change action. (AC: AC5, AC6)
- [ ] Task 6: Record review consultations and review actions through the existing audit event path. (AC: AC6, AC10)
- [ ] Task 7: Add guards that prevent rejected raw content from client-facing routes. (AC: AC7, AC8)
- [ ] Task 8: Add `TestClient`, `app.routes`, `app.openapi()` and DB-backed tests for the workflow. (AC: AC1, AC6, AC9)
- [ ] Task 9: Document the manual correction limits for prompt, contract and validation follow-up. (AC: AC8)
- [ ] Task 10: Persist validation, source checklist and scoped surface evidence under the CS-269 evidence folder. (AC: AC11)

## Files to Inspect First

- `_story_briefs/cs-269-add-rejected-answer-review-workflow.md` - source brief.
- `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/00-story.md` - rejection workflow dependency.
- `_condamad/stories/CS-267-admin-answer-audit-api/00-story.md` - protected admin answer audit dependency.
- `_condamad/stories/CS-268-answer-audit-access-logs/00-story.md` - access logging dependency.
- `backend/app/api/v1/routers/admin/audit.py` - existing protected admin audit route owner.
- `backend/app/api/v1/routers/admin/**` - expected protected admin namespace for answer audit routes.
- `backend/app/services/ops/audit_service.py` - canonical audit event recording owner.
- `backend/app/infra/db/models/audit_event.py` - canonical audit event persistence owner.
- `backend/tests/api/admin/**` - expected protected admin API test ownership.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output only.

## Runtime Source of Truth

- Primary source of truth:
  - Protected admin route behavior in `app.routes`, `app.openapi()` and `TestClient`.
  - Existing audit persistence through `AuditService.record_event` and `audit_events`.
  - DB-backed `pytest` assertions for list, detail, status change and audit logging.
  - Targeted `rg` or `AST guard` checks for public client exposure boundaries.
- Secondary evidence:
  - Targeted scans over backend admin answer audit files, tests and manual-limit documentation.
- Static scans alone are not sufficient because:
  - route protection, OpenAPI exposure, review status writes and audit rows must be proven from runtime behavior.

## Contract Shape

- Contract type:
  - Protected admin API workflow for rejected narrative answer review.
- Route family:
  - `GET /v1/admin/answer-audits/rejected` for filtered rejected answer list consultation.
  - `GET /v1/admin/answer-audits/rejected/{answer_id}` for one rejected answer review detail.
  - `PATCH /v1/admin/answer-audits/rejected/{answer_id}/review` for internal review status changes.
- Fields:
  - `contract_id`: exact value `admin_answer_audit_v1`.
  - `answer_id`: rejected narrative answer identifier.
  - `status`: exact rejected answer status value from CS-261.
  - `review_status`: one internal review state owned by this workflow.
  - `rejection_reason`: structured reason code from the rejected answer workflow.
  - `missing_evidence_refs`: missing or invalid proof references from CS-260 or CS-289.
  - `prompt_version`: prompt version active at generation time.
  - `projection_version`: public projection version active at generation time.
  - `provider`: LLM provider identifier.
  - `model`: LLM model identifier.
  - `created_at`: rejection creation timestamp.
  - `reviewed_at`: internal review update timestamp.
  - `reviewed_by`: authorized admin actor identifier.
  - `review_note`: bounded internal note for diagnosis.
  - `manual_correction_limits`: documented limits for prompts, contracts and validation follow-up.
  - `audit_event`: access or action event written through canonical audit logging.
- Required fields:
  - `contract_id`
  - `answer_id`
  - `status`
  - `review_status`
  - `rejection_reason`
  - `missing_evidence_refs`
  - `prompt_version`
  - `projection_version`
  - `provider`
  - `model`
  - `created_at`
- Optional fields:
  - `reviewed_at`
  - `reviewed_by`
  - `review_note`
  - `manual_correction_limits`
- Status codes:
  - `200` for successful protected admin list or detail consultation.
  - `204` for successful protected review status update without response body.
  - `400` for invalid review status transition.
  - `401` when authentication is missing.
  - `403` when the authenticated user is not admin.
  - `404` when the rejected answer audit record is not found.
  - `503` when the backing audit store is unavailable.
- Serialization names:
  - JSON keys use the exact snake_case names listed in this contract.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must expose only protected `/v1/admin/answer-audits/rejected` paths for this workflow.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-269-add-rejected-answer-review-workflow.md`
  - `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/00-story.md`
  - `_condamad/stories/CS-267-admin-answer-audit-api/00-story.md`
  - `_condamad/stories/CS-268-answer-audit-access-logs/00-story.md`
  - `backend/app/api/v1/routers/admin/audit.py`
  - `backend/app/services/ops/audit_service.py`
  - `backend/app/infra/db/models/audit_event.py`
- Comparison after implementation:
  - `backend/app/api/v1/routers/admin/**`
  - `backend/app/services/**`
  - `backend/tests/api/admin/test_rejected_answer_review_workflow.py`
  - `docs/architecture/rejected-answer-review-workflow-limits.md`
  - `_condamad/stories/CS-269-add-rejected-answer-review-workflow/evidence/validation.txt`
  - `_condamad/stories/CS-269-add-rejected-answer-review-workflow/evidence/app-surface-status.txt`
- Expected invariant:
  - The only intended runtime delta is protected admin review of already rejected narrative answers.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Admin rejected answer review routes | `backend/app/api/v1/routers/admin/**` | public routers or frontend |
| Answer audit contract fields | `admin_answer_audit_v1` owners from CS-267 | duplicate DTO taxonomy |
| Rejected answer semantics | CS-261 rejected workflow owners | support or client delivery code |
| Review status behavior | backend admin answer audit service layer | route-local unstructured mutation |
| Audit event persistence | `backend/app/services/ops/audit_service.py` | new parallel log service |
| Audit event storage | `backend/app/infra/db/models/audit_event.py` | new access log table |
| Manual correction limits | `docs/architecture/rejected-answer-review-workflow-limits.md` | prompt code comments only |
| Evidence artifacts | `_condamad/stories/CS-269-add-rejected-answer-review-workflow/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse CS-261 rejected answer status and `rejection_reason` vocabulary.
- Reuse CS-267 admin answer audit route family, auth behavior, masking rules and response field names.
- Reuse CS-268 audit event action patterns and `AuditService.record_event` ownership.
- Reuse existing admin route dependency patterns instead of creating a second admin auth gate.
- Keep one review status model or enum for this workflow.
- Do not add external packages, duplicate audit stores, duplicate rejected reason taxonomies or public support workflow code.

## No Legacy / Forbidden Paths

- No legacy public route path may be added for rejected answer review.
- No compatibility route path may be added for rejected answer review.
- No fallback route path may be added for rejected answer review.
- No client endpoint may expose rejected raw answer content.
- No replay endpoint, prompt auto-correction job, advanced annotation tool, frontend UI or generated client is authorized by this story.
- No new audit event table, parallel access log service or route-local raw sensitive detail persistence is authorized.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/v1/routers/public/**`
  - generated OpenAPI clients
  - replay jobs
  - prompt mutation services
  - public customer support modules

## Reintroduction Guard

- Forbidden route paths:
  - `/v1/answer-audits/rejected`
  - `/v1/users/me/answer-audits/rejected`
  - `/v1/admin/answer-audit-replay`
  - `/v1/support/rejected-answers`
- Forbidden workflow symbols:
  - `RejectedAnswerReplay`
  - `AnswerAuditAccessLogModel`
  - `admin_rejected_answer_public`
  - `auto_correct_rejected_prompt`
- Forbidden client exposure:
  - rejected raw answer content in public or client response serializers.
- Required guards:
  - `pytest -q backend/tests/api/admin/test_rejected_answer_review_workflow.py` proves protected behavior.
  - `python` checks `app.routes` and `app.openapi()` for forbidden public paths.
  - `AST guard` or `rg` checks rejected raw content is not serialized to client routes.
  - `rg` checks no parallel audit store or replay symbol was introduced.

## Regression Guardrails

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `Routeurs API v1` | Review routes stay under canonical API v1 admin ownership. | `app.routes`; targeted `pytest`. |
| RG-003 `Architecture des routes API v1` | Public and client routers do not own rejected answer review. | `app.openapi()`; route `rg`. |
| RG-007 `Endpoints admin LLM observability` | LLM answer review remains protected admin behavior. | `TestClient`; OpenAPI check. |
| RG-022 `Plans de validation des stories prompt-generation` | Backend tests cover prompt and provider audit terms. | `pytest`; targeted `rg`. |
| Registry gap | No exact rejected answer review workflow guardrail exists in resolver output. | Story-local guards. |
| Non-applicable example | RG-047 frontend inline style guardrail is out of scope. | No frontend source edits. |
| Non-applicable example | RG-052 CSS namespace guardrail is out of scope. | No CSS or build edits. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation output | `_condamad/stories/CS-269-add-rejected-answer-review-workflow/evidence/validation.txt` | Keep validation transcript. |
| Application surface status | `_condamad/stories/CS-269-add-rejected-answer-review-workflow/evidence/app-surface-status.txt` | Prove scoped app changes. |
| Source checklist | `_condamad/stories/CS-269-add-rejected-answer-review-workflow/evidence/source-checklist.md` | Record source coverage. |
| Client exposure scan | `_condamad/stories/CS-269-add-rejected-answer-review-workflow/evidence/client-exposure-scan.txt` | Prove no client delivery. |
| Review output | `_condamad/stories/CS-269-add-rejected-answer-review-workflow/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this protected admin workflow story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/api/v1/routers/admin/**` - add protected rejected answer review endpoints.
- `backend/app/services/**` - add or extend the admin answer audit service workflow.
- `docs/architecture/rejected-answer-review-workflow-limits.md` - document manual correction limits.
- `_condamad/stories/CS-269-add-rejected-answer-review-workflow/evidence/validation.txt` - persist validation output.
- `_condamad/stories/CS-269-add-rejected-answer-review-workflow/evidence/app-surface-status.txt` - persist scoped status output.
- `_condamad/stories/CS-269-add-rejected-answer-review-workflow/evidence/source-checklist.md` - persist source coverage.
- `_condamad/stories/CS-269-add-rejected-answer-review-workflow/evidence/client-exposure-scan.txt` - persist client exposure scan.

Likely tests:

- `backend/tests/api/admin/test_rejected_answer_review_workflow.py` - `TestClient`, DB assertions, `app.routes` and `app.openapi()` checks.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/v1/routers/public/**` - out of scope; no client route is touched.
- `backend/migrations/**` - out of scope unless CS-288 implementation proves a user-approved schema gap.
- `backend/app/infra/db/models/**` - out of scope unless existing audit and answer audit persistence cannot store required fields.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `pytest -q backend/tests/api/admin/test_rejected_answer_review_workflow.py`
- VC2: `python -c "from app.main import app; assert any('/v1/admin/answer-audits/rejected' in getattr(r, 'path', '') for r in app.routes)"`
- VC3: `python -c "from app.main import app; assert '/v1/users/me/answer-audits/rejected' not in str(app.openapi())"`
- VC4: `python -c "from app.main import app; assert '/v1/support/rejected-answers' not in str(app.openapi())"`
- VC5: `rg -n "rejection_reason|missing_evidence_refs|review_status|prompt_version|projection_version" backend/app backend/tests`
- VC6: `rg -n "admin_rejected_answer_reviewed|admin_rejected_answer_review_accessed" backend/app backend/tests`
- VC7: `rg -n "RejectedAnswerReplay|auto_correct_rejected_prompt|admin_rejected_answer_public" backend/app backend/tests`
- VC8: `rg -n "manual correction|prompt|contract|validation" docs/architecture/rejected-answer-review-workflow-limits.md`
- VC9: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-269-add-rejected-answer-review-workflow/evidence/validation.txt').exists()"`
- VC10: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-269-add-rejected-answer-review-workflow/evidence/client-exposure-scan.txt').exists()"`
- VC11: `git status --short -- backend/app backend/tests docs/architecture frontend/src`
- VC12: `ruff format .`
- VC13: `ruff check .`
- VC14: `pytest -q`

Before VC1 through VC14, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- A rejected answer review endpoint could expose raw content through a public or client route.
- Internal review status could become a customer support status and blur public workflow boundaries.
- Review action logging could bypass the existing audit event path and create a second audit source.
- Missing proof indicators could be hidden, preventing prompt, contract or validation diagnosis.
- Manual correction limits could be softened into prompt mutation, replay or advanced annotation work.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Inspect existing owners before creating any new route, builder, service, model or test helper.
- Keep all new or significantly modified application files documented with a French top-level comment or docstring.
- Keep rejected answer review under protected admin routes and away from public support or client response surfaces.
- Persist validation output under the CS-269 evidence folder before requesting review.

## References

- `_story_briefs/cs-269-add-rejected-answer-review-workflow.md`
- `_condamad/stories/CS-261-add-rejection-workflow-for-ungrounded-narrative-answers/00-story.md`
- `_condamad/stories/CS-267-admin-answer-audit-api/00-story.md`
- `_condamad/stories/CS-268-answer-audit-access-logs/00-story.md`
- `backend/app/api/v1/routers/admin/audit.py`
- `backend/app/services/ops/audit_service.py`
- `backend/app/infra/db/models/audit_event.py`
- `_condamad/stories/regression-guardrails.md`
