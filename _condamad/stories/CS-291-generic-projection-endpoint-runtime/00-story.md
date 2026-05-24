# Story CS-291 generic-projection-endpoint-runtime: Implement Generic Projection Endpoint
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-291-implement-generic-projection-endpoint.md`.
- Related dependency: CS-263 defines the endpoint contract for `POST /v1/astrology/projections`.
- Related dependency: CS-264 defines optional projection persistence and `projection_hash`.
- Related dependency: CS-266 defines OpenAPI guards against internal projection exposure.
- Related dependency: CS-283 defines B2C projection entitlements for free, basic and premium plans.
- Related dependency: CS-285, CS-286 and CS-287 define the delivered public projection builders.
- Existing owner found: `backend/app/api/v1/routers/registry.py` owns API v1 router registration.
- Existing owner found: `backend/app/api/v1/routers/public/natal_interpretation.py` shows public authenticated route patterns.
- Existing owner found: `backend/app/infra/db/repositories/chart_result_repository.py` owns existing chart lookup semantics.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: `POST /v1/astrology/projections` is contracted but not implemented as the canonical B2C projection command.
- Source-alignment evidence: PASS; ACs preserve chart source selection, builder orchestration, entitlements, persistence and OpenAPI denial.

## Objective

Implement the canonical backend API route `POST /v1/astrology/projections` for B2C projection generation.

The implementation must orchestrate existing chart lookup or birth-input calculation, select only delivered public builders, enforce B2C entitlement
rules, apply optional persistence through CS-264, and prove with OpenAPI/runtime tests that internal projections remain unavailable to clients.

## Target State

- `POST /v1/astrology/projections` is registered on the loaded FastAPI app through the canonical API v1 router registry.
- Requests accept either an existing `chart_id` or a `birth_input` calculation source according to CS-263.
- The route calls the chart calculation service only when no reusable existing chart is selected.
- The route dispatches to an implemented public builder for `structured_facts_v1`, `beginner_summary_v1` or `client_interpretation_projection_v1`.
- Internal projection identifiers such as expert, admin, debug, raw runtime, prompt, audit and provider payload surfaces are rejected.
- Free, basic and premium plan access follows CS-283 and returns controlled denial errors for unauthorized projections or plan depth.
- `persist=true` writes eligible projection payloads only through the CS-264 persistence service and returns persisted identity/hash metadata.
- OpenAPI exposes only the public request and response schemas, without internal projection contracts or runtime payload schemas.
- No frontend UI, B2B API, new projection builder, migration, payment flow, prompt, provider integration or generated client is introduced.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-291-implement-generic-projection-endpoint.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-291`.
- Evidence 3: `_condamad/stories/CS-263-generic-projection-endpoint-contract/00-story.md` - endpoint contract dependency read.
- Evidence 4: `_condamad/stories/CS-264-projection-persistence-projection-hash/00-story.md` - persistence dependency read.
- Evidence 5: `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md` - OpenAPI guard dependency read.
- Evidence 6: `_condamad/stories/CS-283-b2c-projection-entitlement-policy/00-story.md` - entitlement dependency read.
- Evidence 7: `_condamad/stories/CS-285-structured-facts-v1-builder/00-story.md` - public builder dependency read.
- Evidence 8: `_condamad/stories/CS-286-beginner-summary-v1-builder/00-story.md` - public builder dependency read.
- Evidence 9: `_condamad/stories/CS-287-client-interpretation-projection-v1-builder-by-plan/00-story.md` - public builder dependency read.
- Evidence 10: `backend/app/api/v1/routers/registry.py` - canonical route registration owner found by targeted search.
- Evidence 11: `_condamad/stories/regression-guardrails.md` - scoped resolver output selected local backend API guardrails only.
- Source-alignment evidence: PASS; the story answers the source brief without creating builders, B2B API, frontend work or internal exposure.

## Domain Boundary

- Domain: backend-api
- In scope:
  - Backend API route implementation for `POST /v1/astrology/projections`.
  - Request and response schemas for the public B2C projection command.
  - Chart source orchestration for `chart_id` versus `birth_input`.
  - Runtime dispatch to delivered public projection builders only.
  - B2C entitlement checks for free, basic and premium plans.
  - Optional persistence through the CS-264 persistence service.
  - OpenAPI and runtime tests proving the public route and forbidden internal surfaces.
- Out of scope:
  - Frontend UI, B2B API, database schema, auth strategy redesign, i18n, styling, build tooling, migrations and generated clients.
  - New projection builders, expert/admin projections, prompt/provider integration, LLM final prose and payment plan mutation.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during this normal story generation.
- Explicit non-goals:
  - No frontend route, screen, client generation, CSS or browser validation.
  - No B2B endpoint, partner endpoint, admin endpoint or internal projection endpoint.
  - No new projection builder beyond the delivered CS-285 to CS-287 public builders.
  - No exposure of expert, admin, debug, raw runtime, prompt, provider or audit payload projections to B2C clients.

## Operation Contract

- Operation type: create
- Primary archetype: api-contract-change
- Archetype reason: the story adds a public API route with OpenAPI, JSON response, authorization and persistence behavior.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only `POST /v1/astrology/projections` as the public B2C projection command.
  - Reuse CS-263 request semantics, CS-264 persistence, CS-283 entitlements and CS-285 to CS-287 builders.
  - Keep internal projection identifiers unavailable to B2C clients.
  - Keep calculation, projection building, entitlement and persistence responsibilities separated.
  - Keep frontend, B2B, admin, DB migration, prompt, provider, i18n, style and build tooling surfaces unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: a required upstream builder or persistence service is missing at implementation time.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `pytest` and `TestClient` prove route registration and behavior. |
| Baseline Snapshot | yes | OpenAPI before and after artifacts prove the only allowed public API surface delta. |
| Ownership Routing | yes | Router, schemas, orchestration service, builders, entitlement and persistence owners must stay separate. |
| Allowlist Exception | no | No allowlist handling is authorized for this single canonical public route. |
| Contract Shape | yes | The endpoint has exact method, path, payload fields, status codes and JSON response rules. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Alternate paths and internal projection identifiers must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The loaded app registers `POST /v1/astrology/projections`. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes`; targeted `pytest`. |
| AC2 | OpenAPI exposes the public projection command. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()`; targeted `pytest`. |
| AC3 | Existing chart requests use `chart_id`. | Evidence profile: json_contract_shape; `TestClient`; `pytest -q backend/tests/api/test_projection_endpoint.py`. |
| AC4 | New chart requests use `birth_input`. | Evidence profile: json_contract_shape; `TestClient`; `pytest -q backend/tests/api/test_projection_endpoint.py`. |
| AC5 | Public projection builders are dispatched. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/unit/services/test_projection_endpoint_service.py`. |
| AC6 | Internal projection identifiers are denied. | Evidence profile: external_usage_blocker; `TestClient`; `pytest -q backend/tests/api/test_projection_authorization.py`. |
| AC7 | Free/basic/premium plan access is enforced. | Evidence profile: api_error_shape_contract; `pytest -q backend/tests/api/test_projection_authorization.py`. |
| AC8 | Optional persistence reuses CS-264. | Evidence profile: json_contract_shape; `pytest -q backend/tests/api/test_projection_persistence_endpoint.py`. |
| AC9 | OpenAPI hides forbidden internal surfaces. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()`; targeted `pytest`. |
| AC10 | Only the canonical projection route is authorized. | Evidence profile: route_absence_runtime; `python` checks `app.routes`; `rg` checks forbidden paths. |
| AC11 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-291 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect CS-263, CS-264, CS-266, CS-283 and CS-285 to CS-287 before editing. (AC: AC1, AC5, AC8, AC9)
- [ ] Task 2: Inspect existing router, auth, chart lookup and calculation owners before choosing implementation seams. (AC: AC1, AC3, AC4)
- [ ] Task 3: Add public request and response schemas for `POST /v1/astrology/projections`. (AC: AC2)
- [ ] Task 4: Register the route through the canonical API v1 router registry. (AC: AC1, AC10)
- [ ] Task 5: Add an orchestration service that resolves `chart_id` or computes from `birth_input`. (AC: AC3, AC4)
- [ ] Task 6: Dispatch only to delivered public projection builders. (AC: AC5, AC6)
- [ ] Task 7: Enforce CS-283 free, basic and premium access before returning projection payloads. (AC: AC6, AC7)
- [ ] Task 8: Reuse CS-264 persistence only when `persist=true` and the projection is eligible. (AC: AC8)
- [ ] Task 9: Add API tests for success, source selection, authorization, errors, persistence and OpenAPI. (AC: AC1, AC2, AC3, AC4, AC6, AC7, AC8, AC9)
- [ ] Task 10: Persist OpenAPI snapshots, validation output and source checklist under the CS-291 evidence folder. (AC: AC9, AC11)

## Files to Inspect First

- `_story_briefs/cs-291-implement-generic-projection-endpoint.md` - source brief.
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/00-story.md` - route contract dependency.
- `_condamad/stories/CS-264-projection-persistence-projection-hash/00-story.md` - persistence dependency.
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md` - public OpenAPI guard dependency.
- `_condamad/stories/CS-283-b2c-projection-entitlement-policy/00-story.md` - entitlement policy dependency.
- `_condamad/stories/CS-285-structured-facts-v1-builder/00-story.md` - first public builder dependency.
- `_condamad/stories/CS-286-beginner-summary-v1-builder/00-story.md` - second public builder dependency.
- `_condamad/stories/CS-287-client-interpretation-projection-v1-builder-by-plan/00-story.md` - third public builder dependency.
- `backend/app/api/v1/routers/registry.py` - canonical route registration owner.
- `backend/app/api/v1/routers/public/natal_interpretation.py` - public authenticated route pattern.
- `backend/app/services/api_contracts/public/astrology_engine.py` - existing public astrology request schema pattern.
- `backend/app/infra/db/repositories/chart_result_repository.py` - existing chart lookup owner.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `app.routes`, `app.openapi()` and `TestClient`.
  - CS-263 endpoint contract for request, response and error semantics.
  - CS-264 projection persistence service for `persist=true`.
  - CS-283 entitlement policy and existing entitlement services for plan authorization.
  - CS-285 to CS-287 delivered builders for public projection payloads.
- Secondary evidence:
  - Targeted `rg` scans for forbidden route paths and internal projection identifiers.
  - OpenAPI before and after snapshots persisted under the CS-291 evidence folder.
- Static scans alone are not sufficient because:
  - route registration, OpenAPI exposure, authorization behavior and persistence orchestration must be proven from the loaded app.

## Contract Shape

- Contract type:
  - API route and OpenAPI path.
- Method and path:
  - `POST /v1/astrology/projections`.
- Fields:
  - `chart_id`: optional existing chart identifier owned by the authenticated B2C user.
  - `birth_input`: optional birth payload used to calculate a chart when no reusable `chart_id` is supplied.
  - `projection_type`: required public projection identifier.
  - `projection_version`: required projection contract version.
  - `persist`: optional boolean controlling eligible persistence through CS-264.
  - `plan`: resolved from authenticated B2C entitlement state, not trusted from client payload.
- Required fields:
  - `projection_type`
  - `projection_version`
- Conditional fields:
  - exactly one accepted chart source is used from `chart_id` or `birth_input`.
- Optional fields:
  - `chart_id`
  - `birth_input`
  - `persist`
- Status codes:
  - `200` for successful non-persisted projection response.
  - `201` for successful eligible persisted projection response.
  - `400` for invalid chart source selection.
  - `401` for unauthenticated access.
  - `403` for unauthorized projection type or insufficient plan.
  - `404` for unknown or inaccessible `chart_id`.
  - `409` for unavailable calculation, builder or persistence dependency.
  - `422` for invalid payload shape or unsupported `projection_version`.
- Serialization names:
  - JSON keys are emitted as `chart_id`, `projection_type`, `projection_version`, `persisted`, `projection_hash`, `payload` and `metadata`.
- Frontend type impact:
  - none; no frontend source or generated client is touched.
- Generated contract impact:
  - `app.openapi()` must expose only the public route and must omit internal projection schemas.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/openapi-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/openapi-after.json`
  - `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/validation.txt`
  - `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/source-checklist.md`
- Expected invariant:
  - The only intended public API surface delta is `POST /v1/astrology/projections` with public schemas and controlled errors.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Projection route | `backend/app/api/v1/routers/public/projections.py` | admin, internal or B2B routers |
| API schemas | `backend/app/services/api_contracts/public/projections.py` | route-local untyped dictionaries |
| Endpoint orchestration | `backend/app/services/projections/projection_endpoint_service.py` | projection builders or route handler |
| Existing chart lookup | `backend/app/infra/db/repositories/chart_result_repository.py` | route-local SQL |
| Public builders | CS-285 to CS-287 builder modules | endpoint-local builder logic |
| Entitlement policy | CS-283 owner or existing entitlement services | client payload fields |
| Persistence | CS-264 persistence service | route-local persistence writes |
| Evidence artifacts | `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse CS-263 request semantics instead of inventing a second endpoint contract.
- Reuse CS-264 persistence service for every persisted projection write.
- Reuse CS-283 plan policy and existing entitlement services instead of trusting client-supplied plan data.
- Reuse CS-285 to CS-287 public builders and stop if a requested public builder is not delivered.
- Reuse the canonical API v1 router registry instead of mounting a parallel route registry.
- Do not add external packages, B2B routes, frontend helpers, DB migrations, new builders, prompts, providers or generated clients.

## No Legacy / Forbidden Paths

- No legacy route path may be added for this projection command.
- No compatibility route path may be added for this projection command.
- No fallback route path may be added for this projection command.
- Do not create aliases, shims, wrappers or parallel routes for the same endpoint.
- Do not build projection payloads inside the route handler.
- Do not expose internal projection identifiers or raw runtime payloads to B2C clients.
- Forbidden route paths:
  - `/v1/projections`
  - `/v1/astrology/projection`
  - `/v1/astrology/projections/internal`
  - `/v1/b2b/astrology/projections`
  - `/v1/admin/astrology/projections`
- Forbidden surfaces:
  - `frontend/src/**`
  - generated OpenAPI clients
  - DB migrations
  - prompt/provider files
  - new public projection builders

## Reintroduction Guard

- Guard target:
  - alternate projection route paths cannot appear in `app.routes` or OpenAPI;
  - internal projection identifiers cannot be accepted by `POST /v1/astrology/projections`;
  - entitlement checks cannot be bypassed by client-supplied plan fields;
  - `persist=true` cannot write outside the CS-264 persistence service;
  - builder selection cannot create payloads without the delivered CS-285 to CS-287 builders.
- Guard mechanism:
  - `app.routes`, `app.openapi()` and `TestClient` checks;
  - targeted authorization and persistence API tests;
  - OpenAPI before and after snapshots;
  - targeted `rg` scans for forbidden paths, client plan trust and internal projection identifiers.
- Guard owner:
  - `backend/app/api/v1/routers/public/projections.py`;
  - `backend/app/services/projections/projection_endpoint_service.py`;
  - `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/validation.txt`.
- Guard evidence:
  - `pytest -q backend/tests/api/test_projection_endpoint.py`;
  - `pytest -q backend/tests/api/test_projection_authorization.py`;
  - `pytest -q backend/tests/api/test_projection_persistence_endpoint.py`;
  - `python -c "from app.main import app; assert '/v1/astrology/projections' in app.openapi().get('paths', {})"`;
  - `python -c "from app.main import app; assert '/v1/astrology/projections' in {getattr(r, 'path', '') for r in app.routes}"`;

## Regression Guardrails

Scope vector:

- backend-api route creation: yes;
- API v1 router registry: yes;
- OpenAPI public contract: yes;
- B2C authorization and entitlement checks: yes;
- optional projection persistence through existing service: yes;
- frontend, DB migration, i18n, style, build and B2B implementation: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Route files stay organized by clear API responsibility. | router diff review; targeted `pytest`. |
| RG-003 `converge-api-v1-route-architecture` | API v1 route is mounted through the canonical registry. | `app.routes`; OpenAPI snapshots. |
| RG-004 `centralize-api-http-errors` | API errors must keep the shared HTTP error shape. | authorization/error tests; route review. |
| Registry gap | No exact `/v1/astrology/projections` guardrail exists in resolver output. | Story-local route and OpenAPI guards. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-007 admin LLM observability is out of scope because this route is public B2C astrology projection.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| OpenAPI before snapshot | `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/openapi-before.json` | Capture public OpenAPI before implementation. |
| OpenAPI after snapshot | `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/openapi-after.json` | Capture public OpenAPI after implementation. |
| Validation output | `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/validation.txt` | Keep lint, tests and route scans. |
| Source checklist | `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/source-checklist.md` | Record dependency and reuse-first checks. |
| Review output | `_condamad/stories/CS-291-generic-projection-endpoint-runtime/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this endpoint implementation story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/api/v1/routers/public/projections.py` - implement the public route.
- `backend/app/api/v1/routers/registry.py` - register the public projection router.
- `backend/app/services/api_contracts/public/projections.py` - define request and response schemas.
- `backend/app/services/projections/projection_endpoint_service.py` - orchestrate source selection, builders, entitlements and persistence.
- `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/openapi-before.json` - baseline OpenAPI artifact.
- `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/openapi-after.json` - after OpenAPI artifact.
- `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/source-checklist.md` - source and reuse evidence.

Likely tests:

- `backend/tests/api/test_projection_endpoint.py` - success and chart source behavior with `TestClient`.
- `backend/tests/api/test_projection_authorization.py` - internal projection and plan denial behavior.
- `backend/tests/api/test_projection_persistence_endpoint.py` - `persist=true` integration with CS-264 service.
- `backend/tests/api/test_projection_openapi.py` - OpenAPI path and public schema checks.
- `backend/tests/unit/services/test_projection_endpoint_service.py` - orchestration service and builder dispatch.
- `backend/tests/architecture/test_api_contract_neutrality.py` - forbidden internal OpenAPI exposure guard.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no database migration is touched.
- `backend/app/api/v1/routers/admin/**` - out of scope; no admin route is touched.
- `backend/app/api/v1/routers/b2b/**` - out of scope; no B2B route is touched.
- prompt and provider files - out of scope; no LLM generation behavior changes.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `pytest -q tests/api/test_projection_endpoint.py`
- VC6: `pytest -q tests/api/test_projection_authorization.py`
- VC7: `pytest -q tests/api/test_projection_persistence_endpoint.py`
- VC8: `pytest -q tests/api/test_projection_openapi.py`
- VC9: `pytest -q tests/unit/services/test_projection_endpoint_service.py`
- VC10: `pytest -q tests/architecture/test_api_contract_neutrality.py`
- VC11: `python -c "from app.main import app; assert '/v1/astrology/projections' in app.openapi().get('paths', {})"`
- VC12: `python -c "from app.main import app; assert '/v1/astrology/projections' in {getattr(r, 'path', '') for r in app.routes}"`
- VC13: `rg -n "/v1/projections|/v1/astrology/projection|/v1/b2b/astrology/projections|/v1/admin/astrology/projections" app tests`
- VC14: `rg -n "expert_technical_projection|astrology_full_data|admin_chart_diagnostics|raw runtime|provider_response" app tests`
- VC15: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-291-generic-projection-endpoint-runtime/evidence/validation.txt').exists()"`
- VC16: `pytest -q`

Before VC3 through VC16, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The endpoint could accept both `chart_id` and `birth_input` without a controlled source-selection error.
- Builder dispatch could create an undeclared projection instead of refusing unavailable builder dependencies.
- Internal projection identifiers could leak through request enums, response schemas or OpenAPI components.
- Plan checks could trust client payload data instead of the authenticated entitlement state.
- Optional persistence could bypass CS-264 and create a second write path or inconsistent `projection_hash`.
- A public API story could drift into frontend, B2B, admin, DB migration, prompt or provider work.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python, Ruff or Pytest command.
- Keep file-level comments and public or non-trivial docstrings in French for new or significantly modified backend files.
- Start with a reuse-first audit of existing contract, builder, entitlement, persistence and router owners.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-291-implement-generic-projection-endpoint.md`
- `_condamad/stories/CS-263-generic-projection-endpoint-contract/00-story.md`
- `_condamad/stories/CS-264-projection-persistence-projection-hash/00-story.md`
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md`
- `_condamad/stories/CS-283-b2c-projection-entitlement-policy/00-story.md`
- `_condamad/stories/CS-285-structured-facts-v1-builder/00-story.md`
- `_condamad/stories/CS-286-beginner-summary-v1-builder/00-story.md`
- `_condamad/stories/CS-287-client-interpretation-projection-v1-builder-by-plan/00-story.md`
- `backend/app/api/v1/routers/registry.py`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/app/infra/db/repositories/chart_result_repository.py`
- `_condamad/stories/regression-guardrails.md`
