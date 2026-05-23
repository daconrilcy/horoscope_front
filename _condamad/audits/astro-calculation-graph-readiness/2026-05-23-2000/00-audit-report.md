# Audit Report - Astro Calculation Graph Readiness

## Audit Scope

- Domain key: `astro-calculation-graph-readiness`
- Domain closure status: `phased-with-map`
- Audit archetype: `custom`
- Read-only scope: backend astrology calculation graph runtime readiness for future graph families.
- Output folder: `_condamad/audits/astro-calculation-graph-readiness/2026-05-23-2000/`

## Closure Analysis

- Prior same-domain audit folders consulted: none; E-004 records that no prior `astro-calculation-graph-readiness` child folder existed.
- Adjacent audit folders consulted: none for same-domain closure; this audit keeps adjacent feature coverage, runtime exposure, reference governance and astronomical accuracy as deferred non-domain context rather than imported evidence.
- Story keys consulted: `CS-225`, `CS-226`, `CS-227`, `CS-228`, `CS-241`, `CS-242`, plus tracker context for the source-brief candidate labels `CS-243`, `CS-244` and `CS-245`.
- Candidate label caveat: the source brief asks this audit to qualify `CS-243`, `CS-244` and `CS-245`, but the current tracker already assigns `CS-243` and `CS-244` to different audit stories. The labels in this folder are therefore source-brief candidate labels and must be remapped by story writing before creating or updating CONDAMAD story folders.
- Active findings after current evidence: F-001, F-002, F-003, F-004 and F-005.
- Closed prior findings: none for this first same-domain audit.
- Guardrails mapped: adjacent RG-144 through RG-148 protect chart object and astrology runtime boundaries; no exact calculation-graph-readiness guardrail exists.
- Implementation files in audited domain: no application file is changed by this audit.
- Governance/test files in audited domain: only the six new audit artifacts are created.
- Deferred non-domain concerns: frontend, API endpoints, DB persistence, auth, i18n, migrations, seed data and product-data exposure remain outside this audit.

## Readiness Matrix

| question | surface_actuelle | preuve_reproductible | niveau_readiness | risque_orchestration | risque_provenance | familles_impactees | story_candidate |
|---|---|---|---|---|---|---|---|
| Runner supports multiple graphs | `CalculationGraphRunner.run(definition, context)` accepts any `CalculationGraphDefinition`; only `natal_chart_v1` is wired by `build_natal_result`. | E-006, E-007, E-010, E-013 | partial | Medium: generic runner exists but no graph selection, registry routing or graph-family catalog is implemented. | Medium: graph identity is returned but no versioned manifest binds graph, inputs and registry. | `transit_chart_v1`, `synastry_chart_v1`, `solar_return_v1`, `progressed_chart_v1`, `composite_chart_v1` | CS-245 |
| `natal_chart_v1` readiness | `natal_chart_v1` has version `1`, 11 inputs, 25 nodes and passes validation. | E-006, E-009, E-010 | ready | Low for natal: execution path is tested through `build_natal_result`. | Medium: provenance is in-memory and minimal. | none | none |
| Nodes are pure | Runner context is immutable and graph definition is pure, but natal node adapters call domain calculators, metrics and provider branches. | E-006, E-010, E-015 | partial | Medium: pure runner is separate from impure calculation adapters, which is acceptable but must be explicit for new families. | Low: no DB/API write found in audited runtime nodes; metrics are the only infra hit. | all five target families | CS-245 |
| Outputs are typed | Contracts carry string `value_type`; selected assembled outputs are type-checked by `NatalResultAssembler`; runner outputs are `object`. | E-006, E-008, E-010 | partial | Medium: graph IO cannot reject a wrong node output before downstream adapter failure. | Medium: replay and comparison cannot rely on machine-readable node IO schemas. | all five target families | CS-244 |
| Dependencies are declared and tested | Validator rejects empty fields, duplicate nodes/outputs/inputs, unknown required dependencies and cycles; natal critical dependencies are tested. | E-006, E-009, E-010 | ready | Low: dependency order is deterministic for current graph. | Low: dependency graph is inspectable. | all five target families | none |
| Graph execution can be traced | Result exposes `node_results`, `execution_order`, `cache_hits` and minimal provenance in memory. | E-007, E-010, E-012 | partial | Medium: no stable trace contract, persistence or redaction policy exists for debug/admin use. | High: provenance currently includes raw output objects and is not replay-grade. | all five target families | CS-243 |
| Graph execution can be replayed | Runner can rerun with a supplied context, but no replay input snapshot, manifest, reference version binding or registry identity contract exists. | E-007, E-012, E-013 | blocked | Medium: same code can be called again but exact historical execution cannot be reconstructed from a persisted trace. | High: reference data and calculator versions are not captured at node IO granularity. | all five target families | CS-243 |
| Graph can be versioned | `CalculationGraphDefinition.version` and `graph_code` exist; `NATAL_GRAPH_VERSION = "1"`. | E-006, E-009 | partial | Medium: version exists but no manifest or compatibility policy defines version changes. | Medium: reference-version invalidation is not tied to graph version. | all five target families | CS-244 |
| Two graphs can be compared | No calculation-graph comparison contract appears in audited runtime surfaces; unrelated API compare/docs are outside this graph domain. | E-012, E-013 | not_started | Medium: future graph-family rollout cannot diff node sets, IO schemas or outputs canonically. | Medium: provenance cannot compare node-level semantics across graph versions or families. | all five target families | CS-244 |
| Local runner cache is sufficient or limited | Local cache skips nodes whose output key is already in the call context and is proven not to mutate the caller input. | E-007, E-010 | partial | Low inside one execution; Medium if treated as application cache. | Low for intra-run reuse; no durability guarantee. | all five target families | none |
| Application cache is required or not required | No application cache exists in the runner; CS-227 explicitly scoped persistent cache out. | E-007, E-012, E-014 | blocked | Medium: multi-family calculations may need durable cache ownership outside runner. | High: invalidation must include graph, reference version, ephemeris and input fingerprint. | all five target families | CS-245 |
| Reference-version invalidation is defined or missing | `NatalResult` stores `reference_version` and ephemeris metadata, and nodes validate missing reference version; no graph cache invalidation contract exists. | E-008, E-012 | partial | Medium: current natal result has reference metadata but runner cache is not invalidation-aware. | High: future app cache cannot safely reuse graph outputs without explicit reference-version invalidation. | all five target families | CS-245 |

## Target Graph Family Readiness

| Graph family | Readiness | Current evidence | Prerequisites | Blocking findings |
|---|---|---|---|---|
| `transit_chart_v1` | partial | Generic runner and declarative dependencies can execute another definition, but no transit graph code or registry exists. | Multi-graph registry, typed IO manifest, trace/replay contract, reference-version invalidation. | F-001, F-002, F-003, F-004, F-005 |
| `synastry_chart_v1` | blocked | No second-chart input model or graph code is present in audited runtime surfaces. | Multi-chart inputs, pairwise output schema, comparison semantics, app cache key. | F-001, F-002, F-003, F-004, F-005 |
| `solar_return_v1` | partial | Runner can execute a definition, but solar-return date/return-event inputs and graph manifest are absent. | Return-event input contract, typed node IO, trace/replay, reference invalidation. | F-001, F-002, F-003, F-004, F-005 |
| `progressed_chart_v1` | blocked | No progression inputs, time-step semantics or graph code exist in audited runtime surfaces. | Progression method contract, multi-chart registry, replay-grade inputs, app cache policy. | F-001, F-002, F-003, F-004, F-005 |
| `composite_chart_v1` | blocked | No composite input pairing, midpoint calculation ownership or graph code exists in audited runtime surfaces. | Multi-chart family inputs, typed IO schemas, comparison/version manifest, cache invalidation. | F-001, F-002, F-003, F-004, F-005 |

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/stories/CS-242-audit-calculation-graph-readiness/00-story.md` | used | E-001 | Source contract for scope, AC and documentation-only boundary. | None. |
| `_story_briefs/cs-242-audit-calculation-graph-readiness-audit.md` | used | E-002 | Source brief for mandatory questions and target families. | File was already untracked before this audit run. |
| `_condamad/stories/regression-guardrails.md` / RG-137..RG-148 | used | E-003 | Existing adjacent astrology invariants consulted before findings. | No exact calculation graph readiness guardrail exists. |
| `docs/architecture/astrology-calculation-graph.md` | used | E-005 | Architecture doc distinguishes calculation graph, astrological graph and `chart_objects`. | It documents intended shape, not runtime behavior alone. |
| `backend/app/domain/astrology/runtime/calculation_graph_contracts.py` | used | E-006 | Defines immutable graph, input, node, validation and status contracts. | `value_type` is a string label, not runtime schema validation. |
| `backend/app/domain/astrology/runtime/calculation_graph_validator.py` | used | E-006, E-010 | Owns dependency validation and topological ordering. | It validates shape and dependencies, not output runtime types. |
| `backend/app/domain/astrology/runtime/calculation_graph_runner.py` | used | E-007, E-010 | Canonical runner with explicit registry, local cache, node results and provenance. | No persistent trace, replay or app cache semantics. |
| `backend/app/domain/astrology/runtime/natal_calculation_graph.py` | used | E-006, E-009, E-010 | Current `natal_chart_v1` graph definition and node dependency map. | Only one production graph family is defined. |
| `backend/app/domain/astrology/runtime/natal_calculation_registry.py` | used | E-009, E-010 | Explicit registry for `natal_chart_v1` calculators. | No multi-graph registry/router exists. |
| `backend/app/domain/astrology/runtime/natal_calculation_nodes.py` | used | E-008, E-015 | Adapters map graph nodes to existing domain calculators. | Contains metrics infra call and provider branches; not all adapters are pure functions. |
| `backend/app/domain/astrology/runtime/natal_result_assembler.py` | used | E-008, E-010 | Type-checks selected graph outputs before assembling `NatalResult`. | Type checks are assembler-local, not graph-contract-wide. |
| `backend/app/domain/astrology/natal_calculation.py` / `build_natal_result` | used | E-009, E-010, E-012 | Runtime facade executes `CalculationGraphRunner` with `natal_chart_v1`. | It does not expose the execution result trace to callers. |
| `backend/tests/unit/domain/astrology/test_calculation_graph_contracts.py` | test-only | E-010 | Contract immutability and doc boundary tests. | No app code changed by audit. |
| `backend/tests/unit/domain/astrology/test_calculation_graph_validator.py` | test-only | E-010 | Dependency and cycle validation tests. | No app code changed by audit. |
| `backend/tests/unit/domain/astrology/test_calculation_graph_runner.py` | test-only | E-010 | Runner execution, cache, provenance and guard tests. | Uses fake graphs, not all target families. |
| `backend/tests/unit/domain/astrology/test_natal_calculation_graph_definition.py` | test-only | E-010 | `natal_chart_v1` definition, dependencies and topology tests. | Natal-only. |
| `backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py` | test-only | E-010 | Proves `build_natal_result` uses `natal_chart_v1` and registry coverage. | Natal-only. |
| `backend/tests/integration/astrology/test_natal_calculation_graph_integration.py` | test-only | E-010 | Integration proof that graph execution returns a complete natal result. | Natal-only. |
| `backend/app/**` outside selected astrology runtime files | out-of-domain | E-001, E-014 | Inspected only through bounded scans; app-code changes are forbidden. | No refactor performed. |
| `frontend/src/**`, `backend/migrations/**`, `docs/db_seeder/**` modification surface | out-of-domain | E-001, E-014 | Explicitly forbidden by story and verified as unchanged by intended final diff. | Existing unrelated worktree changes predate this audit run. |

## DRY No Legacy Mono-Domain And Dependency Direction

- DRY: current runner, validator and contracts are reused; no duplicate runner is created by this audit. F-001 identifies a future duplication risk if each graph family creates its own registry/routing conventions.
- No Legacy: this audit creates no wrapper, alias, fallback, compatibility route or runtime branch.
- Mono-domain: findings stay in backend astrology calculation graph readiness; API/debug endpoints, frontend product surfaces and DB persistence are deferred.
- Dependency direction: `calculation_graph_runner.py` and `natal_calculation_graph.py` stay free of API/DB/service imports; `natal_calculation_nodes.py` has one infra metrics dependency that must remain explicit for node-purity claims.

## Exhaustive Active Finding Surface

- F-001: `backend/app/domain/astrology/runtime/calculation_graph_runner.py`, `backend/app/domain/astrology/runtime/natal_calculation_registry.py`, `backend/app/domain/astrology/natal_calculation.py`, future graph-family definition and registry files selected by the source-brief `CS-245` candidate label. No file is changed by this audit.
- F-002: `backend/app/domain/astrology/runtime/calculation_graph_contracts.py`, `backend/app/domain/astrology/runtime/natal_calculation_graph.py`, `backend/app/domain/astrology/runtime/natal_result_assembler.py`, future manifest/schema files selected by the source-brief `CS-244` candidate label. No file is changed by this audit.
- F-003: `backend/app/domain/astrology/runtime/calculation_graph_runner.py`, `backend/app/domain/astrology/natal_calculation.py`, future trace DTO/persistence/API owners selected by the source-brief `CS-243` candidate label. No file is changed by this audit.
- F-004: future graph comparison/manifest governance files selected by the source-brief `CS-244` candidate label; no current in-domain implementation file owns comparison. No file is changed by this audit.
- F-005: future application cache owner outside the runner plus runner invalidation interface selected by the source-brief `CS-245` candidate label. No file is changed by this audit.

## Deferred Non-Domain Context

- Calculation interpretation boundaries remain covered by the existing tracker story `CS-243-audit-calculation-interpretation-boundary` and are not implemented here.
- Product data needs and public exposure remain covered by the existing tracker story `CS-244-audit-product-data-needs` and adjacent runtime exposure work, not by this graph-readiness folder.
- Astronomical accuracy, ephemeris file guarantees and golden references remain covered by the sibling `CS-241` audit story context.
