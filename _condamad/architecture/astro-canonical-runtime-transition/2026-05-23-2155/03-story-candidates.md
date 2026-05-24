# Story Candidates - CS-245 Remapped Roadmap

Tracker remap applied on 2026-05-23: candidates `SC-ARCH-001` to `SC-ARCH-008` are mapped to concrete story IDs `CS-246` to `CS-254` in `_condamad/stories/story-status.md`.

Operational order follows the P0 foundation first, then the astronomy-proof gate before any public temporal runtime work. `SC-ARCH-006` remains blocked until `SC-ARCH-006A` / `CS-250` is completed or explicitly risk-accepted by product.

| Order | Source candidate | Story ID | Priority | Story title | Brief |
|---|---|---|---|---|---|
| 1 | SC-ARCH-001 | CS-246 | P0 | Define canonical astrology graph family registry | `_story_briefs/cs-246-canonical-astrology-graph-family-registry.md` |
| 2 | SC-ARCH-002 | CS-247 | P0 | Add graph manifest and node IO schema contract | `_story_briefs/cs-247-graph-manifest-node-io-schema-contract.md` |
| 3 | SC-ARCH-003 | CS-248 | P0 | Add calculation graph execution trace contract | `_story_briefs/cs-248-calculation-graph-execution-trace-contract.md` |
| 4 | SC-ARCH-004 | CS-249 | P1 | Define chart object capability and object taxonomy matrix | `_story_briefs/cs-249-chart-object-capability-taxonomy-matrix.md` |
| 5 | SC-ARCH-006A | CS-250 | P1 gate | Harden astronomical proof before public temporal runtime | `_story_briefs/cs-250-astronomical-proof-before-public-temporal-runtime.md` |
| 6 | SC-ARCH-005 | CS-251 | P1 | Define official product primitives and public projection roadmap | `_story_briefs/cs-251-official-product-primitives-public-projection-roadmap.md` |
| 7 | SC-ARCH-007 | CS-252 | P1 | Define astrology doctrine and school governance model | `_story_briefs/cs-252-astrology-doctrine-school-governance-model.md` |
| 8 | SC-ARCH-006 | CS-253 | P1 blocked by CS-250 | Select first temporal technique implementation path | `_story_briefs/cs-253-first-temporal-technique-implementation-path.md` |
| 9 | SC-ARCH-008 | CS-254 | P2 | Define AI scoring and narrative input contract from canonical runtime | `_story_briefs/cs-254-ai-scoring-narrative-input-contract.md` |

## SC-ARCH-001 / CS-246 - Define canonical astrology graph family registry

- Story ID: CS-246
- Source findings: CS-237 F-001/F-005; CS-242 F-001/F-005
- Source labels: CS-242 SC-003 source-label CS-245
- Priority: P0
- Primary domain: backend astrology calculation graph runtime
- Likely files to modify: graph-family registry/router selected by implementation story under `backend/app/domain/astrology/runtime/**`; focused tests.
- Files explicitly out of scope: `frontend/src/**`, `backend/app/api/**`, `backend/migrations/**`, seed files.
- Expected validation: family-code scans, runner/natal graph tests, architecture scan for duplicate routing.
- Stop condition: every target family has owner, inputs, status, blockers and cache boundary.
- User decisions: first temporal technique and multi-chart input model.

## SC-ARCH-002 / CS-247 - Add graph manifest and node IO schema contract for canonical runtime

- Story ID: CS-247
- Source findings: CS-242 F-002/F-004
- Source labels: CS-242 SC-002 source-label CS-244; CS-242 SC-004
- Priority: P0
- Primary domain: backend astrology graph contracts
- Likely files to modify: `calculation_graph_contracts.py`, `calculation_graph_validator.py`, `natal_calculation_graph.py`, manifest/schema module if selected.
- Files explicitly out of scope: public API, frontend, DB migrations.
- Expected validation: manifest/schema validator tests; compatibility comparison tests.
- Stop condition: `natal_chart_v1` has manifest coverage and graph comparison is owned.
- User decisions: schema language.

## SC-ARCH-003 / CS-248 - Add calculation graph execution trace contract

- Story ID: CS-248
- Source findings: CS-238 F-003; CS-242 F-003
- Source labels: CS-242 SC-001 source-label CS-243
- Priority: P0
- Primary domain: backend astrology graph runtime / observability
- Likely files to modify: graph runner/result contracts and trace tests.
- Files explicitly out of scope: public unauthenticated route, frontend, persistence unless approved.
- Expected validation: success/error/cache trace tests; redaction and no raw public exposure scans.
- Stop condition: trace/provenance/replay are separate terms with a stable redacted trace.
- User decisions: persistence, retention, admin/debug exposure.

## SC-ARCH-004 / CS-249 - Define chart object capability and object taxonomy matrix

- Story ID: CS-249
- Source findings: CS-237 F-003/F-004; CS-239 F-001..F-005
- Source labels: CS-239 SC-001/SC-003/SC-004/SC-005
- Priority: P1
- Primary domain: backend astrology chart object runtime
- Likely files to modify: capability matrix/guard, `chart_object_runtime_data.py`, builder tests only if runtime guard is implemented.
- Files explicitly out of scope: calculators for lots/asteroids/Chiron/midpoints until taxonomy accepted.
- Expected validation: chart object architecture tests, negative scan for ad hoc `object_type` branching.
- Stop condition: every object family has one canonical capability decision or `needs-user-decision`.
- User decisions: lots, nodes, angle aspectability, derived points.

## SC-ARCH-006A / CS-250 - Harden astronomical proof before public temporal runtime

- Story ID: CS-250
- Source findings: CS-241 F-001..F-004; CS-242 F-005
- Source labels: CS-241 SC-001..SC-004
- Priority: P1, gate before temporal runtime implementation
- Primary domain: backend astrology astronomical validation
- Likely files to modify: production-mode guards, golden chart fixtures/tests, ephemeris trace tests selected by implementation story.
- Files explicitly out of scope: new temporal calculator, frontend, public API.
- Expected validation: production `swisseph` proof, sensitive golden suite, ephemeris version/hash/config evidence.
- Stop condition: temporal implementation has a trustworthy astronomical baseline, or product explicitly accepts residual risk before non-public experimentation only.
- User decisions: external reference sources, tolerances and policy for unstable house edge cases.

## SC-ARCH-005 / CS-251 - Define official product primitives and public projection roadmap

- Story ID: CS-251
- Source findings: CS-238 F-001/F-002/F-005; CS-244 F-001..F-003
- Source labels: CS-238 SC-001/SC-002; CS-244 SC-001..SC-003
- Priority: P1
- Primary domain: public chart projection contracts
- Likely files to modify: public projection owner, API/client contracts, frontend components only after contract selection.
- Files explicitly out of scope: raw `chart_objects`, `ChartObjectRuntimeData`, internal fixed-star payload exposure.
- Expected validation: OpenAPI/schema diff, public projection tests, frontend/API negative raw-runtime scans.
- Stop condition: beginner, expert and fixed-star needs have named projections or product rejection.
- User decisions: exact expert fields, fixed-star public/gated policy.

## SC-ARCH-007 / CS-252 - Define astrology doctrine and school governance model

- Story ID: CS-252
- Source findings: CS-240 F-001..F-006; CS-241 F-003
- Source labels: CS-240 SC-001..SC-006
- Priority: P1
- Primary domain: doctrine/reference governance
- Likely files to modify: governance registry/tests and selected reference ownership artifacts.
- Files explicitly out of scope: silent threshold/weight changes, migrations without decision.
- Expected validation: scans for thresholds/weights/profiles, ownership guard tests.
- Stop condition: every audited rule family is DB-owned, Python-owned, mixed, test-only, documentation-only or needs-user-decision.
- User decisions: doctrine owner and school model.

## SC-ARCH-006 / CS-253 - Select first temporal technique implementation path

- Story ID: CS-253
- Source findings: CS-237 F-001; CS-242 F-001/F-005; CS-241 F-002/F-004
- Source labels: CS-237 SC-001
- Priority: P1, blocked by CS-250 unless explicitly risk-accepted
- Primary domain: backend astrology forecast runtime
- Likely files to modify: selected technique runtime graph/calculator and tests after product decision and astronomy proof hardening.
- Files explicitly out of scope: batch implementation of all temporal families, API/frontend.
- Expected validation: before/after scans for temporal family codes; focused runtime tests.
- Stop condition: one selected technique is fully specified or implemented only after the astronomy proof gate is closed; unselected techniques remain unclaimed.
- User decisions: choose transits, synastry, returns, progressions, composite, profections or forecasting.

## SC-ARCH-008 / CS-254 - Define AI scoring and narrative input contract from canonical runtime

- Story ID: CS-254
- Source findings: CS-243 F-001..F-003; CS-244 F-002
- Source labels: CS-243 SC-001/SC-002/SC-003
- Priority: P2
- Primary domain: interpretation / LLM input / narration guard
- Likely files to modify: interpretation input contracts, readiness projection, architecture guards.
- Files explicitly out of scope: prompt copy, provider integration, commercial scoring policy.
- Expected validation: boundary guard tests, no-provider scans, narrative-token guard.
- Stop condition: LLM consumes versioned facts; prompt output cannot become astrology source of truth.
- User decisions: scoring policy and public/narrative masking.
