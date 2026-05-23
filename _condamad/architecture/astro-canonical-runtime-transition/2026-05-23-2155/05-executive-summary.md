# Executive Summary - CS-245 Canonical Astrology Runtime Transition

## Decision Summary

The architecture adopts `ChartObjectRuntimeData` and `CalculationGraph` as canonical internal primitives for astrology runtime evolution, but explicitly rejects raw public exposure. `natal_chart_v1` is the only implemented family. All future families must pass through a graph family registry, manifest/node IO schema, trace contract, cache/invalidation rules and projection contracts before product/API/frontend use.

## Safe Decisions

- `ChartObjectRuntimeData` remains internal and feeds selected projections only.
- `CalculationGraph` is the target orchestration mechanism for future families.
- Public value must be expressed as `chart_facts_v1`, `expert_technical_v1`, `beginner_summary_v1` and optional `fixed_star_display_v1`.
- LLM/narration consumes versioned facts/readiness; prompts are not astrology source of truth.
- Candidate stories are blocked at `needs-tracker-remap` until the tracker owner assigns concrete new IDs; no implementation story should be generated from the source labels.

## Blocked Decisions

- First temporal technique: product decision required, with transits as suggested default.
- Admin/debug/replay exposure: security and product decision required.
- Durable app cache: data/architecture owner required.
- Doctrine and school governance: product astrology/data owner required.
- Lots, Chiron, asteroids, midpoints, node/angle aspectability: doctrine/product decisions required.
- Astronomical proof: external references and tolerances required for sensitive golden cases.

## Audits Used

CS-237 feature coverage, CS-238 runtime surface exposure, CS-239 chart object capability payload, CS-240 reference governance, CS-241 astronomical accuracy, CS-242 calculation graph readiness, CS-243 calculation interpretation boundary, and CS-244 product data needs were used as source-of-truth audit bundles.

## Roadmap Priority

1. Graph family registry.
2. Graph manifest and node IO schema.
3. Execution trace contract.
4. Public projection registry and raw exposure guards.
5. Doctrine/source ownership.
6. Expert, beginner and fixed-star product projections.
7. Astronomy proof hardening.
8. First temporal technique path.
9. Non-planetary object taxonomy.
10. AI scoring and narrative input contract.

## Implementation Gate

Before any implementation story is created, the tracker owner must assign concrete IDs for the candidates in `03-story-candidates.md`. Stories must cite the remapped ID, the source candidate, and this architecture folder. Source labels such as CS-243, CS-244 and CS-245 must not be reused.

Temporal runtime implementation is gated by CS-241 hardening: production-mode proof and the sensitive golden suite must be completed or explicitly accepted as a blocking product risk before a public temporal technique can be implemented.

## Validation Snapshot

Fresh review result: PASS after correction on `2026-05-23`.

The corrected report now covers the CS-245 story expectations: six required files exist, all CS-237..CS-244 references are present, the runtime family matrix includes target owners, the mandatory object capability matrix includes every required object row and capability column, candidate stories remain blocked at `needs-tracker-remap`, roadmap categories remain separated, temporal implementation is gated by astronomy proof, and application surfaces remain unchanged.

Dedicated architecture review: `06-architecture-review.md`.
