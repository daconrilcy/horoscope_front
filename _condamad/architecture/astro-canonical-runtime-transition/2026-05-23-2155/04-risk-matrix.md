# Risk Matrix - CS-245 Canonical Runtime Transition

| Risk ID | Area | Severity | Probability | Blast radius | Regression risk | Mitigation | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 | architecture | High | High | all future astrology families | duplicate graph routers and incompatible inputs | graph family registry before new families | CS-242 F-001 |
| R-002 | contract | High | High | graph execution, tests, future manifests | node IO failures only discovered after execution | manifest + schema validation | CS-242 F-002/F-004 |
| R-003 | exposure | High | High | API/frontend/product | raw `chart_objects` or `ChartObjectRuntimeData` leak | projection registry + no raw guard | CS-238 F-001, CS-244 F-001 |
| R-004 | observability | High | Medium | support/admin/debug | provenance confused with stable trace/replay | trace contract + redaction decision | CS-242 F-003, CS-238 F-003 |
| R-005 | cache | High | Medium | chart results, forecasts | stale output after ref/eph/graph change | no durable cache without invalidation keys | CS-242 F-005 |
| R-006 | doctrine | High | High | dignity, conditions, dominance, interpretation | DB/Python rules diverge | source ownership registry | CS-240 F-001..F-006 |
| R-007 | astronomy proof | High | Medium | accuracy claims, temporal techniques | simplified path or missing golden case overtrusted | production mode proof + golden suite before public temporal runtime | CS-241 F-001..F-004 |
| R-008 | object taxonomy | Medium | High | lots, Chiron, asteroids, midpoints, composite | wrong object subtype becomes durable | taxonomy decision before calculators | CS-237 F-004, CS-239 F-003 |
| R-009 | product projection | Medium | High | beginner/expert/fixed-star UI | frontend infers internals by convenience | public projection contracts | CS-244 F-001..F-003 |
| R-010 | narration/AI | Medium | Medium | LLM, scoring, prompt code | prompts become source of truth | readiness + LLM input registry | CS-243 F-001..F-003 |
| R-011 | tracker/remap | Medium | High | story creation | allocated labels reused | block implementation story generation until tracker owner assigns concrete IDs | CS-242 03-story-candidates, story-status.md |

## Highest-Risk Dependencies

1. Graph registry and manifest must precede non-natal graph work.
2. Public projections must precede frontend or API exposure.
3. Doctrine ownership must precede broad temporal/traditional expansion.
4. Trace/cache/replay ownership must precede durable caching or support replay.
5. Astronomical proof must precede public temporal runtime implementation and strong accuracy claims for sensitive options.
6. Tracker remap must precede every implementation story generated from this architecture.
