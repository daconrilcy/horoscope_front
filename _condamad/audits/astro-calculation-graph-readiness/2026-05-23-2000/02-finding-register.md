# Finding Register - Astro Calculation Graph Readiness

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | missing-canonical-owner | astro-calculation-graph-readiness | E-006, E-009, E-011, E-013, E-016 | Future graph families can each invent their own definition lookup, registry wiring and input setup, creating duplicate orchestration paths. | Use the source-brief `CS-245` candidate label to define a multi-chart graph-family registry/routing contract and close the full multi-graph readiness gap; remap to the next available tracker ID during story writing. | yes |
| F-002 | High | High | runtime-contract-drift | astro-calculation-graph-readiness | E-006, E-008, E-009, E-010, E-012, E-016 | Graph contracts expose string `value_type` labels but cannot validate node input/output schemas across future families before execution. | Use the source-brief `CS-244` candidate label to add graph manifest and node IO schema validation, with `natal_chart_v1` as the baseline manifest; remap because tracker CS-244 is already allocated. | yes |
| F-003 | High | High | observability-gap | astro-calculation-graph-readiness | E-007, E-010, E-012, E-016 | Current provenance is in-memory, minimal and includes raw outputs; it is not a stable trace or replay contract for debugging, audit or support. | Use the source-brief `CS-243` candidate label to add a calculation graph execution trace contract separate from provenance and replay; remap because tracker CS-243 is already allocated. | yes |
| F-004 | Medium | High | missing-test-coverage | astro-calculation-graph-readiness | E-012, E-013, E-016 | Graph comparison, version compatibility and graph-family readiness cannot be proven with current runtime/tests. | Route to the source-brief `CS-244` manifest candidate for comparison and compatibility checks; stop if product needs a separate comparison story or if tracker remapping is unresolved. | yes |
| F-005 | Medium | High | data-integrity-risk | astro-calculation-graph-readiness | E-007, E-008, E-012, E-014, E-016 | Runner-local cache is safe inside one execution, but future application caching would be unsafe without graph, input, reference-version and ephemeris invalidation keys. | Route to the source-brief `CS-245` candidate for application cache boundary and reference-version invalidation ownership; do not put durable cache inside the runner. | yes |
| F-006 | Low | High | missing-guard | astro-calculation-graph-readiness | E-003, E-014 | Adjacent astrology guardrails exist, but none names the calculation graph trace/manifest/multi-family invariants. | Do not update guardrails in this audit; future implementation stories should add exact guards when they create durable runtime invariants. | no |

## F-001 Multi-Graph Runtime Ownership Is Not Canonical Yet

- Severity: High
- Confidence: High
- Category: missing-canonical-owner
- Domain: astro-calculation-graph-readiness
- Evidence: E-006, E-009, E-011, E-013, E-016
- Expected rule: a runner intended for multiple graph families should have one canonical owner for graph selection, registry routing, input preparation and family-specific prerequisites.
- Actual state: `CalculationGraphRunner` is generic, but app runtime wires only `natal_chart_v1`; target family codes have no app/test/architecture surfaces.
- Impact: Future graph families can each invent their own definition lookup, registry wiring and input setup, creating duplicate orchestration paths.
- Recommended action: Use the source-brief `CS-245` candidate label to define a multi-chart graph-family registry/routing contract and close the full multi-graph readiness gap; remap to the next available tracker ID during story writing.
- Story candidate: yes
- Suggested archetype: graph-family-readiness
- Closure decision: phased-with-map, because the source-brief `CS-245` candidate should cover all five target families and stop when no family lacks owner/routing/input prerequisites.

## F-002 Node IO Typing Is Descriptive, Not Enforced By The Graph Contract

- Severity: High
- Confidence: High
- Category: runtime-contract-drift
- Domain: astro-calculation-graph-readiness
- Evidence: E-006, E-008, E-009, E-010, E-012, E-016
- Expected rule: future graph families should define machine-checkable node inputs and outputs so a manifest can validate compatibility before execution.
- Actual state: `CalculationInputDefinition.value_type` is a string; runner outputs are `object`; selected natal outputs are type-checked only later by `NatalResultAssembler`.
- Impact: Graph contracts expose string `value_type` labels but cannot validate node input/output schemas across future families before execution.
- Recommended action: Use the source-brief `CS-244` candidate label to add graph manifest and node IO schema validation, with `natal_chart_v1` as the baseline manifest; remap because tracker CS-244 is already allocated.
- Story candidate: yes
- Suggested archetype: graph-manifest-contract
- Closure decision: full-closure if every current natal node and every target family template has an explicit IO contract or a documented user-decision blocker.

## F-003 Provenance Is Not A Stable Trace Or Replay Contract

- Severity: High
- Confidence: High
- Category: observability-gap
- Domain: astro-calculation-graph-readiness
- Evidence: E-007, E-010, E-012, E-016
- Expected rule: trace, provenance and replay should be separate contracts: trace is stable/redacted, provenance explains source values, replay captures reproducible inputs and versions.
- Actual state: runner result exposes `node_results`, `execution_order`, `cache_hits` and minimal provenance in memory, but no stable trace DTO, persistence, redaction, replay input snapshot or replay validator exists.
- Impact: Current provenance is in-memory, minimal and includes raw outputs; it is not a stable trace or replay contract for debugging, audit or support.
- Recommended action: Use the source-brief `CS-243` candidate label to add a calculation graph execution trace contract separate from provenance and replay; remap because tracker CS-243 is already allocated.
- Story candidate: yes
- Suggested archetype: trace-contract-hardening
- Closure decision: full-closure for tracing if the source-brief `CS-243` candidate defines stable trace shape, redaction, validation and tests; replay may remain a documented follow-up only if blocked by product storage policy.

## F-004 Graph Comparison And Version Compatibility Are Not Ready

- Severity: Medium
- Confidence: High
- Category: missing-test-coverage
- Domain: astro-calculation-graph-readiness
- Evidence: E-012, E-013, E-016
- Expected rule: two graph definitions or versions should be comparable by graph code, version, inputs, nodes, dependencies and IO schema before multi-family rollout.
- Actual state: scoped runtime surfaces contain no graph comparison contract; target family codes are absent from app/test/architecture surfaces.
- Impact: Graph comparison, version compatibility and graph-family readiness cannot be proven with current runtime/tests.
- Recommended action: Route to the source-brief `CS-244` manifest candidate for comparison and compatibility checks; stop if product needs a separate comparison story or if tracker remapping is unresolved.
- Story candidate: yes
- Suggested archetype: graph-manifest-contract
- Closure decision: full-closure if the source-brief `CS-244` candidate includes comparison rules and tests, or `needs-user-decision` if comparison semantics are product-dependent.

## F-005 Application Cache And Reference-Version Invalidation Are Not Owned

- Severity: Medium
- Confidence: High
- Category: data-integrity-risk
- Domain: astro-calculation-graph-readiness
- Evidence: E-007, E-008, E-012, E-014, E-016
- Expected rule: runner-local cache should remain per-execution, while any durable app cache needs explicit invalidation keys including graph version, input fingerprint, reference version and ephemeris evidence.
- Actual state: runner local cache is tested and safe inside one call; no application cache or reference-version invalidation owner exists in graph runtime surfaces.
- Impact: Runner-local cache is safe inside one execution, but future application caching would be unsafe without graph, input, reference-version and ephemeris invalidation keys.
- Recommended action: Route to the source-brief `CS-245` candidate for application cache boundary and reference-version invalidation ownership; do not put durable cache inside the runner.
- Story candidate: yes
- Suggested archetype: graph-family-readiness
- Closure decision: full-closure if the source-brief `CS-245` candidate defines durable cache ownership or an explicit no-cache decision with exact guards.

## F-006 Exact Calculation Graph Guardrail Is Missing

- Severity: Low
- Confidence: High
- Category: missing-guard
- Domain: astro-calculation-graph-readiness
- Evidence: E-003, E-014
- Expected rule: durable graph trace, manifest, schema and multi-family routing decisions should gain exact reintroduction guards when implementation stories create them.
- Actual state: adjacent RG-144 through RG-148 protect astrology runtime contracts, but no guardrail names calculation graph readiness invariants yet.
- Impact: Adjacent astrology guardrails exist, but none names the calculation graph trace/manifest/multi-family invariants.
- Recommended action: Do not update guardrails in this audit; future implementation stories should add exact guards when they create durable runtime invariants.
- Story candidate: no
- Suggested archetype: architecture-guard-hardening
- Closure decision: no direct candidate because this audit creates documentation artifacts only and no durable runtime invariant.
