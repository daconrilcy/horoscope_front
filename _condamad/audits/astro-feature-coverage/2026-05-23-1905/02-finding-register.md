# Finding Register - Astro Feature Coverage

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | runtime-contract-drift | astro-feature-coverage | E-005, E-014, E-015 | Product can ask for predictive workflows that look documented but have no backend astrology runtime owner. | Create a bounded predictive-technique roadmap story that starts with one canonical graph/calculator family and keeps natal runtime separate. | yes |
| F-002 | Medium | High | missing-canonical-owner | astro-feature-coverage | E-005, E-013 | Fixed-star coverage can be overstated because only zodiacal conjunction contacts are implemented; parans and other fixed-star techniques are absent. | Create a fixed-star coverage decision story separating public projection of existing conjunctions from new paran/aspect calculators. | yes |
| F-003 | Medium | High | runtime-contract-drift | astro-feature-coverage | E-008, E-009, E-012 | Nodes, Lilith and apsides are calculated internally but remain partial product coverage because public exposure and capability policy are not complete. | Create an astral-point productization story deciding public projection, aspect participation, dignity/dominance eligibility and interpretation input ownership. | yes |
| F-004 | Medium | High | missing-canonical-owner | astro-feature-coverage | E-014, E-015 | Parts arabes/lots, asteroids, Chiron and midpoints have no runtime owner, while future product briefs name them as possible coverage. | Create a non-planetary-object intake story to decide object taxonomy before adding calculators. | yes |
| F-005 | Medium | High | missing-test-coverage | astro-feature-coverage | E-006, E-007, E-010, E-014 | Implemented natal coverage is well tested, but missing-technique assertions are not guarded by a durable audit/test contract. | Add a governance guard or audit follow-up that prevents future stories from claiming implemented status without runtime plus test evidence. | yes |

## F-001 Predictive Techniques Are Reference-Only Or Missing

- Severity: High
- Confidence: High
- Category: runtime-contract-drift
- Domain: astro-feature-coverage
- Evidence: E-005, E-014, E-015
- Expected rule: Techniques classified as implemented must have a backend runtime calculator or graph path plus test/runtime-contract proof.
- Actual state: Transits and progressions have reference data or research docs, while transits, progressions, solar returns, lunar returns, synastry, composite, profections, symbolic directions and firdaria/time lords have no in-domain runtime calculator under `backend/app/domain/astrology`.
- Impact: Product can ask for predictive workflows that look documented but have no backend astrology runtime owner.
- Recommended action: Create a bounded predictive-technique roadmap story that starts with one canonical graph/calculator family and keeps natal runtime separate.
- Story candidate: yes
- Suggested archetype: feature-coverage-roadmap

## F-002 Fixed-Star Coverage Is Conjunction-Only

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: astro-feature-coverage
- Evidence: E-005, E-013
- Expected rule: Fixed-star coverage claims must distinguish catalog/runtime object coverage, conjunction calculation, public projection, parans and other contact types.
- Actual state: The runtime calculates fixed-star conjunction payloads from chart objects, but the post-CS-236 baseline explicitly excludes parans, oppositions, fixed-star aspects and heliacal risings.
- Impact: Fixed-star coverage can be overstated because only zodiacal conjunction contacts are implemented; parans and other fixed-star techniques are absent.
- Recommended action: Create a fixed-star coverage decision story separating public projection of existing conjunctions from new paran/aspect calculators.
- Story candidate: yes
- Suggested archetype: runtime-surface-productization

## F-003 Astral Points Are Calculated But Product Coverage Is Partial

- Severity: Medium
- Confidence: High
- Category: runtime-contract-drift
- Domain: astro-feature-coverage
- Evidence: E-008, E-009, E-012
- Expected rule: Nodes, Lilith and apsides should be classified separately across calculation, runtime payload, public projection and interpretive input.
- Actual state: Runtime data and tests prove configured astral points, nodes, lunar apsides and Black Moon Lilith can be calculated internally; `chart_objects` remains excluded from public JSON and capability choices are limited by current chart-object policy.
- Impact: Nodes, Lilith and apsides are calculated internally but remain partial product coverage because public exposure and capability policy are not complete.
- Recommended action: Create an astral-point productization story deciding public projection, aspect participation, dignity/dominance eligibility and interpretation input ownership.
- Story candidate: yes
- Suggested archetype: contract-shape-productization

## F-004 Lots Asteroids Chiron And Midpoints Have No Runtime Owner

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: astro-feature-coverage
- Evidence: E-014, E-015
- Expected rule: Non-planetary object families should have a canonical runtime taxonomy before calculators or projections are added.
- Actual state: `ChartObjectType.ARABIC_PART` exists only as taxonomy, and no calculator/module/test was found for parts arabes/lots, asteroids, Chiron or midpoints in `backend/app/domain/astrology`; only taxonomy or research/future-product mentions were found.
- Impact: Parts arabes/lots, asteroids, Chiron and midpoints have no runtime owner, while future product briefs name them as possible coverage.
- Recommended action: Create a non-planetary-object intake story to decide object taxonomy before adding calculators.
- Story candidate: yes
- Suggested archetype: domain-taxonomy-decision

## F-005 Missing-Technique Claims Lack A Durable Guard

- Severity: Medium
- Confidence: High
- Category: missing-test-coverage
- Domain: astro-feature-coverage
- Evidence: E-006, E-007, E-010, E-014
- Expected rule: Future implemented-status claims should require runtime code plus test or contract evidence.
- Actual state: Existing tests strongly guard implemented natal surfaces, but this audit found no dedicated guard preventing future documentation from classifying missing predictive and non-natal techniques as implemented without runtime evidence.
- Impact: Implemented natal coverage is well tested, but missing-technique assertions are not guarded by a durable audit/test contract.
- Recommended action: Add a governance guard or audit follow-up that prevents future stories from claiming implemented status without runtime plus test evidence.
- Story candidate: yes
- Suggested archetype: test-guard-hardening
