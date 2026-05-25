# Story CS-276 admin-chart-diagnostics-v1: Implement admin_chart_diagnostics_v1
Status: done

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-276-implement-admin-chart-diagnostics-v1.md`.
- Required dependency: CS-275 admin chart diagnostics retention, redaction and replay policy.
- Required dependency: CS-272 admin endpoint domain segmentation.
- Existing owner found: `backend/app/api/v1/routers/admin/logs.py` uses `require_admin_user` for admin-only route protection.
- Existing owner found: `backend/app/services/api_contracts/admin/logs.py` owns Pydantic contracts for admin API responses.
- Existing owner found: `backend/app/infra/db/models/audit_event.py` owns persisted access-event fields.
- Existing owner found: `backend/app/core/sensitive_data.py` owns masking rules for admin API sensitive domain data.
- Existing owner found: `backend/app/domain/astrology/runtime/natal_calculation_graph.py` owns calculation graph projection identifiers.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: admins need a protected calculation diagnostic projection without exposing replay or AI answer audit data.
- Source-alignment evidence: PASS; the story preserves admin protection, masking, access logs, tests and replay separation.

## Objective

Implement one protected backend API projection named `admin_chart_diagnostics_v1` for admin-side astrology calculation diagnostics.

The implementation must expose only the approved diagnostic projection through an admin route, mask sensitive data through the existing policy, persist a
consultation log entry, and keep the projection separate from replay snapshots, public clients and narrative answer audit.

## Target State

- A canonical admin API route exposes `admin_chart_diagnostics_v1` under the admin astrology or diagnostics route family from CS-272.
- The route uses `require_admin_user` or the current admin-only dependency used by sibling admin routes.
- The response model is defined under `backend/app/services/api_contracts/admin`.
- The service reuses existing natal calculation graph, chart result and runtime projection owners instead of duplicating calculation logic.
- Sensitive birth data, coordinates, user identifiers, chart identifiers and raw inputs are masked through the existing sensitive-data policy.
- Each successful or denied consultation writes an `audit_events` row with actor, role, action, target, status, request id and sanitized details.
- Permission tests cover authorized admin access and denied non-admin access through `TestClient`.
- Redaction tests prove sensitive fields are absent, masked, hashed or truncated according to the policy.
- Error tests cover missing chart, unavailable diagnostic source and invalid access without leaking raw payloads.
- OpenAPI exposes the admin route as an admin-only contract and does not expose it through public client route families.
- The projection stays distinct from `replay_snapshot_v1`, LLM replay and narrative answer audit.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-276-implement-admin-chart-diagnostics-v1.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-276`.
- Evidence 3: `_condamad/stories/CS-275-admin-chart-diagnostics-policy/00-story.md` - policy dependency inspected.
- Evidence 4: `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/00-story.md` - admin segmentation dependency inspected.
- Evidence 5: `backend/app/api/v1/routers/registry.py` - API v1 route registration owner inspected.
- Evidence 6: `backend/app/api/v1/routers/admin/logs.py` - admin route protection pattern inspected.
- Evidence 7: `backend/app/services/api_contracts/admin/logs.py` - admin Pydantic contract pattern inspected.
- Evidence 8: `backend/app/infra/db/models/audit_event.py` - consultation log persistence owner inspected.
- Evidence 9: `backend/app/core/sensitive_data.py` - sensitive data masking owner inspected.
- Evidence 10: `_condamad/stories/regression-guardrails.md` - registry consulted through scoped resolver output only.
- Evidence 11: `resolve_guardrails.py` - scoped resolver run for backend API, admin route, OpenAPI, redaction and audit-log scope.
- Repository structure alert: backend, backend/app, backend/tests, frontend and frontend/src exist in this workspace.
- Source-alignment evidence: PASS; no brief criterion was dropped, softened or replaced by generic admin API cleanup.

## Domain Boundary

- Domain: backend-api
- In scope:
  - Backend admin API route for `admin_chart_diagnostics_v1`.
  - Response contract, service orchestration, masking rules, consultation logs and targeted tests.
  - Runtime route and schema evidence through `app.routes`, `app.openapi()`, `TestClient` and `pytest`.
  - Reuse of CS-275 policy and CS-272 admin endpoint segmentation.
- Out of scope:
  - Frontend UI, database schema, auth redesign, i18n, styling, build tooling, migrations, seeds and public client generation.
  - `replay_snapshot_v1`, LLM replay, narrative answer audit, public fixed stars and broad calculation engine redesign.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No B2C client route, public projection, generated frontend client, replay builder, replay storage model or AI answer audit merge.
  - No new role system, token claim redesign, account seed, DB migration or calculation-result recomputation.

## Operation Contract

- Operation type: create
- Primary archetype: api-contract-change
- Archetype reason: the story adds one protected admin API route with OpenAPI, JSON response, masking and audit logging.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the canonical `admin_chart_diagnostics_v1` admin route, contract, service, registration and targeted tests.
  - Reuse `require_admin_user`, current API v1 router registration and existing admin contract patterns.
  - Reuse `AuditEventModel` for consultation logs unless an existing audit service already wraps it.
  - Reuse `backend/app/core/sensitive_data.py` for masking instead of defining a parallel sanitizer.
  - Reuse calculation graph and chart runtime owners instead of recomputing astrology facts in the route.
  - Keep public routes, frontend files, DB migrations, auth roles, LLM replay and narrative answer audit unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-275 leaves retention or raw-field visibility undecided for this runtime projection.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `TestClient` and `pytest` prove route, schema and authorization behavior. |
| Baseline Snapshot | yes | OpenAPI and route snapshots prove the only allowed surface delta is the admin diagnostic route. |
| Ownership Routing | yes | Route, contract, service, sanitizer, audit log and calculation owners must stay separated. |
| Allowlist Exception | no | No allowlist handling is authorized for this single canonical admin projection. |
| Contract Shape | yes | The route has exact admin-only access, status codes, JSON fields, masking and log behavior. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Public client exposure, replay merging, raw sensitive data and duplicate diagnostics must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The admin diagnostic route is registered. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes`; `TestClient` is named in tests. |
| AC2 | OpenAPI exposes the admin contract. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` for `admin_chart_diagnostics_v1`. |
| AC3 | Admin access succeeds. | Evidence profile: json_contract_shape; `pytest -q backend/app/tests/integration/test_admin_chart_diagnostics_api.py`. |
| AC4 | Non-admin access is denied. | Evidence profile: api_error_shape_contract; `pytest -q backend/app/tests/integration/test_admin_chart_diagnostics_api.py`. |
| AC5 | Sensitive diagnostic fields are masked. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/test_admin_chart_diagnostics_redaction.py`. |
| AC6 | Each consultation is logged. | Evidence profile: json_contract_shape; `pytest -q backend/app/tests/integration/test_admin_chart_diagnostics_api.py`. |
| AC7 | Missing source errors are typed. | Evidence profile: api_error_shape_contract; `pytest -q backend/app/tests/integration/test_admin_chart_diagnostics_api.py`. |
| AC8 | Replay stays separate. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks replay terms in diagnostic owners and tests. |
| AC9 | Narrative answer audit stays separate. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks answer-audit owners are not imported. |
| AC10 | Duplicate diagnostic owners are absent. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` checks bounded backend owners. |
| AC11 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-276 evidence paths. |

## Implementation Tasks

- [x] Task 1: Inspect the brief, CS-275, CS-272, admin route patterns, sensitive data policy and audit event model. (AC: AC1, AC5, AC6)
- [x] Task 2: Define the `admin_chart_diagnostics_v1` Pydantic request or response contract under admin API contracts. (AC: AC2, AC3)
- [x] Task 3: Implement the service that assembles diagnostic facts from existing calculation graph and chart runtime owners. (AC: AC3, AC7)
- [x] Task 4: Apply sensitive-data masking through the existing sanitizer or a local wrapper around that policy. (AC: AC5)
- [x] Task 5: Persist consultation logs with sanitized details for successful and denied reads. (AC: AC6)
- [x] Task 6: Add the admin route with `require_admin_user` and register it through the canonical API v1 registry. (AC: AC1, AC2, AC3, AC4)
- [x] Task 7: Add integration tests for admin success, non-admin denial, typed errors and log creation. (AC: AC3, AC4, AC6, AC7)
- [x] Task 8: Add unit tests for masking policy and no raw birth data leakage in the response payload. (AC: AC5)
- [x] Task 9: Add architecture guards for replay separation, answer-audit separation and duplicate owner absence. (AC: AC8, AC9, AC10)
- [x] Task 10: Persist OpenAPI, route, validation and source-checklist evidence under the CS-276 evidence folder. (AC: AC2, AC11)

## Files to Inspect First

- `_story_briefs/cs-276-implement-admin-chart-diagnostics-v1.md` - source brief.
- `_condamad/stories/CS-275-admin-chart-diagnostics-policy/00-story.md` - retention, masking and replay policy dependency.
- `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/00-story.md` - admin route-family dependency.
- `backend/app/api/v1/routers/registry.py` - canonical API v1 router registration.
- `backend/app/api/v1/routers/admin/logs.py` - sibling admin route protection and DB dependency pattern.
- `backend/app/services/api_contracts/admin/logs.py` - sibling admin Pydantic response contract pattern.
- `backend/app/services/ops/admin_logs.py` - current admin log service pattern.
- `backend/app/api/dependencies/auth.py` - `require_admin_user` behavior.
- `backend/app/core/sensitive_data.py` - canonical masking policy.
- `backend/app/infra/db/models/audit_event.py` - access-log persistence fields.
- `backend/app/infra/db/repositories/chart_result_repository.py` - persisted chart result owner.
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py` - calculation graph projection owner.
- `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py` - trace and replay separation owner.
- `backend/app/main.py` - loaded FastAPI app for `app.routes` and `app.openapi()`.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `app.routes` for the registered admin route.
  - `app.openapi()` for the admin schema and public exposure check.
  - `TestClient` for authorization, JSON payload and typed error behavior.
  - `AuditEventModel` and DB test session for consultation log persistence.
  - `backend/app/core/sensitive_data.py` for masking behavior.
- Secondary evidence:
  - Targeted `rg` scans for `admin_chart_diagnostics_v1`, replay terms, answer-audit imports and duplicate diagnostic owners.
  - `pytest -q backend/app/tests/integration/test_admin_chart_diagnostics_api.py` for route behavior and audit log evidence.
  - `pytest -q backend/tests/unit/test_admin_chart_diagnostics_redaction.py` for masking evidence.
- Static scans alone are not sufficient because:
  - Route registration, OpenAPI exposure, auth behavior and DB log creation must be proven from runtime tests.

## Contract Shape

- Contract type:
  - Protected admin API route and OpenAPI path.
- Fields:
  - `projection_id`: exact value `admin_chart_diagnostics_v1`.
  - `chart_reference`: masked or hashed chart reference.
  - `calculation_graph`: sanitized graph family, node status, source versions and proof references.
  - `diagnostic_summary`: non-sensitive calculation status and warning summary.
  - `redaction`: applied masking policy names and omitted raw-field categories.
  - `limits`: statement that replay, public fixed stars and narrative answer audit are not included.
  - `generated_at`: server timestamp for the diagnostic projection.
  - `correlation_id`: request or generated correlation id.
- Required fields:
  - `projection_id`
  - `chart_reference`
  - `calculation_graph`
  - `diagnostic_summary`
  - `redaction`
  - `limits`
  - `generated_at`
  - `correlation_id`
- Optional fields:
  - none.
- Status codes:
  - `200` for successful admin diagnostic read.
  - `401` for missing or invalid authentication.
  - `403` for authenticated non-admin access.
  - `404` for missing chart or unavailable diagnostic source.
- Serialization names:
  - JSON keys are emitted exactly as listed in the required fields.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must expose the route only under the admin route family.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-276-implement-admin-chart-diagnostics-v1.md`
  - `_condamad/stories/CS-275-admin-chart-diagnostics-policy/00-story.md`
  - `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/00-story.md`
  - `backend/app/api/v1/routers/registry.py`
  - `backend/app/core/sensitive_data.py`
  - `backend/app/infra/db/models/audit_event.py`
- Comparison after implementation:
  - `_condamad/stories/CS-276-admin-chart-diagnostics-v1/evidence/openapi-before.json`
  - `_condamad/stories/CS-276-admin-chart-diagnostics-v1/evidence/openapi-after.json`
  - `_condamad/stories/CS-276-admin-chart-diagnostics-v1/evidence/routes-after.txt`
  - `_condamad/stories/CS-276-admin-chart-diagnostics-v1/evidence/validation.txt`
- Expected invariant:
  - The only intended API surface difference is the canonical admin route for `admin_chart_diagnostics_v1`.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Admin route | `backend/app/api/v1/routers/admin/chart_diagnostics.py` | public routers or frontend clients |
| API contract | `backend/app/services/api_contracts/admin/chart_diagnostics.py` | route-local dict payloads |
| Diagnostic assembly | `backend/app/services/ops/admin_chart_diagnostics.py` | FastAPI route handler logic |
| Sensitive masking | `backend/app/core/sensitive_data.py` | ad hoc field filtering in route code |
| Consultation log | `backend/app/infra/db/models/audit_event.py` or existing audit service | stdout or frontend logs |
| Calculation graph facts | `backend/app/domain/astrology/runtime/**` existing owners | duplicated calculator code |
| Story evidence artifacts | `_condamad/stories/CS-276-admin-chart-diagnostics-v1/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse CS-275 as the policy source for masking, retained data and replay separation.
- Reuse CS-272 for admin route-family placement instead of inventing a second admin route taxonomy.
- Reuse `require_admin_user` for admin-only access.
- Reuse `backend/app/core/sensitive_data.py` for sensitive data classification and masking behavior.
- Reuse `AuditEventModel` or an existing audit service for consultation logs.
- Reuse existing calculation graph, trace and chart runtime owners; do not recalculate astrology facts in HTTP code.
- Keep one canonical `admin_chart_diagnostics_v1` projection contract and one canonical route owner.
- Do not add external packages, generated clients, parallel sanitizers, duplicate diagnostic services or duplicate audit tables.

## No Legacy / Forbidden Paths

- No legacy diagnostic route path may be added.
- No compatibility diagnostic route path may be added.
- No fallback branch may expose raw diagnostic payloads.
- Do not create aliases, shims, compatibility wrappers or parallel diagnostic endpoints.
- Do not expose raw birth date, birth time, birth place, coordinates, raw chart input, prompt payloads or replay inputs.
- Do not merge calculation diagnostics with narrative answer audit, LLM replay or `replay_snapshot_v1`.
- Forbidden surfaces:
  - `frontend/src/**`
  - `backend/app/api/v1/routers/public/**`
  - `backend/app/services/api_contracts/public/**`
  - `backend/migrations/**`
  - generated OpenAPI clients
  - LLM replay snapshot builders and narrative answer audit services

## Reintroduction Guard

- Guard target:
  - `admin_chart_diagnostics_v1` is registered exactly once in `app.routes`.
  - `admin_chart_diagnostics_v1` appears in `app.openapi()` only under the admin route family.
  - sensitive birth and chart fields cannot appear raw in the JSON response.
  - consultation reads cannot complete without an audit log entry.
  - replay snapshot and narrative answer audit modules cannot be imported by the diagnostic service.
  - public routers and frontend files cannot consume this projection.
- Guard mechanism:
  - `python` checks `app.routes` and `app.openapi()`;
  - `pytest` with `TestClient` checks access, payload, errors and logs;
  - `rg` checks bounded route, service, contract and test owners;
  - `AST guard` checks forbidden imports in the diagnostic service.
- Guard owner:
  - `backend/app/tests/integration/test_admin_chart_diagnostics_api.py`;
  - `backend/tests/unit/test_admin_chart_diagnostics_redaction.py`;
  - `backend/tests/architecture/test_admin_chart_diagnostics_boundaries.py`;
  - `_condamad/stories/CS-276-admin-chart-diagnostics-v1/evidence/validation.txt`.

## Regression Guardrails

Scope vector:

- backend-api: yes;
- admin route creation: yes;
- admin diagnostic projection contract: yes;
- OpenAPI runtime exposure: yes;
- redaction and audit-log behavior: yes;
- calculation graph runtime: read-only reuse;
- frontend, DB migration, auth redesign, i18n, style and build: no.

Selected guardrails:

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `Routeurs API v1` | Backend route ownership stays in canonical API v1 paths. | `app.routes`; targeted `pytest`. |
| RG-003 `Architecture des routes API v1` | Router registration remains tied to the canonical registry. | `python`; architecture `pytest`. |
| RG-007 `Endpoints admin LLM observability` | Sensitive admin diagnostics stay protected and internal. | `app.openapi()`; `TestClient`. |
| RG-022 `Plans de validation des stories prompt-generation` | Sensitive projection validation needs targeted tests. | `pytest`; bounded `rg`. |
| Registry gap | No exact `admin_chart_diagnostics_v1` guardrail exists in resolver output. | Story-local route and masking guards. |

Non-applicable examples:

- RG-041 entitlement documentation is out of scope because this story implements diagnostics, not product entitlement docs.
- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 frontend CSS namespace migration is out of scope because no style or build output is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| OpenAPI before snapshot | `_condamad/stories/CS-276-admin-chart-diagnostics-v1/evidence/openapi-before.json` | Prove baseline API surface. |
| OpenAPI after snapshot | `_condamad/stories/CS-276-admin-chart-diagnostics-v1/evidence/openapi-after.json` | Prove final API surface. |
| Route inventory | `_condamad/stories/CS-276-admin-chart-diagnostics-v1/evidence/routes-after.txt` | Capture `app.routes` evidence. |
| Validation output | `_condamad/stories/CS-276-admin-chart-diagnostics-v1/evidence/validation.txt` | Keep validation transcript. |
| Source checklist | `_condamad/stories/CS-276-admin-chart-diagnostics-v1/evidence/source-checklist.md` | Record source coverage. |
| Review output | `_condamad/stories/CS-276-admin-chart-diagnostics-v1/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this admin diagnostics story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/api/v1/routers/admin/chart_diagnostics.py` - define the protected admin diagnostic route.
- `backend/app/api/v1/routers/registry.py` - register the new admin router through the canonical registry.
- `backend/app/services/api_contracts/admin/chart_diagnostics.py` - define request, response and error payload contracts.
- `backend/app/services/ops/admin_chart_diagnostics.py` - assemble projection, apply masking and log consultations.
- `backend/app/services/api_contracts/admin/__init__.py` - expose the contract only when current package patterns require it.
- `backend/app/services/ops/__init__.py` - expose the service only when current package patterns require it.
- `backend/app/tests/integration/test_admin_chart_diagnostics_api.py` - cover admin access, denial, errors and logs.
- `backend/tests/unit/test_admin_chart_diagnostics_redaction.py` - cover masking and sensitive field denial.
- `backend/tests/architecture/test_admin_chart_diagnostics_boundaries.py` - cover route, import and public exposure boundaries.
- `_condamad/stories/CS-276-admin-chart-diagnostics-v1/evidence/openapi-before.json` - persist pre-change OpenAPI evidence.
- `_condamad/stories/CS-276-admin-chart-diagnostics-v1/evidence/openapi-after.json` - persist post-change OpenAPI evidence.
- `_condamad/stories/CS-276-admin-chart-diagnostics-v1/evidence/routes-after.txt` - persist route inventory evidence.
- `_condamad/stories/CS-276-admin-chart-diagnostics-v1/evidence/validation.txt` - persist validation output.
- `_condamad/stories/CS-276-admin-chart-diagnostics-v1/evidence/source-checklist.md` - persist source coverage.

Likely tests:

- `backend/app/tests/integration/test_admin_chart_diagnostics_api.py` - HTTP, authorization, error, log and OpenAPI behavior.
- `backend/tests/unit/test_admin_chart_diagnostics_redaction.py` - sensitive-data masking and raw field denial.
- `backend/tests/architecture/test_admin_chart_diagnostics_boundaries.py` - route registration, imports and public exposure guards.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; consultation logs reuse existing audit-event storage.
- `backend/app/api/v1/routers/public/**` - out of scope; no public client route is touched.
- `backend/app/services/api_contracts/public/**` - out of scope; no public API contract is touched.
- `backend/app/infra/db/models/llm/**` - out of scope; no LLM replay or answer audit model is touched.
- `backend/app/domain/llm/**` - out of scope; no prompt, replay or answer audit behavior is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `python -c "from app.main import app; assert any('admin_chart_diagnostics_v1' in getattr(r, 'path', '') for r in app.routes)"`
- VC2: `python -c "from app.main import app; data=str(app.openapi()); assert 'admin_chart_diagnostics_v1' in data"`
- VC3: `python -c "from app.main import app; assert all('admin_chart_diagnostics_v1' not in p for p in app.openapi()['paths'] if p.startswith('/v1/public'))"`
- VC4: `pytest -q backend/app/tests/integration/test_admin_chart_diagnostics_api.py`
- VC5: `pytest -q backend/tests/unit/test_admin_chart_diagnostics_redaction.py`
- VC6: `pytest -q backend/tests/architecture/test_admin_chart_diagnostics_boundaries.py`
- VC7: `rg -n "admin_chart_diagnostics_v1|chart_diagnostics" backend/app/api/v1/routers/admin backend/app/services backend/tests`
- VC8: `rg -n "replay_snapshot_v1|llm_replay|narrative_answer_audit" backend/app/services/ops/admin_chart_diagnostics.py`
- VC9: `rg -n "birth_date|birth_time|birth_place|coordinates|raw_input" backend/app/services/ops/admin_chart_diagnostics.py backend/tests`
- VC10: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-276-admin-chart-diagnostics-v1/evidence/openapi-after.json').exists()"`
- VC11: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-276-admin-chart-diagnostics-v1/evidence/validation.txt').exists()"`
- VC12: `git status --short -- backend/app frontend/src backend/migrations`
- VC13: `ruff format .`
- VC14: `ruff check .`
- VC15: `pytest -q`

Before VC1 through VC6, VC10, VC11, VC13, VC14 and VC15, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The admin route may expose sensitive birth or chart input values without masking.
- The diagnostic service may duplicate calculation logic instead of reusing graph and runtime owners.
- A denied or successful consultation may skip audit-log persistence.
- Public OpenAPI, frontend clients or public routers may receive internal diagnostics.
- Replay snapshot semantics may be mixed into current diagnostics.
- Narrative answer audit may become coupled to calculation diagnostics.
- Error responses may leak raw diagnostic payloads while handling missing chart or unavailable source states.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python virtual environment before every Python command.
- Keep frontend, migrations, public routers, public API contracts and generated clients unchanged.
- Keep `replay_snapshot_v1`, LLM replay and narrative answer audit outside this implementation.
- Use existing masking and audit-log owners before adding any new helper.
- Persist OpenAPI, route and validation evidence under the CS-276 evidence folder before requesting review.

## References

- `_story_briefs/cs-276-implement-admin-chart-diagnostics-v1.md`
- `_condamad/stories/CS-275-admin-chart-diagnostics-policy/00-story.md`
- `_condamad/stories/CS-272-admin-endpoint-domain-segmentation/00-story.md`
- `backend/app/api/v1/routers/registry.py`
- `backend/app/api/v1/routers/admin/logs.py`
- `backend/app/services/api_contracts/admin/logs.py`
- `backend/app/services/ops/admin_logs.py`
- `backend/app/api/dependencies/auth.py`
- `backend/app/core/sensitive_data.py`
- `backend/app/infra/db/models/audit_event.py`
- `backend/app/infra/db/repositories/chart_result_repository.py`
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`
- `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py`
- `backend/app/main.py`
- `_condamad/stories/regression-guardrails.md`
