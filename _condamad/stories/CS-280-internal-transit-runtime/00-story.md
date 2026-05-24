# Story CS-280 internal-transit-runtime: Implement Internal Transit Runtime
Status: ready-to-dev

## Trigger / Source

- Source reference: `_story_briefs/cs-280-implement-internal-transit-runtime.md`.
- Selected mode: Repo-informed story.
- Source problem statement: `transit_chart_v1` needs one testable internal runtime while client exposure remains closed.
- Source stakes:
  - Runtime work must reuse the existing astrology runtime owner instead of creating a parallel transit implementation.
  - Astronomical proof, doctrine limits and internal trace evidence must be present before any product-facing surface.
  - No client route, frontend screen, LLM interpretation or fixed-star exposure is authorized.
- Source-alignment evidence:
  - The objective, ACs, tasks, validation plan and guardrails map to runtime, proof, doctrine, trace and public-neutrality stakes.
  - Accepted assumption: CS-279 manifest files are expected but not present yet in this workspace checkout.

## Objective

Implement one canonical, testable backend-domain runtime for `transit_chart_v1` without exposing it to client or frontend surfaces.

## Target State

- `transit_chart_v1` has one internal runtime entry point under the astrology runtime domain.
- The runtime reuses existing graph, chart-object, aspect, astronomical proof and doctrine governance primitives.
- The runtime returns deterministic structural transit data for internal callers only.
- The runtime records bounded diagnostic trace keys that do not include narrative, user-facing copy or raw fixed-star exposure.
- API and frontend surfaces remain neutral: no route, OpenAPI schema, generated client or screen is added.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-280-implement-internal-transit-runtime.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-280`.
- Evidence 3: `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/00-story.md` - dependency story inspected.
- Evidence 4: `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py` - existing family registry includes `transit_chart_v1`.
- Evidence 5: `backend/app/domain/astrology/runtime/calculation_graph_runner.py` - existing graph runner and trace surface inspected.
- Evidence 6: `backend/app/domain/astrology/runtime/astronomical_proof.py` - proof gate and golden evidence owner inspected.
- Evidence 7: `backend/tests/architecture/test_api_contract_neutrality.py` - OpenAPI and route neutrality checks inspected.
- Evidence 8: guardrail resolver run for backend-domain transit runtime scope; no exact `transit_chart_v1` route guardrail was returned.
- Repository structure alert: `backend/app/domain/astrology/runtime/transit_chart_manifest.py` is absent in this workspace.
- Repository structure alert: `backend/tests/unit/domain/astrology/test_transit_chart_manifest.py` is absent in this workspace.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Internal runtime creation for `transit_chart_v1`.
  - Factory helpers or resolver behavior that build the runtime from existing astrology primitives.
  - Unit tests, architecture proof tests and persistent evidence artifacts for the internal runtime.
  - Controlled diagnostic traces that support review without client exposure.
- Out of scope:
  - Frontend UI, database schema, auth, i18n, styling, build tooling, migrations, API client generation and public routes.
  - LLM transit interpretation, narrative generation, product projection and fixed-star publication.
- Explicit non-goals:
  - No frontend route, screen, client generation or UI validation.
  - No public API endpoint, public serializer, OpenAPI transit schema or admin endpoint.
  - No durable cache, replay storage, DB model, migration or fixed-star transit output.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only an internal `transit_chart_v1` runtime and its tests.
  - Keep public API and frontend surfaces unchanged.
  - Reuse existing astrology runtime primitives before adding new runtime helpers.
- Deletion allowed: no
- Replacement allowed: no
- Additional validation rules:
  - Runtime evidence must include `pytest -q backend/tests/unit/domain/astrology/test_transit_chart_runtime.py`.
  - Public-neutrality evidence must include `app.openapi()`, `app.routes` and `TestClient`.
  - Architecture evidence must include an `AST guard` or bounded `rg` scan proving no public transit route was introduced.
- User decision required if: the runtime cannot be implemented without public route exposure or new external packages.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Runtime must be proven by unit tests, `AST guard`, loaded modules and public-neutrality checks. |
| Baseline Snapshot | yes | Before and after artifacts prove only the internal runtime surface changed. |
| Ownership Routing | yes | Canonical ownership prevents a parallel prediction or API transit runtime. |
| Allowlist Exception | no | No allowlist handling is authorized for this internal runtime. |
| Contract Shape | yes | The runtime payload, trace keys and doctrine limits need explicit structural fields. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Public transit routes, frontend surfaces and fixed-star exposure must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Existing transit ownership is reused. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/unit/domain/astrology/test_transit_chart_runtime.py`. |
| AC2 | The runtime returns structural transit objects. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_transit_chart_runtime.py`. |
| AC3 | Transit relationships are deterministic. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_transit_chart_runtime.py`. |
| AC4 | Astronomical proof references are emitted. | Evidence profile: baseline_before_after_diff; `pytest -q backend/tests/unit/domain/astrology/test_transit_chart_runtime.py`. |
| AC5 | Doctrine limits are documented. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks doctrine limit markers. |
| AC6 | Internal trace keys stay bounded. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_transit_chart_runtime.py`. |
| AC7 | Public API surface remains neutral. | Evidence profile: route_absence_runtime; `python` checks `app.openapi()` and `app.routes`; `TestClient` smoke. |
| AC8 | Client surfaces remain closed. | Evidence profile: repo_wide_negative_scan; `app.routes`; `app.openapi()`; `rg` checks frontend and API paths. |
| AC9 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks the story evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect existing transit, graph, chart-object and proof primitives before creating any runtime file. (AC: AC1)
- [ ] Task 2: Add the canonical internal runtime entry point for `transit_chart_v1`. (AC: AC1, AC2)
- [ ] Task 3: Build transiting chart objects through existing astrology runtime primitives. (AC: AC2)
- [ ] Task 4: Compute transit-to-natal relationships with deterministic structural fields. (AC: AC3)
- [ ] Task 5: Attach astronomical proof references from the existing proof owner. (AC: AC4)
- [ ] Task 6: Document doctrine limits in the runtime contract without narrative interpretation. (AC: AC5)
- [ ] Task 7: Emit bounded internal trace keys for runtime review and diagnostics. (AC: AC6)
- [ ] Task 8: Extend architecture tests proving no route, OpenAPI schema or frontend transit surface was added. (AC: AC7, AC8)
- [ ] Task 9: Persist validation and runtime evidence artifacts under the story evidence directory. (AC: AC9)

## Files to Inspect First

- `_story_briefs/cs-280-implement-internal-transit-runtime.md` - source brief.
- `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/00-story.md` - prerequisite manifest story.
- `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py` - current `transit_chart_v1` family declaration.
- `backend/app/domain/astrology/runtime/calculation_graph_runner.py` - graph execution and trace behavior.
- `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py` - trace shape owner.
- `backend/app/domain/astrology/runtime/astronomical_proof.py` - proof gate and golden evidence owner.
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - chart-object runtime payloads.
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` - reusable chart-object builder.
- `backend/app/domain/astrology/builders/aspect_runtime_builder.py` - reusable aspect runtime builder.
- `backend/app/domain/astrology/fixed_stars/fixed_star_conjunction_calculator.py` - forbidden fixed-star publication boundary.
- `backend/tests/architecture/test_api_contract_neutrality.py` - existing OpenAPI and route neutrality tests.
- `backend/tests/unit/domain/astrology/test_transit_chart_runtime.py` - expected implementation-created test path.
- `backend/app/domain/astrology/runtime/transit_chart_runtime.py` - expected implementation-created runtime path.

## Runtime Source of Truth

- Primary source of truth:
  - `pytest -q backend/tests/unit/domain/astrology/test_transit_chart_runtime.py`.
  - `AST guard` over runtime imports and forbidden API ownership.
  - Loaded `app.openapi()`, `app.routes` and `TestClient` for public-neutrality checks.
- Secondary evidence:
  - Targeted `rg` scans for public transit route, frontend and migration surfaces.
- Static scans alone are not sufficient for this story because:
  - Runtime behavior, proof links, trace fields and public API neutrality must be proven from executable code.

## Contract Shape

- Contract type:
  - Internal backend-domain runtime payload.
- Fields:
  - `family_code`: exact value `transit_chart_v1`.
  - `transiting_chart_objects`: tuple or immutable sequence of structural chart-object runtime data.
  - `transit_to_natal_relationships`: tuple or immutable sequence of deterministic relationship records.
  - `astronomical_proof_refs`: tuple of proof IDs or golden-case references from the existing proof owner.
  - `doctrine_limits`: tuple of explicit non-interpretive limits.
  - `trace`: bounded internal diagnostic keys for runtime review.
  - `public_exposure`: exact value `blocked`.
- Required fields:
  - `family_code`
  - `transiting_chart_objects`
  - `transit_to_natal_relationships`
  - `astronomical_proof_refs`
  - `doctrine_limits`
  - `trace`
  - `public_exposure`
- Optional fields:
  - none
- Status codes:
  - none because no HTTP route is in scope.
- Serialization names:
  - Internal field names must remain stable in Python and evidence snapshots.
- Frontend type impact:
  - none because no frontend generated client is in scope.
- Generated contract impact:
  - `app.openapi()` must not expose `transit_chart_v1`, transit runtime schemas or transit paths.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-280-internal-transit-runtime/evidence/openapi-before.json`
  - `_condamad/stories/CS-280-internal-transit-runtime/evidence/transit-runtime-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-280-internal-transit-runtime/evidence/openapi-after.json`
  - `_condamad/stories/CS-280-internal-transit-runtime/evidence/transit-runtime-after.json`
- Expected invariant:
  - The only intended surface delta is the internal backend-domain runtime and its tests.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Transit runtime | `backend/app/domain/astrology/runtime/transit_chart_runtime.py` | `backend/app/api/**` |
| Transit graph family | `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py` | `backend/app/domain/prediction/**` |
| Transit chart objects | existing astrology chart-object runtime builders | new duplicated chart-object model |
| Transit relationships | existing aspect and chart-object runtime primitives | public serializer or LLM prompt builder |
| Astronomical proof refs | `backend/app/domain/astrology/runtime/astronomical_proof.py` | transit runtime hardcoded proof tables |
| Doctrine limits | `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py` | transit narrative or product copy |
| Public neutrality tests | `backend/tests/architecture/test_api_contract_neutrality.py` | frontend test suite |
| Story evidence artifacts | `_condamad/stories/CS-280-internal-transit-runtime/evidence/` | application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse `astrology_graph_family_registry.py` for the `transit_chart_v1` family and owner status.
- Reuse chart-object runtime data and builders instead of defining a second chart-object payload model.
- Reuse aspect runtime or calculation primitives for transit-to-natal relationship structure.
- Reuse astronomical proof constants, golden-case references and gate vocabulary from `astronomical_proof.py`.
- Reuse doctrine governance vocabulary instead of embedding a transit-specific school policy.
- Reuse `test_api_contract_neutrality.py` patterns for `app.openapi()`, `app.routes` and `TestClient` checks.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy transit runtime path may be added outside the canonical astrology runtime owner.
- No compatibility route path may expose `transit_chart_v1` publicly.
- No fallback route, serializer, generated client or frontend page may expose transit data.
- Do not promote existing prediction temporal code as the canonical transit runtime.
- Do not duplicate chart-object, aspect, proof or doctrine primitives for transit-only use.
- Do not add public transit schemas to OpenAPI.
- Do not expose fixed stars through the transit runtime output.

## Reintroduction Guard

- Forbidden public route fragments:
  - `/transit`
  - `/transits`
  - `/temporal`
  - `/forecast`
- Forbidden public schema fragments:
  - `TransitChartRuntime`
  - `transit_chart_v1`
  - `TransitToNatal`
- Forbidden frontend surfaces:
  - `frontend/src/**/transit*`
  - `frontend/src/**/Transit*`
- Required deterministic guards:
  - `python -c "from app.main import app; assert 'transit_chart_v1' not in str(app.openapi())"`
  - `python -c "from app.main import app; assert all('transit' not in getattr(r, 'path', '') for r in app.routes)"`
  - `rg -n "transit_chart_v1|TransitChartRuntime|TransitToNatal" backend/app/api frontend/src backend/migrations`

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `Routeurs API v1` | API router ownership must stay untouched. | `app.routes`; `rg` API scan. |
| RG-022 `Plans de validation` | Backend tests and validation evidence must stay explicit. | `pytest`; validation artifact. |
| Registry gap | No exact `transit_chart_v1` runtime guardrail exists in resolver output. | Story-local runtime and API guards. |
| Non-applicable: RG-047 | Frontend inline styles are outside this backend-domain story. | Frontend remains untouched. |
| Non-applicable: RG-052 | CSS namespace migration is outside this backend-domain story. | No style files in scope. |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| OpenAPI before snapshot | `_condamad/stories/CS-280-internal-transit-runtime/evidence/openapi-before.json` | Prove API baseline. |
| OpenAPI after snapshot | `_condamad/stories/CS-280-internal-transit-runtime/evidence/openapi-after.json` | Prove API neutrality. |
| Runtime before status | `_condamad/stories/CS-280-internal-transit-runtime/evidence/transit-runtime-before.txt` | Record initial runtime absence. |
| Runtime after snapshot | `_condamad/stories/CS-280-internal-transit-runtime/evidence/transit-runtime-after.json` | Keep internal runtime payload. |
| API neutrality | `_condamad/stories/CS-280-internal-transit-runtime/evidence/api-neutrality.md` | Prove routes and OpenAPI stayed closed. |
| Validation output | `_condamad/stories/CS-280-internal-transit-runtime/evidence/validation.txt` | Keep validation transcript. |
| Source checklist | `_condamad/stories/CS-280-internal-transit-runtime/evidence/source-checklist.md` | Record brief coverage. |
| Review output | `_condamad/stories/CS-280-internal-transit-runtime/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this internal runtime.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/transit_chart_runtime.py` - expected implementation-created internal runtime.
- `backend/app/domain/astrology/runtime/transit_chart_manifest.py` - expected implementation-created or prerequisite manifest path.
- `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py` - reuse or unblock `transit_chart_v1` metadata.
- `backend/tests/unit/domain/astrology/test_transit_chart_runtime.py` - cover runtime payload, proof refs, doctrine limits and trace.
- `backend/tests/architecture/test_api_contract_neutrality.py` - extend public-neutrality checks for transit runtime.
- `_condamad/stories/CS-280-internal-transit-runtime/evidence/openapi-before.json` - persist API baseline.
- `_condamad/stories/CS-280-internal-transit-runtime/evidence/openapi-after.json` - persist API after snapshot.
- `_condamad/stories/CS-280-internal-transit-runtime/evidence/transit-runtime-after.json` - persist runtime payload.
- `_condamad/stories/CS-280-internal-transit-runtime/evidence/api-neutrality.md` - persist API neutrality proof.
- `_condamad/stories/CS-280-internal-transit-runtime/evidence/validation.txt` - persist validation output.
- `_condamad/stories/CS-280-internal-transit-runtime/evidence/source-checklist.md` - persist source coverage.

Likely tests:

- `backend/tests/unit/domain/astrology/test_transit_chart_runtime.py` - runtime, proof, doctrine, trace and reuse checks.
- `backend/tests/architecture/test_api_contract_neutrality.py` - app OpenAPI, route and TestClient neutrality checks.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no API route or public serializer is touched.
- `backend/migrations/**` - out of scope; no persistence schema is touched.
- `backend/app/domain/llm/**` - out of scope; no LLM transit interpretation is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `pytest -q backend/tests/unit/domain/astrology/test_transit_chart_runtime.py`
- VC2: `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`
- VC3: `python -c "from app.main import app; assert 'transit_chart_v1' not in str(app.openapi())"`
- VC4: `python -c "from app.main import app; assert all('transit' not in getattr(r, 'path', '') for r in app.routes)"`
- VC5: `python -c "from fastapi.testclient import TestClient; from app.main import app; assert TestClient(app).get('/openapi.json').status_code == 200"`
- VC6: `rg -n "transit_chart_v1|TransitChartRuntime|TransitToNatal" backend/app/api frontend/src backend/migrations`
- VC7: `rg -n "fixed_star|fixed-stars|fixed stars" backend/app/domain/astrology/runtime/transit_chart_runtime.py`
- VC8: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-280-internal-transit-runtime/evidence/validation.txt').exists()"`
- VC9: `ruff format .`
- VC10: `ruff check .`
- VC11: `pytest -q`

## Regression Risks

- Existing prediction temporal code may become a second canonical transit owner.
- Public API exposure may appear through a route, schema, generated client or admin shortcut.
- Astronomical proof may be represented as prose instead of reusable proof references.
- Doctrine-heavy interpretation may leak into structural runtime output.
- Fixed-star data may be exposed before product and proof gates authorize it.
- Internal traces may contain user-facing narrative or unstable raw payloads.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate the Python virtual environment before every Python command:
  - `.\.venv\Scripts\Activate.ps1`
- Run backend validation from `backend` after activation, matching the project workflow.
- Keep `transit_chart_v1` internal and non-public.
- Persist the evidence artifacts listed in this story before moving to review.

## References

- `_story_briefs/cs-280-implement-internal-transit-runtime.md`
- `_story_briefs/cs-279-define-transit-chart-v1-internal-manifest.md`
- `_condamad/stories/CS-279-transit-chart-v1-internal-manifest/00-story.md`
- `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`
- `backend/app/domain/astrology/runtime/calculation_graph_runner.py`
- `backend/app/domain/astrology/runtime/astronomical_proof.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
