# Story CS-249 chart-object-capability-taxonomy-matrix: Define Chart Object Capability And Object Taxonomy Matrix
Status: ready-to-review

## 1. Objective

Define one canonical backend-domain matrix for chart object capabilities and object taxonomy so astrology runtime code
stops relying on ad hoc `object_type` decisions for eligibility, scoring, interpretation and public projection policy.

## 2. Trigger / Source

- Source type: architecture-runtime-contract.
- Source reference: `_story_briefs/cs-249-chart-object-capability-taxonomy-matrix.md`.
- Architecture source: `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/03-story-candidates.md#SC-ARCH-004`.
- Remapped architecture item: `SC-ARCH-004`.
- Selected story writer mode: Fast Story Writer Mode.
- Source-alignment review: the story preserves the brief by covering all named object families, capability columns,
  explicit `needs-user-decision` values, branch guards, unchanged behavior and no new calculators.

## 3. Domain Boundary

This story belongs to one domain:

- Domain: backend-domain
- In scope:
  - canonical chart object capability matrix under `backend/app/domain/astrology/runtime`;
  - typed taxonomy entries for object family, canonical type, source kind and capability booleans;
  - coverage for Sun, Moon, classical planets, modern planets, ASC/MC/angles, lunar nodes, Lilith, apsides, lots,
    asteroids, Chiron, midpoints and fixed stars;
  - explicit `decision_status` values, including `needs-user-decision` for unresolved doctrine or product choices;
  - validation that every required family is classified exactly once;
  - a guard or architecture test preventing new unclassified families and unmanaged `object_type` branches;
  - targeted unit and architecture tests.
- Out of scope:
  - implementing lots, asteroids, Chiron or midpoints as calculators;
  - changing aspect orbs, fixed-star contact rules, scoring formulas, public projection, DB schema or migrations;
  - modifying API routes, OpenAPI payloads, frontend, auth, i18n, styles or build tooling;
  - choosing doctrine or product decisions for unresolved families.
- Explicit non-goals:
  - no frontend route, screen, client generation or UI validation;
  - no Alembic migration or persistence model;
  - no public JSON contract change;
  - no new calculator for lots, asteroids, Chiron, midpoints or fixed stars;
  - no registry enrichment in `_condamad/stories/regression-guardrails.md` during this story generation.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain capability matrix contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add one canonical typed capability matrix for chart object families.
  - Preserve existing runtime capabilities unless a value is only marked `needs-user-decision`.
  - Add validation and guards for complete classification and unmanaged family growth.
  - Keep public API, frontend, DB, migrations and public projection unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: a family capability cannot be represented without changing business behavior.
- Additional validation rules:
  - every required object family from the brief is represented exactly once.
  - every entry exposes `object_family`, `canonical_type`, `source_kind`, capability booleans and `decision_status`.
  - unknown or duplicate object families fail deterministic validation.
  - unresolved doctrine or product choices are marked `needs-user-decision`.
  - existing capability values from `ChartObjectRuntimeData` remain behavior-preserving.
  - architecture guards fail on new unmanaged `object_type` branches.
  - `app.routes`, `app.openapi()`, `pytest` and `TestClient` prove no public API delta.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | The matrix becomes the runtime source for object family capability classification. |
| Baseline Snapshot | yes | Before and after matrix artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Matrix ownership must stay under astrology runtime, not API, DB, frontend or docs-only paths. |
| Allowlist Exception | no | No allowlist handling is authorized for this single canonical matrix. |
| Contract Shape | yes | The taxonomy fields and capability columns are the core implementation contract. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Unclassified families and unmanaged `object_type` branches must stay blocked. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `backend/app/domain/astrology/runtime/chart_object_capability_taxonomy.py`;
  - `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`;
  - `backend/tests/architecture/test_chart_runtime_surface_guardrails.py`.
- Runtime/domain artifacts:
  - typed taxonomy entry contract;
  - required object family enum or tuple;
  - capability booleans matching current runtime concepts;
  - `decision_status` values for active and unresolved families;
  - resolver behavior for known and unknown families.
- Secondary evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_chart_object_capability_taxonomy.py`;
  - `pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py`;
  - `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`;
  - `AST guard`, `app.routes`, `app.openapi()` and `TestClient`.
- Static scans alone are not sufficient because:
  - classification completeness, unknown-family rejection and API neutrality must be proven from executable tests.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/evidence/taxonomy-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/evidence/taxonomy-after.json`
- Expected invariant:
  - the only allowed surface delta is an internal backend runtime capability matrix plus targeted tests and evidence.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Capability matrix | `backend/app/domain/astrology/runtime/chart_object_capability_taxonomy.py` | API routers, DB models, frontend |
| Runtime capability contract | `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` | duplicate taxonomy modules |
| Matrix tests | `backend/tests/unit/domain/astrology/test_chart_object_capability_taxonomy.py` | docs-only checks |
| Branch architecture guard | `backend/tests/architecture/test_chart_runtime_surface_guardrails.py` | broad manual review only |
| API neutrality proof | `backend/tests/architecture/test_api_contract_neutrality.py` | frontend smoke tests |

## 4e. Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this canonical backend-domain matrix.

## 4f. Contract Shape

- Contract type:
  - internal typed taxonomy matrix for chart object families;
  - no HTTP endpoint, public serializer or frontend type.
- Fields:
  - `object_family`;
  - `canonical_type`;
  - `source_kind`;
  - `positionable`;
  - `aspectable`;
  - `interpretable`;
  - `scorable`;
  - `dignity_eligible`;
  - `dominance_eligible`;
  - `public_projection`;
  - `decision_status`;
  - `motion_visibility`;
  - `house_rulership`;
  - `fixed_star_contact`.
- Required fields:
  - `object_family`;
  - `canonical_type`;
  - `source_kind`;
  - `positionable`;
  - `aspectable`;
  - `interpretable`;
  - `scorable`;
  - `dignity_eligible`;
  - `dominance_eligible`;
  - `public_projection`;
  - `decision_status`;
  - `motion_visibility`;
  - `house_rulership`;
  - `fixed_star_contact`.
- Required object families:
  - `sun`;
  - `moon`;
  - `classical_planet`;
  - `modern_planet`;
  - `angle`;
  - `lunar_node`;
  - `lilith`;
  - `apside`;
  - `lot`;
  - `asteroid`;
  - `chiron`;
  - `midpoint`;
  - `fixed_star`.
- Required decision values:
  - `active`;
  - `needs-user-decision`.
- Optional fields:
  - none.
- Status codes:
  - no HTTP endpoint, method or status code is changed.
- Serialization names:
  - no public JSON key is renamed or added.
- Frontend type impact:
  - none; no frontend contract changes are allowed.
- Generated contract impact:
  - `app.openapi()` must not expose the internal capability matrix.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## 4h. Reintroduction Guard

- Guard target:
  - no required object family is missing from the matrix;
  - no duplicate object family is accepted;
  - no unknown family is accepted by resolver behavior;
  - no new calculator appears for lots, asteroids, Chiron or midpoints;
  - no unmanaged `object_type` branch appears outside canonical projection owners;
  - no public API, OpenAPI, DB migration or frontend delta is introduced.
- Guard mechanism:
  - unit tests for required family completeness and field completeness;
  - unit tests for duplicate and unknown family rejection;
  - architecture test or AST guard for unmanaged `object_type` branches;
  - targeted `rg` scans for new calculator surfaces and public exposure;
  - `TestClient`, `app.routes` and `app.openapi()` API neutrality evidence.
- Guard owner:
  - `backend/tests/unit/domain/astrology/test_chart_object_capability_taxonomy.py`;
  - `backend/tests/architecture/test_chart_runtime_surface_guardrails.py`;
  - `backend/tests/architecture/test_api_contract_neutrality.py`.
- Guard evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_chart_object_capability_taxonomy.py`;
  - `pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py`;
  - `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`;
  - `AST guard`, `app.routes`, `app.openapi()` and `TestClient`.

## 4i. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation evidence | `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/evidence/validation.md` | Keep lint, tests and scans. |
| Taxonomy before | `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/evidence/taxonomy-before.md` | Record current capability baseline. |
| Taxonomy after | `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/evidence/taxonomy-after.json` | Capture final matrix contract. |
| API neutrality | `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/evidence/openapi-routes.md` | Keep routes and OpenAPI proof. |
| Review output | `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/generated/11-code-review.md` | Keep automatic review separately. |

## 5. Current State Evidence

- Evidence 1: `_story_briefs/cs-249-chart-object-capability-taxonomy-matrix.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to update `CS-249`.
- Evidence 3: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` - current capability contract read.
- Evidence 4: `backend/tests/architecture/test_chart_runtime_surface_guardrails.py` - existing branch guard read.
- Evidence 5: `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md` - dependency story read.
- Evidence 6: `resolve_guardrails.py` - scoped resolver run for backend-domain taxonomy matrix surfaces.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - consulted only through scoped IDs and targeted ID lookup.
- Source-alignment evidence: ACs cover complete object family classification, current behavior preservation, decision
  blockers, unmanaged branch prevention, no new calculators, API neutrality and persisted evidence.

## 6. Target State

- One canonical typed matrix classifies all required chart object families.
- Every entry exposes the required taxonomy fields and capability columns.
- Existing runtime capabilities are preserved for currently supported objects.
- Ambiguous families use `needs-user-decision` instead of implied business behavior.
- Unknown and duplicate families fail deterministic validation.
- Runtime consumers have one canonical matrix to query instead of adding unmanaged `object_type` branches.
- Public projection, API, frontend, DB, migrations, auth, i18n, style and build surfaces stay unchanged.

## 6a. Regression Guardrails

Scope vector:

- backend-domain: yes;
- chart-object runtime: yes;
- capability taxonomy: yes;
- architecture guard: yes;
- public API: no behavior delta;
- DB/migrations: no;
- frontend/style/build/i18n/auth: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | local | Backend ownership stays in canonical app paths; taxonomy does not move into API routing. |
| RG-022 | local | Backend tests and validation evidence remain mandatory for story closure. |
| RG-144 | local | Chart object runtime stays capability-driven without new unmanaged `object_type` branches. |

Non-applicable examples:

- RG-047 frontend inline styles: out of scope, no TSX or CSS surface is touched.
- RG-052 frontend CSS namespace migration: out of scope, no style or build output is touched.
- RG-041 entitlement documentation: out of scope, no entitlement or frontend build surface is touched.

Registry gap:

- No exact chart object capability taxonomy matrix invariant was returned by the scoped resolver.
- Do not enrich `_condamad/stories/regression-guardrails.md` during this normal story generation.

## 7. Acceptance Criteria

| AC | Requirement | Evidence |
|---|---|---|
| AC1 | All required object families are registered. | Evidence profile: json_contract_shape; `pytest` runs taxonomy tests. |
| AC2 | Each matrix row exposes required columns. | Evidence profile: json_contract_shape; `pytest` runs taxonomy tests. |
| AC3 | Existing capability values are preserved. | Evidence profile: baseline_before_after_diff; `pytest` runs taxonomy tests. |
| AC4 | Unknown object families are rejected. | Evidence profile: json_contract_shape; `pytest` runs taxonomy tests. |
| AC5 | Unresolved object decisions are explicit. | Evidence profile: json_contract_shape; `pytest` runs taxonomy tests. |
| AC6 | New unmanaged `object_type` branches fail. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py`. |
| AC7 | New family calculators are not introduced. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans backend/app/domain/astrology. |
| AC8 | Public API runtime contract is unchanged. | Evidence profile: runtime_openapi_contract; `pytest`; `TestClient`; `app.routes`; `app.openapi()`. |
| AC9 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-249 evidence paths. |

## 8. Implementation Tasks

- [ ] Task 1: Create the typed capability taxonomy module with French file comment and docstrings. (AC: AC1, AC2)
- [ ] Task 2: Declare all required object families and every capability column from the brief. (AC: AC1, AC2)
- [ ] Task 3: Map existing supported families to current `ChartObjectCapabilities` semantics. (AC: AC3)
- [ ] Task 4: Mark unresolved lots, asteroids, Chiron, midpoints and doctrine-sensitive families explicitly. (AC: AC5)
- [ ] Task 5: Add resolver and validator behavior for unknown and duplicate families. (AC: AC4)
- [ ] Task 6: Extend or reuse the architecture guard against unmanaged `object_type` branching. (AC: AC6)
- [ ] Task 7: Add targeted scans or tests preventing new family calculators without decision. (AC: AC7)
- [ ] Task 8: Add or reuse API neutrality proof with `app.routes`, `app.openapi()` and `TestClient`. (AC: AC8)
- [ ] Task 9: Persist before, after, API neutrality and validation evidence under the CS-249 story folder. (AC: AC9)

## 9. Mandatory Reuse / DRY Constraints

- Reuse `ChartObjectType`, `ChartObjectSourceType` and `ChartObjectCapabilities`.
- Reuse existing architecture guard patterns in `test_chart_runtime_surface_guardrails.py`.
- Keep one canonical capability matrix module.
- Do not duplicate capability values in API schemas, frontend code, DB seed files or documentation-only tables.
- Do not add external packages for matrix validation, serialization or scans.
- Keep names explicit and typed; avoid unstructured dictionaries for core taxonomy data.

## 10. No Legacy / Forbidden Paths

- No legacy capability matrix may be added outside the canonical runtime module.
- No compatibility route path may expose chart object taxonomy data.
- No fallback resolver may silently map unknown object families.
- No shim may convert unresolved families into active capability values.
- No frontend file may be modified.
- No DB model, seed or migration may be modified.
- No public API route, serializer or OpenAPI schema may expose the internal matrix.
- No calculator for lots, asteroids, Chiron or midpoints may be introduced.

## 11. Files to Inspect First

- `_story_briefs/cs-249-chart-object-capability-taxonomy-matrix.md`.
- `_condamad/stories/CS-245-canonical-astrology-runtime-transition/00-story.md`.
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md`.
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`.
- `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`.
- `backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py`.
- `backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py`.
- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py`.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## 12. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/chart_object_capability_taxonomy.py`.
- `backend/app/domain/astrology/runtime/__init__.py`.
- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py`.
- `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/evidence/validation.md`.
- `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/evidence/taxonomy-before.md`.
- `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/evidence/taxonomy-after.json`.
- `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/evidence/openapi-routes.md`.

Likely tests:

- `backend/tests/unit/domain/astrology/test_chart_object_capability_taxonomy.py`.
- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py`.
- `backend/tests/architecture/test_api_contract_neutrality.py`.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no API route is touched.
- `backend/app/infra/**` - out of scope; no persistence or external adapter is touched.
- `backend/alembic/**` - out of scope; no migration is touched.

## 13. Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## 14. Validation Plan

Run all Python commands from the repository root after activating the venv:

```powershell
.\.venv\Scripts\Activate.ps1
ruff format backend
ruff check backend
pytest -q backend/tests
```

Run targeted backend-domain validation from the repository root after activating the venv:

```powershell
pytest -q backend/tests/unit/domain/astrology/test_chart_object_capability_taxonomy.py
pytest -q backend/tests/architecture/test_chart_runtime_surface_guardrails.py
pytest -q backend/tests/architecture/test_api_contract_neutrality.py
```

Run API neutrality proof from the repository root after activating the venv:

```powershell
$env:PYTHONPATH='backend'; python -c "from app.main import app; assert 'ChartObjectCapabilityTaxonomy' not in str(app.openapi())"
$env:PYTHONPATH='backend'; python -c "from app.main import app; assert not any('capability-taxonomy' in getattr(r, 'path', '') for r in app.routes)"
```

Run ownership and no-drift scans from the repository root:

```powershell
rg -n "ChartObjectCapability|decision_status|needs-user-decision" backend/app/domain/astrology/runtime backend/tests
rg -n "if .*object_type|\\.object_type ==|match .*object_type" backend/app/domain/astrology -g "*.py"
rg -n "LotCalculator|AsteroidCalculator|ChironCalculator|MidpointCalculator" backend/app/domain/astrology backend/tests
```

Persist evidence checks from the repository root after activating the venv:

```powershell
python -c "from pathlib import Path; assert Path('_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/evidence/validation.md').exists()"
python -c "from pathlib import Path; assert Path('_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/evidence/taxonomy-after.json').exists()"
```

## 15. Regression Risks

- A governance matrix can accidentally become a business behavior change for ambiguous object families.
- Unresolved families can appear active unless `needs-user-decision` is tested.
- A second taxonomy can drift from `ChartObjectRuntimeData`.
- New `object_type` branches can bypass capability-driven runtime selection.
- Public projection can change silently if internal capability values leak into serializers.

## 16. Dev Agent Instructions

- Start by reading the files listed in `Files to Inspect First`.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Keep the implementation typed, small and local to astrology runtime.
- Keep French global comments and public or non-trivial docstrings in new or significantly modified application files.
- Do not create `requirements.txt`.
- Do not modify frontend, DB migrations, API routes, auth, i18n, style or build tooling.
- Do not implement new calculators for lots, asteroids, Chiron or midpoints.
- Do not change public projection or aspect orb behavior.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Persist commands, results, scans, `app.routes`, `app.openapi()` and matrix snapshots under the CS-249 folder.

## 17. References

- `_story_briefs/cs-249-chart-object-capability-taxonomy-matrix.md`.
- `_condamad/stories/story-status.md`.
- `_condamad/stories/CS-245-canonical-astrology-runtime-transition/00-story.md`.
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md`.
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`.
- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py`.
- Scoped guardrail resolver output for backend-domain taxonomy matrix scope.
