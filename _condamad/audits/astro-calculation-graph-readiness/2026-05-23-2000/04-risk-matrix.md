# Risk Matrix - Astro Calculation Graph Readiness

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | Medium | Future graph-family routing, registry ownership and input preparation | High: each family can create a duplicate active graph path without a canonical owner | Medium | P1 |
| F-002 | High | High | Graph contracts, node IO validation and future family manifests | High: wrong node output types can fail only downstream or after partial execution | Medium | P1 |
| F-003 | High | High | Debug trace, replay evidence and support/audit diagnosis | High: raw in-memory provenance can be confused with stable trace or replay | Medium | P1 |
| F-004 | Medium | Medium | Graph comparison, version compatibility and rollout gates | Medium: incompatible graph versions can be accepted without manifest comparison | Medium | P2 |
| F-005 | Medium | Medium | Durable cache, reference-version invalidation and ephemeris drift | High: stale graph outputs can be reused if a future app cache ignores invalidation keys | Medium | P2 |
| F-006 | Low | Medium | Future story guardrails and reintroduction checks | Low: adjacent guards exist but are not exact for graph trace/manifest decisions | Low | P3 |

## Readiness Risk Notes

- Orchestration: the runner is graph-agnostic, but only natal has a wired graph and registry today.
- Provenance: current provenance is useful for in-memory debugging but not replay-grade.
- Replay: blocked until trace shape, input snapshot, graph manifest and reference-version binding exist.
- Cache: local runner cache is safe per run; durable app cache must not be added inside the runner by accident.
- Dependency direction: runner and graph definition are clean; natal node adapters intentionally delegate to domain calculators and include metrics.
