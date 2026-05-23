# Finding Register - Astro Runtime Surface Exposure

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | runtime-contract-drift | astro-runtime-surface-exposure | E-005, E-006, E-007, E-008, E-014 | Product value exists for `chart_objects`, but raw exposure would couple the frontend to internal calculation graph details and violate existing public exclusion guards. | Create a controlled public projection such as `chart_facts`; keep `ChartObjectRuntimeData` internal and preserve no-raw-runtime guards. | yes |
| F-002 | Medium | High | missing-canonical-owner | astro-runtime-surface-exposure | E-006, E-011, E-012, E-014 | Fixed-star contacts are calculated and interpretation-ready, but no stable public projection contract exists for user-facing display. | Define a reduced fixed-star contact projection with target, star, orb, source/rule and display labels; do not expose full payloads. | yes |
| F-003 | Medium | Medium | observability-gap | astro-runtime-surface-exposure | E-006, E-007, E-014 | Runtime graph and payloads are useful for diagnosis, but no protected admin/debug exposure exists and raw public exposure is forbidden. | Design a protected admin/debug endpoint or trace artifact only after auth/authorization decisions; stop if protection cannot be specified. | yes |
| F-004 | Low | High | missing-guard | astro-runtime-surface-exposure | E-003, E-005, E-008, E-015 | Existing guards protect raw chart-object non-exposure, but there is no exact durable guardrail for future runtime exposure decision vocabulary. | Do not update application guards in this audit; future story-writer should add or map a guard when implementing projections. | no |
| F-005 | Info | High | needs-user-decision | astro-runtime-surface-exposure | E-012, E-013 | Dignity, dominance, sign profile, condition and aspect-hint surfaces already feed public or interpretation projections in different shapes; product must decide which details are user-facing. | Keep current public projections stable; route new exposure through explicit product stories rather than broad raw payload publication. | no |

## Finding Details

### F-001 - Raw `chart_objects` exposure is unsafe despite product value

- Severity: High
- Confidence: High
- Category: runtime-contract-drift
- Domain: astro-runtime-surface-exposure
- Evidence: E-005, E-006, E-007, E-008, E-014
- Expected rule: raw `ChartObjectRuntimeData` remains internal; frontend/public contracts receive only stable, reduced facts.
- Actual state: `chart_objects` is canonical internal runtime and excluded from schema/public dump, while no dedicated `chart_facts` projection exists yet.
- Impact: Product value exists for `chart_objects`, but raw exposure would couple the frontend to internal calculation graph details and violate existing public exclusion guards.
- Recommended action: Create a controlled public projection such as `chart_facts`; keep `ChartObjectRuntimeData` internal and preserve no-raw-runtime guards.
- Story candidate: yes
- Suggested archetype: `api-contract-change`
- Closure decision: `phased-with-map`; candidate SC-001 is intended to close the public product part without exposing raw runtime. Admin/debug remains SC-003.

### F-002 - Fixed-star contacts lack a public projection owner

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: astro-runtime-surface-exposure
- Evidence: E-006, E-011, E-012, E-014
- Expected rule: useful fixed-star contacts should be exposed through a stable projection if product wants them public.
- Actual state: contacts are calculated and fed into interpretation input, but no public natal projection contract was found.
- Impact: Fixed-star contacts are calculated and interpretation-ready, but no stable public projection contract exists for user-facing display.
- Recommended action: Define a reduced fixed-star contact projection with target, star, orb, source/rule and display labels; do not expose full payloads.
- Story candidate: yes
- Suggested archetype: `api-contract-change`
- Closure decision: `full-closure`; candidate SC-002 can close the public projection decision for fixed-star contacts.

### F-003 - Full calculation graph trace needs protected admin/debug design

- Severity: Medium
- Confidence: Medium
- Category: observability-gap
- Domain: astro-runtime-surface-exposure
- Evidence: E-006, E-007, E-014
- Expected rule: internal graph traces may be exposed only behind an explicit protected admin/debug surface.
- Actual state: runtime graph nodes and payloads exist, but no admin/debug endpoint or trace exposure is in scope or proven.
- Impact: Runtime graph and payloads are useful for diagnosis, but no protected admin/debug exposure exists and raw public exposure is forbidden.
- Recommended action: Design a protected admin/debug endpoint or trace artifact only after auth/authorization decisions; stop if protection cannot be specified.
- Story candidate: yes
- Suggested archetype: `observability-guard-hardening`
- Closure decision: `blocked`; candidate SC-003 requires auth/admin protection decisions before implementation.

### F-004 - Exact exposure guardrail is absent

- Severity: Low
- Confidence: High
- Category: missing-guard
- Domain: astro-runtime-surface-exposure
- Evidence: E-003, E-005, E-008, E-015
- Expected rule: durable exposure decisions should become executable guards once projections are implemented.
- Actual state: adjacent guardrails exist, but no exact guardrail names this audit's decision matrix.
- Impact: Existing guards protect raw chart-object non-exposure, but there is no exact durable guardrail for future runtime exposure decision vocabulary.
- Recommended action: Do not update application guards in this audit; future story-writer should add or map a guard when implementing projections.
- Story candidate: no
- Suggested archetype: `test-guard-hardening`
- Closure decision: no implementation candidate from this audit because app/test guard changes are out of scope.

### F-005 - Product granularity remains a decision for secondary payloads

- Severity: Info
- Confidence: High
- Category: needs-user-decision
- Domain: astro-runtime-surface-exposure
- Evidence: E-012, E-013
- Expected rule: existing public projections stay stable, while new user-facing detail is intentionally selected.
- Actual state: dignity and dominance have public projections; sign profiles, condition profiles and aspect hints are mainly interpretation-oriented.
- Impact: Dignity, dominance, sign profile, condition and aspect-hint surfaces already feed public or interpretation projections in different shapes; product must decide which details are user-facing.
- Recommended action: Keep current public projections stable; route new exposure through explicit product stories rather than broad raw payload publication.
- Story candidate: no
- Suggested archetype: `needs-user-decision`
- Closure decision: no direct candidate until product selects detail granularity.
