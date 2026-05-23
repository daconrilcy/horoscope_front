# Story CS-247 graph-manifest-node-io-schema-contract: Add Graph Manifest And Node IO Schema Contract
Status: ready-to-dev

## 1. Objective

Create one internal backend-domain manifest contract for `CalculationGraph` so graph identity, version, family, global inputs,
node IO schemas, optional dependencies and compatibility policy become inspectable and comparable.

## 2. Trigger / Source

- Source type: architecture-runtime-contract.
- Source reference: `_story_briefs/cs-247-graph-manifest-node-io-schema-contract.md`.
- Architecture source: `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/03-story-candidates.md#SC-ARCH-002`.
- Selected story writer mode: Fast Story Writer Mode.
- Source-alignment evidence: the story preserves the brief goal by covering manifest identity, node IO, validation,
  comparison, `natal_chart_v1`, compatibility policy and public surface neutrality.

## 3. Domain Boundary

This story belongs to one domain:

- Domain: backend-domain
- In scope:
  - internal graph manifest model for `CalculationGraph`;
  - node IO schema contract for declared node inputs, outputs, type descriptors and optional dependencies;
  - `natal_chart_v1` manifest generated from the current natal graph definition;
  - manifest validation for duplicate outputs, unknown inputs, missing schemas and missing graph family linkage;
  - deterministic manifest comparison for contract changes;
  - targeted unit and architecture tests.
- Out of scope:
  - public API routes, OpenAPI payload additions, frontend UI, DB schema, migrations, auth, i18n, styles and build tooling;
  - temporal technique implementation;
  - debug UI or public manifest exposure;
  - external schema language selection;
  - calculation runner behavior changes.
- Explicit non-goals:
  - no frontend route, screen, client generation or UI validation;
  - no Alembic migration or persistence model;
  - no public JSON contract change;
  - no new graph executor feature;
  - no registry enrichment in `_condamad/stories/regression-guardrails.md` during this story generation.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only an internal manifest and node IO schema contract for calculation graphs.
  - Attach `natal_chart_v1` to a complete manifest that describes the existing graph.
  - Add validation and comparison behavior for graph manifest contracts.
  - Keep public API, frontend, DB, migrations and calculation outputs unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: manifest comparison requires a compatibility policy not expressible as `compatible` or `breaking`.
- Additional validation rules:
  - `natal_chart_v1` manifest must match `build_natal_calculation_graph_definition()`.
  - Every declared node must expose a non-empty `input_schema` and `output_schema`.
  - Manifest validation must reject duplicate output keys, unknown required inputs and absent node schemas.
  - Manifest comparison must classify graph version, input, output and type descriptor deltas.
  - `app.routes`, `app.openapi()`, `pytest` and `TestClient` prove no public API delta.
  - Generated manifest evidence must be deterministic across repeated test runs.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | The manifest is derived from executable backend graph contracts and validated in tests. |
| Baseline Snapshot | yes | Before and after manifest artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Manifest ownership must stay under astrology runtime, not API, DB or frontend. |
| Allowlist Exception | no | No allowlist handling is authorized for this internal manifest story. |
| Contract Shape | yes | The graph manifest and node IO schema are the core implementation contract. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Schema gaps and public exposure must remain blocked. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`;
  - `backend/app/domain/astrology/runtime/natal_calculation_graph.py`;
  - `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`;
  - new manifest contract module under `backend/app/domain/astrology/runtime`.
- Runtime/domain artifacts:
  - `CalculationGraphDefinition`;
  - graph family registry entry for `natal_chart_v1`;
  - graph manifest contract;
  - node IO schema contract;
  - manifest validator;
  - manifest comparison result.
- Secondary evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_manifest.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_manifest.py`;
  - `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`;
  - `AST guard`, `app.routes`, `app.openapi()` and `TestClient`.
- Static scans alone are not sufficient because:
  - runtime derivation, schema validation, comparison behavior and API neutrality must be proven from executable tests.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/evidence/manifest-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/evidence/manifest-after.json`
- Expected invariant:
  - the only allowed surface delta is an internal backend runtime manifest contract plus targeted tests and evidence files.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Graph manifest contract | `backend/app/domain/astrology/runtime/calculation_graph_manifest.py` | API routers, DB models, frontend |
| Manifest validation | `backend/app/domain/astrology/runtime/calculation_graph_manifest_validator.py` | runner-only code |
| Natal manifest factory | `backend/app/domain/astrology/runtime/natal_calculation_graph.py` | duplicate graph module |
| Manifest tests | `backend/tests/unit/domain/astrology/test_calculation_graph_manifest.py` | broad integration tests only |
| API neutrality proof | `backend/tests/architecture/test_api_contract_neutrality.py` | frontend smoke tests |

## 4e. Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this internal graph manifest contract.

## 4f. Contract Shape

- Contract type:
  - internal typed manifest for calculation graphs;
  - internal typed node IO schema;
  - no HTTP endpoint, public serializer or frontend type.
- Fields:
  - `graph_code`: stable graph identifier;
  - `graph_version`: stable graph version;
  - `family_code`: graph family code from the canonical family registry;
  - `required_inputs`: stable input descriptors;
  - `nodes`: ordered node manifest entries;
  - `compatibility_policy`: allowed delta classification for comparisons.
- Node manifest fields:
  - `code`: stable node identifier;
  - `input_schema`: required input descriptors consumed by the node;
  - `output_schema`: produced output descriptor;
  - `depends_on`: required dependency keys;
  - `optional_depends_on`: optional dependency keys.
- Required graph:
  - `natal_chart_v1`.
- Required fields:
  - `graph_code`;
  - `graph_version`;
  - `family_code`;
  - `required_inputs`;
  - `nodes`;
  - `nodes[].code`;
  - `nodes[].input_schema`;
  - `nodes[].output_schema`;
  - `nodes[].depends_on`;
  - `compatibility_policy`.
- Optional fields:
  - `nodes[].optional_depends_on`.
- Compatibility policy values:
  - `compatible`;
  - `breaking`.
- Status codes:
  - no HTTP endpoint, method or status code is changed.
- Serialization names:
  - no public JSON key is renamed or added.
- Frontend type impact:
  - none; no frontend contract changes are allowed.
- Generated contract impact:
  - `app.openapi()` must not expose graph manifest or node IO schema models.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## 4h. Reintroduction Guard

- Guard target:
  - every node keeps a declared input schema;
  - every node keeps a declared output schema;
  - duplicate output keys are rejected;
  - unknown node inputs are rejected;
  - manifest models stay internal to backend domain runtime;
  - no public API, OpenAPI, DB migration or frontend delta is introduced.
- Guard mechanism:
  - unit tests for valid `natal_chart_v1` manifest;
  - unit tests for invalid manifests with duplicate outputs, unknown inputs and absent schemas;
  - unit tests for manifest comparison classifications;
  - AST guard or targeted `rg` scan for ownership and public exposure;
  - `TestClient`, `app.routes` and `app.openapi()` API neutrality evidence.
- Guard owner:
  - `backend/tests/unit/domain/astrology/test_calculation_graph_manifest.py`;
  - `backend/tests/unit/domain/astrology/test_natal_calculation_graph_manifest.py`;
  - `backend/tests/architecture/test_api_contract_neutrality.py`.
- Guard evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_manifest.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_manifest.py`;
  - `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`;
  - `AST guard`, `app.routes`, `app.openapi()` and `TestClient`.

## 4i. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation evidence | `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/evidence/validation.md` | Keep lint, tests and scans. |
| Manifest before | `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/evidence/manifest-before.json` | Capture prior graph contract. |
| Manifest after | `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/evidence/manifest-after.json` | Capture final manifest. |
| Comparison evidence | `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/evidence/manifest-comparison.md` | Record delta checks. |
| Review output | `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## 5. Current State Evidence

- Evidence 1: `_story_briefs/cs-247-graph-manifest-node-io-schema-contract.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to update `CS-247`.
- Evidence 3: `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md` - dependency story read.
- Evidence 4: `backend/app/domain/astrology/runtime/calculation_graph_contracts.py` - graph contracts read.
- Evidence 5: `backend/app/domain/astrology/runtime/natal_calculation_graph.py` - current `natal_chart_v1` graph read.
- Evidence 6: `backend/app/domain/astrology/runtime/calculation_graph_validator.py` - current validation behavior read.
- Evidence 7: `backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py` - existing graph tests read.
- Evidence 8: `resolve_guardrails.py` - scoped resolver run for backend-domain graph manifest surfaces.
- Source-alignment evidence: ACs cover manifest fields, node IO schema, natal graph linkage, invalid manifests,
  comparison behavior, no public exposure and persisted evidence.

## 6. Target State

- `natal_chart_v1` exposes a validated internal manifest with graph identity, version, family and compatibility policy.
- Every node in `natal_chart_v1` declares input and output schema descriptors.
- Manifest validation rejects duplicate outputs, unknown required inputs and missing input or output schemas.
- Manifest comparison classifies contract deltas deterministically as compatible or breaking.
- The manifest describes the graph currently executed by the natal runtime without changing calculation behavior.
- No public API, frontend, DB, migration, auth, i18n, style or build surface changes.

## 6a. Regression Guardrails

Scope vector:

- backend-domain: yes;
- calculation-graph: yes;
- runtime-manifest: yes;
- node-io-schema: yes;
- public API: no behavior delta;
- DB/migrations: no;
- frontend/style/build/i18n/auth: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | local | Backend ownership stays in canonical app paths; manifest does not move into API routing. |
| RG-022 | local | Backend tests and validation evidence remain mandatory for story closure. |

Non-applicable examples:

- RG-047 frontend inline styles: out of scope, no TSX or CSS surface is touched.
- RG-052 frontend CSS namespace migration: out of scope, no style or build output is touched.
- RG-041 entitlement documentation: out of scope, no entitlement or frontend build surface is touched.

Registry gap:

- No exact graph-manifest or node-IO invariant was returned by the scoped resolver.
- Do not enrich `_condamad/stories/regression-guardrails.md` during this normal story generation.

## 7. Acceptance Criteria

| AC | Requirement | Evidence |
|---|---|---|
| AC1 | `natal_chart_v1` exposes a validated manifest. | Evidence profile: json_contract_shape; `pytest` and generated manifest. |
| AC2 | Each node declares input schema descriptors. | Evidence profile: json_contract_shape; `pytest`; `AST guard`; generated manifest. |
| AC3 | Each node declares one output schema descriptor. | Evidence profile: json_contract_shape; `pytest`; `AST guard`; generated manifest. |
| AC4 | Duplicate output keys are rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_manifest.py`. |
| AC5 | Unknown required inputs are rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_manifest.py`. |
| AC6 | Missing node schemas are rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_manifest.py`. |
| AC7 | Manifest comparison classifies breaking deltas. | Evidence profile: baseline_before_after_diff; `pytest`; generated manifest. |
| AC8 | Public API runtime contract is unchanged. | Evidence profile: runtime_openapi_contract; `pytest` runs API neutrality; `app.routes`; `app.openapi()`. |
| AC9 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-247 evidence paths. |

## 8. Implementation Tasks

- [ ] Task 1: Create typed graph manifest and node IO schema contracts with French file comment and docstrings. (AC: AC1, AC2, AC3)
- [ ] Task 2: Build the `natal_chart_v1` manifest from the existing graph definition and family registry. (AC: AC1)
- [ ] Task 3: Validate duplicate outputs, unknown inputs and missing node schemas. (AC: AC4, AC5, AC6)
- [ ] Task 4: Add deterministic comparison behavior for compatibility policy decisions. (AC: AC7)
- [ ] Task 5: Add targeted unit tests for valid natal manifest and invalid manifest cases. (AC: AC1, AC2, AC3, AC4, AC5, AC6)
- [ ] Task 6: Add or reuse API neutrality proof with `app.routes`, `app.openapi()` and `TestClient`. (AC: AC8)
- [ ] Task 7: Persist before, after, comparison and validation evidence under the CS-247 story folder. (AC: AC9)

## 9. Mandatory Reuse / DRY Constraints

- Reuse `CalculationGraphDefinition`, `CalculationInputDefinition` and `CalculationNodeDefinition`.
- Reuse the canonical graph family registry from CS-246 for `family_code`.
- Keep one manifest model and one validator path for graph manifest validation.
- Do not duplicate node lists outside the existing natal graph definition and manifest factory.
- Do not add external packages for schema description, validation or comparison.
- Keep names typed and explicit; avoid unstructured dictionaries for core manifest data.

## 10. No Legacy / Forbidden Paths

- No legacy manifest model may be added outside the canonical runtime module.
- No compatibility route path may expose graph manifest data.
- No fallback resolver may silently accept unknown graph inputs.
- No shim may tolerate missing node input or output schemas.
- No frontend file may be modified.
- No DB model, seed or migration may be modified.
- No public API route, serializer or OpenAPI schema may expose the internal manifest.

## 11. Files to Inspect First

- `_story_briefs/cs-247-graph-manifest-node-io-schema-contract.md`.
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md`.
- `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`.
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`.
- `backend/app/domain/astrology/runtime/calculation_graph_validator.py`.
- `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`.
- `backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`.
- `backend/tests/unit/domain/astrology/test_calculation_graph_validator.py`.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output only.

## 12. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/calculation_graph_manifest.py`.
- `backend/app/domain/astrology/runtime/calculation_graph_manifest_validator.py`.
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`.
- `backend/app/domain/astrology/runtime/__init__.py`.
- `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/evidence/validation.md`.
- `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/evidence/manifest-before.json`.
- `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/evidence/manifest-after.json`.
- `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/evidence/manifest-comparison.md`.

Likely tests:

- `backend/tests/unit/domain/astrology/test_calculation_graph_manifest.py`.
- `backend/tests/unit/domain/astrology/test_natal_calculation_graph_manifest.py`.
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
pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_manifest.py
pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_manifest.py
pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py
pytest -q backend/tests/architecture/test_api_contract_neutrality.py
```

Run API neutrality proof:

```powershell
python -c "from app.main import app; assert 'CalculationGraphManifest' not in str(app.openapi())"
python -c "from app.main import app; assert not any('graph-manifest' in getattr(r, 'path', '') for r in app.routes)"
```

Run ownership and no-drift scans:

```powershell
rg -n "GraphManifest|NodeIOSchema|calculation_graph_manifest" backend/app/domain/astrology/runtime backend/tests/unit/domain/astrology
rg -n "GraphManifest|NodeIOSchema|graph-manifest|node-io-schema" backend/app/api frontend backend/alembic -g "*.py" -g "*.ts" -g "*.tsx"
```

Persist evidence checks:

```powershell
python -c "from pathlib import Path; assert Path('_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/evidence/validation.md').exists()"
python -c "from pathlib import Path; assert Path('_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/evidence/manifest-after.json').exists()"
```

## 15. Regression Risks

- A manifest generated from duplicated graph data can drift from the executed natal graph.
- Loose type descriptors can make future graph families appear comparable while their IO contracts diverge.
- Public exposure can leak internal graph topology before debug and product decisions are approved.
- A comparison function that ignores removed inputs or outputs can miss breaking contract changes.

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
- Persist commands, results, scans, `app.routes`, `app.openapi()` and manifest snapshots under the CS-247 folder.

## 17. References

- `_story_briefs/cs-247-graph-manifest-node-io-schema-contract.md`.
- `_condamad/stories/story-status.md`.
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md`.
- `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`.
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`.
- `backend/app/domain/astrology/runtime/calculation_graph_validator.py`.
- `backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`.
- Scoped guardrail resolver output for backend-domain graph manifest scope.
