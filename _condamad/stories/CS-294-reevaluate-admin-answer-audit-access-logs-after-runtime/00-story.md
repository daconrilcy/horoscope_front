# Story CS-294 reevaluate-admin-answer-audit-access-logs-after-runtime: Reevaluate Admin Answer Audit Access Logs After Runtime
Status: ready-to-dev

## Trigger / Source

- Source type: audit-to-story with repository-informed boundary.
- Source reference: `_story_briefs/cs-294-reevaluate-admin-answer-audit-access-logs-after-runtime.md`.
- Related dependency: CS-267 defines the protected `admin_answer_audit_v1` admin API contract.
- Related dependency: CS-268 is the access-log story that must be rechecked after runtime became available.
- Related dependency: CS-288 provides persistence for narrative answer audit evidence.
- Related dependency: CS-290 provides the rejected answer workflow runtime and admin review routes.
- Existing owner found: `backend/app/api/v1/routers/admin/answer_audit.py` exposes the rejected answer audit admin routes.
- Existing owner found: `backend/app/services/ops/rejected_answer_review.py` logs list, detail and review status activity via `AuditService`.
- Existing test owner found: `backend/tests/api/admin/test_rejected_answer_review_workflow.py` covers protected runtime routes.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: CS-268 needs current runtime proof that admin answer audit consultations are logged without sensitive data leakage.
- Source-alignment evidence: PASS; ACs cover runtime inventory, audit events, sensitive fields, 401/403 decision and CS-268 closure evidence.

## Objective

Reevaluate and complete the CS-268 access-log evidence against the current rejected answer audit runtime.

The implementation must prove which `admin_answer_audit_v1` admin consultations are covered, decide the `401/403` logging policy,
close CS-268 with final evidence, or write a bounded follow-up story only for a concrete remaining gap.

## Target State

- Runtime routes for `/v1/admin/answer-audits/rejected` are inventoried from `app.routes` and `app.openapi()`.
- Successful list, detail and review status activity have deterministic audit event evidence through the existing `AuditService` path.
- Audit events include `actor_user_id`, `target_id`, `action`, `status`, timestamp and `contract_id` for every covered successful activity.
- Audit event details exclude `raw_rejected_answer`, full prompts, secrets, raw birth data and raw rejected answer payloads.
- The expected behavior for `401/403` refusals is explicitly documented and backed by tests or bounded security rationale.
- CS-268 receives a final evidence capsule that no longer depends on the historical CS-288 blocker.
- No second audit store, client surface, support surface, replay surface or raw sensitive log payload is introduced.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-294-reevaluate-admin-answer-audit-access-logs-after-runtime.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-294`.
- Evidence 3: `_condamad/stories/CS-268-answer-audit-access-logs/00-story.md` - blocked access-log contract to reevaluate.
- Evidence 4: `_condamad/stories/CS-267-admin-answer-audit-api/00-story.md` - upstream admin answer audit contract read.
- Evidence 5: `_condamad/stories/CS-290-rejected-narrative-answer-workflow/00-story.md` - runtime dependency read.
- Evidence 6: `backend/app/api/v1/routers/admin/answer_audit.py` - current route owner inspected.
- Evidence 7: `backend/app/services/ops/rejected_answer_review.py` - current `AuditService` logging owner inspected.
- Evidence 8: `backend/tests/api/admin/test_rejected_answer_review_workflow.py` - runtime `TestClient` coverage inspected.
- Evidence 9: `backend/tests/unit/test_sensitive_data_non_leakage.py` - audit sanitization coverage inspected.
- Evidence 10: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Evidence 11: `resolve_guardrails.py` - scoped resolver run for backend API, admin answer audit, audit-log and sensitive-data scope.
- Repository structure alert: backend, backend app and backend tests roots exist in this workspace.
- Source-alignment evidence: PASS; no brief stake was narrowed to documentation-only, API-only or generic cleanup work.

## Domain Boundary

- Domain: backend-api
- In scope:
  - Runtime inventory of current admin `answer-audits` routes.
  - Audit event proof for rejected answer list, detail and review status activity.
  - Verification of `actor_user_id`, `target_id`, `action`, `status`, timestamp and `contract_id`.
  - Sensitive detail non-leakage tests for raw rejected answers, prompts, secrets and raw birth data.
  - Explicit `401/403` logging decision for the protected admin answer audit workflow.
  - Final CS-268 evidence capsule or one bounded follow-up story for a remaining uncovered gap.
- Out of scope:
  - Frontend UI, client API, support API, replay, DB schema, migrations, auth redesign, i18n, styling and build tooling.
  - Creating a second audit store or changing the canonical `AuditService` persistence path.
  - Implementing `replay_snapshot_v1`.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No support, client or replay surface for rejected answer audits.
  - No raw prompt, secret, raw birth data, full rejected answer or `raw_rejected_answer` value in audit event details.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits this backend runtime evidence and closure story.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Reuse the current `answer_audit.py` route owner and `RejectedAnswerReviewService` before adding any helper.
  - Add only tests, evidence artifacts, documentation and minimal runtime changes required by a proven audit-log gap.
  - Keep `AuditService` as the single audit event persistence path.
  - Keep frontend, client routes, support routes, replay, DB migrations, auth redesign, i18n, style and build tooling unchanged.
  - Keep audit event details minimal and sanitized.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product wants denied unauthenticated probes logged without a stable authenticated actor identity.
- Additional validation rules:
  - The runtime route inventory must name `app.routes` and `app.openapi()` evidence.
  - `TestClient` tests must prove successful list, detail and review status behavior through HTTP.
  - `pytest` or an `AST guard` must prove forbidden sensitive fields are not persisted in access log details.
  - The final evidence must state whether CS-268 is fully closed or name the exact remaining bounded follow-up.
  - A follow-up story may be created only when runtime evidence proves a concrete uncovered gap.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `TestClient`, DB-backed `pytest` and `AuditService` prove runtime behavior. |
| Baseline Snapshot | yes | Before and after evidence proves CS-268 closure no longer depends on the historic CS-288 blocker. |
| Ownership Routing | yes | Existing admin route, rejected review service and audit service owners must be reused. |
| Allowlist Exception | no | No allowlist handling is authorized for this reevaluation story. |
| Contract Shape | yes | Audit events have exact actor, target, action, status, timestamp and contract fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Raw sensitive fields, client routes and parallel audit stores must stay absent. |
| Persistent Evidence | yes | CS-268 and CS-294 evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Runtime admin routes are inventoried. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`. |
| AC2 | List consultation access is logged. | Evidence profile: json_contract_shape; `pytest -q backend/tests/api/admin/test_rejected_answer_review_workflow.py`. |
| AC3 | Detail consultation access is logged. | Evidence profile: json_contract_shape; `pytest -q backend/tests/api/admin/test_rejected_answer_review_workflow.py`. |
| AC4 | Review status activity is logged. | Evidence profile: json_contract_shape; `pytest -q backend/tests/api/admin/test_rejected_answer_review_workflow.py`. |
| AC5 | Audit event identity fields are complete. | Evidence profile: json_contract_shape; `pytest` checks actor_user_id, target_id, action, status and timestamp. |
| AC6 | Audit event contract id is complete. | Evidence profile: json_contract_shape; `pytest` checks details.contract_id. |
| AC7 | Sensitive audit details stay out. | Evidence profile: targeted_forbidden_symbol_scan; `pytest` and `AST guard` check forbidden detail fields. |
| AC8 | Access refusal policy is decided. | Evidence profile: api_error_shape_contract; `pytest` checks 401/403 and `rg` checks documented decision. |
| AC9 | CS-268 final evidence is current. | Evidence profile: baseline_before_after_diff; `python` checks CS-268 final evidence artifact paths. |
| AC10 | No parallel audit store is added. | Evidence profile: no_legacy_contract; `rg` checks parallel store symbols in backend paths. |
| AC11 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-294 evidence artifact paths. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-268, CS-267, CS-290, route owner, review service and current tests before editing. (AC: AC1, AC10)
- [ ] Task 2: Produce a runtime route inventory with `app.routes` and `app.openapi()` for admin answer audit routes. (AC: AC1)
- [ ] Task 3: Extend `TestClient` coverage for list consultation audit events. (AC: AC2, AC5, AC6)
- [ ] Task 4: Extend `TestClient` coverage for detail consultation audit events. (AC: AC3, AC5, AC6)
- [ ] Task 5: Extend `TestClient` coverage for review status audit events. (AC: AC4, AC5, AC6)
- [ ] Task 6: Add sensitive-detail assertions for raw rejected answers, prompts, secrets and raw birth data. (AC: AC7)
- [ ] Task 7: Decide and document the `401/403` logging policy with security rationale and tests. (AC: AC8)
- [ ] Task 8: Add a bounded guard against parallel audit stores or client/support/replay route drift. (AC: AC1, AC10)
- [ ] Task 9: Persist CS-268 final evidence showing closure status after current runtime checks. (AC: AC9)
- [ ] Task 10: Create one bounded follow-up story only when evidence proves an uncovered CS-268 gap. (AC: AC9)
- [ ] Task 11: Persist CS-294 validation transcript, route inventory and sensitive scan artifacts. (AC: AC11)

## Files to Inspect First

- `_story_briefs/cs-294-reevaluate-admin-answer-audit-access-logs-after-runtime.md` - source brief.
- `_condamad/stories/CS-268-answer-audit-access-logs/00-story.md` - access-log contract to reevaluate.
- `_condamad/stories/CS-267-admin-answer-audit-api/00-story.md` - protected admin API contract.
- `_condamad/stories/CS-290-rejected-narrative-answer-workflow/00-story.md` - rejected answer runtime dependency.
- `backend/app/api/v1/routers/admin/answer_audit.py` - route owner for current admin answer audit runtime.
- `backend/app/services/ops/rejected_answer_review.py` - current audit logging service owner.
- `backend/tests/api/admin/test_rejected_answer_review_workflow.py` - current runtime `TestClient` suite.
- `backend/tests/unit/test_sensitive_data_non_leakage.py` - existing audit sanitization suite.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output only.

## Runtime Source of Truth

- Primary source of truth:
  - `app.routes`, `app.openapi()`, `TestClient`, DB-backed `pytest`, `AuditService` and `audit_events`.
- Secondary evidence:
  - Targeted `rg` scans for unauthorized route paths, parallel audit store symbols and forbidden sensitive detail fields.
- Static scans alone are not sufficient because:
  - route registration, OpenAPI exposure, HTTP protection and persisted audit events must be proven from loaded runtime behavior.

## Contract Shape

- Contract type:
  - Backend admin access-log reevaluation for current `admin_answer_audit_v1` rejected answer runtime.
- Covered route family:
  - `GET /v1/admin/answer-audits/rejected`
  - `GET /v1/admin/answer-audits/rejected/{answer_id}`
  - `PATCH /v1/admin/answer-audits/rejected/{answer_id}/review`
- Event actions:
  - `admin_rejected_answer_review_accessed` for list and detail consultation.
  - `admin_rejected_answer_reviewed` for review status changes.
- Fields:
  - `actor_user_id`: authenticated admin user identifier.
  - `target_id`: requested answer identifier or null for list consultation.
  - `action`: stable event action.
  - `status`: exact value `success` for successful covered activity.
  - `created_at`: audit event timestamp from `audit_events`.
  - `details.contract_id`: exact value `admin_answer_audit_v1`.
  - `details.consultation`: exact value `list` for list consultation.
  - `details.review_status`: bounded review status metadata.
- Required fields:
  - `actor_user_id`
  - `action`
  - `status`
  - `created_at`
  - `details.contract_id`
- Optional fields:
  - `target_id` for list consultation.
  - `details.consultation`
  - `details.review_status`
- Status codes:
  - Existing route status codes remain unchanged.
  - `401` for missing authentication stays protected by current auth dependency.
  - `403` for non-admin authenticated user stays protected by current auth dependency.
- Serialization names:
  - Audit detail keys use exact snake_case names from this contract.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must expose only the protected admin answer audit route family.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-294-reevaluate-admin-answer-audit-access-logs-after-runtime.md`
  - `_condamad/stories/CS-268-answer-audit-access-logs/00-story.md`
  - `backend/app/api/v1/routers/admin/answer_audit.py`
  - `backend/app/services/ops/rejected_answer_review.py`
  - `backend/tests/api/admin/test_rejected_answer_review_workflow.py`
- Comparison after implementation:
  - `_condamad/stories/CS-268-answer-audit-access-logs/evidence/final-runtime-closure.md`
  - `_condamad/stories/CS-294-reevaluate-admin-answer-audit-access-logs-after-runtime/evidence/route-inventory.txt`
  - `_condamad/stories/CS-294-reevaluate-admin-answer-audit-access-logs-after-runtime/evidence/validation.txt`
  - `_condamad/stories/CS-294-reevaluate-admin-answer-audit-access-logs-after-runtime/evidence/sensitive-detail-scan.txt`
- Expected invariant:
  - The only intended runtime delta is closing proven audit-log gaps for current admin rejected answer audit activity.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Admin answer audit routes | `backend/app/api/v1/routers/admin/answer_audit.py` | public, support or frontend routes |
| Rejected answer review behavior | `backend/app/services/ops/rejected_answer_review.py` | route-local duplicate logic |
| Audit event persistence | `backend/app/services/ops/audit_service.py` | new access log store |
| Audit event storage | `backend/app/infra/db/models/audit_event.py` | new access log table |
| Runtime tests | `backend/tests/api/admin/test_rejected_answer_review_workflow.py` | unrelated test suites |
| Sensitive data policy tests | `backend/tests/unit/test_sensitive_data_non_leakage.py` | route-local masking only |
| Final CS-268 closure evidence | `_condamad/stories/CS-268-answer-audit-access-logs/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse `backend/app/api/v1/routers/admin/answer_audit.py` for admin route behavior.
- Reuse `RejectedAnswerReviewService` for rejected answer review operations.
- Reuse `AuditService.record_event` and the existing `audit_events` store for all access event persistence.
- Reuse the existing `TestClient` suite before creating a separate admin answer audit test family.
- Reuse existing sensitive-data sanitization policy tests for forbidden audit details.
- Do not add external packages, duplicate services, duplicate stores, duplicate route families or parallel sensitive-data masking logic.

## No Legacy / Forbidden Paths

- No legacy route path may be added for this endpoint family.
- No compatibility route path may be added for this endpoint family.
- No fallback route path may be added for this endpoint family.
- No public, client, support or replay route may expose rejected answer audit access logs.
- No new access log table, repository, model, frontend UI or generated client is authorized by this story.
- No raw prompt, secret, raw birth data, full rejected answer or `raw_rejected_answer` value may be stored in event details.

## Reintroduction Guard

- Forbidden route paths:
  - `/v1/answer-audits/rejected`
  - `/v1/users/me/answer-audits/rejected`
  - `/v1/support/rejected-answers`
  - `/v1/admin/answer-audit-replay`
- Forbidden persistence symbols:
  - `AnswerAuditAccessLogModel`
  - `admin_answer_audit_access_logs`
  - `answer_audit_access_log_repository`
- Forbidden detail fields:
  - `raw_rejected_answer`
  - `prompt`
  - `secret`
  - `birth_date`
  - `birth_time`
  - `birth_place`
  - `birth_lat`
  - `birth_lon`
  - `birth_timezone`
- Required guards:
  - `pytest -q backend/tests/api/admin/test_rejected_answer_review_workflow.py` proves access event behavior.
  - `pytest -q backend/tests/unit/test_sensitive_data_non_leakage.py` proves canonical audit sanitization.
  - `python` checks `app.routes` and `app.openapi()` for protected admin-only route exposure.
  - `AST guard` or targeted `rg` over runtime owners proves forbidden detail fields are not passed to access log event details.

## Regression Guardrails

Scope vector:

- backend-api admin answer audit runtime: yes;
- `AuditService` access-log evidence: yes;
- `app.routes`, `app.openapi()` and `TestClient`: yes;
- sensitive audit details: yes;
- frontend, DB migration, auth redesign, i18n, style and build: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | Backend route behavior stays under canonical API v1 paths. | `app.routes`; targeted `pytest`. |
| RG-003 | Public and client routers do not own admin answer audit surfaces. | `app.openapi()`; route `rg`. |
| RG-007 | LLM observability endpoints remain protected admin behavior. | `TestClient`; OpenAPI check. |
| RG-022 | Backend prompt/audit validation paths stay executable. | `pytest`; persisted validation. |
| Registry gap | No exact `admin_answer_audit_v1` access-log guardrail exists in resolver output. | Story-local closure guards. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because this story targets admin answer audit access logs.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| CS-268 final closure | `_condamad/stories/CS-268-answer-audit-access-logs/evidence/final-runtime-closure.md` | Record final runtime reevaluation. |
| Route inventory | `_condamad/stories/CS-294-reevaluate-admin-answer-audit-access-logs-after-runtime/evidence/route-inventory.txt` | Prove route scope. |
| Validation output | `_condamad/stories/CS-294-reevaluate-admin-answer-audit-access-logs-after-runtime/evidence/validation.txt` | Keep validation transcript. |
| Sensitive detail scan | `_condamad/stories/CS-294-reevaluate-admin-answer-audit-access-logs-after-runtime/evidence/sensitive-detail-scan.txt` | Prove no leakage. |
| Source checklist | `_condamad/stories/CS-294-reevaluate-admin-answer-audit-access-logs-after-runtime/evidence/source-checklist.md` | Record source coverage. |
| Review output | `_condamad/stories/CS-294-reevaluate-admin-answer-audit-access-logs-after-runtime/generated/11-code-review.md` | Review handoff. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this reevaluation story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/tests/api/admin/test_rejected_answer_review_workflow.py` - extend runtime access-log and refusal-policy coverage.
- `backend/tests/unit/test_sensitive_data_non_leakage.py` - extend canonical audit sanitization coverage for forbidden details.
- `backend/app/services/ops/rejected_answer_review.py` - minimal change only for a proven logging gap.
- `_condamad/stories/CS-268-answer-audit-access-logs/evidence/final-runtime-closure.md` - persist final CS-268 closure evidence.
- `_condamad/stories/CS-294-reevaluate-admin-answer-audit-access-logs-after-runtime/evidence/route-inventory.txt` - route inventory.
- `_condamad/stories/CS-294-reevaluate-admin-answer-audit-access-logs-after-runtime/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-294-reevaluate-admin-answer-audit-access-logs-after-runtime/evidence/sensitive-detail-scan.txt` - sensitive scan.
- `_condamad/stories/CS-294-reevaluate-admin-answer-audit-access-logs-after-runtime/evidence/source-checklist.md` - source coverage.

Likely tests:

- `backend/tests/api/admin/test_rejected_answer_review_workflow.py` - `TestClient`, DB assertions, `app.routes` and `app.openapi()` checks.
- `backend/tests/unit/test_sensitive_data_non_leakage.py` - `AuditService` sanitization and forbidden detail checks.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no persistence schema is created.
- `backend/app/api/v1/routers/public/**` - out of scope; no client route is touched.
- `backend/app/api/v1/routers/support/**` - out of scope; no support route is touched.
- Generated OpenAPI clients - out of scope; no client contract is generated.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `. .\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff check .`
- VC4: `pytest -q tests/api/admin/test_rejected_answer_review_workflow.py tests/unit/test_sensitive_data_non_leakage.py --tb=short`
- VC5: `python -B -c "from app.main import app; paths={getattr(r,'path','') for r in app.routes}; assert '/v1/admin/answer-audits/rejected' in paths"`
- VC6: `python -B -c "from app.main import app; assert '/v1/admin/answer-audits/rejected/{answer_id}' in {getattr(r,'path','') for r in app.routes}"`
- VC7: `python -B -c "from app.main import app; assert '/v1/admin/answer-audit-replay' not in str(app.openapi())"`
- VC8: `rg -n "admin_rejected_answer_review_accessed|admin_rejected_answer_reviewed" app tests`
- VC9: `rg -n "AnswerAuditAccessLogModel|admin_answer_audit_access_logs|answer_audit_access_log_repository" app tests`
- VC10: `rg -n "raw_rejected_answer|prompt|secret|birth_" app/services/ops/rejected_answer_review.py app/api/v1/routers/admin/answer_audit.py`
- VC11: `python -B -c "from pathlib import Path; assert Path('../_condamad/stories/CS-268-answer-audit-access-logs/evidence/final-runtime-closure.md').exists()"`
- VC12: `python -B -c "import os; assert os.path.exists('../_condamad/stories/CS-294-reevaluate-admin-answer-audit-access-logs-after-runtime/evidence')"`
- VC13: `python -B -c "import os; assert os.path.exists('../_condamad/stories/CS-294-reevaluate-admin-answer-audit-access-logs-after-runtime/evidence/validation.txt')"`
- VC14: `python -B -c "import os; assert os.path.exists('../_condamad/stories/CS-294-reevaluate-admin-answer-audit-access-logs-after-runtime/evidence/sensitive-detail-scan.txt')"`
- VC15: `pytest -q`

Before VC3 through VC15, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- CS-268 could be closed on detail consultation only while list or review status activity remains unproven.
- Denied `401/403` behavior could remain implicit and leave security expectations ambiguous.
- Audit details could leak raw rejected answer content through route-local metadata.
- A parallel audit store could bypass existing `AuditService` sanitization and fragment review evidence.
- The follow-up path could become broad instead of naming one concrete uncovered CS-268 gap.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Start by proving whether the current runtime already covers each CS-268 acceptance criterion.
- Reuse existing route, service, audit store and tests before adding any new owner.
- Keep all new or significantly modified application files documented with a French top-level comment or docstring.
- Persist CS-268 closure evidence and CS-294 validation artifacts before requesting review.

## References

- `_story_briefs/cs-294-reevaluate-admin-answer-audit-access-logs-after-runtime.md`
- `_condamad/stories/CS-268-answer-audit-access-logs/00-story.md`
- `_condamad/stories/CS-267-admin-answer-audit-api/00-story.md`
- `_condamad/stories/CS-290-rejected-narrative-answer-workflow/00-story.md`
- `backend/app/api/v1/routers/admin/answer_audit.py`
- `backend/app/services/ops/rejected_answer_review.py`
- `backend/tests/api/admin/test_rejected_answer_review_workflow.py`
- `backend/tests/unit/test_sensitive_data_non_leakage.py`
- `_condamad/stories/regression-guardrails.md`
