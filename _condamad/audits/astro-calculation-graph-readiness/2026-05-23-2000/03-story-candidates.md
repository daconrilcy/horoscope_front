# Story Candidates - Astro Calculation Graph Readiness

This file qualifies the source-brief labels CS-243, CS-244 and CS-245 as proposals for story writing, not implementation in this audit.

Identifier caveat: `CS-243` and `CS-244` are already allocated in `_condamad/stories/story-status.md` to different audit stories. The labels below preserve the source brief vocabulary, but story writing must remap them to available CONDAMAD story IDs before creating or modifying story folders.

## SC-001 CS-243 Add Calculation Graph Execution Trace Contract

- Source finding: F-003
- Suggested story title: Source-label CS-243 - Add calculation graph execution trace contract
- Suggested archetype: trace-contract-hardening
- Primary domain: backend astrology calculation graph runtime
- Priority: P1
- Required contracts: Runtime Source of Truth, Baseline Snapshot, Contract Shape, Ownership Routing, Reintroduction Guard, Persistent Evidence
- Draft objective: Define a stable execution trace contract for graph runs that records graph code/version, node status, input keys, output keys, cache hits, errors, timings if approved, and redacted provenance without exposing raw objects as the only trace.
- Closure intent: full-closure
- Must include: separate trace/provenance/replay vocabulary; trace DTO or dataclass; redaction policy; tests for success, cache hit, validation failure, missing input, unknown calculator and calculator failure; explicit decision whether trace is returned only in-process or persisted by another owner.
- Validation hints: run `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_runner.py`; add focused trace contract tests; scan for `trace`, `provenance`, `raw output`, `cache_hits` and `CalculationGraphExecutionResult`.
- Blockers: stop if trace persistence location, retention or exposure channel is required but no product/security decision exists; also stop before story creation if the source-label CS-243 has not been remapped away from the existing tracker story.

### Exhaustive Files To Modify

- Application files: exact runner/contract files selected by the remapped source-label CS-243 candidate, expected starting surface `backend/app/domain/astrology/runtime/calculation_graph_runner.py` and possibly a new graph trace contract file under the same runtime owner.
- Governance/test files: focused unit tests under existing `backend/tests/unit/domain/astrology/` ownership; optional guardrail update only after a durable trace invariant exists.
- Before evidence: E-007, E-010, E-012.
- After evidence: trace contract tests prove every node result and graph-level error has a stable redacted trace; provenance remains distinct from replay; F-003 closes.
- Stop condition: no in-domain execution path exposes only raw in-memory provenance when a trace is requested; if persistence is not approved, the story explicitly marks replay persistence as blocked rather than emitting another discovery follow-up.

## SC-002 CS-244 Add Graph Manifest And Node IO Schema Validation

- Source finding: F-002
- Suggested story title: Source-label CS-244 - Add graph manifest and node IO schema validation
- Suggested archetype: graph-manifest-contract
- Primary domain: backend astrology calculation graph contracts
- Priority: P1
- Required contracts: Runtime Source of Truth, Baseline Snapshot, Contract Shape, Ownership Routing, Reintroduction Guard, Persistent Evidence, No Legacy
- Draft objective: Turn descriptive graph definitions into manifest-backed contracts that can validate node IO schemas, graph versions and compatibility for `natal_chart_v1` and future family templates.
- Closure intent: full-closure
- Must include: `natal_chart_v1` manifest, node input/output schema ownership, graph version compatibility policy, comparison rules for two manifests, validation errors for missing schema and incompatible node output, and no wildcard allowlist.
- Validation hints: run `pytest -q backend/tests/unit/domain/astrology/test_calculation_graph_contracts.py backend/tests/unit/domain/astrology/test_calculation_graph_validator.py backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py`; add manifest/schema validation tests; targeted scans for `value_type`, `output_key`, `graph_code`, `version`, `schema`, `manifest`, `compare`.
- Blockers: stop if product or architecture cannot decide whether schemas are Pydantic, dataclass metadata, JSON Schema or an internal minimal schema language; also stop before story creation if the source-label CS-244 has not been remapped away from the existing tracker story.

### Exhaustive Files To Modify

- Application files: `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`, `backend/app/domain/astrology/runtime/calculation_graph_validator.py`, `backend/app/domain/astrology/runtime/natal_calculation_graph.py`, plus an exact new manifest/schema module only if selected by the story.
- Governance/test files: targeted tests under `backend/tests/unit/domain/astrology/`; guardrail entry only after manifest/schema behavior becomes durable.
- Before evidence: E-006, E-008, E-009, E-010, E-012, E-013.
- After evidence: manifest validation fails for missing or incompatible node IO schema; `natal_chart_v1` manifest validates; comparison tests classify compatible/incompatible graph versions; F-002 and F-004 close.
- Stop condition: every current natal node has schema coverage or a documented user-decision blocker, and graph comparison no longer remains a separate unowned concern inside this domain.

## SC-003 CS-245 Prepare Graph Runner For Multi-Chart Graph Families

- Source finding: F-001
- Suggested story title: Source-label CS-245 - Prepare graph runner for multi-chart graph families
- Suggested archetype: graph-family-readiness
- Primary domain: backend astrology calculation graph runtime
- Priority: P1
- Required contracts: Runtime Source of Truth, Baseline Snapshot, Ownership Routing, Reintroduction Guard, Persistent Evidence, No Legacy
- Draft objective: Establish the canonical multi-graph family routing, registry ownership, input prerequisites and cache/invalidation boundary needed before `transit_chart_v1`, `synastry_chart_v1`, `solar_return_v1`, `progressed_chart_v1` and `composite_chart_v1` are implemented.
- Closure intent: phased-with-map
- Must include: one graph-family registry/router decision; exact treatment for single-chart versus multi-chart inputs; family prerequisite matrix; cache boundary that keeps runner-local cache separate from application cache; reference-version, ephemeris and input fingerprint invalidation rules; no new graph implementation unless explicitly authorized by the story.
- Validation hints: run existing runner/natal graph tests; add architecture tests or scans proving no duplicate graph routing path; targeted scans for all five family codes and cache/invalidation terms.
- Blockers: stop if product cannot decide whether multi-chart families share one runtime reference, how synastry/composite pair inputs are represented, or whether durable application cache is required; also stop before story creation if the source-label CS-245 conflicts with the tracker at writing time.

### Exhaustive Files To Modify

- Application files: exact graph-family routing/registry files selected by CS-245; likely starting surfaces are `backend/app/domain/astrology/runtime/calculation_graph_runner.py`, `backend/app/domain/astrology/runtime/natal_calculation_registry.py`, `backend/app/domain/astrology/natal_calculation.py`, and a new narrowly named runtime graph-family registry only if needed.
- Governance/test files: focused unit/architecture tests under `backend/tests/unit/domain/astrology/`; optional guardrail update after multi-family routing and cache boundary become durable.
- Before evidence: E-006, E-007, E-009, E-011, E-012, E-013, E-014.
- After evidence: one canonical routing owner exists; target family prerequisites are finite and testable; no duplicate routing/registry conventions exist; app cache is either explicitly out of scope with guard or owned with invalidation keys; F-001 and F-005 close or remain blocked by named user decisions.
- Stop condition: all five target families have a readiness row with owner, required inputs, registry decision, cache decision and blocker status; no "next family batch" follow-up is needed for basic runner readiness.

## SC-004 CS-244 Add Graph Manifest Comparison And Version Compatibility

- Source finding: F-004
- Suggested story title: Source-label CS-244 - Add graph manifest comparison and version compatibility
- Suggested archetype: graph-manifest-contract
- Primary domain: backend astrology calculation graph contracts
- Priority: P2, implemented only as part of the P1 source-label CS-244 manifest work from SC-002 after tracker remapping.
- Required contracts: Runtime Source of Truth, Baseline Snapshot, Contract Shape, Ownership Routing, Reintroduction Guard, Persistent Evidence
- Draft objective: Close the graph comparison/version compatibility gap inside the graph manifest story by comparing graph code, version, inputs, nodes, dependencies and IO schema compatibility.
- Closure intent: full-closure
- Must include: comparison tests for compatible and incompatible manifests; explicit output for added, removed and changed nodes; no separate comparison service unless the manifest contract proves it is required.
- Validation hints: use the same remapped source-label CS-244 manifest commands as SC-002 plus targeted scans for `compare`, `comparison`, `graph_code`, `version` and all five family codes.
- Blockers: stop if comparison semantics are product-dependent and cannot be decided at contract level.

### Exhaustive Files To Modify

- Application files: same remapped source-label CS-244 manifest/schema files selected by SC-002; no API, frontend, DB or migration file expected.
- Governance/test files: same remapped source-label CS-244 unit tests plus comparison-specific test cases.
- Before evidence: E-012, E-013, E-016.
- After evidence: comparison tests classify compatible and incompatible manifests; F-004 closes without another discovery-only follow-up.
- Stop condition: graph comparison no longer remains an unowned concern inside this audited domain.

## SC-005 CS-245 Define Application Cache Boundary And Reference Invalidation

- Source finding: F-005
- Suggested story title: Source-label CS-245 - Define application cache boundary and reference invalidation
- Suggested archetype: graph-family-readiness
- Primary domain: backend astrology calculation graph runtime
- Priority: P2, implemented only as part of the P1 source-label CS-245 multi-family readiness work from SC-003 after tracker remapping.
- Required contracts: Runtime Source of Truth, Baseline Snapshot, Ownership Routing, Reintroduction Guard, Persistent Evidence, No Legacy
- Draft objective: Close the cache/invalidation gap by keeping runner-local cache per execution and assigning any durable cache to an explicit owner with graph, input, reference-version and ephemeris invalidation keys.
- Closure intent: full-closure
- Must include: no durable cache inside `CalculationGraphRunner`; invalidation key definition; tests or guard proving app cache cannot ignore graph version, reference version and ephemeris metadata; explicit no-cache decision if durable cache is deferred.
- Validation hints: use the same remapped source-label CS-245 commands as SC-003 plus targeted scans for `cache`, `cache_hits`, `reference_version`, `ephemeris_path_hash`, `invalidation`.
- Blockers: stop if durable cache ownership or product need cannot be decided; document a no-cache decision instead of adding an implicit fallback.

### Exhaustive Files To Modify

- Application files: same remapped source-label CS-245 graph-family routing/cache-boundary files selected by SC-003; no runner persistent cache implementation expected.
- Governance/test files: same remapped source-label CS-245 tests plus cache-boundary/invalidation guards.
- Before evidence: E-007, E-008, E-012, E-014.
- After evidence: durable cache is explicitly out of runner scope or has exact invalidation keys; F-005 closes.
- Stop condition: no app cache path can reuse graph outputs without graph version, input fingerprint, reference version and ephemeris evidence.

## Deferred Non-Domain Candidates

- Frontend display, API debug/admin endpoints and persisted trace access are deferred until a product/API story explicitly chooses exposure.
- Astronomical reference-data accuracy and ephemeris hash persistence remain covered by the astronomical accuracy audit and should not be reimplemented by graph-readiness stories.
