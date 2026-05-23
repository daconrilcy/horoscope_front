# Story CS-253 first-temporal-technique-implementation-path: Select First Temporal Technique Implementation Path
Status: ready-to-dev

## 1. Objective

Select `transit_chart_v1` as the first temporal technique path and create a backend-domain contract that keeps the work non-public
until CS-250 is `done` or a written product risk acceptance authorizes bounded non-public experimentation.

## 2. Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-253-first-temporal-technique-implementation-path.md`.
- Architecture source: `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/03-story-candidates.md#SC-ARCH-006`.
- Remapped architecture item: `SC-ARCH-006`.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: the first temporal technique must be chosen once, documented, and blocked from public rollout until the astronomy gate closes.
- Source-alignment evidence: PASS; the story preserves unique selection, candidate comparison, inputs, graph, objects, CS-250 gate and anti-batch proof.

## 3. Domain Boundary

This story belongs to one domain:

- Domain: backend-domain
- In scope:
  - select exactly one first temporal family, `transit_chart_v1`;
  - document the non-selection reason for synastry, returns, progressions, composite, profections and forecasting;
  - define required inputs for a transit path: natal chart input, target date or date range, timezone and location policy;
  - define required graph path through `CalculationGraph`, graph family registry and graph manifest contracts;
  - define required chart objects and transit-to-natal relationships;
  - define non-public projection status while CS-250 is not `done`;
  - add backend tests and architecture scans proving only one temporal family path is opened;
  - persist the decision and validation evidence under this story folder.
- Out of scope:
  - implementing every temporal family;
  - opening a public API route, OpenAPI payload, frontend UI, DB schema, migration, auth, i18n, style or build surface;
  - bypassing CS-250 through product copy, LLM narration or prediction-only code;
  - adding runtime calculation algorithms beyond the minimal non-public selection skeleton.
- Explicit non-goals:
  - No frontend route, screen, client generation or UI validation.
  - No public endpoint, public serializer or generated client change.
  - No narration LLM, prompt enrichment or AI scoring change.
  - No registry enrichment in `_condamad/stories/regression-guardrails.md` during this story generation.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain decision and temporal gate contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add one canonical backend decision contract for the first temporal technique path.
  - Select `transit_chart_v1` as the only opened first temporal family.
  - Keep the selected path non-public until CS-250 is `done` or written risk acceptance limits the surface.
  - Keep public API, frontend, DB, migrations, auth, i18n, styling and build tooling unchanged.
  - Keep existing prediction temporal code from becoming the canonical runtime path by default.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product rejects `transit_chart_v1` or wants a public temporal surface before CS-250 closure.
- Additional validation rules:
  - The selected technique must be represented by one stable family code, one decision owner and one status value.
  - Non-selected candidate families must have explicit reasons and remain closed to implementation.
  - The contract must reference CS-246 registry, CS-247 manifest and CS-248 trace requirements by stable story IDs.
  - Runtime evidence must include `AST guard`, generated manifest or targeted `pytest` checks for the decision contract.
  - API neutrality must be proven with `app.routes`, `app.openapi()` and `TestClient`.
  - A targeted scan must prove no public route, UI path or second temporal family was introduced.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | The decision contract and tests prove the loaded backend temporal selection behavior. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta is a non-public selection contract. |
| Ownership Routing | yes | The selection owner must stay in backend astrology runtime, not prediction, API, DB or frontend. |
| Allowlist Exception | no | No allowlist handling is authorized for this single temporal path selection. |
| Contract Shape | yes | The selected family, candidate reasons, inputs, graph, objects and gate fields are the contract. |
| Batch Migration | no | Batch implementation of multiple temporal families is explicitly out of scope. |
| Reintroduction Guard | yes | Closed temporal families and public surfaces must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - expected `backend/app/domain/astrology/runtime/temporal_technique_selection.py`;
  - expected graph family registry from CS-246;
  - expected graph manifest contract from CS-247;
  - `AST guard`, generated manifest, targeted `pytest`, `app.routes`, `app.openapi()` and `TestClient`.
- Runtime/domain artifacts:
  - selected temporal family code;
  - candidate comparison records;
  - non-public gate status;
  - required input descriptors;
  - graph and chart object relationship descriptors;
  - closure criteria for opening later implementation work.
- Secondary evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_temporal_technique_selection.py`;
  - `pytest -q backend/tests/architecture/test_temporal_family_single_path.py`;
  - `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`;
  - targeted `rg` scans for closed temporal family codes and public surfaces.
- Static scans alone are not sufficient because:
  - the selected family, gate state, API neutrality and closed-family behavior must be proven from executable tests.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_story_briefs/cs-253-first-temporal-technique-implementation-path.md`;
  - `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md`;
  - `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/00-story.md`;
  - `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/00-story.md`;
  - `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/00-story.md`.
- Comparison after implementation:
  - `_condamad/stories/CS-253-first-temporal-technique-implementation-path/evidence/temporal-selection-after.json`;
  - `_condamad/stories/CS-253-first-temporal-technique-implementation-path/evidence/validation.md`;
  - `_condamad/stories/CS-253-first-temporal-technique-implementation-path/evidence/api-neutrality.md`.
- Expected invariant:
  - the only allowed surface delta is a non-public backend decision contract selecting `transit_chart_v1`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Temporal technique selection | `backend/app/domain/astrology/runtime/temporal_technique_selection.py` | `backend/app/domain/prediction/**` |
| Candidate comparison tests | `backend/tests/unit/domain/astrology/test_temporal_technique_selection.py` | broad API-only tests |
| Single-family architecture guard | `backend/tests/architecture/test_temporal_family_single_path.py` | frontend smoke tests |
| API neutrality proof | `backend/tests/architecture/test_api_contract_neutrality.py` | public route tests only |
| Story evidence artifacts | `_condamad/stories/CS-253-first-temporal-technique-implementation-path/evidence/` | `backend/app/**` |

## 4e. Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this backend-domain temporal selection story.

## 4f. Contract Shape

- Contract type:
  - internal backend-domain decision contract for the first temporal technique path;
  - no HTTP endpoint, public serializer or frontend type.
- Selected technique:
  - `transit_chart_v1`.
- Fields:
  - `selected_family_code`: stable family code for the first temporal path.
  - `selected_technique_name`: human-readable technique name.
  - `selection_status`: current internal status of the selected path.
  - `public_projection_status`: public exposure gate state.
  - `cs250_gate_state`: astronomy proof dependency state.
  - `product_rationale`: short reason for choosing transits first.
  - `required_inputs`: required input descriptors for the selected path.
  - `required_graph_code`: expected calculation graph code.
  - `required_chart_objects`: required runtime chart object descriptors.
  - `required_relationships`: required transit-to-natal relationship descriptors.
  - `dependency_story_ids`: prerequisite or linked story IDs.
  - `end_criteria`: closure criteria for opening implementation follow-up work.
  - `rejected_candidates`: closed families with reasons.
- Required fields:
  - `selected_family_code`;
  - `selected_technique_name`;
  - `selection_status`;
  - `public_projection_status`;
  - `cs250_gate_state`;
  - `product_rationale`;
  - `required_inputs`;
  - `required_graph_code`;
  - `required_chart_objects`;
  - `required_relationships`;
  - `dependency_story_ids`;
  - `end_criteria`;
  - `rejected_candidates`.
- Optional fields:
  - none.
- Candidate families that remain closed:
  - `synastry_chart_v1`;
  - `solar_return_v1`;
  - `lunar_return_v1`;
  - `progressed_chart_v1`;
  - `composite_chart_v1`;
  - `profection_v1`;
  - `forecasting_v1`.
- Required input descriptors:
  - natal chart input;
  - transit target date or bounded date range;
  - timezone policy;
  - location policy;
  - calculation mode proof reference from CS-250.
- Required graph path:
  - graph family registry entry from CS-246;
  - graph manifest and node IO schema from CS-247;
  - execution trace requirements from CS-248;
  - astronomy proof gate from CS-250.
- Required chart object relationships:
  - transit object to natal object relationship;
  - transit-to-natal aspect relationship;
  - house transit relationship for non-public diagnostics only.
- Status values:
  - `selected-blocked-by-cs250`;
  - `selected-risk-accepted-non-public`;
  - `selected-ready-after-cs250`.
- Status codes:
  - no HTTP endpoint, method or status code is changed.
- Serialization names:
  - internal evidence artifacts use snake_case field names.
- Frontend type impact:
  - none.
- Generated contract impact:
  - `app.openapi()` must not expose the temporal selection contract.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-family temporal implementation is in scope.

## 4h. Reintroduction Guard

- Guard target:
  - `transit_chart_v1` remains the only selected first temporal family;
  - non-selected families remain closed to implementation;
  - the selected path remains non-public while CS-250 is not `done`;
  - existing prediction temporal code is not promoted as canonical astrology runtime by default;
  - no public API, OpenAPI, DB migration or frontend delta is introduced.
- Guard mechanism:
  - unit tests for selected family, rejected families, inputs, graph and object relationships;
  - architecture tests proving single-family opening and API neutrality;
  - targeted `rg` scans for public route, UI and additional temporal family openings;
  - `TestClient`, `app.routes` and `app.openapi()` API neutrality evidence.
- Guard owner:
  - `backend/tests/unit/domain/astrology/test_temporal_technique_selection.py`;
  - `backend/tests/architecture/test_temporal_family_single_path.py`;
  - `backend/tests/architecture/test_api_contract_neutrality.py`.
- Guard evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_temporal_technique_selection.py`;
  - `pytest -q backend/tests/architecture/test_temporal_family_single_path.py`;
  - `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`;
  - `AST guard`, `app.routes`, `app.openapi()` and targeted `rg`.

## 4i. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation evidence | `_condamad/stories/CS-253-first-temporal-technique-implementation-path/evidence/validation.md` | Keep lint, tests and scans. |
| Selection snapshot | `_condamad/stories/CS-253-first-temporal-technique-implementation-path/evidence/temporal-selection-after.json` | Record selected and closed families. |
| Gate evidence | `_condamad/stories/CS-253-first-temporal-technique-implementation-path/evidence/cs-250-gate.md` | Record CS-250 state or risk acceptance. |
| API neutrality | `_condamad/stories/CS-253-first-temporal-technique-implementation-path/evidence/api-neutrality.md` | Keep routes and OpenAPI proof. |
| Review output | `_condamad/stories/CS-253-first-temporal-technique-implementation-path/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## 5. Current State Evidence

- Evidence 1: `_story_briefs/cs-253-first-temporal-technique-implementation-path.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to convert `CS-253` from brief-ready to ready-to-dev.
- Evidence 3: `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md` - dependency story read.
- Evidence 4: `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/00-story.md` - dependency story read.
- Evidence 5: `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/00-story.md` - dependency story read.
- Evidence 6: `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/00-story.md` - required gate story read.
- Evidence 7: scoped scan found existing temporal and transit code under `backend/app/domain/prediction`, not canonical astrology runtime.
- Evidence 8: scoped path check found `backend/app/domain/astrology/runtime/calculation_graph_runner.py` exists.
- Evidence 9: scoped path check found CS-246 registry and CS-247 manifest implementation files are not yet present.
- Evidence 10: `_condamad/stories/regression-guardrails.md` was consulted through scoped resolver output only.
- Source-alignment evidence: ACs cover unique technique, rejected candidates, inputs, graph, objects, CS-250 gate and anti-batch proof.

Repository structure alert:

- `backend` exists in this workspace.
- `backend/app/domain/astrology/runtime` exists in this workspace.
- Expected CS-246 and CS-247 implementation files are not present yet, so implementation must create or consume them in dependency order.

## 6. Target State

- `transit_chart_v1` is the single selected first temporal technique path.
- Every non-selected family has an explicit reason and remains closed.
- Required inputs, graph path, chart objects, relationships and end criteria are recorded in one canonical contract.
- CS-250 gate state is enforced as `selected-blocked-by-cs250` until proof closure or written non-public risk acceptance.
- Existing prediction temporal code is treated as historical or non-canonical evidence unless explicitly migrated by this contract.
- No public API, frontend, DB, migration, auth, i18n, style or build surface changes.

## 6a. Regression Guardrails

Scope vector:

- backend-domain: yes;
- astrology runtime selection: yes;
- calculation-graph: yes;
- graph family registry and manifest: yes;
- public API: no behavior delta;
- DB/migrations: no;
- frontend/style/build/i18n/auth: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | local | Backend ownership stays in canonical app paths; selection does not move into API routing. |
| RG-010 | local | Backend tests stay under collected roots documented by backend pytest configuration. |
| RG-095 | local | Astrology runtime must not import prediction owners while selecting the temporal path. |

Non-applicable examples:

- RG-041 entitlement documentation is out of scope because no billing or entitlement surface is touched.
- RG-047 frontend inline styles are out of scope because no TSX or CSS surface is touched.
- RG-052 frontend CSS namespace migration is out of scope because no styling or build output is touched.

Registry gap:

- No exact first-temporal-technique selection invariant was returned by the scoped resolver.
- Do not enrich `_condamad/stories/regression-guardrails.md` during this normal story generation.

## 7. Acceptance Criteria

| AC | Requirement | Evidence |
|---|---|---|
| AC1 | `transit_chart_v1` is the single selected family. | Evidence profile: json_contract_shape; `pytest` runs selection tests. |
| AC2 | Rejected candidate reasons are explicit. | Evidence profile: json_contract_shape; `pytest`; generated selection artifact. |
| AC3 | Required inputs are declared. | Evidence profile: json_contract_shape; `pytest`; generated selection artifact. |
| AC4 | Graph requirements are declared. | Evidence profile: json_contract_shape; `pytest`; `AST guard`; generated manifest. |
| AC5 | Chart object relationships are declared. | Evidence profile: json_contract_shape; `pytest`; generated selection artifact. |
| AC6 | Public projection stays blocked by CS-250. | Evidence profile: reintroduction_guard; `pytest -q backend/tests/architecture/test_temporal_family_single_path.py`. |
| AC7 | No second temporal family is opened. | Evidence profile: targeted_forbidden_symbol_scan; `pytest`; `rg` checks closed family codes. |
| AC8 | Public API runtime contract is unchanged. | Evidence profile: runtime_openapi_contract; `pytest`; `TestClient`; `app.routes`; `app.openapi()`. |
| AC9 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-253 evidence paths. |

## 8. Implementation Tasks

- [ ] Task 1: Create the typed temporal selection contract with French file comment and docstrings. (AC: AC1, AC2, AC3)
- [ ] Task 2: Encode `transit_chart_v1` as the only selected first temporal family. (AC: AC1)
- [ ] Task 3: Record non-selection reasons for synastry, returns, progressions, composite, profections and forecasting. (AC: AC2)
- [ ] Task 4: Declare required transit inputs, graph family, manifest, trace, chart objects and relationships. (AC: AC3, AC4, AC5)
- [ ] Task 5: Enforce CS-250 gate state so the selected path remains non-public before proof closure or risk acceptance. (AC: AC6)
- [ ] Task 6: Add a single-family architecture guard against additional temporal family openings. (AC: AC7)
- [ ] Task 7: Add or reuse API neutrality proof with `app.routes`, `app.openapi()` and `TestClient`. (AC: AC8)
- [ ] Task 8: Persist validation, selection snapshot, gate evidence and API neutrality artifacts. (AC: AC9)

## 9. Mandatory Reuse / DRY Constraints

- Reuse the CS-246 graph family registry once implemented.
- Reuse the CS-247 graph manifest and node IO schema once implemented.
- Reuse the CS-248 trace vocabulary instead of creating a parallel trace contract.
- Reuse existing `CalculationGraph` and `chart_objects` contracts rather than duplicating runtime structures.
- Keep one canonical temporal selection module.
- Do not add external packages for comparison, selection, manifest generation or validation.
- Do not duplicate existing prediction temporal logic into astrology runtime without an explicit migration task.

## 10. No Legacy / Forbidden Paths

- No legacy temporal selection module may be added outside the canonical astrology runtime owner.
- No compatibility route path may expose this selection publicly.
- No fallback resolver may choose another temporal family after `transit_chart_v1` is selected.
- No shim may promote existing prediction temporal code as the canonical astrology runtime path by default.
- No public API route, serializer, OpenAPI schema, frontend file, DB model, seed or migration may be modified.
- No second opened family is allowed for synastry, returns, progressions, composite, profections or forecasting.

## 11. Files to Inspect First

- `_story_briefs/cs-253-first-temporal-technique-implementation-path.md`.
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md`.
- `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/00-story.md`.
- `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/00-story.md`.
- `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/00-story.md`.
- `backend/app/domain/astrology/runtime/calculation_graph_runner.py`.
- `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`.
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`.
- `backend/app/domain/prediction/transit_signal_builder.py`.
- `backend/app/domain/prediction/temporal_sampler.py`.
- `backend/app/domain/prediction/enriched_astro_events_builder.py`.
- `backend/tests/architecture/test_api_contract_neutrality.py`.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output only.

## 12. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/temporal_technique_selection.py`.
- `backend/app/domain/astrology/runtime/__init__.py`.
- `_condamad/stories/CS-253-first-temporal-technique-implementation-path/evidence/validation.md`.
- `_condamad/stories/CS-253-first-temporal-technique-implementation-path/evidence/temporal-selection-after.json`.
- `_condamad/stories/CS-253-first-temporal-technique-implementation-path/evidence/cs-250-gate.md`.
- `_condamad/stories/CS-253-first-temporal-technique-implementation-path/evidence/api-neutrality.md`.

Likely tests:

- `backend/tests/unit/domain/astrology/test_temporal_technique_selection.py`.
- `backend/tests/architecture/test_temporal_family_single_path.py`.
- `backend/tests/architecture/test_api_contract_neutrality.py`.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no public API route is touched.
- `backend/app/infra/**` - out of scope; no persistence or external adapter is touched.
- `backend/migrations/**` - out of scope; no database migration is touched.
- `docs/db_seeder/**` - out of scope; no seed artifact is touched.

## 13. Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## 14. Validation Plan

Run all Python commands from the repository root after activating the venv:

```powershell
.\.venv\Scripts\Activate.ps1
ruff format backend
ruff check backend
pytest -q
```

Run targeted backend-domain validation:

```powershell
pytest -q backend/tests/unit/domain/astrology/test_temporal_technique_selection.py
pytest -q backend/tests/architecture/test_temporal_family_single_path.py
pytest -q backend/tests/architecture/test_api_contract_neutrality.py
```

Run API neutrality proof:

```powershell
python -c "from app.main import app; assert 'temporal_technique_selection' not in str(app.openapi())"
python -c "from app.main import app; assert not any('temporal' in getattr(r, 'path', '') for r in app.routes)"
```

Run single-family and public-surface scans:

```powershell
rg -n "transit_chart_v1|synastry_chart_v1|solar_return_v1|progressed_chart_v1" backend/app/domain/astrology backend/tests
rg -n "temporal|transit_chart|synastry_chart|solar_return" backend/app/api frontend backend/migrations -g "*.py" -g "*.ts" -g "*.tsx"
```

Persist evidence checks:

```powershell
python -c "from pathlib import Path; assert Path('_condamad/stories/CS-253-first-temporal-technique-implementation-path/evidence/validation.md').exists()"
python -c "from pathlib import Path; assert Path('_condamad/stories/CS-253-first-temporal-technique-implementation-path/evidence/temporal-selection-after.json').exists()"
```

## 15. Regression Risks

- A convenient existing prediction transit module can be treated as the canonical runtime path without graph and chart object contracts.
- A public API or UI path can open before CS-250 proof closure.
- Candidate comparison can become a batch implementation plan instead of one selected family.
- Candidate reasons can drift into doctrine or product decisions not covered by this story.
- Missing CS-246 or CS-247 implementation can hide the required registry and manifest linkage.

## 16. Dev Agent Instructions

- Start by reading the files listed in `Files to Inspect First`.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Keep the implementation typed, small and local to astrology runtime.
- Keep French global comments and public or non-trivial docstrings in new or significantly modified application files.
- Do not create `requirements.txt`.
- Do not modify frontend, DB migrations, public API routes, auth, i18n, style or build tooling.
- Do not open synastry, returns, progressions, composite, profections or forecasting implementation paths.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Persist commands, results, scans, `app.routes`, `app.openapi()`, selection snapshot and gate evidence under the CS-253 folder.

## 17. References

- `_story_briefs/cs-253-first-temporal-technique-implementation-path.md`.
- `_condamad/stories/story-status.md`.
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md`.
- `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/00-story.md`.
- `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/00-story.md`.
- `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/00-story.md`.
- `backend/app/domain/astrology/runtime/calculation_graph_runner.py`.
- `backend/app/domain/prediction/transit_signal_builder.py`.
- Scoped guardrail resolver output for backend-domain temporal selection scope.
