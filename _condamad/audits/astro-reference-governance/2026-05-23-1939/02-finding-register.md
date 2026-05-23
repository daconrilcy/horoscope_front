# Finding Register - Astro Reference Governance

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | duplicate-responsibility | astro-reference-governance | E-008, E-014 | Solar proximity thresholds have active DB and Python owners with divergent under-beams values, so future changes can update one source while runtime uses another. | Move advanced planetary condition proximity thresholds to one versioned runtime reference or explicitly mark Python as canonical with guard evidence. | yes |
| F-002 | High | High | duplicate-responsibility | astro-reference-governance | E-009, E-014, E-015 | Motion and station rules are split between DB relations, one DB threshold and Python mean-speed profiles/formulas, making source ownership unclear. | Converge planetary motion and station thresholds into a versioned ownership contract and remove unguarded duplicate thresholds. | yes |
| F-003 | Medium | High | missing-canonical-owner | astro-reference-governance | E-010, E-015 | Dominance, sign and house weighting mix DB weights with Python scoring constants; the matrix cannot identify one canonical owner for all weighting families. | Inventory all active weighting constants and classify each as DB-owned, Python-owned by decision, or migration candidate. | yes |
| F-004 | Medium | Medium | missing-canonical-owner | astro-reference-governance | E-011, E-017 | Interpretation rule ownership is split between DB profiles and Python profile catalogs/projectors without a complete source ownership registry. | Add governance tests and a source registry proving which interpretation rules are DB-modifiable and which are code-owned. | yes |
| F-005 | Medium | Medium | missing-canonical-owner | astro-reference-governance | E-007, E-013 | Doctrine sources are partial and not consistently linked to versioned rule families, especially for thresholds and weights. | Create a doctrine/source index or require each migrated rule source to cite reference/source metadata. | yes |
| F-006 | High | High | missing-guard | astro-reference-governance | E-003, E-018, E-019 | Existing guards protect runtime boundaries but not source ownership drift; a future change can add a new threshold or weight without updating the governance matrix. | Add a no-wildcard source-ownership guard for thresholds, weights, profiles and reference-data movement. | yes |

## F-001 Solar Proximity Threshold Ownership Is Duplicated

- Severity: High
- Confidence: High
- Category: duplicate-responsibility
- Domain: astro-reference-governance
- Evidence: E-008, E-014
- Expected rule: Cazimi, combustion and under-beams thresholds must have one canonical owner or an explicit dual-source governance decision.
- Actual state: DB accidental dignity rules define solar distance thresholds, while Python `SolarProximityThresholds` and visibility thresholds define separate active limits; under-beams is `17` in DB rules and `15.0` in Python advanced conditions.
- Impact: Solar proximity thresholds have active DB and Python owners with divergent under-beams values, so future changes can update one source while runtime uses another.
- Recommended action: Move advanced planetary condition proximity thresholds to one versioned runtime reference or explicitly mark Python as canonical with guard evidence.
- Story candidate: yes
- Suggested archetype: reference-governance-convergence

## F-002 Motion And Station Threshold Ownership Is Split

- Severity: High
- Confidence: High
- Category: duplicate-responsibility
- Domain: astro-reference-governance
- Evidence: E-009, E-014, E-015
- Expected rule: Planetary speed, mean-speed relation and station thresholds must have one auditable owner.
- Actual state: DB rules define motion states and a generic station threshold, while Python owns per-planet mean speeds, station formulas and local `0.05` comparisons.
- Impact: Motion and station rules are split between DB relations, one DB threshold and Python mean-speed profiles/formulas, making source ownership unclear.
- Recommended action: Converge planetary motion and station thresholds into a versioned ownership contract and remove unguarded duplicate thresholds.
- Story candidate: yes
- Suggested archetype: reference-governance-convergence

## F-003 Dominance Sign And House Weights Lack A Complete Canonical Owner

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: astro-reference-governance
- Evidence: E-010, E-015
- Expected rule: Dominance, house strength, sign weighting and dignity weights should be clearly classified as DB-owned or Python-owned.
- Actual state: Planet dominance factor weights are DB-backed, while sign runtime weights, house strength scores and dominance level thresholds are Python constants.
- Impact: Dominance, sign and house weighting mix DB weights with Python scoring constants; the matrix cannot identify one canonical owner for all weighting families.
- Recommended action: Inventory all active weighting constants and classify each as DB-owned, Python-owned by decision, or migration candidate.
- Story candidate: yes
- Suggested archetype: rule-source-inventory

## F-004 Interpretation Rule Ownership Is Not Fully Registered

- Severity: Medium
- Confidence: Medium
- Category: missing-canonical-owner
- Domain: astro-reference-governance
- Evidence: E-011, E-017
- Expected rule: Interpretation rules should state whether their source is DB reference data, Python catalog code, or non-runtime documentation.
- Actual state: DB profiles, translation/profile seeds and Python advanced-condition profile catalogs coexist without a complete source ownership registry.
- Impact: Interpretation rule ownership is split between DB profiles and Python profile catalogs/projectors without a complete source ownership registry.
- Recommended action: Add governance tests and a source registry proving which interpretation rules are DB-modifiable and which are code-owned.
- Story candidate: yes
- Suggested archetype: governance-test-hardening

## F-005 Doctrine Links Are Partial And Non-Canonical

- Severity: Medium
- Confidence: Medium
- Category: missing-canonical-owner
- Domain: astro-reference-governance
- Evidence: E-007, E-013
- Expected rule: Versioned astrology reference rules should be traceable to doctrine/source metadata or an explicit documented absence.
- Actual state: DB seeds include some `reference_version_id`, source and micro-note fields, while docs provide research context; the audit found no complete doctrine registry for every threshold, weight and profile family.
- Impact: Doctrine sources are partial and not consistently linked to versioned rule families, especially for thresholds and weights.
- Recommended action: Create a doctrine/source index or require each migrated rule source to cite reference/source metadata.
- Story candidate: yes
- Suggested archetype: doctrine-source-index

## F-006 Rule Source Ownership Has No Reintroduction Guard

- Severity: High
- Confidence: High
- Category: missing-guard
- Domain: astro-reference-governance
- Evidence: E-003, E-018, E-019
- Expected rule: New thresholds, weights and rule profiles should fail a guard unless classified in the source ownership matrix.
- Actual state: Existing guardrails protect adjacent runtime boundaries, but no guard enforces that new rule sources update reference-governance ownership.
- Impact: Existing guards protect runtime boundaries but not source ownership drift; a future change can add a new threshold or weight without updating the governance matrix.
- Recommended action: Add a no-wildcard source-ownership guard for thresholds, weights, profiles and reference-data movement.
- Story candidate: yes
- Suggested archetype: governance-test-hardening
