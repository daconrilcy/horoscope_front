# Story CS-266 openapi-internal-public-exposure-guards: Add OpenAPI Internal Public Exposure Guards
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-266-add-openapi-internal-public-exposure-guards.md`.
- Selected mode: Repo-informed story in Fast Story Writer Mode.
- Problem statement: public OpenAPI must not expose internal admin, expert, techno, debug, runtime, or trace projections.
- Source stakes: prevent accidental client contract exposure, preserve controlled access errors, and keep internal projection contracts non-public.
- Source alignment evidence: objective, ACs, tasks, evidence, validation plan, and guardrails map to the source brief without narrowing scope.

## Objective

Add backend OpenAPI exposure guards proving that internal projection contracts remain absent from public OpenAPI and protected at route level.

## Target State

- The public OpenAPI document is scanned by deterministic tests for forbidden internal projection tokens.
- Internal route families are mapped from `app.routes` and remain protected by their existing authorization dependencies.
- Public and internal OpenAPI responsibilities are documented in the backend architecture or API contract documentation.
- Existing public API behavior stays unchanged apart from stronger validation coverage.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-266-add-openapi-internal-public-exposure-guards.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-266`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted guardrail IDs resolved from backend API and OpenAPI scope.
- Evidence 4: `backend/app/main.py` - loaded FastAPI `app` exposes `app.openapi()` and includes API v1 routers.
- Evidence 5: `backend/app/api/v1/routers/registry.py` - canonical API v1 router registry exists.
- Evidence 6: `backend/tests/architecture/test_api_contract_neutrality.py` - existing OpenAPI neutrality tests cover runtime terms.
- Evidence 7: `backend/app/tests/integration/test_api_openapi_contract.py` - existing integration coverage checks public OpenAPI paths.

## Domain Boundary

- Domain: backend-api
- In scope:
  - Backend OpenAPI public/internal exposure guardrails.
  - Runtime checks using `app.openapi()`, `app.routes`, `pytest`, and `TestClient`.
  - Backend documentation separating public OpenAPI from internal admin, expert, techno, debug, and runtime contracts.
- Out of scope:
  - Frontend UI, database schema, auth strategy redesign, i18n, styling, build tooling, migrations, and business logic.
- Explicit non-goals:
  - No implementation of expert projections.
  - No B2B developer portal.
  - No global authorization strategy change.
  - No runtime trace exposure.

## Operation Contract

- Operation type: create
- Primary archetype: api-contract-change
- Archetype reason: the story adds backend API contract guards for public OpenAPI exposure and protected internal route surfaces.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only OpenAPI exposure tests, route protection assertions, documentation, and evidence artifacts.
  - Keep existing public endpoint payloads and route paths unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: internal OpenAPI publication becomes a product requirement.
- Additional validation rules:
  - Public OpenAPI token scans must run against `app.openapi()` output, not only repository text.
  - Route protection checks must inspect `app.routes` and exercise protected endpoints with `TestClient`.
  - Existing API contract test files must be extended before adding parallel guard modules.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, and `TestClient` prove runtime API exposure behavior. |
| Baseline Snapshot | yes | OpenAPI before and after artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Canonical ownership is required for public, admin, ops, b2b, and internal route guards. |
| Allowlist Exception | no | No allowlist handling is authorized for forbidden public OpenAPI tokens. |
| Contract Shape | yes | The public OpenAPI artifact has exact forbidden-token absence rules. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Internal projection tokens must stay absent from public OpenAPI. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Public OpenAPI omits forbidden internal tokens. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`. |
| AC2 | Internal routes stay protected. | Evidence profile: runtime_openapi_contract; `TestClient`; `pytest -q backend/app/tests/integration/test_api_openapi_contract.py`. |
| AC3 | Public route inventory is mapped. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` route family prefixes. |
| AC4 | Public OpenAPI schema is snapshot-checked. | Evidence profile: openapi_before_after_snapshot; `python` writes and compares `app.openapi()` evidence JSON. |
| AC5 | Forbidden token scan is automated. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n` scans the exact forbidden token set. |
| AC6 | Public/internal OpenAPI separation is documented. | Evidence profile: baseline_before_after_diff; `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`. |
| AC7 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect existing OpenAPI and router guard tests before adding new coverage. (AC: AC1, AC2, AC3)
- [ ] Task 2: Extend the canonical OpenAPI neutrality test with the complete forbidden token set. (AC: AC1, AC5)
- [ ] Task 3: Add runtime route-family assertions from `app.routes` for public, admin, ops, b2b, and internal paths. (AC: AC2, AC3)
- [ ] Task 4: Add `TestClient` checks proving protected internal families reject unauthenticated access with controlled errors. (AC: AC2)
- [ ] Task 5: Persist OpenAPI before and after snapshots under this story evidence folder. (AC: AC4, AC7)
- [ ] Task 6: Document public OpenAPI versus internal projection ownership in the backend docs. (AC: AC6)
- [ ] Task 7: Run lint, targeted tests, full backend tests, and forbidden-token scans from the activated venv. (AC: AC1, AC2, AC5, AC7)

## Files to Inspect First

- `backend/tests/architecture/test_api_contract_neutrality.py` - existing public OpenAPI neutrality owner.
- `backend/app/tests/integration/test_api_openapi_contract.py` - existing OpenAPI integration owner.
- `backend/app/api/v1/routers/registry.py` - canonical API v1 route registration.
- `backend/app/main.py` - loaded FastAPI app and `app.openapi()` source.
- `backend/app/api/v1/routers/admin/**` - admin route protection owners.
- `backend/app/api/v1/routers/ops/**` - ops route protection owners.
- `backend/app/api/v1/routers/internal/**` - internal route protection owners.
- `backend/docs/**` - backend documentation owner for API contract separation.

## Runtime Source of Truth

- Primary source of truth:
  - `app.routes`, `app.openapi()`, and `TestClient`.
- Secondary evidence:
  - Targeted `rg` scans for forbidden OpenAPI tokens.
- Static scans alone are not sufficient for this story because:
  - Route registration, OpenAPI exposure, and authorization behavior must be proven from the loaded app.

## Contract Shape

- Contract type:
  - Public OpenAPI exposure guard and internal route protection guard.
- Fields:
  - `paths`: public OpenAPI path map from `app.openapi()`.
  - `components.schemas`: public OpenAPI schema map from `app.openapi()`.
  - `forbidden_public_tokens`: exact internal token set from the source brief.
- Required fields:
  - `paths`
  - `components.schemas`
  - `forbidden_public_tokens`
- Optional fields:
  - none
- Status codes:
  - `200` for successful `GET /openapi.json`.
  - `401` or `403` for protected internal route access without credentials.
- Serialization names:
  - Forbidden tokens are checked by exact string names from the source brief.
- Frontend type impact:
  - none; no frontend generated client is in scope.
- Generated contract impact:
  - `app.openapi()` must not expose forbidden internal tokens in public OpenAPI.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/evidence/openapi-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/evidence/openapi-after.json`
- Expected invariant:
  - The only intended API surface delta is stronger guard evidence; public route payload contracts remain unchanged.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Public OpenAPI exposure guards | `backend/tests/architecture/test_api_contract_neutrality.py` | Frontend tests or ad hoc scripts |
| OpenAPI integration smoke | `backend/app/tests/integration/test_api_openapi_contract.py` | Parallel unregistered test roots |
| API v1 route inventory | `backend/app/api/v1/routers/registry.py` | Direct router mounting outside registry |
| API contract docs | `backend/docs/**` | Story-only documentation |

## Mandatory Reuse / DRY Constraints

- Reuse existing OpenAPI neutrality and integration tests before creating new test modules.
- Reuse `app.openapi()`, `app.routes`, and `TestClient` rather than duplicating route discovery logic.
- Keep the forbidden token set centralized in one test helper or constant for the OpenAPI guard.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy public projection path may be added for internal contracts.
- No compatibility route path may be added for internal contracts.
- No fallback route path may be added for internal contracts.
- Forbidden public OpenAPI tokens:
  - `ChartObjectRuntimeData`
  - `chart_objects`
  - `CalculationGraph`
  - `execution_trace`
  - `replay_snapshot`
  - `llm_input`
  - `expert_technical_projection`
  - `astrology_full_data`
  - `admin_chart_diagnostics`
- Forbidden surfaces:
  - `frontend/src/**`
  - database models and migrations
  - global authentication strategy
  - runtime trace publication

## Reintroduction Guard

- Guard exact forbidden tokens in public OpenAPI with `app.openapi()` serialization checks.
- Guard alternate public exposure by scanning route paths from `app.routes`.
- Guard repository drift with the exact `rg` forbidden-token scan from the Validation Plan.
- The only allowed surface delta is test, documentation, and evidence coverage for OpenAPI exposure protection.

## Regression Guardrails

| Guardrail | Local invariant | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Route guards stay in canonical API router ownership. | `app.routes`; targeted `pytest`. |
| RG-003 `converge-api-v1-route-architecture` | API v1 route architecture uses the canonical registry. | `app.routes`; OpenAPI snapshot. |
| RG-007 `converge-admin-llm-observability-router` | Admin LLM observability remains owned by its router. | runtime route inventory. |

- Non-applicable examples:
  - RG-020 prompt ownership is out of scope because this story only guards OpenAPI exposure and route protection.
  - RG-022 prompt validation paths are out of scope because no prompt-generation story validation path is touched.
  - RG-041 entitlement documentation is out of scope because entitlement docs are not touched.
  - RG-047 frontend inline styles are out of scope because no frontend surface is touched.
  - RG-052 CSS namespace migration is out of scope because no styling surface is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| OpenAPI before snapshot | `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/evidence/openapi-before.json` | Capture public OpenAPI before implementation. |
| OpenAPI after snapshot | `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/evidence/openapi-after.json` | Capture public OpenAPI after implementation. |
| Validation log | `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/evidence/validation.txt` | Keep lint, tests, and scan output. |
| Review output | `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for forbidden public OpenAPI tokens.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/tests/architecture/test_api_contract_neutrality.py` - extend public OpenAPI forbidden token guards.
- `backend/app/tests/integration/test_api_openapi_contract.py` - add route protection and OpenAPI integration checks.
- `backend/docs/architecture/openapi-public-internal-boundary.md` - document public/internal OpenAPI separation.
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/evidence/openapi-before.json` - persist baseline evidence.
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/evidence/openapi-after.json` - persist after evidence.
- `_condamad/stories/CS-266-openapi-internal-public-exposure-guards/evidence/validation.txt` - persist validation output.

Likely tests:

- `backend/tests/architecture/test_api_contract_neutrality.py` - OpenAPI public exposure guards.
- `backend/app/tests/integration/test_api_openapi_contract.py` - OpenAPI and protected route behavior.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/infra/**` - out of scope; no persistence or external adapter is touched.
- `backend/alembic/**` - out of scope; no migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `pytest -q tests/architecture/test_api_contract_neutrality.py`
- VC6: `pytest -q app/tests/integration/test_api_openapi_contract.py`
- VC7: `pytest -q`
- VC8: `python -c "from app.main import app; assert '/openapi.json' in {getattr(r, 'path', '') for r in app.routes}"`
- VC9: `python -c "from app.main import app; data=str(app.openapi()); assert 'ChartObjectRuntimeData' not in data"`
- VC10: forbidden-token scan with `rg`:

```powershell
$tokens = "ChartObjectRuntimeData|chart_objects|CalculationGraph|execution_trace|replay_snapshot|llm_input|expert_technical_projection"
$tokens = "$tokens|astrology_full_data|admin_chart_diagnostics"
rg -n $tokens .\backend
```

## Regression Risks

- Public OpenAPI may expose an internal schema through a response model imported into a public route.
- Internal route families may appear in `app.routes` without an authorization dependency.
- Documentation may describe internal OpenAPI as public unless the ownership boundary is explicit.
- A broad token scan may catch intended internal code; the implementation must distinguish public OpenAPI output from backend internals.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python, Ruff, or Pytest command.
- Persist validation output under this story evidence folder.

## References

- `_story_briefs/cs-266-add-openapi-internal-public-exposure-guards.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/main.py`
- `backend/app/api/v1/routers/registry.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `backend/app/tests/integration/test_api_openapi_contract.py`
