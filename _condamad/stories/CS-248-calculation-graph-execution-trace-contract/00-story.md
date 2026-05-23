# Story CS-248 calculation-graph-execution-trace-contract: Add Calculation Graph Execution Trace Contract
Status: ready-to-dev

## 1. Objective

Create one internal, versioned execution trace contract for calculation graph runs so trace, provenance and replay snapshot
stay distinct while runner success, failure and cache behavior become observable without exposing raw runtime payloads.

## 2. Trigger / Source

- Source type: architecture-runtime-contract.
- Source reference: `_story_briefs/cs-248-calculation-graph-execution-trace-contract.md`.
- Architecture source: `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/03-story-candidates.md#SC-ARCH-003`.
- Remapped architecture item: `SC-ARCH-003`.
- Selected story writer mode: Fast Story Writer Mode.
- Source-alignment evidence: the story preserves the brief stakes by covering ordered trace, redaction, cache,
  normalized errors, provenance references, internal-only scope and the trace/provenance/replay distinction.

## 3. Domain Boundary

This story belongs to one domain:

- Domain: backend-domain
- In scope:
  - internal execution trace model for calculation graph runs;
  - trace factory or builder connected to `CalculationGraphRunner` results;
  - ordered node trace entries for success, failed node and cache hit cases;
  - redaction of sensitive or large inputs and outputs into keys or references;
  - normalized technical error kinds without raw payload dumps;
  - provenance references from runner output without duplicating full provenance payload values;
  - documentation in code or backend docs that separates `trace`, `provenance` and `replay snapshot`;
  - targeted unit and architecture tests.
- Out of scope:
  - public API routes, OpenAPI payload additions, frontend UI, DB schema, migrations, auth, i18n, styles and build tooling;
  - admin UI, trace persistence, retention policy and external observability export;
  - turning the trace into a replay snapshot;
  - changing astrology calculation algorithms or migrating a public runtime surface.
- Explicit non-goals:
  - no frontend route, screen, client generation or UI validation;
  - no Alembic migration or persistence model;
  - no public JSON contract change;
  - no replay reconstruction capability;
  - no registry enrichment in `_condamad/stories/regression-guardrails.md` during this story generation.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain trace contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only an internal execution trace contract for calculation graph runs.
  - Connect the trace to runner success, failed node and cache hit results.
  - Keep provenance as referenced source evidence, not copied raw payload output.
  - Keep replay snapshot behavior out of scope.
  - Keep public API, frontend, DB, migrations and calculation outputs unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: trace storage, public exposure, retention, admin access or replay reconstruction is requested.
- Additional validation rules:
  - `execution_trace.version` is stable and asserted by tests.
  - `execution_trace.graph_code` and `execution_trace.graph_version` come from the executed graph definition.
  - the trace exposes the runner node order deterministically.
  - every node trace has `code`, `status`, `cache_status`, `duration_ms`, `input_keys`, `output_keys`, `error_kind` and provenance refs.
  - input and output payload values are redacted into key lists or references.
  - cache hits expose hit state without cached values.
  - failed node traces expose normalized error kind without raw cause objects.
  - trace, provenance and replay snapshot are documented as separate contracts.
  - `app.routes`, `app.openapi()`, `pytest` and `TestClient` prove no public API delta.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Runner results and graph definitions are the runtime basis for trace construction. |
| Baseline Snapshot | yes | Before and after trace artifacts prove the only allowed backend runtime delta. |
| Ownership Routing | yes | Trace ownership must stay under astrology runtime, not API, DB, frontend or docs-only paths. |
| Allowlist Exception | no | No allowlist handling is authorized for this internal trace story. |
| Contract Shape | yes | The versioned trace schema is the core implementation contract. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Raw payload exposure, public routes and replay behavior must stay blocked. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `backend/app/domain/astrology/runtime/calculation_graph_runner.py`;
  - `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`;
  - expected new module `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py`;
  - expected tests under `backend/tests/unit/domain/astrology/`.
- Runtime/domain artifacts:
  - `CalculationGraphExecutionResult`;
  - `CalculationNodeResult`;
  - `CalculationGraphExecutionError`;
  - `CalculationGraphDefinition`;
  - new versioned execution trace contract;
  - redaction policy value or typed enum;
  - trace/provenance/replay contract note.
- Secondary evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_execution_trace.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`;
  - `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`;
  - `AST guard`, `app.routes`, `app.openapi()` and `TestClient`.
- Static scans alone are not sufficient because:
  - success, failed node, cache and redaction behavior must be proven from executable runner results.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/evidence/trace-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/evidence/trace-after.json`
- Expected invariant:
  - the only allowed surface delta is an internal backend runtime execution trace contract plus targeted tests and evidence.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Execution trace contract | `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py` | API routers, DB models, frontend |
| Trace builder | `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py` | public serializer or admin route |
| Runner trace hookup | `backend/app/domain/astrology/runtime/calculation_graph_runner.py` | calculator modules |
| Trace tests | `backend/tests/unit/domain/astrology/test_calculation_graph_execution_trace.py` | broad API-only tests |
| API neutrality proof | `backend/tests/architecture/test_api_contract_neutrality.py` | frontend smoke tests |

## 4e. Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this internal execution trace contract.

## 4f. Contract Shape

- Contract type:
  - internal typed execution trace for calculation graph runs;
  - no HTTP endpoint, public serializer or frontend type.
- Fields:
  - `version`;
  - `graph_code`;
  - `graph_version`;
  - `run_id`;
  - `nodes`;
  - `redaction_policy`;
  - `provenance_refs`.
- Required fields:
  - `version`;
  - `graph_code`;
  - `graph_version`;
  - `nodes`;
  - `redaction_policy`;
  - `nodes[].code`;
  - `nodes[].status`;
  - `nodes[].cache_status`;
  - `nodes[].input_keys`;
  - `nodes[].output_keys`;
  - `nodes[].error_kind`.
- Node fields:
  - `code`;
  - `status`;
  - `cache_status`;
  - `duration_ms`;
  - `input_keys`;
  - `output_keys`;
  - `error_kind`;
  - `provenance_ref`.
- Required trace fields from the brief:
  - `execution_trace.version`;
  - `execution_trace.graph_code`;
  - `execution_trace.graph_version`;
  - `execution_trace.nodes[].code`;
  - `execution_trace.nodes[].status`;
  - `execution_trace.nodes[].cache_status`;
  - `execution_trace.nodes[].input_keys`;
  - `execution_trace.nodes[].output_keys`;
  - `execution_trace.nodes[].error_kind`;
  - `execution_trace.redaction_policy`.
- Optional fields:
  - `run_id` may be derived from a supplied correlation id;
  - `duration_ms` may be null for tests that do not measure time.
- Status codes:
  - no HTTP endpoint, method or status code is changed.
- Serialization names:
  - no public JSON key is renamed or added.
- Frontend type impact:
  - none; no frontend contract changes are allowed.
- Generated contract impact:
  - `app.openapi()` must not expose execution trace, provenance refs or replay snapshot models.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## 4h. Reintroduction Guard

- Guard target:
  - trace payloads expose only keys, statuses, cache state, normalized error kinds and provenance references;
  - no raw input, raw output, cause object or cached value is dumped into the trace;
  - trace and provenance stay separate;
  - replay snapshot stays unimplemented;
  - no public API, OpenAPI, DB migration or frontend delta is introduced;
  - no second trace contract appears outside the canonical runtime module.
- Guard mechanism:
  - unit tests for success trace ordering;
  - unit tests for failed node trace shape;
  - unit tests for cache hit trace shape;
  - unit tests or AST guard for redaction and no replay snapshot;
  - targeted `rg` scans for public exposure and replay keywords;
  - `TestClient`, `app.routes` and `app.openapi()` API neutrality evidence.
- Guard owner:
  - `backend/tests/unit/domain/astrology/test_calculation_graph_execution_trace.py`;
  - `backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`;
  - `backend/tests/architecture/test_api_contract_neutrality.py`.
- Guard evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_execution_trace.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`;
  - `pytest -q backend/tests/architecture/test_api_contract_neutrality.py`;
  - `AST guard`, `app.routes`, `app.openapi()` and `TestClient`.

## 4i. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation evidence | `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/evidence/validation.md` | Keep lint, tests and scans. |
| Trace before | `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/evidence/trace-before.md` | Record absence or baseline. |
| Trace after | `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/evidence/trace-after.json` | Capture final trace contract. |
| API neutrality | `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/evidence/openapi-routes.md` | Keep routes and OpenAPI proof. |
| Review output | `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## 5. Current State Evidence

- Evidence 1: `_story_briefs/cs-248-calculation-graph-execution-trace-contract.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to update `CS-248`.
- Evidence 3: `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md` - dependency story read.
- Evidence 4: `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/00-story.md` - dependency story read.
- Evidence 5: `_condamad/stories/CS-227-calculation-graph-runner-cache-provenance/00-story.md` - runner provenance story read.
- Evidence 6: `backend/app/domain/astrology/runtime/calculation_graph_runner.py` - runner result and provenance behavior read.
- Evidence 7: `backend/app/domain/astrology/runtime/natal_calculation_graph.py` - graph code and version behavior read.
- Evidence 8: `backend/tests/unit/domain/astrology/test_calculation_graph_runner.py` - current success, error and cache tests read.
- Evidence 9: `resolve_guardrails.py` - scoped resolver run for backend-domain execution trace surfaces.
- Source-alignment evidence: ACs cover success trace, failed node trace, cache visibility, redaction, terminology,
  internal-only scope, API neutrality and persisted evidence without narrowing the brief.

## 6. Target State

- A single internal execution trace contract exists under astrology runtime.
- Every trace includes stable version, graph code, graph version, run id or correlation id, ordered nodes and redaction policy.
- Every node trace includes code, status, cache status, non-sensitive duration metric, input keys, output keys,
  normalized error kind and provenance reference.
- Success, failed node and cache hit runner outcomes produce deterministic trace entries.
- Trace values never contain raw sensitive or large input and output payloads.
- `trace`, `provenance` and `replay snapshot` are documented as distinct concepts.
- No public API, frontend, DB, migration, auth, i18n, style or build surface changes.

## 6a. Regression Guardrails

Scope vector:

- backend-domain: yes;
- calculation-graph: yes;
- execution-trace: yes;
- redaction: yes;
- public API: no behavior delta;
- DB/migrations: no;
- frontend/style/build/i18n/auth: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-002 | local | Backend ownership stays in canonical app paths; trace does not move into API routing. |
| RG-003 | local | API route architecture remains unchanged while trace stays internal. |
| RG-010 | local | Backend test topology stays under collected backend test roots for trace and neutrality tests. |

Non-applicable examples:

- RG-047 frontend inline styles: out of scope, no TSX or CSS surface is touched.
- RG-052 frontend CSS namespace migration: out of scope, no style or build output is touched.
- RG-041 entitlement documentation: out of scope, no entitlement or frontend build surface is touched.

Registry gap:

- No exact calculation-graph execution trace, redaction or replay invariant was returned by the scoped resolver.
- Do not enrich `_condamad/stories/regression-guardrails.md` during this normal story generation.

## 7. Acceptance Criteria

| AC | Requirement | Evidence |
|---|---|---|
| AC1 | A successful graph run produces ordered nodes. | Evidence profile: json_contract_shape; `backend/tests/unit/domain/astrology/test_calculation_graph_execution_trace.py`. |
| AC2 | The trace exposes stable graph identity fields. | Evidence profile: json_contract_shape; `pytest`; generated trace artifact. |
| AC3 | Node traces expose non-sensitive duration metrics. | Evidence profile: json_contract_shape; `pytest`; generated trace artifact. |
| AC4 | Failed node traces expose error kind. | Evidence profile: json_contract_shape; `backend/tests/unit/domain/astrology/test_calculation_graph_execution_trace.py`. |
| AC5 | Cache hits hide cached values. | Evidence profile: json_contract_shape; `backend/tests/unit/domain/astrology/test_calculation_graph_execution_trace.py`. |
| AC6 | Raw input payload values are redacted. | Evidence profile: targeted_forbidden_symbol_scan; `pytest`; `AST guard`. |
| AC7 | Raw output payload values are redacted. | Evidence profile: targeted_forbidden_symbol_scan; `pytest`; `AST guard`. |
| AC8 | The terminology contract separates trace. | Evidence profile: json_contract_shape; `pytest`; targeted `rg`. |
| AC9 | Public API runtime contract is unchanged. | Evidence profile: runtime_openapi_contract; `pytest`; `TestClient`; `app.routes`; `app.openapi()`. |
| AC10 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-248 evidence paths. |

## 8. Implementation Tasks

- [ ] Task 1: Create the typed execution trace contract module with French file comment and docstrings. (AC: AC1, AC2, AC3)
- [ ] Task 2: Add a trace builder that consumes graph definition and runner result objects. (AC: AC1, AC2, AC3)
- [ ] Task 3: Map non-sensitive node duration or technical metric into the trace without payload values. (AC: AC3)
- [ ] Task 4: Map runner failed node results to normalized `error_kind` values. (AC: AC4)
- [ ] Task 5: Map cache hit node results to `cache_status` without copied cached values. (AC: AC5)
- [ ] Task 6: Add redaction behavior for input and output payload values. (AC: AC6, AC7)
- [ ] Task 7: Add contract text or typed naming that separates trace, provenance and replay snapshot. (AC: AC8)
- [ ] Task 8: Add targeted unit tests for success, failed node, cache, duration metric and redaction cases. (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7)
- [ ] Task 9: Add or reuse API neutrality proof with `app.routes`, `app.openapi()` and `TestClient`. (AC: AC9)
- [ ] Task 10: Persist before, after, API neutrality and validation evidence under the CS-248 story folder. (AC: AC10)

## 9. Mandatory Reuse / DRY Constraints

- Reuse `CalculationGraphExecutionResult`, `CalculationNodeResult` and `CalculationGraphExecutionError`.
- Reuse `CalculationGraphDefinition.graph_code` and graph version data instead of duplicating graph identity.
- Reuse runner provenance references without copying raw provenance values into the trace.
- Keep one canonical execution trace module.
- Do not add external packages for trace generation, serialization, timing or redaction.
- Keep names typed and explicit; avoid unstructured dictionaries for core trace data.

## 10. No Legacy / Forbidden Paths

- No legacy trace contract may be added outside the canonical runtime module.
- No compatibility route path may expose execution trace data.
- No fallback resolver may emit raw inputs or outputs when redaction cannot classify a value.
- No shim may transform the trace into a replay snapshot.
- No frontend file may be modified.
- No DB model, seed or migration may be modified.
- No public API route, serializer or OpenAPI schema may expose the internal trace.
- No persistent trace store, retention policy, admin endpoint or external exporter may be added.

## 11. Files to Inspect First

- `_story_briefs/cs-248-calculation-graph-execution-trace-contract.md`.
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md`.
- `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/00-story.md`.
- `_condamad/stories/CS-227-calculation-graph-runner-cache-provenance/00-story.md`.
- `backend/app/domain/astrology/runtime/calculation_graph_runner.py`.
- `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`.
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`.
- `backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output only.

## 12. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py`.
- `backend/app/domain/astrology/runtime/calculation_graph_runner.py`.
- `backend/app/domain/astrology/runtime/__init__.py`.
- `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/evidence/validation.md`.
- `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/evidence/trace-before.md`.
- `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/evidence/trace-after.json`.
- `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/evidence/openapi-routes.md`.

Likely tests:

- `backend/tests/unit/domain/astrology/test_calculation_graph_execution_trace.py`.
- `backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`.
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
pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_execution_trace.py
pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py
pytest -q backend/tests/architecture/test_api_contract_neutrality.py
```

Run API neutrality proof:

```powershell
python -c "from app.main import app; assert 'ExecutionTrace' not in str(app.openapi())"
python -c "from app.main import app; assert not any('execution-trace' in getattr(r, 'path', '') for r in app.routes)"
```

Run redaction and no-drift scans:

```powershell
rg -n "ExecutionTrace|redaction_policy|provenance_ref" backend/app/domain/astrology/runtime backend/tests/unit/domain/astrology
rg -n "ExecutionTrace|execution-trace|replay_snapshot|raw_input|raw_output" backend/app/api frontend backend/alembic -g "*.py" -g "*.ts" -g "*.tsx"
```

Persist evidence checks:

```powershell
python -c "from pathlib import Path; assert Path('_condamad/stories/CS-248-calculation-graph-execution-trace-contract/evidence/validation.md').exists()"
python -c "from pathlib import Path; assert Path('_condamad/stories/CS-248-calculation-graph-execution-trace-contract/evidence/trace-after.json').exists()"
```

## 15. Regression Risks

- Copying raw provenance values into trace output can leak sensitive or large runtime payloads.
- Treating trace as replay can imply deterministic reconstruction that is not approved.
- Public exposure can leak internal graph topology and technical failure details before product decisions.
- A second trace model can drift from the runner result contract.
- Cache hit visibility can become a value leak without explicit redaction tests.

## 16. Dev Agent Instructions

- Start by reading the files listed in `Files to Inspect First`.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Keep the implementation typed, small and local to astrology runtime.
- Keep French global comments and public or non-trivial docstrings in new or significantly modified application files.
- Do not create `requirements.txt`.
- Do not modify frontend, DB migrations, API routes, auth, i18n, style or build tooling.
- Do not persist traces or create public exposure.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Persist commands, results, scans, `app.routes`, `app.openapi()` and trace snapshots under the CS-248 folder.

## 17. References

- `_story_briefs/cs-248-calculation-graph-execution-trace-contract.md`.
- `_condamad/stories/story-status.md`.
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/00-story.md`.
- `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/00-story.md`.
- `_condamad/stories/CS-227-calculation-graph-runner-cache-provenance/00-story.md`.
- `backend/app/domain/astrology/runtime/calculation_graph_runner.py`.
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`.
- `backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`.
- Scoped guardrail resolver output for backend-domain execution trace scope.
