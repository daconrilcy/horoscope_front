# Story Candidates - Astro Chart Object Capability Payload

## Candidate Summary

| Candidate | Priority | Source findings | Required story key qualification |
|---|---|---|---|
| SC-001 | P0 | F-001, F-004, F-005 | CS-246 - Formalize chart object capability matrix. |
| SC-002 | P0 | F-002 | CS-247 - Add runtime validation for capability/payload consistency. |
| SC-003 | P1 | F-003, F-005 | CS-248 - Add support for derived calculated points as first-class chart objects. |
| SC-004 | P1 | F-004 | CS-246 bounded policy row for angle and cusp aspectability. |
| SC-005 | P1 | F-005 | CS-246/CS-248 bounded node taxonomy decision. |

## SC-001 - Formalize Chart Object Capability Matrix

- Source finding: F-001
- Suggested story title: CS-246 - Formalize chart object capability matrix.
- Suggested archetype: runtime-contract-preservation
- Primary domain: backend/app/domain/astrology/runtime
- Required contracts: Runtime Source of Truth; Contract Shape; No Legacy; DRY; Reintroduction Guard.
- Draft objective: Create a canonical, test-guarded capability matrix for every active and reserved `ChartObjectType`, including object family, capability flags, required payloads, optional payloads, producers, consumers, public projection status and interpretation projection status.
- Closure intent: full-closure for F-001 and policy closure for F-004/F-005 if the story records explicit decisions without changing runtime behavior.
- Must include: exact matrix rows for `PLANET`, `LUMINARY`, `ASTRAL_POINT`, `ANGLE`, `HOUSE_CUSP`, `FIXED_STAR`, `ARABIC_PART` and `CALCULATED_POINT`; one semantic consequence per `supports_*` flag; phase-aware note for dignity, dominance and rulership; explicit decisions for angle aspects, cusp aspects and node category; no new runtime calculator behavior.
- Validation hints: run `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py`; add or update a focused matrix guard if implementation creates a code artifact; run `rg -n "object_type ==|\\.object_type ==|ChartObjectType\\." backend/app/domain/astrology/calculators backend/app/domain/astrology/dignities backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation -g "*.py"`.
- Blockers: stop if product cannot decide angle, cusp or node policy; do not emit another partial matrix story unless the remaining undecided rows and stop condition are explicit.
- Exhaustive Files To Modify: selection rule is one canonical matrix artifact under existing runtime/domain governance or docs location chosen by the story plus targeted tests; no frontend, API, DB or migration files.
- Before/After Evidence Required: before scan of current capability assignments in `chart_object_runtime_builder.py`; after matrix artifact and guard proving every `ChartObjectType` and `supports_*` field is represented.
- Ownership Routing Decisions: matrix is runtime taxonomy governance, not public serializer or frontend state.
- Mandatory No-Wildcard Allowlist And No Legacy Checks: no wildcard object family exceptions; no compatibility alias or duplicated selector path.
- Reintroduction Guard Requirements: guard against adding a `ChartObjectCapabilities` field or `ChartObjectType` without matrix coverage.
- Stop Condition: F-001 closes when every object type and capability has one canonical row and tests/scans prove no consumer introduced object-type eligibility branching.
- Expected File Classification Changes: new matrix artifact should be `used` or `test-only` if a guard file; existing runtime files remain `used`.

## SC-002 - Add Runtime Validation For Capability Payload Consistency

- Source finding: F-002
- Suggested story title: CS-247 - Add runtime validation for capability/payload consistency.
- Suggested archetype: runtime-contract-preservation
- Primary domain: backend/app/domain/astrology/runtime
- Required contracts: Runtime Source of Truth; Contract Shape; No Legacy; DRY; Phase-aware Runtime Validation; Reintroduction Guard.
- Draft objective: Add a single phase-aware validation entry point or guarded set of validators that proves capability/payload consistency after each expected enrichment phase without breaking valid intermediate states.
- Closure intent: full-closure for F-002.
- Must include: exact phase definitions for initial construction, fixed-star enrichment, dignity enrichment, dominance enrichment and rulership enrichment; validation for payloads that require capabilities; documented exception for documentary family payloads such as `fixed_star`, `angle` and `house_cusp`; tests for positive and negative states.
- Validation hints: run targeted tests for chart object runtime builder, fixed-star runtime, dignity runtime, dominance runtime, house/rulership runtime and architecture guard; run `rg -n "payloads\\.|supports_" backend/app/domain/astrology/runtime backend/app/domain/astrology/builders backend/app/domain/astrology/dignities backend/app/domain/astrology/dominance backend/app/domain/astrology/fixed_stars -g "*.py"`.
- Blockers: stop if CS-246 has not defined the semantic matrix for documentary payloads and phase-required payloads; do not add fallback validation that silently ignores unknown payloads.
- Exhaustive Files To Modify: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`, existing enrichers that call validators if needed, and focused unit tests under `backend/tests/unit/domain/astrology/**`.
- Before/After Evidence Required: before negative tests showing current partial validation boundaries; after tests proving every capability/payload mismatch is rejected at the correct phase.
- Ownership Routing Decisions: validators belong to runtime contract or existing enricher phase boundaries, not API serializers.
- Mandatory No-Wildcard Allowlist And No Legacy Checks: exact payload names only; no broad "ignore unknown payload" or folder-wide exception.
- Reintroduction Guard Requirements: a test must fail when a new payload or capability is added without validation coverage.
- Stop Condition: F-002 closes when every payload in `ChartObjectPayloads` is classified as capability-required, phase-required, documentary family payload or explicitly optional, with tests for each class.
- Expected File Classification Changes: runtime validator remains `used`; new or updated tests remain `test-only`.

## SC-003 - Add Support For Derived Calculated Points As First-Class Chart Objects

- Source finding: F-003
- Suggested story title: CS-248 - Add support for derived calculated points as first-class chart objects.
- Suggested archetype: runtime-contract-preservation
- Primary domain: backend/app/domain/astrology
- Required contracts: Runtime Source of Truth; Ownership Routing; No Legacy; DRY; Product Taxonomy Decision; Reintroduction Guard.
- Draft objective: Decide and implement first-class derived point support only after the taxonomy states whether lots, midpoints, nodes and other calculated points are `ARABIC_PART`, `CALCULATED_POINT`, `ASTRAL_POINT` variants or separate object families.
- Closure intent: full-closure for F-003 if the story implements the selected first derived family, or blocked if product decision is unavailable.
- Must include: exact selected object families; producer source; payload contract; capability eligibility for aspects, dignities, houses, dominance, rulership and interpretation; public and interpretation projection decisions; migration-free integration with existing chart-object builder.
- Validation hints: run `rg -n "ARABIC_PART|CALCULATED_POINT|ChartObjectType\\.ARABIC_PART|ChartObjectType\\.CALCULATED_POINT" backend/app backend/tests -g "*.py"` before and after; run focused builder, aspect input and public non-exposure tests.
- Blockers: needs user/product decision for which derived point family ships first and which capabilities are allowed; stop if the story tries to implement lots, midpoints and nodes as one broad batch.
- Exhaustive Files To Modify: exact files depend on the selected family; likely existing runtime contract, chart-object builder, one producer/resolver module if already canonical or a new bounded domain module with explicit approval, and focused tests. No API/frontend/DB changes unless a later story authorizes them.
- Before/After Evidence Required: before negative scan showing inactive `ARABIC_PART`/`CALCULATED_POINT`; after runtime tests proving produced objects have correct capabilities and payloads.
- Ownership Routing Decisions: calculated point construction belongs to backend astrology domain runtime, not API, frontend or public serializer.
- Mandatory No-Wildcard Allowlist And No Legacy Checks: no catch-all calculated-point fallback; no object-type branch in consumers; no public raw `ChartObjectRuntimeData`.
- Reintroduction Guard Requirements: guard against future derived point producers bypassing the canonical chart-object builder or matrix.
- Stop Condition: F-003 closes when the selected derived point family has a producer, payload/capability policy and tests, and all unselected families are explicitly deferred by decision.
- Expected File Classification Changes: selected producer becomes `used`; any fixture-only derived object remains `test-only` unless production code consumes it.

## SC-004 - Record Angle And Cusp Aspectability Policy In CS-246

- Source finding: F-004
- Suggested story title: CS-246 - Formalize chart object capability matrix.
- Suggested archetype: runtime-contract-preservation
- Primary domain: backend/app/domain/astrology/runtime
- Required contracts: Runtime Source of Truth; Contract Shape; No Legacy; DRY; Reintroduction Guard.
- Draft objective: Ensure CS-246 records explicit matrix policy for angle and house-cusp aspect participation, preserving current graph behavior unless a later story authorizes behavior change.
- Closure intent: full-closure for F-004 through the CS-246 matrix policy row.
- Must include: current evidence that builder can make angles aspectable while the graph disables angle aspects; explicit yes/no decision for angles; explicit yes/no decision for house cusps; no calculator behavior change.
- Validation hints: run `rg -n "include_angles_in_aspects|include_astral_points_in_aspects|supports_aspects" backend/app/domain/astrology backend/tests/unit/domain/astrology -g "*.py"` and targeted aspect input tests.
- Blockers: stop if product cannot accept or decide the canonical angle/cusp policy.
- Exhaustive Files To Modify: same canonical matrix artifact as SC-001 and focused tests or guards only; no API/frontend/DB files.
- Before/After Evidence Required: before scan from E-016; after matrix row and guard proving angle and cusp policy is represented.
- Ownership Routing Decisions: policy belongs to chart-object runtime matrix, not aspect calculator branching.
- Mandatory No-Wildcard Allowlist And No Legacy Checks: no broad point or angle exception; no `object_type` branch in consumers.
- Reintroduction Guard Requirements: guard fails when graph options or builder defaults change without matrix update.
- Stop Condition: F-004 closes when the canonical matrix has explicit angle and house-cusp rows for `supports_aspects`.
- Expected File Classification Changes: matrix artifact becomes `used`; guard tests remain `test-only`.

## SC-005 - Record Node Runtime Category Decision In CS-246 Or CS-248

- Source finding: F-005
- Suggested story title: CS-246/CS-248 - Decide node category before derived point expansion.
- Suggested archetype: runtime-contract-preservation
- Primary domain: backend/app/domain/astrology
- Required contracts: Runtime Source of Truth; Ownership Routing; No Legacy; DRY; Product Taxonomy Decision.
- Draft objective: Ensure the CS-246 matrix or CS-248 derived-point story decides whether lunar nodes remain `ASTRAL_POINT`, become `CALCULATED_POINT`, or receive a dedicated category.
- Closure intent: full-closure for F-005 if the decision is encoded in CS-246 or CS-248; blocked if product cannot decide.
- Must include: current evidence that nodes are produced as astral points, are non-physical, and do not receive dignity, dominance or motion payloads; explicit aspect participation policy through point-aspect options.
- Validation hints: run targeted scans for `north_node`, `south_node`, `supports_aspects` and `ChartObjectType.ASTRAL_POINT`; run chart-object builder and natal result chart-object tests.
- Blockers: needs product decision if nodes should become planet-like or a dedicated category.
- Exhaustive Files To Modify: canonical matrix artifact and, only if behavior is changed, the existing astral point resolver/builder and focused tests.
- Before/After Evidence Required: before test evidence from E-014/E-016; after matrix decision and tests proving the chosen category.
- Ownership Routing Decisions: node taxonomy belongs to backend astrology runtime, not public serializer or frontend.
- Mandatory No-Wildcard Allowlist And No Legacy Checks: no compatibility alias that maps nodes to multiple object families.
- Reintroduction Guard Requirements: guard against adding node-specific object-type branches in calculators.
- Stop Condition: F-005 closes when nodes have one documented family and one capability policy across aspects, dignities, houses, dominance, motion and interpretation.
- Expected File Classification Changes: existing runtime files remain `used`; any decision-only artifact becomes `used`.

## Deferred Non-Domain Context

- Public projection for fixed-star contacts and chart facts belongs to the adjacent runtime exposure domain, not this capability/payload audit.
- Frontend rendering, API route creation, admin/debug auth and database migrations are intentionally excluded by E-001 and E-002.
