# Evidence Log - CS-245 Product Architecture

| Evidence ID | Type | Source | Result | Used for | Notes |
| --- | --- | --- | --- | --- | --- |
| PA-E-001 | source story | `_condamad/stories/CS-245-canonical-astrology-runtime-transition/00-story.md` | PASS | output contract | Requires six files, four matrices, CS-237..CS-244 citations, no app changes. |
| PA-E-002 | source brief | `_story_briefs/cs-245-archi-canonical-astrology-runtime-transition.md` | PASS | scope | Defines mandatory families, surfaces, objects, roadmap categories and remap rule. |
| PA-E-003 | audit bundle | `_condamad/audits/astro-feature-coverage/2026-05-23-1905` | PASS | capability matrix | CS-237 F-001..F-005; E-005/E-006/E-010/E-014/E-015. |
| PA-E-004 | audit bundle | `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919` | PASS | surface decisions | CS-238 F-001..F-005; raw `chart_objects` non-exposure. |
| PA-E-005 | audit bundle | `_condamad/audits/astro-chart-object-capability-payload/2026-05-23-1928` | PASS | object decisions | CS-239 F-001..F-006; capability/payload taxonomy. |
| PA-E-006 | audit bundle | `_condamad/audits/astro-reference-governance/2026-05-23-1939` | PASS | doctrine/rules | CS-240 F-001..F-006; DB/Python ownership drift. |
| PA-E-007 | audit bundle | `_condamad/audits/astro-astronomical-accuracy/2026-05-23-1950` | PASS | validation/risk | CS-241 F-001..F-005; SwissEph/golden/ephemeris evidence. |
| PA-E-008 | audit bundle | `_condamad/audits/astro-calculation-graph-readiness/2026-05-23-2000` | PASS | graph registry | CS-242 F-001..F-006; label remap caveat. |
| PA-E-009 | audit bundle | `_condamad/audits/astro-calculation-interpretation-boundary/2026-05-23-2013` | PASS | LLM/narration | CS-243 F-001..F-004; internal/public/LLM split. |
| PA-E-010 | audit bundle | `_condamad/audits/astro-product-data-needs/2026-05-23-2024` | PASS | product projections | CS-244 F-001..F-005; expert/beginner/fixed-star needs. |
| PA-E-011 | tracker | `_condamad/stories/story-status.md` | PASS | remap | Confirms CS-237..CS-245 are allocated; future candidates need remap. |
| PA-E-012 | source stories | `_condamad/stories/CS-237-*` to `_condamad/stories/CS-244-*` | PASS | provenance | Story contracts align with audit folders and no-app-change audit shape. |
| PA-E-013 | review validation | fresh CS-245 report review on `2026-05-23` | PASS | final alignment | Confirmed six files, CS-237..CS-244 coverage, owner cible, mandatory object matrix columns/rows, remapped candidates, and empty app-surface git status. |
| PA-E-014 | architecture review | `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/06-architecture-review.md` | PASS | implementation readiness | Closes temporal/astronomy ordering, dedicated review evidence and operational tracker-remap gates. |

## Material Evidence Links

| Decision subject | Observed / inferred / decision / blocker | Evidence | Finding IDs | Story candidate IDs |
| --- | --- | --- | --- | --- |
| Natal is implemented | observed | CS-237 E-006/E-010; CS-242 E-016 | CS-237 F-001 | none |
| Predictive families not implemented | observed | CS-237 E-014/E-015 | CS-237 F-001/F-005 | CS-237 SC-001 |
| `ChartObjectRuntimeData` internal | decision | CS-238 E-005..E-008; CS-239 E-013; CS-244 E-010/E-019 | CS-238 F-001; CS-239 F-006; CS-244 F-001 | CS-238 SC-001 |
| Public projections required | decision | CS-238 E-011/E-012; CS-244 E-007..E-009 | CS-238 F-001/F-002; CS-244 F-001..F-003 | CS-244 SC-001..SC-003 |
| Graph registry required | decision | CS-242 E-006/E-009/E-011/E-013/E-016 | CS-242 F-001 | CS-242 SC-003 |
| Manifest/node IO required | decision | CS-242 E-006/E-008/E-010/E-012 | CS-242 F-002/F-004 | CS-242 SC-002/SC-004 |
| Trace/replay blocked | blocker | CS-238 E-006/E-007; CS-242 E-007/E-010/E-012 | CS-238 F-003; CS-242 F-003 | CS-242 SC-001 |
| Cache boundary | decision/blocker | CS-242 E-007/E-008/E-014 | CS-242 F-005 | CS-242 SC-005 |
| Doctrine owner drift | blocker | CS-240 E-008/E-009/E-010/E-011/E-013 | CS-240 F-001..F-006 | CS-240 SC-001..SC-006 |
| Astronomy proof incomplete | blocker | CS-241 E-013/E-014/E-016 | CS-241 F-001..F-004 | CS-241 SC-001..SC-004 |
| LLM input split | decision | CS-243 E-006..E-014 | CS-243 F-001/F-002/F-003 | CS-243 SC-001..SC-003 |

## Validation Evidence To Produce

- Documentary shape: six files under this folder.
- Citation coverage: `rg` over CS-237..CS-244.
- Contract coverage: `rg` over required family/surface/status keywords.
- No application delta: `git status --short -- frontend/src backend/app backend/tests backend/app/tests backend/migrations docs/db_seeder`.

## Fresh Review Result

Result: PASS after correction.

- Correction applied: `00-architecture-plan.md` now includes `Owner cible` in the runtime family matrix and a story-compliant `Mandatory Astrology Object Capability Matrix` with the required columns and object rows.
- Hardening applied: public temporal runtime implementation is now gated by astronomy proof, and implementation story generation is blocked until tracker remap assigns concrete new IDs.
- Structural validation: all six architecture files exist in `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/`.
- Review artifact: `06-architecture-review.md` records the architecture-local review and closed findings.
- Traceability validation: `rg` confirms CS-237 through CS-244 references across the architecture folder.
- Contract validation: `rg` confirms mandatory runtime families, `Owner cible`, mandatory object rows, object capability columns, roadmap categories, `needs-tracker-remap`, stop conditions, and user decisions.
- Scope validation: `git status --short -- frontend/src backend/app backend/tests backend/app/tests backend/migrations docs/db_seeder` returned no application-surface delta.
