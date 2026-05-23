# Finding Register - Astro Astronomical Accuracy

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | duplicate-responsibility | astro-astronomical-accuracy | E-005, E-007, E-008, E-014 | Astronomical reliability can be overstated because production-grade calculation still depends on runtime flags and engine routing while simplified code remains callable. | Create CS-240 to enforce or prove `swisseph`-only production calculation mode, with a deliberate dev/test-only simplified allowance. | yes |
| F-002 | High | High | missing-test-coverage | astro-astronomical-accuracy | E-006, E-010, E-011, E-012, E-013, E-016 | Existing tests prove contracts and selected behavior, but not a complete externally comparable audit-grade astronomical baseline for sensitive cases. | Create CS-241 to add the astronomical golden chart regression suite covering all required sensitive profiles. | yes |
| F-003 | Medium | High | observability-gap | astro-astronomical-accuracy | E-008, E-009, E-013 | Result traces can miss a reviewable ephemeris file/version/hash guarantee when configuration omits an expected hash or when a scenario is not tied to a persisted trace. | Create CS-242 to persist ephemeris configuration evidence in `chart_result` trace and validation artifacts. | yes |
| F-004 | Medium | Medium | runtime-contract-drift | astro-astronomical-accuracy | E-006, E-012, E-013 | Sidereal, topocentric, altitude and house-system options exist, but the audit cannot prove all edge behavior against external references. | Route to CS-241 golden charts; stop if external reference values or accepted tolerances are unavailable. | yes |
| F-005 | Low | High | missing-guard | astro-astronomical-accuracy | E-003, E-015 | Adjacent astrology guardrails exist, but none names the astronomical accuracy evidence set or forbids replacing audit recommendations with runtime changes during audit stories. | Do not change guardrails in this audit; future implementation stories should add exact guards after golden or production-mode changes. | no |

## F-001 Simplified And SwissEph Calculation Paths Remain Active

- Severity: High
- Confidence: High
- Category: duplicate-responsibility
- Domain: astro-astronomical-accuracy
- Evidence: E-005, E-007, E-008, E-014
- Expected rule: audit-grade production calculation should have one proven astronomical runtime path, or a documented and guarded non-production simplified exception.
- Actual state: `swisseph` providers and bootstrap exist, but `build_natal_result` defaults to `engine="simplified"` at the domain facade and graph nodes branch to simplified calculators unless the service-resolved engine is `swisseph`.
- Impact: Astronomical reliability can be overstated because production-grade calculation still depends on runtime flags and engine routing while simplified code remains callable.
- Recommended action: Create CS-240 to enforce or prove `swisseph`-only production calculation mode, with a deliberate dev/test-only simplified allowance.
- Story candidate: yes
- Suggested archetype: engine-mode-guard-hardening
- Closure decision: full-closure for the audited engine-mode risk if CS-240 proves production cannot select simplified except an exact dev/test path.

## F-002 Golden Chart Coverage Is Not Complete For Sensitive Astronomical Cases

- Severity: High
- Confidence: High
- Category: missing-test-coverage
- Domain: astro-astronomical-accuracy
- Evidence: E-006, E-010, E-011, E-012, E-013, E-016
- Expected rule: astronomical accuracy claims should be backed by external-reference golden cases that cover normal, temporal, zodiac/frame and house edge behavior.
- Actual state: a versioned `swisseph` dataset exists, temporal and option-contract tests exist, but the repository does not prove all required golden profiles: Paris normal, DST ambiguous time, DST nonexistent time, high latitude, Sidereal Lahiri, topocentric, whole sign and Placidus edge.
- Impact: Existing tests prove contracts and selected behavior, but not a complete externally comparable audit-grade astronomical baseline for sensitive cases.
- Recommended action: Create CS-241 to add the astronomical golden chart regression suite covering all required sensitive profiles.
- Story candidate: yes
- Suggested archetype: golden-regression-suite
- Closure decision: full-closure if the suite records objective, input, reference source, tolerance and expected outputs for every required chart.

## F-003 Ephemeris Evidence Is Implemented But Not Fully Guaranteed By Configuration

- Severity: Medium
- Confidence: High
- Category: observability-gap
- Domain: astro-astronomical-accuracy
- Evidence: E-008, E-009, E-013
- Expected rule: audit-grade chart results should carry reproducible ephemeris evidence: dataset version, required file list or fingerprint, computed hash and startup validation status.
- Actual state: bootstrap computes a hash when required-file validation is active and services/API propagate version/hash, but `EPHEMERIS_PATH_HASH` is optional and the current golden dataset describes `swisseph-moshier-integrated` without a persisted file hash contract per result.
- Impact: Result traces can miss a reviewable ephemeris file/version/hash guarantee when configuration omits an expected hash or when a scenario is not tied to a persisted trace.
- Recommended action: Create CS-242 to persist ephemeris configuration evidence in `chart_result` trace and validation artifacts.
- Story candidate: yes
- Suggested archetype: observability-trace-hardening
- Closure decision: full-closure if persisted traces include enough metadata to reproduce the exact ephemeris source and detect drift.

## F-004 Edge Options Exist But Need External Reference Proof

- Severity: Medium
- Confidence: Medium
- Category: runtime-contract-drift
- Domain: astro-astronomical-accuracy
- Evidence: E-006, E-012, E-013
- Expected rule: sidereal ayanamsa, topocentric altitude, whole sign and Placidus high-latitude behavior should be proven by deterministic reference cases.
- Actual state: provider code implements Lahiri, topocentric, altitude and whole-sign/Placidus selections; tests cover option propagation and errors, but no complete external golden set proves the edge outputs.
- Impact: Sidereal, topocentric, altitude and house-system options exist, but the audit cannot prove all edge behavior against external references.
- Recommended action: Route to CS-241 golden charts; stop if external reference values or accepted tolerances are unavailable.
- Story candidate: yes
- Suggested archetype: golden-regression-suite
- Closure decision: full-closure through CS-241 golden chart acceptance if reference values and tolerances are explicitly sourced.

## F-005 Astronomical Accuracy Guardrail Is Adjacent But Not Exact

- Severity: Low
- Confidence: High
- Category: missing-guard
- Domain: astro-astronomical-accuracy
- Evidence: E-003, E-015
- Expected rule: durable astronomical accuracy decisions should gain exact guards when implementation stories change mode selection, golden baselines or trace metadata.
- Actual state: RG-137 through RG-148 protect adjacent astrology runtime boundaries; no current invariant names the production `swisseph` mode plus golden evidence requirement.
- Impact: Adjacent astrology guardrails exist, but none names the astronomical accuracy evidence set or forbids replacing audit recommendations with runtime changes during audit stories.
- Recommended action: Do not change guardrails in this audit; future implementation stories should add exact guards after golden or production-mode changes.
- Story candidate: no
- Suggested archetype: test-guard-hardening
- Closure decision: no direct candidate because this audit is documentation-only and does not create durable runtime behavior.
