# Story Candidates - Astro Feature Coverage

## SC-001 Predictive Runtime Roadmap And First Forecast Owner

- Source finding: F-001
- Suggested story title: Define the first canonical predictive runtime owner
- Suggested archetype: feature-coverage-roadmap
- Primary domain: backend astrology forecast runtime
- Required contracts: Runtime Source of Truth; Baseline Snapshot; Ownership Routing; Contract Shape; Reintroduction Guard; Persistent Evidence
- Draft objective: Select and specify the first predictive runtime family, preferably transits, without modifying natal graph behavior or claiming progressions, returns, synastry, composite, profections, directions or firdaria as implemented.
- Closure intent: phased-with-map
- Must include: exact technique selected; explicit non-goals for the other forecast techniques; before evidence from E-014 and E-015; no public API change unless a separate API story is created; no `chart_objects` public exposure; no wildcard allowlist.
- Validation hints: Repeat `rg -n "transit|progression|synastr|composite|profection|firdaria|time_lord|solar_return|lunar_return" backend/app/domain/astrology backend/tests/unit/domain/astrology backend/tests/integration/astrology -g "*.py"` before and after; run targeted tests for the selected new owner; run architecture scans preventing new dependencies from API, infra or services into pure domain calculators.
- Blockers: Stop if product cannot select the first forecast technique or if implementation would require API/public-contract changes in the same story.

### Exhaustive Files To Modify

- Application files: none for this audit. Future implementation selection rule: new or existing forecast owner under `backend/app/domain/astrology/**`, not `backend/app/api/**`, not `frontend/src/**`, not `backend/migrations/**`.
- Governance/test files: targeted backend domain tests for the selected technique; no wildcard folder allowlist.
- Before evidence: E-014 and E-015 absence/reference scans.
- After evidence required: runtime calculator or graph path plus tests proving one selected forecast technique; negative scans proving unselected techniques remain unclaimed.
- Stop condition: selected predictive technique has runtime plus tests, and all unselected techniques remain explicitly out of the implementation scope.

## SC-002 Fixed-Star Coverage Productization Decision

- Source finding: F-002
- Suggested story title: Decide fixed-star public projection versus new paran runtime
- Suggested archetype: runtime-surface-productization
- Primary domain: backend astrology fixed-star runtime
- Required contracts: Runtime Source of Truth; Ownership Routing; Contract Shape; Reintroduction Guard; Persistent Evidence
- Draft objective: Split existing fixed-star conjunction support from missing parans and non-conjunction contacts, then choose whether to expose current conjunction contacts or implement a new calculator in a later story.
- Closure intent: full-closure
- Must include: exact decision for public projection of existing conjunction payloads; explicit decision that parans require a separate calculator; no raw `chart_objects` exposure; before evidence from E-013; no wildcard allowlist.
- Validation hints: Repeat fixed-star scans from E-013; run fixed-star unit tests if code changes later; verify public contract tests still exclude raw internal payloads unless a dedicated API contract changes.
- Blockers: Stop if product cannot decide whether conjunctions should be user-facing before parans.

### Exhaustive Files To Modify

- Application files: none for this audit. Future decision story may touch only fixed-star projection/contract owner chosen by product; no app-code changes are implied here.
- Governance/test files: fixed-star decision artifact or targeted tests if projection is later implemented.
- Before evidence: E-013 and E-009.
- After evidence required: explicit decision record plus validation proving either unchanged internal-only status or a stable public projection that does not expose raw `chart_objects`.
- Stop condition: fixed-star conjunctions and parans have separate statuses and no remaining ambiguous "fixed stars complete" claim.

## SC-003 Astral Point Productization And Capability Policy

- Source finding: F-003
- Suggested story title: Decide public and capability policy for nodes Lilith and apsides
- Suggested archetype: contract-shape-productization
- Primary domain: backend astrology astral points
- Required contracts: Runtime Source of Truth; Ownership Routing; Contract Shape; Reintroduction Guard; Persistent Evidence
- Draft objective: Decide how calculated nodes, Lilith and apsides should appear in public projections, aspects, interpretation input, dignity/dominance eligibility and chart-object capabilities.
- Closure intent: full-closure
- Must include: exact current point list; before evidence from E-012; public projection decision; capability matrix; no raw `chart_objects` exposure; negative checks for ad hoc object-type branching.
- Validation hints: Repeat E-012 scan; run `test_astral_point_calculation_resolver`, `test_natal_result_contains_configured_points`, `test_natal_result_chart_objects` and relevant chart-object architecture tests if implementation follows.
- Blockers: Stop if product cannot decide whether astral points are display-only, aspectable, interpretive, dignity-eligible or dominance-eligible.

### Exhaustive Files To Modify

- Application files: none for this audit. Future implementation selection rule: `backend/app/domain/astrology/astral_point_calculation_resolver.py`, `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`, projection owner if selected, and tests matching the chosen capability policy.
- Governance/test files: capability matrix or guard; targeted tests for every point whose classification changes.
- Before evidence: E-008, E-009, E-012.
- After evidence required: before/after point inventory, public projection diff if any, and tests proving capability behavior.
- Stop condition: every configured point has a documented calculation, projection and capability status.

## SC-004 Non-Planetary Object Taxonomy For Lots Asteroids Chiron And Midpoints

- Source finding: F-004
- Suggested story title: Classify lots and non-planetary object taxonomy before calculators
- Suggested archetype: domain-taxonomy-decision
- Primary domain: backend astrology object taxonomy
- Required contracts: Runtime Source of Truth; Ownership Routing; Contract Shape; Reintroduction Guard; Persistent Evidence
- Draft objective: Decide whether parts arabes/lots, asteroids, Chiron and midpoints are planets, astral points, calculated points, arabic parts, or a new chart-object subtype before adding any ephemeris or calculation code.
- Closure intent: blocked
- Must include: product/astrology decision table; explicit handling of existing `ChartObjectType.ARABIC_PART` taxonomy without treating it as implemented lot calculation; no calculator implementation; no seed or migration until taxonomy is accepted; before evidence from E-014 and E-015.
- Validation hints: Repeat E-014; verify no new runtime files are added during the decision story; if a later implementation follows, require tests proving canonical object taxonomy and no duplicate eligibility path.
- Blockers: User/product decision is required on taxonomy and priority order.

### Exhaustive Files To Modify

- Application files: none until the taxonomy decision is made.
- Governance/test files: decision artifact only; no app/test code required for the decision candidate.
- Before evidence: E-014 and E-015.
- After evidence required: accepted taxonomy decision and exact next-story scope.
- Stop condition: parts arabes/lots, asteroids, Chiron and midpoints each have one canonical owner or are explicitly deferred.

## SC-005 Feature Coverage Claim Guard

- Source finding: F-005
- Suggested story title: Guard implemented-status claims with runtime and test evidence
- Suggested archetype: test-guard-hardening
- Primary domain: CONDAMAD governance for astrology feature coverage
- Required contracts: Runtime Source of Truth; Baseline Snapshot; Reintroduction Guard; Persistent Evidence
- Draft objective: Add a governance guard or audit rule requiring every future `implemented` astrology-feature claim to cite runtime code plus test or runtime-contract evidence.
- Closure intent: full-closure
- Must include: exact allowed evidence profile; no wildcard allowlist; no backend calculator changes; before evidence from E-006, E-007, E-010 and E-014; mapping to regression guardrails if a durable invariant is added.
- Validation hints: Validate the guard with a fixture audit/story containing one valid implemented claim and one invalid reference-only claim; run existing domain-auditor validation and lint scripts.
- Blockers: Stop if the guard cannot be scoped to audit/story artifacts without touching app runtime.

### Exhaustive Files To Modify

- Application files: none.
- Governance/test files: exact guard script or CONDAMAD validation artifact to be selected by the story writer; no wildcard folder exception.
- Before evidence: E-006, E-007, E-010, E-014.
- After evidence required: failing fixture for unsupported `implemented` claim and passing fixture for runtime plus test backed claim.
- Stop condition: future feature-coverage audit/story cannot pass with an `implemented` status that cites only docs or reference data.

## Deferred Non-Domain Context

- API exposure: deferred to a contract-shape/API story if public projection is selected.
- Frontend: deferred until backend public contract exists.
- DB migrations and seed expansion: deferred until taxonomy or calculator ownership is accepted.
- Auth, i18n, styling and build tooling: out of scope.
