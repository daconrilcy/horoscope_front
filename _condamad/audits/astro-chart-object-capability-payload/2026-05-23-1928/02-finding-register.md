# Finding Register - Astro Chart Object Capability Payload

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | missing-canonical-owner | astro-chart-object-capability-payload | E-005, E-006, E-014, E-016, E-017 | Capability semantics are spread across dataclass fields, builder defaults, graph options and tests; future contributors must infer the canonical matrix from code. | Create a canonical capability matrix and guard it against drift without changing runtime behavior. | yes |
| F-002 | High | High | missing-guard | astro-chart-object-capability-payload | E-005, E-007, E-009, E-010, E-011, E-014 | Runtime validation is partial: construction validates required motion, visibility and house position immediately, while dignity, dominance and rulership require phase validators and fixed-star/documentary payload semantics are looser. | Add a centralized runtime consistency validation story that preserves phase-aware enrichment and rejects incoherent payload/capability states at stable boundaries. | yes |
| F-003 | Medium | High | needs-user-decision | astro-chart-object-capability-payload | E-005, E-015, E-019 | `ARABIC_PART` and `CALCULATED_POINT` exist in the enum but have no active producer or payload policy; lots, midpoints or other derived points cannot be classified from current runtime evidence. | Decide derived point taxonomy before implementation; candidate CS-248 should define object family, payloads and consumer eligibility. | yes |
| F-004 | Medium | High | needs-user-decision | astro-chart-object-capability-payload | E-006, E-008, E-014, E-016 | Angles can be built as aspectable by builder option, but current graph disables angle aspects; house cusps are never aspectable. Product semantics are not fully encoded as a stable matrix decision. | Record explicit aspectability policy for angles and cusps in the canonical matrix before changing calculators. | yes |
| F-005 | Medium | High | needs-user-decision | astro-chart-object-capability-payload | E-006, E-014, E-016, E-019 | Nodes are active `ASTRAL_POINT` objects, non-physical and non-dignity/non-dominance/non-motion in the default evidence, but can participate in aspects when point aspects are enabled. Their category is not a dedicated runtime type. | Keep current behavior until CS-246/CS-248 decides whether nodes stay astral points or become a dedicated object family. | yes |
| F-006 | Info | High | runtime-contract-drift | astro-chart-object-capability-payload | E-011, E-012, E-013, E-018 | Fixed stars are active documentary chart objects and contact sources, but raw runtime payloads stay internal and public exposure is intentionally deferred. | No immediate implementation; route public projection decisions through the runtime exposure candidate from the adjacent audit. | no |

## Finding Details

### F-001 - Capability matrix lacks a single canonical declaration

- Severity: High
- Confidence: High
- Category: missing-canonical-owner
- Domain: astro-chart-object-capability-payload
- Evidence: E-005, E-006, E-014, E-016, E-017
- Expected rule: Each `ChartObjectCapabilities` flag should have one documented semantic consequence, eligible object families, required payload relationship and consumer list.
- Actual state: Capability meaning is inferable from `ChartObjectCapabilities`, builder assignments, graph options and tests, but no single matrix declares the rules for planets, luminaires, astral points, angles, cusps, fixed stars, lots and calculated points.
- Impact: Capability semantics are spread across dataclass fields, builder defaults, graph options and tests; future contributors must infer the canonical matrix from code.
- Recommended action: Create a canonical capability matrix and guard it against drift without changing runtime behavior.
- Story candidate: yes
- Suggested archetype: runtime-contract-preservation

### F-002 - Runtime capability/payload validation is not one complete boundary

- Severity: High
- Confidence: High
- Category: missing-guard
- Domain: astro-chart-object-capability-payload
- Evidence: E-005, E-007, E-009, E-010, E-011, E-014
- Expected rule: Every payload that is required by a capability should be checked at the boundary where that payload is supposed to exist, and every payload without an allowed capability should be rejected consistently.
- Actual state: `motion`, `visibility` and `house_position` are immediate constructor invariants; dignity, dominance and rulership use phase validators; fixed-star payloads and angle/house-cusp payloads are typed but not expressed in one runtime consistency validator.
- Impact: Runtime validation is partial: construction validates required motion, visibility and house position immediately, while dignity, dominance and rulership require phase validators and fixed-star/documentary payload semantics are looser.
- Recommended action: Add a centralized runtime consistency validation story that preserves phase-aware enrichment and rejects incoherent payload/capability states at stable boundaries.
- Story candidate: yes
- Suggested archetype: runtime-contract-preservation

### F-003 - Derived calculated point and lot taxonomy is unimplemented

- Severity: Medium
- Confidence: High
- Category: needs-user-decision
- Domain: astro-chart-object-capability-payload
- Evidence: E-005, E-015, E-019
- Expected rule: Enum object families should either have active producers and payload policy or be explicitly reserved with a decision.
- Actual state: `ARABIC_PART` and `CALCULATED_POINT` are enum values, but scans found no active application producer. Lots are missing according to the adjacent feature audit.
- Impact: `ARABIC_PART` and `CALCULATED_POINT` exist in the enum but have no active producer or payload policy; lots, midpoints or other derived points cannot be classified from current runtime evidence.
- Recommended action: Decide derived point taxonomy before implementation; candidate CS-248 should define object family, payloads and consumer eligibility.
- Story candidate: yes
- Suggested archetype: runtime-contract-preservation

### F-004 - Angle and cusp aspectability policy remains split

- Severity: Medium
- Confidence: High
- Category: needs-user-decision
- Domain: astro-chart-object-capability-payload
- Evidence: E-006, E-008, E-014, E-016
- Expected rule: Aspectability should be a stable capability decision per object family.
- Actual state: Builder supports angle aspectability through `include_angles_in_aspects`, current graph hard-codes `include_angles_in_aspects=False`, and house cusps carry only house-position semantics.
- Impact: Angles can be built as aspectable by builder option, but current graph disables angle aspects; house cusps are never aspectable. Product semantics are not fully encoded as a stable matrix decision.
- Recommended action: Record explicit aspectability policy for angles and cusps in the canonical matrix before changing calculators.
- Story candidate: yes
- Suggested archetype: runtime-contract-preservation

### F-005 - Node category policy is implicit

- Severity: Medium
- Confidence: High
- Category: needs-user-decision
- Domain: astro-chart-object-capability-payload
- Evidence: E-006, E-014, E-016, E-019
- Expected rule: Nodes should have a clear object-family decision and consumer eligibility policy.
- Actual state: Nodes are `ASTRAL_POINT` objects, non-physical, non-dignity, non-dominance and non-motion in current evidence, while point-aspect support can include them when enabled.
- Impact: Nodes are active `ASTRAL_POINT` objects, non-physical and non-dignity/non-dominance/non-motion in the default evidence, but can participate in aspects when point aspects are enabled. Their category is not a dedicated runtime type.
- Recommended action: Keep current behavior until CS-246/CS-248 decides whether nodes stay astral points or become a dedicated object family.
- Story candidate: yes
- Suggested archetype: runtime-contract-preservation

### F-006 - Fixed-star projection remains intentionally internal

- Severity: Info
- Confidence: High
- Category: runtime-contract-drift
- Domain: astro-chart-object-capability-payload
- Evidence: E-011, E-012, E-013, E-018
- Expected rule: Fixed stars can be internal runtime objects while raw payloads remain outside public API.
- Actual state: Fixed stars are `ChartObjectRuntimeData` documentary objects and contact sources; public API tests exclude raw fixed-star runtime payload classes.
- Impact: Fixed stars are active documentary chart objects and contact sources, but raw runtime payloads stay internal and public exposure is intentionally deferred.
- Recommended action: No immediate implementation; route public projection decisions through the runtime exposure candidate from the adjacent audit.
- Story candidate: no
- Suggested archetype: non-domain
