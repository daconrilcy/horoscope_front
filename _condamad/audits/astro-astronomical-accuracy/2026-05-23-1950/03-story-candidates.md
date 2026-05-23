# Story Candidates - Astro Astronomical Accuracy

This file qualifies the three story keys required by CS-241. Candidates are proposals for story writing, not implementation in this audit.

## SC-001 CS-240 Enforce Swisseph-Only Production Calculation Mode

- Source finding: F-001
- Suggested story title: CS-240 - Enforce swisseph-only production calculation mode
- Suggested archetype: engine-mode-guard-hardening
- Primary domain: backend astrology calculation mode
- Priority: P1
- Required contracts: Runtime Source of Truth, Baseline Snapshot, Ownership Routing, Reintroduction Guard, Persistent Evidence, No Legacy
- Draft objective: Ensure production and accurate user-facing natal calculations cannot silently use the simplified engine while preserving an explicitly guarded dev/test-only simplified path if still required.
- Closure intent: full-closure
- Must include: exact inventory of `backend/app/core/config.py`, `backend/app/services/natal/calculation_service.py`, `backend/app/domain/astrology/natal_calculation.py`, `backend/app/domain/astrology/runtime/natal_calculation_nodes.py`, public astrology API routes, compare endpoint behavior and tests that intentionally use simplified.
- Validation hints: run targeted scans for `engine="simplified"`, `engine == "swisseph"`, `NATAL_ENGINE_DEFAULT`, `NATAL_ENGINE_SIMPLIFIED_ENABLED`; run focused service/API/unit tests proving production mode uses `swisseph` or fails explicitly.
- Blockers: stop if product wants simplified available to production users; record a `needs-user-decision` exception instead of broad fallback.

### Exhaustive Files To Modify

- Application files: exact files selected by CS-240 from the inventory above; no frontend, seed or migration file expected.
- Governance/test files: focused tests or guardrail entries proving no unguarded simplified production route remains.
- Before evidence: E-005, E-007, E-008, E-014.
- After evidence: production-mode scan shows no unclassified simplified path; tests prove bootstrap failure returns explicit error, not silent simplified fallback.
- Stop condition: F-001 closes fully or a product-approved exception is documented with exact guards.

## SC-002 CS-241 Add Astronomical Golden Chart Regression Suite

- Source finding: F-002, F-004
- Suggested story title: CS-241 - Add astronomical golden chart regression suite
- Suggested archetype: golden-regression-suite
- Primary domain: backend astrology astronomical accuracy tests
- Priority: P1 for F-002 coverage closure; includes P2 F-004 house and option edge closure in the same suite.
- Required contracts: Runtime Source of Truth, Baseline Snapshot, Contract Shape, Persistent Evidence, Reintroduction Guard
- Draft objective: Add external-reference golden chart tests that prove the required sensitive astronomical profiles with explicit inputs, expected outputs, tolerances and source provenance.
- Closure intent: full-closure
- Must include: Paris normal case; DST ambiguous time; DST nonexistent time; high latitude case; Sidereal Lahiri case; topocentric case; whole sign case; Placidus edge case; expected planets, ASC/MC/cusps where applicable; source/tolerance metadata; exact input profile, expected house/angle outputs, tolerance, and documented behavior when SwissEph raises or returns unstable Placidus data.
- Validation hints: run the new golden suite, existing `test_natal_golden_swisseph.py`, temporal tests and targeted scans for all eight golden chart names plus `high latitude`, `Placidus`, `whole sign`, and `topocentric`.
- Blockers: stop if authoritative expected values, accepted tolerances, house-system behavior for Placidus edge, DST input policy, or the explicit fail/fallback policy for unstable Placidus cannot be decided.

### Exhaustive Files To Modify

- Application files: none expected unless testability requires a narrowly approved trace/read helper.
- Governance/test files: golden dataset/test files under existing backend golden-test ownership; optional documentation under the story capsule.
- Before evidence: E-006, E-010, E-011, E-012, E-013, E-016.
- After evidence: all eight required profiles have reproducible reference values, tolerances and passing tests; edge case outputs are externally referenced or blocked by documented user decision; F-002 and F-004 close.
- Stop condition: no required sensitive profile remains without a reference, explicit skip policy or user-decision blocker, and F-004 closes without another discovery-only follow-up.

## SC-003 CS-242 Persist Ephemeris Configuration Evidence In Chart Result Trace

- Source finding: F-003
- Suggested story title: CS-242 - Persist ephemeris configuration evidence in chart_result trace
- Suggested archetype: observability-trace-hardening
- Primary domain: backend astrology result traceability
- Priority: P2
- Required contracts: Runtime Source of Truth, Baseline Snapshot, Ownership Routing, Reintroduction Guard, Persistent Evidence
- Draft objective: Persist enough ephemeris evidence with chart results to reproduce or audit the exact ephemeris configuration used for a `swisseph` calculation.
- Closure intent: full-closure
- Must include: `ephemeris_path_version`, computed or expected hash, required files evidence, validation status, `swisseph` enabled state, engine, zodiac, frame, ayanamsa, house system, altitude and time scale where currently available.
- Validation hints: inspect `backend/app/core/ephemeris.py`, `backend/app/services/natal/calculation_service.py`, chart-result persistence and API metadata tests; run scans for `ephemeris_path_version` and `ephemeris_path_hash`.
- Blockers: stop if raw filesystem path exposure is requested; persist privacy-safe/versioned metadata, not local secret paths.

### Exhaustive Files To Modify

- Application files: exact persistence and service/API files selected by CS-242 after inspecting chart-result ownership; no frontend change unless a later story requests display.
- Governance/test files: integration/unit tests proving trace persistence and metadata redaction.
- Before evidence: E-008, E-009, E-013.
- After evidence: a persisted chart trace proves engine, ephemeris version/hash/evidence and time-scale configuration; F-003 closes.
- Stop condition: every `swisseph` chart trace has reproducible ephemeris evidence or the calculation fails explicitly.

## SC-004 CS-241 House And Option Edge Closure Within The Golden Suite

- Source finding: F-004
- Suggested story title: CS-241 - Add astronomical golden chart regression suite
- Suggested archetype: golden-regression-suite
- Primary domain: backend astrology house-system edge accuracy
- Priority: P2, implemented only as part of the P1 CS-241 golden suite from SC-002.
- Required contracts: Runtime Source of Truth, Baseline Snapshot, Contract Shape, Persistent Evidence, Reintroduction Guard
- Draft objective: Close F-004 inside the same CS-241 golden suite by proving high latitude, Placidus edge, whole sign and topocentric altitude behavior with external reference values or an explicit accepted failure policy.
- Closure intent: full-closure
- Must include: exact input profile, expected house/angle outputs, tolerance, and documented behavior when SwissEph raises or returns unstable Placidus data; no second test harness or follow-up discovery story.
- Validation hints: use the same CS-241 golden suite commands as SC-002 plus targeted scans for `high latitude`, `Placidus`, `whole sign`, and `topocentric`.
- Blockers: stop if user/product cannot decide whether Placidus edge should fail explicitly, fallback by request, or require another house system.

### Exhaustive Files To Modify

- Application files: none expected.
- Governance/test files: same CS-241 golden dataset/test files selected by SC-002; no duplicate harness.
- Before evidence: E-006, E-012, E-013.
- After evidence: edge case outputs are externally referenced or blocked by documented user decision, and F-004 closes in the same CS-241 implementation batch.
- Stop condition: F-004 closes without another discovery-only follow-up candidate.

## Deferred Non-Domain Candidates

- API/frontend display of accuracy metadata is out of this audit unless a future product-data story explicitly requests it.
- Reference-governance threshold ownership remains covered by `_condamad/audits/astro-reference-governance/2026-05-23-1939`, not this precision audit.
