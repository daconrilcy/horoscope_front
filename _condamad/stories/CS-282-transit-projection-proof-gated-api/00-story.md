# Story CS-282 transit-projection-proof-gated-api: Expose Transit Projection Only After Proof Gate
Status: done

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-282-expose-transit-projection-only-after-proof-gate.md`.
- Related dependency: CS-280 must provide internal `transit_chart_v1` runtime evidence before exposure work starts.
- Related dependency: CS-281 must provide `transit_client_projection_v1` contract evidence before exposure work starts.
- Related dependency: CS-266 governs public OpenAPI exposure guards.
- Existing owner found: `backend/app/domain/prediction/public_projection.py` owns an existing projection pattern.
- Existing owner found: `backend/app/services/entitlement/b2c_runtime_gate.py` owns B2C runtime gate behavior.
- Existing owner found: `backend/tests/architecture/test_api_contract_neutrality.py` owns public OpenAPI neutrality checks.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: transit projection must become client-accessible only after proof, projection, audit and plan gates are validated.
- Source-alignment evidence: PASS; ACs preserve proof-gated exposure, controlled projection shape and B2C segmentation.

## Objective

Expose one controlled backend API projection for client transits only after CS-280, CS-281 and proof-gate evidence are validated.

The implementation must block exposure when required proof is missing, return only the client projection, respect B2C plans and keep raw runtime data private.

## Target State

- A canonical public API route exposes `transit_client_projection_v1` after validating the proof gate.
- The route refuses access before CS-280 and CS-281 evidence artifacts prove runtime and projection readiness.
- The response contains only client-safe projection fields, degraded states and plan-scoped content.
- Free, basic and premium users receive only their authorized projection depth.
- OpenAPI exposes the public projection route without raw `transit_chart_v1`, graph traces, debug fields or internal proof payloads.
- Tests prove authorization, blocked states, degraded states, public schema shape and raw runtime non-exposure.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-282-expose-transit-projection-only-after-proof-gate.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-282`.
- Evidence 3: `_condamad/stories/CS-280-internal-transit-runtime/00-story.md` - runtime dependency boundary inspected.
- Evidence 4: `_condamad/stories/CS-281-transit-client-projection-by-plan/00-story.md` - projection dependency boundary inspected.
- Evidence 5: `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md` - OpenAPI guard dependency inspected.
- Evidence 6: `backend/app/domain/prediction/public_projection.py` - existing projection ownership pattern found.
- Evidence 7: `backend/app/services/entitlement/b2c_runtime_gate.py` - existing B2C gate ownership found.
- Evidence 8: `backend/tests/architecture/test_api_contract_neutrality.py` - public API neutrality owner found.
- Evidence 9: guardrail resolver run for backend API, transit projection, OpenAPI, proof gate and plan segmentation scope.
- Source-alignment evidence: PASS; final story keeps exposure conditional on proof evidence and forbids raw runtime output.

## Domain Boundary

- Domain: backend-api
- In scope:
  - Public backend API route for `transit_client_projection_v1`.
  - Proof-gate verification before route success.
  - B2C plan segmentation for free, basic and premium transit projection payloads.
  - Client response states for unavailable, degraded, unauthorized and proof-blocked outcomes.
  - OpenAPI public schema for the controlled projection only.
  - Backend API, service and architecture tests proving the exposure boundary.
- Out of scope:
  - Frontend UI, database schema, migrations, auth model redesign, i18n, styling, build tooling and fixed-star publication.
  - Raw `transit_chart_v1` runtime exposure, admin expert projection, LLM provider calls and new product pricing.
- Explicit non-goals:
  - No frontend route, screen, CSS, browser flow or generated client work.
  - No DB table, migration, replay storage, cache layer or entitlement model redesign.
  - No raw runtime payload, graph trace, debug object, internal proof payload or fixed-star output in public responses.
  - No bypass of CS-280, CS-281 or CS-266 evidence gates.

## Operation Contract

- Operation type: create
- Primary archetype: api-contract-change
- Archetype reason: the story adds a public API route with OpenAPI, authorization and JSON response contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only one canonical client transit projection route.
  - Return success only after CS-280, CS-281 and proof-gate evidence validation.
  - Expose only `transit_client_projection_v1` client-safe fields.
  - Keep raw runtime, trace, debug, fixed-star and internal proof payloads private.
  - Keep frontend, DB, migrations, i18n, styling and build tooling unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-280 or CS-281 proof artifacts do not exist or fail validation at implementation time.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `TestClient` and proof artifact checks prove runtime API behavior. |
| Baseline Snapshot | yes | OpenAPI before and after artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | API, projection, proof gate and B2C plan enforcement require separate canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this single canonical route. |
| Contract Shape | yes | The route has exact status codes, client states and JSON response fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Forbidden raw transit runtime and alternate public paths must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The public route is registered once. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes`; targeted `pytest`. |
| AC2 | OpenAPI exposes the controlled route. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()`; targeted `pytest`. |
| AC3 | Proof gate blocks missing evidence. | Evidence profile: json_contract_shape; `TestClient`; `pytest -q backend/app/tests/integration/test_transit_projection_api.py`. |
| AC4 | The success payload is client-safe. | Evidence profile: json_contract_shape; `pytest -q backend/app/tests/integration/test_transit_projection_api.py`. |
| AC5 | Raw runtime fields stay private. | Evidence profile: targeted_forbidden_symbol_scan; `python` checks `app.openapi()`; `rg` checks API and contract paths. |
| AC6 | B2C plan depth is enforced. | Evidence profile: json_contract_shape; `pytest -q backend/app/tests/integration/test_transit_projection_api.py`. |
| AC7 | Client degraded states are explicit. | Evidence profile: api_error_shape_contract; `TestClient`; `pytest -q backend/app/tests/integration/test_transit_projection_api.py`. |
| AC8 | Dependency evidence is required. | Evidence profile: baseline_before_after_diff; `python` checks CS-280 and CS-281 proof paths. |
| AC9 | Public exposure guard tests cover transits. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`. |
| AC10 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-282 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect existing projection, entitlement, API registry and proof files before creating new code. (AC: AC1, AC4, AC6)
- [ ] Task 2: Add the canonical public API route for `transit_client_projection_v1`. (AC: AC1, AC2)
- [ ] Task 3: Add a proof-gate service that validates CS-280, CS-281 and runtime proof artifacts before success. (AC: AC3, AC8)
- [ ] Task 4: Build the client-safe response from the existing projection contract owner. (AC: AC4, AC5)
- [ ] Task 5: Enforce free, basic and premium projection depth through the existing B2C gate owner. (AC: AC6)
- [ ] Task 6: Return explicit client states for unavailable, degraded, unauthorized and proof-blocked outcomes. (AC: AC3, AC7)
- [ ] Task 7: Extend OpenAPI and architecture guards for transit public exposure. (AC: AC2, AC5, AC9)
- [ ] Task 8: Add integration tests with `TestClient` for proof gate, plan segmentation and forbidden fields. (AC: AC3, AC4, AC6, AC7)
- [ ] Task 9: Persist OpenAPI, dependency proof, validation and source checklist artifacts. (AC: AC8, AC10)

## Files to Inspect First

- `_story_briefs/cs-282-expose-transit-projection-only-after-proof-gate.md` - source brief.
- `_condamad/stories/CS-280-internal-transit-runtime/00-story.md` - runtime proof dependency.
- `_condamad/stories/CS-281-transit-client-projection-by-plan/00-story.md` - projection contract dependency.
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md` - OpenAPI guard dependency.
- `backend/app/api/v1/routers/registry.py` - canonical route registration owner.
- `backend/app/api/v1/routers/public/entitlements.py` - existing public route style and dependency pattern.
- `backend/app/domain/prediction/public_projection.py` - existing projection pattern to reuse before creating transit projection code.
- `backend/app/services/entitlement/b2c_runtime_gate.py` - B2C runtime gate owner.
- `backend/app/services/entitlement/public_entitlements.py` - public entitlement query behavior.
- `backend/tests/architecture/test_api_contract_neutrality.py` - public API exposure guard owner.
- `backend/app/tests/integration/test_transit_projection_api.py` - expected implementation-created integration test path.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `app.routes`, `app.openapi()` and `TestClient`.
  - `pytest -q backend/app/tests/integration/test_transit_projection_api.py`.
  - `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`.
  - Loaded dependency proof artifacts from CS-280 and CS-281 evidence directories.
- Secondary evidence:
  - Targeted `rg` scans for raw runtime fields, alternate transit paths and forbidden public schema tokens.
- Static scans alone are not sufficient for this story because:
  - route registration, OpenAPI exposure, proof blocking, plan behavior and error shapes must be proven from the loaded app.

## Contract Shape

- Contract type:
  - Public API route and OpenAPI path for controlled client transit projection.
- Fields:
  - `projection_id`: exact value `transit_client_projection_v1`.
  - `status`: one of `available`, `degraded`, `unavailable`, `unauthorized` or `proof_blocked`.
  - `plan_code`: B2C plan code used to shape the projection.
  - `content`: client-safe transit projection sections allowed for the plan.
  - `supporting_facts`: client-readable fact references without raw runtime objects.
  - `degraded_reason`: stable client state reason when status is not `available`.
  - `proof_refs`: public-safe proof reference IDs, not internal proof payloads.
  - `projection_hash`: stable hash of the client projection payload.
- Required fields:
  - `projection_id`
  - `status`
  - `plan_code`
  - `content`
  - `supporting_facts`
  - `proof_refs`
  - `projection_hash`
- Optional fields:
  - `degraded_reason`
  - `upgrade_hint`
- Status codes:
  - `200` for successful available or degraded projection responses.
  - `403` for unauthorized plan access.
  - `409` for proof-blocked exposure.
  - `503` for unavailable upstream runtime or proof service state.
- Serialization names:
  - JSON keys are emitted exactly as named in this contract.
- Frontend type impact:
  - none; no frontend generated client or UI source is touched.
- Generated contract impact:
  - `app.openapi()` must expose the controlled route and must not expose raw `transit_chart_v1` internals.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-282-transit-projection-proof-gated-api/evidence/openapi-before.json`
  - `_condamad/stories/CS-282-transit-projection-proof-gated-api/evidence/routes-before.txt`
  - `_condamad/stories/CS-282-transit-projection-proof-gated-api/evidence/dependency-proof-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-282-transit-projection-proof-gated-api/evidence/openapi-after.json`
  - `_condamad/stories/CS-282-transit-projection-proof-gated-api/evidence/routes-after.txt`
  - `_condamad/stories/CS-282-transit-projection-proof-gated-api/evidence/dependency-proof-after.md`
- Expected invariant:
  - The only intended public API surface delta is the canonical controlled transit projection route.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Transit projection route | `backend/app/api/v1/routers/public/transit_projection.py` | admin, ops or frontend source |
| Route registration | `backend/app/api/v1/routers/registry.py` | ad hoc app mounting |
| Response contract | `backend/app/services/api_contracts/public/transit_projection.py` | route-local dict literals |
| Projection assembly | backend service or domain owner derived from CS-281 contract | API handler business logic |
| Proof gate | backend service owner for transit projection proof validation | frontend or route-local checks |
| B2C plan enforcement | existing entitlement gate services | projection builder bypass |
| OpenAPI exposure tests | `backend/tests/architecture/test_api_contract_neutrality.py` | frontend tests |
| Evidence artifacts | `_condamad/stories/CS-282-transit-projection-proof-gated-api/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse the existing API v1 router registry and public router patterns.
- Reuse CS-281 `transit_client_projection_v1` contract vocabulary for plan-specific client fields.
- Reuse CS-280 runtime proof terminology and evidence artifact expectations for proof-gate validation.
- Reuse existing B2C entitlement gate services instead of adding a transit-only plan model.
- Reuse centralized API error helpers and public API contract modules instead of route-local response envelopes.
- Reuse OpenAPI neutrality guard patterns from CS-266 and `test_api_contract_neutrality.py`.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy public transit route path may be added.
- No compatibility public transit route path may be added.
- No fallback route path may expose transit data.
- Do not add aliases, shims or wrappers for the same transit projection route.
- Do not expose raw `transit_chart_v1`, graph traces, debug fields, internal proof payloads or fixed-star data.
- Do not duplicate B2C plan segmentation outside the existing entitlement gate owner.
- Forbidden public route fragments:
  - `/transit/raw`
  - `/transits/raw`
  - `/transit_chart_v1`
  - `/transit-debug`
  - `/fixed-stars/transits`
- Forbidden public schema tokens:
  - `TransitChartRuntime`
  - `transit_chart_v1`
  - `execution_trace`
  - `debug_payload`
  - `fixed_star_conjunctions`

## Reintroduction Guard

- Guard exact route registration with `app.routes` so only the canonical public projection route is added.
- Guard public OpenAPI with `app.openapi()` so forbidden raw runtime and debug schema tokens stay absent.
- Guard proof-gate bypass by testing missing CS-280 and CS-281 evidence paths with `TestClient`.
- Guard plan bypass by testing free, basic and premium payload depth from the same route.
- Guard repository drift with targeted `rg` scans over API, service contract, tests and frontend source paths.
- The only allowed surface delta is the controlled transit projection API, its backend tests and its story evidence artifacts.

## Regression Guardrails

Scope vector:

- backend-api route creation: yes;
- public OpenAPI contract: yes;
- transit proof gate: yes;
- B2C plan segmentation: yes;
- frontend UI, DB, auth model, i18n, style, build and migration: no.

Selected guardrails:

| Guardrail | Local invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Route ownership stays in canonical API v1 structure. | `app.routes`; targeted `pytest`. |
| RG-003 `converge-api-v1-route-architecture` | API v1 route registration uses the canonical registry. | `app.routes`; OpenAPI snapshot. |
| RG-022 `align-prompt-generation-story-validation-paths` | Validation paths remain concrete and collected. | `pytest`; validation artifact. |
| Registry gap | No exact `transit_client_projection_v1` exposure guardrail exists. | Story-local proof and API guards. |

Non-applicable examples:

- RG-047 frontend inline styles are out of scope because no TSX or CSS file is modified.
- RG-052 CSS namespace migration is out of scope because no style or build output is touched.
- RG-041 entitlement documentation is out of scope because this story enforces runtime plan gates, not docs maintenance.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| OpenAPI before snapshot | `_condamad/stories/CS-282-transit-projection-proof-gated-api/evidence/openapi-before.json` | Capture public OpenAPI baseline. |
| OpenAPI after snapshot | `_condamad/stories/CS-282-transit-projection-proof-gated-api/evidence/openapi-after.json` | Capture controlled route schema. |
| Routes before snapshot | `_condamad/stories/CS-282-transit-projection-proof-gated-api/evidence/routes-before.txt` | Capture runtime route baseline. |
| Routes after snapshot | `_condamad/stories/CS-282-transit-projection-proof-gated-api/evidence/routes-after.txt` | Capture runtime route delta. |
| Dependency proof report | `_condamad/stories/CS-282-transit-projection-proof-gated-api/evidence/dependency-proof-after.md` | Prove CS-280 and CS-281 readiness. |
| Validation output | `_condamad/stories/CS-282-transit-projection-proof-gated-api/evidence/validation.txt` | Keep lint, tests and scan output. |
| Source checklist | `_condamad/stories/CS-282-transit-projection-proof-gated-api/evidence/source-checklist.md` | Record source and dependency coverage. |
| Review output | `_condamad/stories/CS-282-transit-projection-proof-gated-api/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this single canonical route.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/api/v1/routers/public/transit_projection.py` - expected implementation-created public route.
- `backend/app/api/v1/routers/registry.py` - register the canonical public route.
- `backend/app/services/api_contracts/public/transit_projection.py` - expected implementation-created response contract.
- `backend/app/services/transit_projection/proof_gate.py` - expected implementation-created proof validation service.
- `backend/app/services/transit_projection/client_projection.py` - expected implementation-created projection service.
- `backend/tests/architecture/test_api_contract_neutrality.py` - extend OpenAPI public exposure guards.
- `backend/app/tests/integration/test_transit_projection_api.py` - cover route behavior, proof gate and plan segmentation.
- `_condamad/stories/CS-282-transit-projection-proof-gated-api/evidence/openapi-before.json` - persist baseline evidence.
- `_condamad/stories/CS-282-transit-projection-proof-gated-api/evidence/openapi-after.json` - persist after evidence.
- `_condamad/stories/CS-282-transit-projection-proof-gated-api/evidence/validation.txt` - persist validation output.
- `_condamad/stories/CS-282-transit-projection-proof-gated-api/evidence/source-checklist.md` - persist source coverage.

Likely tests:

- `backend/app/tests/integration/test_transit_projection_api.py` - TestClient route, proof gate, plan and response-shape coverage.
- `backend/tests/architecture/test_api_contract_neutrality.py` - OpenAPI and route exposure guard coverage.

Files not expected to change:

- `frontend/src/**` - out of scope; client states are API response states for this story.
- `backend/migrations/**` - out of scope; no persistence schema is touched.
- `backend/app/infra/**` - out of scope; no external adapter or DB repository is touched.
- `backend/app/domain/astrology/fixed_stars/**` - out of scope; no fixed-star public transit output is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `pytest -q app/tests/integration/test_transit_projection_api.py`
- VC6: `pytest -q tests/architecture/test_api_contract_neutrality.py`
- VC7: `pytest -q`
- VC8: `python -c "from app.main import app; assert any('/transit' in getattr(r, 'path', '') for r in app.routes)"`
- VC9: `python -c "from app.main import app; assert 'transit_client_projection_v1' in str(app.openapi())"`
- VC10: `python -c "from app.main import app; data=str(app.openapi()); assert 'TransitChartRuntime' not in data"`
- VC11: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-280-internal-transit-runtime').exists()"`
- VC12: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-281-transit-client-projection-by-plan').exists()"`
- VC13: `rg -n "transit_chart_v1|TransitChartRuntime|execution_trace|debug_payload" app/api app/services/api_contracts`
- VC14: `rg -n "/transit/raw|/transits/raw|/transit_chart_v1|/transit-debug|/fixed-stars/transits" app tests`
- VC15: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-282-transit-projection-proof-gated-api/evidence/validation.txt').exists()"`
- VC16: `cd ..\frontend`
- VC17: `npm test -- --run`
- VC18: `npm run lint`

Run VC16 to VC18 only if the implementation changes frontend files despite the mono-domain boundary.

## Regression Risks

- Transit data may become public before CS-280 and CS-281 evidence is validated.
- The route may leak raw runtime, graph trace, debug, internal proof or fixed-star fields through OpenAPI.
- B2C plan differences may drift into debug access instead of client-safe projection depth.
- Proof-blocked or degraded states may be represented as successful available projections.
- A route handler may accumulate business logic instead of delegating proof, projection and entitlement decisions.
- Frontend, DB, migration or product-pricing work may enter this backend API story.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python, Ruff or Pytest command in this repository.
- Inspect existing projection and entitlement owners before adding any new contract, service, model, route or test.
- Stop before implementation if CS-280 or CS-281 evidence artifacts are missing or fail the proof-gate checks.
- Keep client states in API response contracts; do not add frontend UI unless a separate story authorizes that domain.
- Persist the required evidence artifacts before moving the story to review.

## References

- `_story_briefs/cs-282-expose-transit-projection-only-after-proof-gate.md`
- `_condamad/stories/CS-280-internal-transit-runtime/00-story.md`
- `_condamad/stories/CS-281-transit-client-projection-by-plan/00-story.md`
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/00-story.md`
- `backend/app/domain/prediction/public_projection.py`
- `backend/app/services/entitlement/b2c_runtime_gate.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/regression-guardrails.md`
