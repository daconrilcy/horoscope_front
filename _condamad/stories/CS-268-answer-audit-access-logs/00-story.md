# Story CS-268 answer-audit-access-logs: Add Admin Answer Audit Access Logs
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-268-add-admin-answer-audit-access-logs.md`.
- Related dependency: CS-267 defines the protected `admin_answer_audit_v1` admin API contract.
- Related dependency: CS-288 provides real persisted answer audit data for full production reads.
- Existing owner found: `backend/app/api/v1/routers/admin/audit.py` exposes admin audit consultation and export.
- Existing owner found: `backend/app/services/ops/audit_service.py` records audit events through `AuditService.record_event`.
- Existing owner found: `backend/app/infra/db/models/audit_event.py` owns the `audit_events` persistence model.
- Existing test owner found: `backend/app/tests/integration/test_admin_logs_api.py` covers admin audit read and export behavior.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: admin consultations of sensitive answer audit data need a systematic access event without leaking sensitive payload data.
- Source-alignment evidence: PASS; ACs cover systematic logging, refusal paths, sanitization, logging failure behavior and retention note.

## Objective

Add backend audit access logging for every protected admin consultation of `admin_answer_audit_v1`.

The implementation must record who accessed which answer audit object, at what time, for which action and with what justification value was
available, while keeping prompts, proof payloads, secrets and raw birth data out of persisted audit log details.

## Target State

- Every successful protected admin read of `admin_answer_audit_v1` records one access event in the existing audit event store.
- Every denied admin answer audit consultation records a failed access event when an authenticated admin identity is available.
- The access event captures admin identity, timestamp from the existing audit model, target object, action, status and safe justification.
- Access log details are sanitized through the existing audit service and do not store raw prompt text, proof payloads, secrets or raw birth data.
- Logging failure handling is explicit and does not expose sensitive diagnostic data in the API response.
- Retention expectations are documented as dependent on the final RGPD policy decision.
- No frontend UI, client exposure, replay feature, new audit store or global back-office logging program is created by this story.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-268-add-admin-answer-audit-access-logs.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-268`.
- Evidence 3: `_condamad/stories/CS-267-admin-answer-audit-api/00-story.md` - upstream admin answer audit API contract read.
- Evidence 4: `backend/app/api/v1/routers/admin/audit.py` - existing admin audit route owner inspected.
- Evidence 5: `backend/app/services/ops/audit_service.py` - existing audit recording service inspected.
- Evidence 6: `backend/app/infra/db/models/audit_event.py` - existing `audit_events` persistence model inspected.
- Evidence 7: `backend/app/tests/integration/test_admin_logs_api.py` - existing admin audit integration tests inspected.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Evidence 9: `resolve_guardrails.py` - scoped resolver run for backend API, admin access logging and JSON response scope.
- Repository structure alert: backend, backend app and backend tests roots exist in this workspace.
- Source-alignment evidence: PASS; no brief stake was narrowed into a generic documentation task.

## Domain Boundary

- Domain: backend-api
- In scope:
  - Backend access logging for protected admin consultations of `admin_answer_audit_v1`.
  - Reuse or extension of the existing `AuditService.record_event` audit event path.
  - Safe event details for admin, action, target answer audit object, status and justification.
  - Tests for successful consultation, denied consultation, data masking and logging failure behavior.
  - Documentation of retention uncertainty while RGPD policy remains undecided.
- Out of scope:
  - Frontend UI, client API access, DB schema redesign, migrations, replay, i18n, styling, build tooling and global admin logging.
  - Exposing audit access logs to clients or adding a new public read surface.
  - Implementing the final RGPD retention policy decision.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No new audit event table, parallel log store, replay endpoint, global back-office audit sweep or client-facing log API.
  - No storage of raw prompts, proof payloads, secrets, birth date, birth time, birth place, coordinates or timezone in access log details.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend admin access logging contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add access logging only for `admin_answer_audit_v1` admin consultation behavior.
  - Reuse existing admin authentication, request id and audit event service patterns.
  - Reuse existing `audit_events` persistence unless implementation proves a user-approved blocker.
  - Keep frontend, client endpoints, replay, global admin logs, migrations and build tooling unchanged.
  - Keep log details minimal and sanitized before persistence.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product asks for final RGPD retention duration or client-visible access logs.
- Additional validation rules:
  - The implementation must inspect existing backend owners before creating a new route, service, model, builder or test helper.
  - The access action name must be stable and specific to `admin_answer_audit_v1` consultation.
  - `AuditService.record_event` or a single wrapper around it must own persistence of access events.
  - `app.routes`, `app.openapi()`, `pytest` and `TestClient` prove admin API behavior stays protected.
  - `AST guard` or targeted `rg` must prove raw prompt, proof payload and birth data fields are not persisted in details.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `TestClient` and DB-backed `pytest` prove protected admin read behavior. |
| Baseline Snapshot | yes | Before and after evidence prove the access log delta and no client surface drift. |
| Ownership Routing | yes | Existing admin audit service, route and model owners must be reused instead of parallel logging. |
| Allowlist Exception | no | No allowlist handling is authorized for this access logging story. |
| Contract Shape | yes | The access event has exact action, target, status and safe detail fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Raw sensitive fields and alternate log stores must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Successful admin consultation records access. | Evidence profile: json_contract_shape; `pytest -q backend/tests/api/admin/test_answer_audit_access_logs.py`. |
| AC2 | Denied consultation records failed access. | Evidence profile: api_error_shape_contract; `pytest -q backend/tests/api/admin/test_answer_audit_access_logs.py`. |
| AC3 | Access event fields are stable. | Evidence profile: json_contract_shape; `pytest` checks action, target_type, target_id and status. |
| AC4 | Justification is captured safely. | Evidence profile: json_contract_shape; `pytest` checks sanitized details for justification. |
| AC5 | Sensitive data is not persisted. | Evidence profile: targeted_forbidden_symbol_scan; `rg` and `AST guard` check forbidden detail fields. |
| AC6 | Logging failure is handled. | Evidence profile: api_error_shape_contract; `pytest -q backend/tests/api/admin/test_answer_audit_access_logs.py`. |
| AC7 | Admin API remains protected. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()` with `TestClient`. |
| AC8 | Retention uncertainty is documented. | Evidence profile: baseline_before_after_diff; `rg` checks RGPD retention policy wording. |
| AC9 | No parallel audit store is added. | Evidence profile: no_legacy_contract; `rg` checks new log store symbols and `audit_events` reuse. |
| AC10 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-268 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-267, existing admin audit routes, `AuditService` and `audit_events` before adding access logging. (AC: AC1, AC9)
- [ ] Task 2: Define one stable access action for `admin_answer_audit_v1` consultations. (AC: AC1, AC3)
- [ ] Task 3: Add the access logging call to the protected admin answer audit consultation flow. (AC: AC1, AC3, AC7)
- [ ] Task 4: Record failed access status for denied consultation paths with authenticated admin context. (AC: AC2, AC6)
- [ ] Task 5: Store only sanitized details for justification and omit prompt, proof payload and raw birth fields. (AC: AC4, AC5)
- [ ] Task 6: Reuse `AuditService.record_event` or one thin wrapper instead of adding a parallel audit store. (AC: AC6, AC9)
- [ ] Task 7: Add integration tests with `TestClient`, DB assertions, `app.routes` and `app.openapi()` evidence. (AC: AC1, AC2, AC7)
- [ ] Task 8: Document retention as pending the final RGPD policy decision. (AC: AC8)
- [ ] Task 9: Persist validation output, source checklist and scoped surface evidence under the CS-268 evidence folder. (AC: AC10)

## Files to Inspect First

- `_story_briefs/cs-268-add-admin-answer-audit-access-logs.md` - source brief.
- `_condamad/stories/CS-267-admin-answer-audit-api/00-story.md` - upstream protected admin answer audit API contract.
- `backend/app/api/v1/routers/admin/audit.py` - existing admin audit route pattern and export audit behavior.
- `backend/app/services/ops/audit_service.py` - canonical audit event recording and sanitization owner.
- `backend/app/infra/db/models/audit_event.py` - existing audit event persistence model.
- `backend/app/tests/integration/test_admin_logs_api.py` - existing DB-backed admin audit integration tests.
- `backend/app/api/v1/routers/admin/**` - expected protected admin route namespace for implemented CS-267 routes.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output only.

## Runtime Source of Truth

- Primary source of truth:
  - `AuditService.record_event`, `audit_events`, `app.routes`, `app.openapi()`, `TestClient`, DB-backed `pytest` and `AST guard`.
- Secondary evidence:
  - Targeted `rg` scans over backend admin answer audit files, tests and documentation.
- Static scans alone are not sufficient because:
  - access logging must be proven from runtime HTTP behavior and persisted audit event rows.

## Contract Shape

- Contract type:
  - Protected admin access log event for `admin_answer_audit_v1` consultation.
- Event action:
  - `admin_answer_audit_accessed` for successful consultation.
  - `admin_answer_audit_access_denied` for denied consultation that has authenticated admin context.
- Fields:
  - `request_id`: existing request identifier from request context.
  - `actor_user_id`: authenticated admin user identifier.
  - `actor_role`: authenticated admin role.
  - `action`: stable access action name.
  - `target_type`: exact value `admin_answer_audit_v1`.
  - `target_id`: consulted answer audit identifier or requested identifier.
  - `status`: `success` or `failed`.
  - `details.justification`: sanitized justification value when supplied by the consultation flow.
  - `details.source_contract`: exact value `admin_answer_audit_v1`.
  - `details.reason`: bounded denied or logging-failure reason code without sensitive payload data.
- Required fields:
  - `request_id`
  - `actor_user_id`
  - `actor_role`
  - `action`
  - `target_type`
  - `target_id`
  - `status`
- Optional fields:
  - `details.justification`
  - `details.reason`
- Status codes:
  - Existing admin answer audit API status codes from CS-267 remain unchanged.
- Serialization names:
  - JSON and persisted detail keys use exact snake_case names from this contract.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must keep `admin_answer_audit_v1` under protected admin paths only.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-268-add-admin-answer-audit-access-logs.md`
  - `_condamad/stories/CS-267-admin-answer-audit-api/00-story.md`
  - `backend/app/api/v1/routers/admin/audit.py`
  - `backend/app/services/ops/audit_service.py`
  - `backend/app/infra/db/models/audit_event.py`
  - `backend/app/tests/integration/test_admin_logs_api.py`
- Comparison after implementation:
  - `backend/app/api/v1/routers/admin/**`
  - `backend/app/services/ops/**`
  - `backend/tests/api/admin/test_answer_audit_access_logs.py`
  - `backend/app/tests/integration/test_admin_logs_api.py`
  - `docs/architecture/admin-answer-audit-access-retention.md`
  - `_condamad/stories/CS-268-answer-audit-access-logs/evidence/validation.txt`
- Expected invariant:
  - The only intended runtime delta is access logging for protected admin answer audit consultation.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Admin answer audit route behavior | `backend/app/api/v1/routers/admin/**` | public routers or frontend |
| Audit event persistence | `backend/app/services/ops/audit_service.py` | new parallel log service |
| Audit event storage | `backend/app/infra/db/models/audit_event.py` | new access log table |
| Sensitive detail sanitization | `AuditService.record_event` path | route-local raw detail writes |
| Retention note | `docs/architecture/admin-answer-audit-access-retention.md` | UI copy or code comments only |
| Evidence artifacts | `_condamad/stories/CS-268-answer-audit-access-logs/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse the existing admin authentication and request id patterns used by admin routes.
- Reuse `AuditService.record_event` as the canonical audit event recording path.
- Reuse the existing `audit_events` model unless a user-approved blocker says the current store cannot meet the contract.
- Reuse CS-267 route family and `admin_answer_audit_v1` terminology.
- Reuse existing sanitization behavior from the audit service path.
- Do not add external packages, duplicate audit stores, duplicate admin auth gates or parallel sensitive-data masking code.

## No Legacy / Forbidden Paths

- No legacy access log path may be added for this endpoint family.
- No compatibility access log path may be added for this endpoint family.
- No fallback access log path may be added for this endpoint family.
- No public or client route may expose `admin_answer_audit_v1` access logs.
- No new access log table, replay endpoint, frontend UI or generated client is authorized by this story.
- No raw prompt, proof payload, secret, birth date, birth time, birth place, coordinate or timezone may be stored in event details.

## Reintroduction Guard

- Forbidden route paths:
  - `/v1/answer-audits/access-logs`
  - `/v1/users/me/answer-audits/access-logs`
  - `/v1/admin/answer-audit-replay`
- Forbidden persistence symbols:
  - `AnswerAuditAccessLogModel`
  - `admin_answer_audit_access_logs`
  - `answer_audit_access_log_repository`
- Forbidden detail fields:
  - `prompt`
  - `proof_payload`
  - `birth_date`
  - `birth_time`
  - `birth_place`
  - `birth_lat`
  - `birth_lon`
  - `birth_timezone`
- Required guards:
  - `pytest -q backend/tests/api/admin/test_answer_audit_access_logs.py` proves persisted access events.
  - `python` checks `app.routes` and `app.openapi()` for protected admin-only route exposure.
  - `AST guard` checks no forbidden detail fields are passed to `AuditService.record_event`.
  - `rg` checks no parallel access log store symbols were introduced.

## Regression Guardrails

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `Routeurs API v1` | Admin answer audit behavior stays under canonical API v1 admin routes. | `app.routes`; targeted `pytest`. |
| RG-003 `Architecture des routes API v1` | Public and client routers do not own admin audit access logs. | `app.openapi()`; route `rg`. |
| RG-007 `Endpoints admin LLM observability` | LLM answer audit consultation remains protected admin behavior. | `TestClient`; OpenAPI check. |
| RG-022 `Plans de validation des stories prompt-generation` | Backend tests cover prompt/provider audit-related access behavior. | `pytest`; targeted `rg`. |
| Registry gap | No exact `admin_answer_audit_v1` access-log guardrail exists in resolver output. | Story-local guards. |
| Non-applicable example | RG-047 frontend inline style guardrail is out of scope. | No frontend source edits. |
| Non-applicable example | RG-052 CSS namespace guardrail is out of scope. | No CSS or build edits. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation output | `_condamad/stories/CS-268-answer-audit-access-logs/evidence/validation.txt` | Keep validation transcript. |
| Application surface status | `_condamad/stories/CS-268-answer-audit-access-logs/evidence/app-surface-status.txt` | Prove scoped app changes. |
| Source checklist | `_condamad/stories/CS-268-answer-audit-access-logs/evidence/source-checklist.md` | Record mandatory source coverage. |
| Sanitization scan | `_condamad/stories/CS-268-answer-audit-access-logs/evidence/sensitive-detail-scan.txt` | Prove forbidden fields stay out. |
| Review output | `_condamad/stories/CS-268-answer-audit-access-logs/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this access logging story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/api/v1/routers/admin/**` - add access logging at the protected admin answer audit consultation boundary.
- `backend/app/services/ops/audit_service.py` - reuse or thinly wrap canonical audit event recording behavior.
- `docs/architecture/admin-answer-audit-access-retention.md` - document RGPD retention uncertainty.
- `_condamad/stories/CS-268-answer-audit-access-logs/evidence/validation.txt` - persist validation output.
- `_condamad/stories/CS-268-answer-audit-access-logs/evidence/app-surface-status.txt` - persist scoped status output.
- `_condamad/stories/CS-268-answer-audit-access-logs/evidence/source-checklist.md` - persist source coverage.
- `_condamad/stories/CS-268-answer-audit-access-logs/evidence/sensitive-detail-scan.txt` - persist sensitive detail scan.

Likely tests:

- `backend/tests/api/admin/test_answer_audit_access_logs.py` - `TestClient`, DB assertions, `app.routes` and `app.openapi()` checks.
- `backend/app/tests/integration/test_admin_logs_api.py` - extend only when existing admin audit listing coverage must prove visibility.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no new persistence schema is created.
- `backend/app/infra/db/models/**` - out of scope unless a documented blocker proves `audit_events` cannot be reused.
- `backend/app/api/v1/routers/public/**` - out of scope; no client route is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `pytest -q backend/tests/api/admin/test_answer_audit_access_logs.py`
- VC2: `pytest -q backend/app/tests/integration/test_admin_logs_api.py`
- VC3: `python -c "from app.main import app; assert any('/v1/admin' in getattr(r, 'path', '') for r in app.routes)"`
- VC4: `python -c "from app.main import app; assert '/v1/users/me/answer-audits/access-logs' not in str(app.openapi())"`
- VC5: `rg -n "admin_answer_audit_accessed|admin_answer_audit_access_denied" backend/app backend/tests`
- VC6: `rg -n "AnswerAuditAccessLogModel|admin_answer_audit_access_logs|answer_audit_access_log_repository" backend/app backend/tests`
- VC7: `rg -n "prompt|proof_payload|birth_date|birth_time|birth_place|birth_lat|birth_lon|birth_timezone" backend/app backend/tests`
- VC8: `python -c "from pathlib import Path; assert Path('docs/architecture/admin-answer-audit-access-retention.md').exists()"`
- VC9: `rg -n "RGPD|retention|politique" docs/architecture/admin-answer-audit-access-retention.md`
- VC10: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-268-answer-audit-access-logs/evidence/validation.txt').exists()"`
- VC11: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-268-answer-audit-access-logs/evidence/sensitive-detail-scan.txt').exists()"`
- VC12: `git status --short -- backend/app backend/tests backend/app/tests docs/architecture`
- VC13: `ruff format .`
- VC14: `ruff check .`
- VC15: `pytest -q`

## Regression Risks

- A protected admin consultation could remain invisible in the audit trail.
- A denied consultation could skip failed access logging and hide probing attempts.
- Route-local detail construction could persist prompt content, proof payloads or raw birth data.
- A new parallel log store could duplicate audit semantics and bypass existing sanitization.
- A logging failure could leak sensitive diagnostics or break the existing admin response contract without an explicit decision.
- The story could overreach into global back-office logging or client-visible log exposure.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python virtual environment before every Python command.
- Inspect existing owners before creating any new route, builder, service, model or test helper.
- Keep all new or significantly modified application files documented with a French top-level comment or docstring.
- Keep implementation inside backend admin answer audit access logging and retention documentation.
- Persist validation output under the CS-268 evidence folder before requesting review.

## References

- `_story_briefs/cs-268-add-admin-answer-audit-access-logs.md`
- `_condamad/stories/CS-267-admin-answer-audit-api/00-story.md`
- `backend/app/api/v1/routers/admin/audit.py`
- `backend/app/services/ops/audit_service.py`
- `backend/app/infra/db/models/audit_event.py`
- `backend/app/tests/integration/test_admin_logs_api.py`
- `_condamad/stories/regression-guardrails.md`
