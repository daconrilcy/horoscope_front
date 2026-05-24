# Story CS-246 canonical-astrology-graph-family-registry: Define Canonical Astrology Graph Family Registry
Status: done

## 1. Objective

Define one canonical backend-domain registry for astrology graph families so `CalculationGraph` families are governed by typed
runtime metadata instead of dispersed string codes.

## 2. Trigger / Source

- Source type: architecture-runtime-registry.
- Source reference: `_story_briefs/cs-246-canonical-astrology-graph-family-registry.md`.
- Architecture source: `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/03-story-candidates.md#SC-ARCH-001`.
- Selected story writer mode: Fast Story Writer Mode.
- Source-alignment review: the story preserves the brief goal by defining the registry, required families, validation,
  blockers, cache and trace policy without changing public API, frontend, DB or temporal technique behavior.

## 3. Domain Boundary

This story belongs to one domain:

- Domain: backend-domain
- In scope:
  - canonical internal registry for astrology graph families under `backend/app/domain/astrology/runtime`;
  - typed family metadata for code, status, owner, required inputs, graph type, required objects, public surfaces,
    internal surfaces, trace/replay needs, cache/invalidation boundary, blockers and user decisions;
  - mandatory family codes `natal_chart_v1`, `transit_chart_v1`, `synastry_chart_v1`, `solar_return_v1`,
    `lunar_return_v1`, `progressed_chart_v1`, `composite_chart_v1`, `profection_v1`, `forecasting_v1`,
    `ai_scoring_v1` and `narrative_generation_v1`;
  - validation against unknown family codes and duplicate declarations;
  - read-only linkage from `natal_chart_v1` to the existing graph definition without public behavior change;
  - targeted unit and architecture tests.
- Out of scope:
  - implementing any temporal technique;
  - modifying public API routes, OpenAPI payloads, frontend, DB schema, migrations, auth, i18n, styles or build tooling;
  - exposing `chart_objects` publicly;
  - choosing the first temporal technique, which belongs to CS-253;
  - adding astronomical proof, doctrine governance or product roadmap decisions beyond explicit blocker values.
- Explicit non-goals:
  - no frontend route, screen, client generation or UI validation;
  - no Alembic migration or persistence model;
  - no public JSON contract change;
  - no new calculation runner behavior;
  - no registry enrichment in `_condamad/stories/regression-guardrails.md` during this story generation.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain registry contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add one canonical typed registry for astrology graph families.
  - Link `natal_chart_v1` to the registry without changing its runtime output.
  - Add validation and tests for family completeness, duplicates and unknown codes.
  - Keep public API, frontend, DB and migrations unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: implementing a family requires an astronomical, doctrine, product, trace or cache decision
  not represented by an explicit blocked status.
- Additional validation rules:
  - `natal_chart_v1` remains resolvable through existing `CalculationGraphDefinition` behavior.
  - Temporal families remain blocked until CS-250 is completed or risk-accepted.
  - Registry lookup rejects unknown family codes deterministically.
  - Registry construction rejects duplicate family codes deterministically.
  - `app.routes`, `app.openapi()`, `pytest` and `TestClient` prove no public API delta.
  - Registry metadata answers owner, required inputs, blocker status and cache boundary queries deterministically.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | The registry becomes the internal source for astrology graph family metadata. |
| Baseline Snapshot | yes | Current graph contracts and `natal_chart_v1` behavior must stay visible before and after. |
| Ownership Routing | yes | Registry ownership must stay under astrology runtime, not API, DB, frontend or services. |
| Allowlist Exception | no | No allowlist handling is authorized for this registry story. |
| Contract Shape | yes | The family metadata schema is the core implementation contract. |
| Batch Migration | no | No multi-step migration or broad conversion is in scope. |
| Reintroduction Guard | yes | Duplicate and unknown family codes must remain blocked. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`;
  - `backend/app/domain/astrology/runtime/natal_calculation_graph.py`;
  - `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`.
- Runtime/domain artifacts:
  - typed registry entry contract;
  - family status values;
  - owner, required input and blocker metadata;
  - cache and trace policy fields;
  - resolver behavior for known and unknown family codes.
- Secondary evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_astrology_graph_family_registry.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`;
  - `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`;
  - `app.routes`, `app.openapi()` and `TestClient`.
- Static scans alone are not sufficient because:
  - runtime registry lookup, duplicate detection and API neutrality must be proven from executable tests.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`;
  - `backend/app/domain/astrology/runtime/natal_calculation_graph.py`;
  - `backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`;
  - `_story_briefs/cs-246-canonical-astrology-graph-family-registry.md`;
  - `_condamad/stories/story-status.md`.
- Comparison after implementation:
  - registry tests prove all mandatory family codes and metadata fields;
  - natal graph tests prove `natal_chart_v1` still validates;
  - API neutrality tests prove public route and OpenAPI stability;
  - targeted scans prove no frontend, DB migration or API route ownership drift.
- Expected invariant:
  - the only allowed surface delta is an internal backend runtime registry plus targeted tests and evidence files.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Graph family registry | `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py` | API routers, DB models, frontend |
| Graph family metadata tests | `backend/tests/unit/domain/astrology/test_astrology_graph_family_registry.py` | broad integration tests only |
| Existing natal graph definition | `backend/app/domain/astrology/runtime/natal_calculation_graph.py` | duplicate registry module |
| API neutrality proof | `backend/tests/architecture/test_api_contract_neutrality.py` | frontend smoke tests |

## 4e. Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this single canonical backend-domain registry.

## 4f. Contract Shape

- Contract type:
  - internal typed registry for astrology graph families;
  - no HTTP endpoint, public serializer or frontend type.
- Fields:
  - family code, status, target owner, inputs, graph type, objects, public surfaces, internal surfaces, trace policy,
    cache boundary, blockers and user decisions.
- Required family codes:
  - `natal_chart_v1`;
  - `transit_chart_v1`;
  - `synastry_chart_v1`;
  - `solar_return_v1`;
  - `lunar_return_v1`;
  - `progressed_chart_v1`;
  - `composite_chart_v1`;
  - `profection_v1`;
  - `forecasting_v1`;
  - `ai_scoring_v1`;
  - `narrative_generation_v1`.
- Required fields:
  - `code`;
  - `status`;
  - `target_owner`;
  - `required_inputs`;
  - `expected_graph_type`;
  - `required_objects`;
  - `authorized_public_surfaces`;
  - `internal_surfaces`;
  - `trace_replay_needs`;
  - `cache_invalidation_boundary`;
  - `blockers`;
  - `user_decisions`.
- Optional fields:
  - none.
- Status values:
  - `active`;
  - `blocked-by-astronomical-proof`;
  - `blocked-by-product-decision`;
  - `blocked-by-doctrine-decision`;
  - `blocked-by-multi-chart-decision`;
  - `blocked-by-trace-decision`;
  - `blocked-by-cache-decision`;
  - `missing`.
- Required query behavior:
  - owner lookup for `transit_chart_v1`;
  - required input lookup for `synastry_chart_v1`;
  - blocked family filtering for astronomical proof;
  - cache boundary lookup for `natal_chart_v1`;
  - unknown code rejection.
- Status codes:
  - no HTTP endpoint, method or status code is changed.
- Serialization names:
  - no public JSON key is renamed or added.
- Frontend type impact:
  - none; no frontend contract changes are allowed.
- Generated contract impact:
  - `app.openapi()` must not expose the internal registry.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## 4h. Reintroduction Guard

- Guard target:
  - no duplicate family code in the registry;
  - no unknown family code accepted by resolver behavior;
  - no second registry under API, services, infra, DB, frontend or docs-only paths;
  - no public API, OpenAPI, DB migration or frontend delta.
- Guard mechanism:
  - unit tests for mandatory family completeness;
  - unit tests for duplicate rejection;
  - unit tests for unknown code rejection;
  - AST guard or targeted `rg` scan for registry ownership;
  - `TestClient`, `app.routes` and `app.openapi()` API neutrality evidence.
- Guard owner:
  - `backend/tests/unit/domain/astrology/test_astrology_graph_family_registry.py`;
  - `backend/tests/architecture/test_api_contract_neutrality.py`.
- Guard evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_astrology_graph_family_registry.py`;
  - `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`;
  - `AST guard`, `app.routes`, `app.openapi()` and `TestClient`.

## 4i. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation evidence | `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/evidence/validation.md` | Keep lint, tests and targeted scan results. |
| API evidence | `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/evidence/openapi-routes.md` | Keep `app.routes` and OpenAPI proof. |
| Registry snapshot | `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/evidence/family-registry.md` | Record family codes and statuses. |
| Review output | `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## 5. Current State Evidence

- Evidence 1: `_story_briefs/cs-246-canonical-astrology-graph-family-registry.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign and update `CS-246`.
- Evidence 3: `backend/app/domain/astrology/runtime/calculation_graph_contracts.py` - existing graph contract source read.
- Evidence 4: `backend/app/domain/astrology/runtime/natal_calculation_graph.py` - existing `natal_chart_v1` definition read.
- Evidence 5: `backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py` - existing natal graph tests read.
- Evidence 6: `resolve_guardrails.py` - scoped resolver run for backend-domain runtime registry surfaces.
- Source-alignment evidence: the ACs cover mandatory families, metadata fields, validation, natal linkage, blockers and API neutrality.

## 6. Target State

- One canonical registry exposes all mandatory astrology graph families.
- Every family entry has status, target owner, inputs, graph type, required objects, public surfaces, internal surfaces,
  trace/replay needs, cache/invalidation boundary, blockers and user decisions.
- `natal_chart_v1` is active and linked to the existing graph definition without behavior change.
- Temporal families are blocked by astronomical proof until CS-250 is completed or risk-accepted.
- Registry lookup answers owner, input, blocker and cache queries deterministically.
- Duplicate and unknown family codes fail deterministic validation.
- No public API, frontend, DB, migration, auth, i18n, style or build surface changes.

## 6a. Regression Guardrails

Scope vector:

- backend-domain: yes;
- runtime-registry: yes;
- calculation-graph: yes;
- public API: no behavior delta;
- DB/migrations: no;
- frontend/style/build/i18n/auth: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | local | Backend ownership stays in canonical app paths; registry does not move into API routing. |
| RG-003 | local | API route architecture remains unchanged while the registry stays internal. |
| RG-022 | local | Backend tests and validation evidence remain mandatory for story closure. |

Non-applicable examples:

- RG-047 frontend inline styles: out of scope, no TSX or CSS surface is touched.
- RG-052 frontend CSS namespace migration: out of scope, no style or build output is touched.
- RG-007 admin LLM observability endpoints: out of scope; API neutrality is proven by AC7 validation evidence.
- DB/migration guardrails: out of scope, no table, model or Alembic migration is modified.

Registry gap:

- No exact route-specific or registry-specific invariant for astrology graph families was returned by the scoped resolver.
- Do not enrich `_condamad/stories/regression-guardrails.md` during this normal story generation.

## 7. Acceptance Criteria

| AC | Requirement | Evidence |
|---|---|---|
| AC1 | All mandatory family codes are registered. | Evidence profile: json_contract_shape; `pytest` runs registry tests. |
| AC2 | Each family exposes required metadata. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_astrology_graph_family_registry.py`. |
| AC3 | `natal_chart_v1` remains linked to the current graph. | Evidence profile: runtime_openapi_contract; `pytest` runs natal graph tests. |
| AC4 | Temporal families are blocked by astronomical proof. | Evidence profile: json_contract_shape; `pytest` runs registry tests. |
| AC5 | Duplicate family codes are rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_astrology_graph_family_registry.py`. |
| AC6 | Unknown family codes are rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_astrology_graph_family_registry.py`. |
| AC7 | Public API runtime contract is unchanged. | Evidence profile: runtime_openapi_contract; `pytest` runs API neutrality; `app.openapi()`. |
| AC8 | Registry evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-246 evidence paths. |

## 8. Implementation Tasks

- [x] Task 1: Create the typed graph family registry module with French file comment and docstrings. (AC: AC1, AC2)
- [x] Task 2: Declare the eleven mandatory family codes and their metadata fields. (AC: AC1, AC2)
- [x] Task 3: Mark temporal families blocked by astronomical proof until CS-250 or risk acceptance. (AC: AC4)
- [x] Task 4: Add resolver and validator behavior for duplicate and unknown family codes. (AC: AC5, AC6)
- [x] Task 5: Link `natal_chart_v1` metadata to the existing natal graph contract without public behavior delta. (AC: AC3, AC7)
- [x] Task 6: Add targeted unit tests for completeness, metadata, blockers, duplicate codes and unknown codes. (AC: AC1, AC2, AC4, AC5, AC6)
- [x] Task 7: Add or reuse API neutrality proof with `app.routes`, `app.openapi()` and `TestClient`. (AC: AC7)
- [x] Task 8: Persist validation, API neutrality and registry snapshot evidence under the CS-246 story folder. (AC: AC8)

## 9. Mandatory Reuse / DRY Constraints

- Reuse `CalculationGraphDefinition` and `natal_calculation_graph.py` concepts instead of redefining graph contracts.
- Keep one canonical registry module for graph families.
- Do not duplicate family metadata in API, frontend, DB seed files or documentation-only tables.
- Do not add external packages for registry validation.
- Keep names explicit and typed; avoid free-form dictionaries when a dataclass, enum or existing typed pattern fits the codebase.

## 10. No Legacy / Forbidden Paths

- No legacy family registry may be added outside the canonical runtime module.
- No compatibility route path may be added for graph family metadata.
- No fallback resolver may silently map unknown family codes.
- No shim may accept duplicate family declarations.
- No frontend file may be modified.
- No DB model, seed or migration may be modified.
- No public API route, serializer or OpenAPI schema may expose the internal registry.

## 11. Files to Inspect First

- `_story_briefs/cs-246-canonical-astrology-graph-family-registry.md`.
- `_condamad/stories/CS-245-canonical-astrology-runtime-transition/00-story.md`.
- `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`.
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`.
- `backend/app/domain/astrology/runtime/calculation_graph_validator.py`.
- `backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`.
- `backend/tests/unit/domain/astrology/test_calculation_graph_validator.py`.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output only.

## 12. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`.
- `backend/app/domain/astrology/runtime/__init__.py`.
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/evidence/validation.md`.
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/evidence/openapi-routes.md`.
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/evidence/family-registry.md`.

Likely tests:

- `backend/tests/unit/domain/astrology/test_astrology_graph_family_registry.py`.
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

Run targeted backend-domain validation:

```powershell
pytest -q backend/tests/unit/domain/astrology/test_astrology_graph_family_registry.py
pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py
pytest -q backend/tests/architecture/test_api_contract_neutrality.py
```

Run API neutrality proof:

```powershell
python -c "from app.main import app; assert 'AstrologyGraphFamily' not in str(app.openapi())"
python -c "from app.main import app; assert not any('graph-family' in getattr(r, 'path', '') for r in app.routes)"
```

Run ownership and no-drift scans:

```powershell
rg -n "transit_chart_v1|synastry_chart_v1|natal_chart_v1" backend/app/domain/astrology/runtime backend/tests/unit/domain/astrology
rg -n "graph-family|graph_family|AstrologyGraphFamily" backend/app/api frontend backend/alembic -g "*.py" -g "*.ts" -g "*.tsx"
```

## 15. Regression Risks

- Over-specified future families can imply implementation decisions that are not approved.
- Under-specified blocker statuses can allow temporal techniques before astronomical proof.
- A second registry can reintroduce dispersed family ownership.
- Public API exposure can leak internal graph metadata before product decisions.

## 16. Dev Agent Instructions

- Start by reading the files listed in `Files to Inspect First`.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Keep the implementation typed, small and local to astrology runtime.
- Keep French global comments and public or non-trivial docstrings in new or significantly modified application files.
- Do not create `requirements.txt`.
- Do not modify frontend, DB migrations, API routes, auth, i18n, style or build tooling.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Persist commands, results, scans, `app.routes`, `app.openapi()` and registry snapshot evidence under the CS-246 folder.

## 17. References

- `_story_briefs/cs-246-canonical-astrology-graph-family-registry.md`.
- `_condamad/stories/story-status.md`.
- `_condamad/stories/CS-245-canonical-astrology-runtime-transition/00-story.md`.
- `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`.
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`.
- `backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`.
- Scoped guardrail resolver output for backend-domain runtime registry scope.
