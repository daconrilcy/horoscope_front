# Gap Register - CS-245 Product Architecture

| Gap ID | Status | observed / inferred / decision / blocker | Gap | Owner | Blocks | Sources | Story recommandée |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GAP-001 | blocker | observed | Techniques prédictives documentées mais sans runtime owner. | product/backend | temporal families | CS-237 F-001/E-014/E-015; CS-241 F-001..F-004 | needs-tracker-remap SC-First-Temporal after SC-Astronomy-Proof |
| GAP-002 | blocker | observed | Aucun registre canonique des familles graphes. | architecture | all non-natal graphs | CS-242 F-001 | needs-tracker-remap SC-Graph-Family-Registry |
| GAP-003 | blocker | observed | `CalculationGraph` décrit les value types mais ne valide pas schemas node IO. | backend architecture | manifest/version compatibility | CS-242 F-002/F-004 | needs-tracker-remap SC-Graph-Manifest |
| GAP-004 | blocker | observed | Provenance in-memory != trace/replay stable. | backend/security | admin debug, replay | CS-242 F-003; CS-238 F-003 | needs-tracker-remap SC-Trace-Contract |
| GAP-005 | decision | observed | Durable app cache has no owner/invalidation keys. | data/architecture | cache product | CS-242 F-005 | needs-tracker-remap cache boundary |
| GAP-006 | decision | observed | Raw `ChartObjectRuntimeData` has product value but cannot be public. | product/API | frontend consumption | CS-238 F-001; CS-244 F-001 | needs-tracker-remap SC-Public-Projections |
| GAP-007 | decision | observed | Fixed-star contacts are runtime/LLM ready but lack reduced public projection. | product/API | fixed-star display | CS-238 F-002; CS-244 F-003 | needs-tracker-remap fixed-star projection |
| GAP-008 | blocker | observed | Admin/debug trace surface lacks authz, retention, redaction decision. | security/product | debug astrologique | CS-238 F-003; CS-244 F-004 | needs-user-decision |
| GAP-009 | blocker | observed | Capability semantics are distributed across dataclass, builder, graph options and tests. | backend astrology | object extension | CS-239 F-001/F-002 | needs-tracker-remap capability matrix |
| GAP-010 | blocker | observed | Lots, Chiron, asteroids, midpoints have no runtime owner. | product doctrine | object taxonomy/composite | CS-237 F-004; CS-239 F-003 | needs-tracker-remap object taxonomy |
| GAP-011 | blocker | observed | Angle/cusp/node aspectability and category policy remain implicit. | product doctrine | capability registry | CS-239 F-004/F-005 | needs-user-decision |
| GAP-012 | blocker | observed | Rule source ownership split across DB and Python. | data/product doctrine | doctrine extension | CS-240 F-001..F-006 | needs-tracker-remap doctrine governance |
| GAP-013 | blocker | observed | Astronomical proof incomplete for sensitive cases; simplified path still callable. | backend/data | accuracy claims and public temporal runtime | CS-241 F-001..F-004 | needs-tracker-remap SC-Astronomy-Proof before temporal implementation |
| GAP-014 | decision | observed | `ChartInterpretationInputRuntimeData` has no internal/public/LLM split. | interpretation/product | LLM/scoring | CS-243 F-001 | needs-tracker-remap AI input |
| GAP-015 | decision | observed | Readiness projection missing for deterministic narration/scoring. | interpretation/product | narrative_generation_v1 | CS-243 F-002; CS-244 F-002 | needs-tracker-remap AI input |
| GAP-016 | blocker | observed | Tracker labels CS-243/244/245 and CS-237..245 are allocated. | CONDAMAD tracker owner | story creation and implementation kickoff | CS-242 03-story-candidates; story-status.md | assign concrete IDs before generating implementation stories |

## Contradictions Preserved

- blocker: `ChartObjectRuntimeData` is canonical internally but forbidden publicly; this is not a backlog cleanup, it is a projection-owner decision (CS-238 F-001, CS-244 F-001).
- blocker: `CalculationGraphRunner` has local cache/provenance today, but durable cache/replay must not be inferred from it (CS-242 F-003/F-005).
- blocker: reference data and Python code both own some thresholds/weights; the architecture cannot choose values without doctrine/data owner approval (CS-240 F-001..F-006).
- blocker: fixed stars are implemented only as zodiacal conjunction contacts; parans/aspects/heliacal techniques are not implemented (CS-237 F-002).
