# Story CS-297 expose-internal-admin-replay-snapshot-v1-api: Expose Internal Admin replay_snapshot_v1 API
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-297-expose-internal-admin-replay-snapshot-v1-api.md`.
- Required dependency: CS-296 replay snapshot service retention and purge.
- Required dependency: CS-270 internal role model and CS-271 admin data permission matrix.
- Existing owner found: `backend/app/api/v1/routers/admin/audit.py` owns canonical admin audit routes.
- Existing owner found: `backend/app/api/v1/routers/admin/chart_diagnostics.py` already exposes protected audit diagnostics.
- Existing owner found: `backend/app/api/v1/routers/registry.py` mounts all API v1 route owners through one registry.
- Existing owner found: `backend/app/services/api_contracts/admin/audit.py` owns admin audit response contracts.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: replay snapshot runtime needs a protected internal admin API without public or client-facing exposure.
- Source-alignment evidence: PASS; admin-only scope, metadata, replay attempt, purge, denial and no-public-route stakes are preserved.

## Objective

Expose a minimal protected internal admin API for `replay_snapshot_v1` metadata, controlled replay attempt and audited manual purge.

The implementation must keep the route under the canonical admin audit namespace, reuse the CS-296 service, deny non-admin actors, avoid raw payload
exposure and prove no public or generated-client route exists.

## Target State

- `GET /v1/admin/audit/replay_snapshot_v1/{snapshot_id}` returns controlled metadata for one replay snapshot.
- `POST /v1/admin/audit/replay_snapshot_v1/{snapshot_id}/replay-attempt` launches one controlled replay attempt through CS-296 service behavior.
- `DELETE /v1/admin/audit/replay_snapshot_v1/{snapshot_id}` performs one audited manual purge through the canonical service.
- Every route uses the approved admin dependency from the current backend auth layer.
- User, support and unauthenticated actors receive `401` or `403` through existing API error behavior.
- Responses exclude raw prompts, raw birth data, exact coordinates, direct identifiers, secrets and encrypted payload bytes.
- `app.openapi()` exposes the route only under `/v1/admin/audit`.
- `app.routes` contains no public, client, support or frontend replay path for `replay_snapshot_v1`.
- No frontend UI, generated public client, public OpenAPI path, export endpoint or global listing is introduced.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-297-expose-internal-admin-replay-snapshot-v1-api.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-297`.
- Evidence 3: `backend/app/api/v1/routers/admin/audit.py` - current admin audit namespace inspected.
- Evidence 4: `backend/app/api/v1/routers/admin/chart_diagnostics.py` - protected audit diagnostic route pattern inspected.
- Evidence 5: `backend/app/api/v1/routers/admin/llm/observability.py` - LLM admin observability boundary inspected.
- Evidence 6: `backend/app/api/v1/routers/registry.py` - canonical API v1 route registry inspected.
- Evidence 7: `backend/app/services/api_contracts/admin/audit.py` - admin audit Pydantic contract owner inspected.
- Evidence 8: `_condamad/stories/CS-270-internal-role-model/00-story.md` - internal role dependency inspected.
- Evidence 9: `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md` - permission matrix dependency inspected.
- Evidence 10: `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/00-story.md` - service dependency inspected.
- Evidence 11: `resolve_guardrails.py` - scoped resolver run for backend API, admin route and replay snapshot contracts.
- Repository structure alert: backend, backend/app, backend/tests, frontend and frontend/src exist in this workspace.
- Source-alignment evidence: PASS; no brief criterion was dropped, softened or replaced by generic LLM observability work.

## Domain Boundary

- Domain: backend-api
- In scope:
  - Backend admin API route creation for `replay_snapshot_v1` under `/v1/admin/audit`.
  - Pydantic request and response contracts for metadata, replay attempt and purge outcomes.
  - Route registration through `backend/app/api/v1/routers/registry.py`.
  - Admin-only authorization using the existing approved admin dependency.
  - TestClient coverage for authorized, denied, missing, expired and purged outcomes.
  - Runtime checks over `app.routes` and `app.openapi()` for internal-only exposure.
- Out of scope:
  - Frontend UI, public/client routes, support routes, B2B routes, export endpoints, global listing, i18n, styling and build tooling.
  - DB schema, migrations, storage policy redesign, replay execution redesign, role taxonomy redesign and generated public clients.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, public API, mass export, free replay, global listing or storage migration.
  - No raw replay payload, raw prompt, birth data, exact coordinate, direct identifier, secret or encrypted bytes in API responses.

## Operation Contract

- Operation type: create
- Primary archetype: api-contract-change
- Archetype reason: the story adds protected admin API routes with OpenAPI and JSON response contracts.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the three `replay_snapshot_v1` admin routes under `/v1/admin/audit`.
  - Use `backend/app/api/v1/routers/registry.py` as the only API v1 mounting mechanism.
  - Use CS-296 service methods for metadata read, controlled replay attempt and manual purge.
  - Keep raw replay payload and sensitive source data out of route responses.
  - Keep public, client, support, frontend and generated-client surfaces unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-296 does not expose a canonical service method for replay attempt or purge.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `pytest` and `TestClient` prove runtime admin API behavior. |
| Baseline Snapshot | yes | OpenAPI before and after artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Route, contract, service and audit ownership must stay separated. |
| Allowlist Exception | no | No allowlist handling is authorized for this single admin API surface. |
| Contract Shape | yes | The routes have exact methods, paths, status codes and JSON payload shapes. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Public, client, support and generated-client replay paths must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Admin replay snapshot routes are registered. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes`. |
| AC2 | OpenAPI exposes admin replay paths only. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()`. |
| AC3 | Metadata response is redacted. | Evidence profile: json_contract_shape; `pytest -q backend/tests/api/admin/test_replay_snapshot_v1_api.py`. |
| AC4 | Replay attempt is controlled. | Evidence profile: json_contract_shape; `pytest -q backend/tests/api/admin/test_replay_snapshot_v1_api.py`. |
| AC5 | Manual purge is audited. | Evidence profile: json_contract_shape; `pytest -q backend/tests/api/admin/test_replay_snapshot_v1_api.py`. |
| AC6 | Non-admin access is denied. | Evidence profile: api_error_shape_contract; `pytest -q backend/tests/api/admin/test_replay_snapshot_v1_api.py`. |
| AC7 | Missing snapshot states are covered. | Evidence profile: json_contract_shape; `pytest -q backend/tests/api/admin/test_replay_snapshot_v1_api.py`. |
| AC8 | Expired snapshot states are covered. | Evidence profile: json_contract_shape; `pytest -q backend/tests/api/admin/test_replay_snapshot_v1_api.py`. |
| AC9 | Purged snapshot states are covered. | Evidence profile: json_contract_shape; `pytest -q backend/tests/api/admin/test_replay_snapshot_v1_api.py`. |
| AC10 | Public replay paths are absent. | Evidence profile: route_absence_runtime; `python` checks `app.routes`; `rg` checks bounded paths. |
| AC11 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-297 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect the brief, admin audit routes, registry, admin contracts and CS-270/CS-271/CS-296 dependencies. (AC: AC1, AC2)
- [ ] Task 2: Add admin audit Pydantic contracts for metadata, replay attempt and purge responses. (AC: AC3, AC4, AC5)
- [ ] Task 3: Add or extend the canonical admin audit router for the three `replay_snapshot_v1` routes. (AC: AC1, AC3, AC4, AC5)
- [ ] Task 4: Register the route owner through `backend/app/api/v1/routers/registry.py`. (AC: AC1, AC2)
- [ ] Task 5: Wire every handler to the CS-296 canonical service without route-level lifecycle decisions. (AC: AC3, AC4, AC5)
- [ ] Task 6: Apply the approved admin dependency and cover unauthenticated, user and support denials. (AC: AC6)
- [ ] Task 7: Map missing, expired and purged service outcomes to stable API status codes and response bodies. (AC: AC7, AC8, AC9)
- [ ] Task 8: Add response redaction tests for forbidden raw fields and encrypted payload bytes. (AC: AC3)
- [ ] Task 9: Add runtime OpenAPI and route absence guards for public, client and support replay paths. (AC: AC2, AC10)
- [ ] Task 10: Persist OpenAPI, route inventory, access-control and validation evidence under the CS-297 folder. (AC: AC11)

## Files to Inspect First

- `_story_briefs/cs-297-expose-internal-admin-replay-snapshot-v1-api.md` - source brief.
- `backend/app/api/v1/routers/admin/**` - existing admin route ownership and auth patterns.
- `backend/app/api/v1/routers/registry.py` - canonical route registration.
- `backend/app/services/api_contracts/admin/**` - admin API response contract owners.
- `_condamad/stories/CS-270-internal-role-model/00-story.md` - role vocabulary dependency.
- `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md` - admin data permission dependency.
- `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/00-story.md` - service dependency.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `app.routes`, `app.openapi()` and `TestClient`.
  - `backend/app/api/v1/routers/registry.py` for API v1 route mounting.
  - CS-296 canonical replay snapshot service for metadata, replay attempt and purge behavior.
- Secondary evidence:
  - Targeted `rg` scans for unauthorized replay route paths.
  - Persisted OpenAPI and route inventory evidence under `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence`.
- Static scans alone are not sufficient for this story because:
  - Route registration, authorization, OpenAPI exposure and HTTP behavior must be proven from the loaded app.

## Contract Shape

- Contract type:
  - Protected admin API route and OpenAPI path.
- Methods and paths:
  - `GET /v1/admin/audit/replay_snapshot_v1/{snapshot_id}`
  - `POST /v1/admin/audit/replay_snapshot_v1/{snapshot_id}/replay-attempt`
  - `DELETE /v1/admin/audit/replay_snapshot_v1/{snapshot_id}`
- Fields:
  - `contract_id`: exact value `admin_replay_snapshot_v1`.
  - `snapshot_id`: replay snapshot identifier.
  - `status`: controlled value from the CS-296 service outcome.
  - `created_at`: snapshot creation timestamp.
  - `expires_at`: snapshot expiry timestamp.
  - `redaction_state`: safe redaction status.
  - `version_identity`: safe version labels.
  - `provenance_refs`: safe trace, audit or diagnostics references.
  - `audit_event_id`: purge or access audit event identifier when produced.
  - `replay_attempt_id`: controlled replay attempt identifier when produced.
- Required fields:
  - `contract_id`
  - `snapshot_id`
  - `status`
  - `created_at`
  - `expires_at`
  - `redaction_state`
- Optional fields:
  - `version_identity`
  - `provenance_refs`
  - `audit_event_id`
  - `replay_attempt_id`
- Forbidden response fields:
  - `raw_prompt`
  - `birth_date`
  - `birth_time`
  - `birth_place`
  - `latitude`
  - `longitude`
  - `email`
  - `password`
  - `api_key`
  - `payload_enc`
- Status codes:
  - `200` for successful metadata read.
  - `202` for an accepted controlled replay attempt.
  - `204` for successful manual purge.
  - `401` or `403` for denied non-admin access through existing auth behavior.
  - `404` for missing snapshot.
  - `410` for expired or already purged snapshot state.
- Serialization names:
  - JSON keys are emitted exactly as the contract field names above.
- Frontend type impact:
  - none; no frontend source or generated public client is touched.
- Generated contract impact:
  - `app.openapi()` must expose the paths only under `/v1/admin/audit`.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/openapi-before.json`
  - `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/routes-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/openapi-after.json`
  - `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/routes-after.txt`
- Expected invariant:
  - The only intended API surface difference is the three protected `/v1/admin/audit/replay_snapshot_v1` admin paths.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Admin replay snapshot routes | `backend/app/api/v1/routers/admin/audit.py` or a subrouter under `admin/audit` | public, support or frontend route |
| API v1 route mounting | `backend/app/api/v1/routers/registry.py` | second route registry |
| Admin response contracts | `backend/app/services/api_contracts/admin/audit.py` | route-local untyped dictionaries |
| Replay snapshot lifecycle | CS-296 canonical replay snapshot service | route handler business logic |
| Audit event write | `backend/app/services/ops/audit_service.py` | raw route-local audit payload dump |
| Story evidence artifacts | `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse the existing admin audit namespace unless implementation evidence proves a stronger existing owner.
- Reuse `require_admin_user` or the current approved admin dependency instead of adding a parallel auth gate.
- Reuse CS-296 service methods and outcome DTOs for metadata, replay attempt and purge behavior.
- Reuse existing admin API contract modules instead of defining response schemas inside route handlers.
- Reuse `raise_api_error` and current API error conventions for denied and unavailable states.
- Do not add external packages, duplicate route registries, duplicate replay services, generated public clients or parallel audit writers.

## No Legacy / Forbidden Paths

- No legacy route path may be added for `replay_snapshot_v1`.
- No compatibility route path may be added for `replay_snapshot_v1`.
- No fallback route path may be added for `replay_snapshot_v1`.
- Do not create aliases, shims, compatibility wrappers or redirects for replay snapshot routes.
- Do not add `/v1/replay_snapshot_v1`, `/v1/public/replay_snapshot_v1`, `/v1/support/replay_snapshot_v1` or `/replay_snapshot_v1`.
- Do not expose replay snapshot routes through frontend source, generated public clients, public OpenAPI docs or global listings.
- Do not return raw replay payload, raw prompt, birth data, exact coordinates, direct identifiers, secrets or encrypted payload bytes.

## Reintroduction Guard

- Forbidden route paths:
  - `/v1/replay_snapshot_v1`
  - `/v1/public/replay_snapshot_v1`
  - `/v1/support/replay_snapshot_v1`
  - `/api/replay_snapshot_v1`
  - `/replay_snapshot_v1`
- Forbidden response fields:
  - `raw_prompt`, `birth_date`, `birth_time`, `birth_place`, `latitude`, `longitude`, `email`, `password`, `api_key`, `payload_enc`
- Required deterministic guards:
  - Run every guard from the repository root after venv activation.
  - `pytest -q backend/tests/api/admin/test_replay_snapshot_v1_api.py`
  - `pytest -q backend/tests/architecture/test_admin_replay_snapshot_v1_public_exposure.py`
  - `$env:PYTHONPATH='backend'; python -c "from app.main import app; assert all(p.startswith('/v1/admin/audit') for p in app.openapi()['paths'] if 'replay_snapshot_v1' in p)"`
  - `$env:PYTHONPATH='backend'; python -c "from app.main import app; assert not any(getattr(r,'path','') in {'/v1/replay_snapshot_v1','/replay_snapshot_v1'} for r in app.routes)"`
  - `rg -n "/v1/replay_snapshot_v1|/v1/public/replay_snapshot_v1|/v1/support/replay_snapshot_v1|/replay_snapshot_v1" backend/app frontend/src`

## Regression Guardrails

Scope vector:

- backend-api: yes;
- operation type: create;
- route path: `/v1/admin/audit/replay_snapshot_v1`;
- contracts: OpenAPI, JSON response, admin access control and audit log;
- frontend, DB schema, migration, i18n, style and build: no.

Selected guardrails:

| Guardrail | Applicable invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend route files keep clear API ownership. | architecture `pytest`; route diff. |
| RG-003 `converge-api-v1-route-architecture` | API v1 routes mount through the canonical registry. | `app.routes`; OpenAPI snapshot. |
| RG-007 `converge-admin-llm-observability-router` | LLM admin observability paths stay preserved. | filtered OpenAPI diff; `rg`. |
| RG-022 `align-prompt-generation-story-validation-paths` | Backend API validation paths must point to collected pytest files. | targeted `pytest`; validation output. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 frontend CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because this story exposes replay snapshot admin API only.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| OpenAPI before | `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/openapi-before.json` | Prove baseline API surface. |
| OpenAPI after | `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/openapi-after.json` | Prove final admin-only API surface. |
| Route inventory | `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/routes-after.txt` | Prove loaded route inventory. |
| Access control | `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/access-control.txt` | Prove denial behavior. |
| Validation output | `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/validation.txt` | Keep lint, tests and scans output. |
| Review output | `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this single admin API surface.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/api/v1/routers/admin/audit.py` - add or mount canonical admin audit replay snapshot routes.
- `backend/app/api/v1/routers/admin/replay_snapshot.py` - optional admin audit subrouter for focused handlers.
- `backend/app/api/v1/routers/registry.py` - register the route owner when a subrouter is introduced.
- `backend/app/services/api_contracts/admin/audit.py` - add admin replay snapshot request and response contracts.
- `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/openapi-before.json` - baseline evidence.
- `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/openapi-after.json` - final evidence.
- `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/routes-after.txt` - route inventory evidence.
- `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/access-control.txt` - auth evidence.
- `_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/validation.txt` - validation evidence.

Likely tests:

- `backend/tests/api/admin/test_replay_snapshot_v1_api.py` - authorized, denied, missing, expired and purged HTTP behavior.
- `backend/tests/architecture/test_admin_replay_snapshot_v1_public_exposure.py` - OpenAPI, app.routes and public path absence.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no persistence schema is created.
- `backend/app/api/v1/routers/public/**` - out of scope; no public route is added.
- `backend/app/api/v1/routers/admin/llm/observability.py` - existing LLM observability endpoints must remain stable.
- `backend/app/infra/db/**` - out of scope; CS-295 owns storage and CS-296 owns lifecycle service behavior.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `pytest -q backend/tests/api/admin/test_replay_snapshot_v1_api.py`
- VC2: `pytest -q backend/tests/architecture/test_admin_replay_snapshot_v1_public_exposure.py`
- VC3: `$env:PYTHONPATH='backend'; python -c "from app.main import app; paths=app.openapi()['paths']; assert '/v1/admin/audit/replay_snapshot_v1/{snapshot_id}' in paths"`
- VC4: `$env:PYTHONPATH='backend'; python -c "from app.main import app; assert '/v1/admin/audit/replay_snapshot_v1/{snapshot_id}' in [getattr(r,'path','') for r in app.routes]"`
- VC5: `$env:PYTHONPATH='backend'; python -c "from app.main import app; assert all(p.startswith('/v1/admin/audit') for p in app.openapi()['paths'] if 'replay_snapshot_v1' in p)"`
- VC6: `rg -n "/v1/replay_snapshot_v1|/v1/public/replay_snapshot_v1|/v1/support/replay_snapshot_v1|/replay_snapshot_v1" backend/app frontend/src`
- VC7: `rg -n "raw_prompt|birth_date|birth_time|birth_place|latitude|longitude|email|password|api_key|payload_enc" backend/tests/api/admin`
- VC8: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/openapi-after.json').exists()"`
- VC9: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-297-expose-internal-admin-replay-snapshot-v1-api/evidence/validation.txt').exists()"`
- VC10: `ruff format .`
- VC11: `ruff check .`
- VC12: `python -B -m pytest -q backend\tests\api\admin backend\tests\architecture --tb=short`
- VC13: `pytest -q`

Before VC1 through VC5, VC8 through VC13, activate the venv with `. .\.venv\Scripts\Activate.ps1`.
Run every validation command from the repository root.

## Regression Risks

- Replay runtime could be exposed as a public or client-facing debug feature.
- Route handlers could duplicate CS-296 lifecycle behavior instead of calling the canonical service.
- API responses could leak raw replay payload, identifiers, coordinates, prompts, secrets or encrypted bytes.
- Non-admin users could receive metadata through a route missing the approved admin dependency.
- OpenAPI could publish a public replay route or generated-client surface.
- Manual purge could skip audit recording or mutate unrelated replay diagnostics.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python virtual environment before every Python command.
- Keep documentation comments and public docstrings in French for new or significantly modified applicative files.
- Keep all `replay_snapshot_v1` API routes under `/v1/admin/audit`.
- Keep route handlers thin and delegate lifecycle behavior to the CS-296 canonical service.
- Persist validation output under the CS-297 evidence folder before requesting review.

## References

- `_story_briefs/cs-297-expose-internal-admin-replay-snapshot-v1-api.md`
- `backend/app/api/v1/routers/admin/audit.py`
- `backend/app/api/v1/routers/admin/chart_diagnostics.py`
- `backend/app/api/v1/routers/admin/llm/observability.py`
- `backend/app/api/v1/routers/registry.py`
- `backend/app/services/api_contracts/admin/audit.py`
- `_condamad/stories/CS-270-internal-role-model/00-story.md`
- `_condamad/stories/CS-271-admin-data-permission-matrix/00-story.md`
- `_condamad/stories/CS-296-replay-snapshot-v1-service-retention-purge/00-story.md`
- `_condamad/stories/regression-guardrails.md`
