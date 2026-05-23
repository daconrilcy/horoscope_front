# Story Candidates - Astro Product Data Needs

## SC-001 CS-255 Define Expert Natal Chart Public Data Contract

- Source finding: F-001
- Suggested story title: CS-255 - Define expert natal chart public data contract
- Suggested archetype: product-projection-contract
- Primary domain: astro-product-data-needs / public natal chart projection
- Required contracts: Runtime Source of Truth, Contract Shape, Ownership Routing, Reintroduction Guard, No Legacy
- Draft objective: Define a stable expert public payload that selects dignities, sect, advanced conditions, traditional conditions, dominance and interpretation adapter fields without exposing `chart_objects`, raw `advanced_planetary_conditions` or `interpretation_input`.
- Closure intent: full-closure
- Must include: exact expert field list, explicit exclusions for raw runtime owners, translation requirements for technical labels, score display policy, no-time/degraded behavior, before/after public payload evidence, and tests proving no raw runtime names enter frontend/public API.
- Validation hints: run targeted unit tests for `json_builder.py`, `test_chart_result_service.py`, architecture guards `test_chart_runtime_surface_guardrails.py` and scans for `chart_objects`, `advanced_planetary_conditions`, `interpretation_input` in frontend/API contracts.
- Blockers: stop if product cannot decide which expert score breakdowns are displayable; do not implement fallback raw payload exposure.

### Exhaustive Files To Modify

- Application files: exact selection rule, not a fixed list yet: public projection owner `backend/app/services/chart/json_builder.py`, public API/client contracts for natal chart, and `frontend/src/features/natal-chart/NatalExpertPanel.tsx` only if the story changes display fields.
- Governance/test files: targeted tests selected by the story writer for public projection and no-raw-runtime guards.
- Deferred non-domain files: none for CS-255 once expert contract is selected.
- Required before/after evidence: payload shape snapshot, frontend type diff, negative raw runtime scan, targeted tests.
- Stop condition: F-001 closes when expert screen fields are all named by the public contract and no internal raw runtime field is exposed.

## SC-002 CS-256 Define Beginner Natal Chart Summary Projection

- Source finding: F-002
- Suggested story title: CS-256 - Define beginner natal chart summary projection
- Suggested archetype: product-projection-contract
- Primary domain: astro-product-data-needs / beginner public projection
- Required contracts: Runtime Source of Truth, Contract Shape, Ownership Routing, Translation, Reintroduction Guard, No Legacy
- Draft objective: Define a compact beginner summary projection for public-user screens that separates translated facts, qualitative highlights, evidence links and complexity masking from LLM final interpretation.
- Closure intent: full-closure
- Must include: target public-user fields, translated labels, empty/degraded states, score-to-band or no-score policy, explicit masking for degree/orb/runtime details, no duplication with AI interpretation payload, and public client consumption plan.
- Validation hints: run translation resolver tests, natal chart public projection tests, scans for duplicated beginner logic in React components, and negative scans for raw expert/runtime terms in beginner UI.
- Blockers: stop if product requires LLM-generated summary as source of truth instead of deterministic projection; that decision changes ownership.

### Exhaustive Files To Modify

- Application files: exact selection rule: public projection owner, frontend API natal chart contract, and beginner/public-user display components in `NatalChartPage` or a dedicated child component selected by implementation.
- Governance/test files: targeted projection tests, translation tests and frontend component tests if UI consumption changes.
- Deferred non-domain files: AI prompt copy remains outside CS-256 unless product explicitly selects LLM as source of truth.
- Required before/after evidence: beginner payload contract, translated label checks, no raw score/runtime scan, targeted tests.
- Stop condition: F-002 closes when beginner/public-user needs are served by one named projection with masking rules and no duplicate LLM/UI business logic.

## SC-003 CS-257 Add Fixed-Star Section Projection For Frontend Display

- Source finding: F-003
- Suggested story title: CS-257 - Add fixed-star section projection for frontend display
- Suggested archetype: product-projection-contract
- Primary domain: astro-product-data-needs / fixed-star public display
- Required contracts: Runtime Source of Truth, Contract Shape, Ownership Routing, Translation, Reintroduction Guard, No Legacy
- Draft objective: Add or define a fixed-star display projection that maps runtime conjunctions to frontend-safe rows with star display name, target object, orb, relevance/display rule and translated labels.
- Closure intent: full-closure
- Must include: exact source selection from fixed-star runtime, public field allowlist, empty state, no raw catalog dump, translation requirements, score/relevance policy and tests proving frontend does not consume internal conjunction objects.
- Validation hints: run fixed-star runtime tests selected by the story writer, public projection tests, `test_chart_runtime_surface_guardrails.py`, and scans for raw `fixed_star_conjunctions` in frontend contracts.
- Blockers: stop if product cannot decide whether fixed-star relevance is a score, rank or simple threshold.

### Exhaustive Files To Modify

- Application files: exact selection rule: fixed-star projection owner under public chart projection, frontend API natal chart contract, and one frontend section/component if display is included in implementation.
- Governance/test files: public projection tests and raw-runtime negative scans.
- Deferred non-domain files: fixed-star catalog seed changes and new calculation rules are outside CS-257 unless separately approved.
- Required before/after evidence: fixed-star projection fixture, negative raw runtime scan, frontend/API type evidence, targeted tests.
- Stop condition: F-003 closes when fixed-star display data exists as a named public projection and no frontend consumer needs internal fixed-star runtime fields.

## Needs-User-Decision Candidate

- Related finding: F-004
- Decision needed: choose whether `debug astrologique` and `interface astrologue` are protected operator/admin surfaces, expert-user surfaces, astrologer-client collaboration surfaces, or out of product scope.
- No implementation story should be emitted until audience, authorization, retention and masking rules are explicit.

## Guardrail Candidate

- Related finding: F-005
- Candidate invariant for future story-writer handling: `cs-xxx-audit-*` product-data audit stories must remain documentation-only and must verify the story's forbidden application/test/migration/seeder surfaces have no worktree delta unless the user explicitly authorizes implementation.
