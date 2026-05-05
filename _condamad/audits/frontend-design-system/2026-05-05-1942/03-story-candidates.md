# Story Candidates - frontend-design-system

## SC-001

- Candidate ID: SC-001
- Source finding: F-002
- Suggested story title: Realigner le guard visual-smoke sur la typographie tokenisee
- Suggested archetype: design-system-guard-contract-realignment
- Primary domain: frontend-design-system
- Required contracts: `RG-046`, `RG-050`, `frontend/src/styles/design-tokens.css`, `frontend/src/tests/visual-smoke.test.tsx`
- Draft objective: make the visual smoke guard assert the canonical tokenized typography contract without reintroducing hardcoded literals.
- Must include:
  - Replace assertions for `font-size: 18px`, `font-size: 12px`, and `font-weight: 500` with token-aware assertions or deterministic token resolution.
  - Keep the existing opacity checks intact.
  - Prove `npm run test -- visual-smoke` and `npm run test` pass.
- Validation hints:
  - `npm run test -- visual-smoke`
  - `npm run test`
  - `npm run test -- design-system theme-tokens`
- Blockers: none.

## SC-002

- Candidate ID: SC-002
- Source finding: F-003
- Suggested story title: Reduire le lot courant de fallbacks CSS design-system
- Suggested archetype: css-fallback-debt-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-048`, `RG-050`, `frontend/src/styles/css-fallback-allowlist.md`, `frontend/src/tests/design-system-allowlist.ts`
- Draft objective: remove a bounded subset of the 68 classified CSS fallbacks while keeping the markdown registry and executable allowlist exact.
- Must include:
  - Select one bounded surface batch from the F-003 file list.
  - Remove only fallbacks whose canonical token is guaranteed.
  - Update both fallback registries and record before/after counts.
- Validation hints:
  - `npm run test -- css-fallback design-system`
  - `rg -n "var\\(--[^,\\)]+,\\s*[^\\)]+\\)" src -g "*.css"`
- Blockers: choose the first surface batch if product priority matters.

## SC-003

- Candidate ID: SC-003
- Source finding: F-004
- Suggested story title: Reduire les exceptions de styles inline frontend
- Suggested archetype: inline-style-debt-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-047`, `RG-050`, `frontend/src/tests/inline-style-allowlist.ts`, `frontend/src/tests/design-system-allowlist.ts`
- Draft objective: move removable inline styles into CSS or custom properties and keep only dynamic runtime bridges.
- Must include:
  - Classify each current inline entry as dynamic bridge, removable static style, or component style-prop pass-through.
  - Move removable entries to CSS files, not inline styles.
  - Update allowlists only after code changes.
- Validation hints:
  - `npm run test -- inline-style design-system`
  - `rg -n "style=\\{" src -g "*.tsx"`
- Blockers: none.

## SC-004

- Candidate ID: SC-004
- Source finding: F-005
- Suggested story title: Migrer un lot prioritaire de valeurs visuelles hardcodees
- Suggested archetype: hardcoded-design-value-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-045`, `RG-046`, `RG-050`, `frontend/src/styles/token-namespace-registry.md`, `frontend/src/styles/typography-roles.md`
- Draft objective: reduce one coherent product-surface batch from the 107-file hardcoded visual list without broad refactor.
- Must include:
  - Pick a bounded cluster, such as prediction components, shared UI primitives, or admin pages.
  - Use existing variables and roles before creating new tokens.
  - Record before/after hit counts and any new semantic token ownership.
- Validation hints:
  - `npm run test -- design-system theme-tokens`
  - `npm run lint`
  - targeted visual/component tests for the chosen surface
- Blockers: choose the product surface to prioritize.

## SC-005

- Candidate ID: SC-005
- Source finding: F-006
- Suggested story title: Retirer les surfaces CSS legacy et aliases compatibility restants
- Suggested archetype: legacy-style-surface-extinction
- Primary domain: frontend-design-system
- Required contracts: `RG-044`, `RG-049`, `RG-050`, `frontend/src/styles/legacy-style-surface-registry.md`, `frontend/src/styles/token-namespace-registry.md`
- Draft objective: retire or narrow classified legacy selectors and compatibility token aliases while keeping No Legacy governance exact.
- Must include:
  - Classify the current legacy selector families and compatibility aliases by remove-now, migrate, or needs-user-decision.
  - Remove only entries with a canonical replacement.
  - Update registries and tests in the same change.
- Validation hints:
  - `npm run test -- legacy-style theme-tokens design-system`
  - targeted scans for `legacy`, `--text-`, `--glass`, and `--primary`
- Blockers: product decision may be needed for aliases that still support broad legacy surfaces.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - token namespaces must remain classified.
  - `RG-045` - migrated hardcoded values must not return unclassified.
  - `RG-046` - semantic typography roles are canonical for migrated surfaces.
  - `RG-047` - static inline styles are forbidden except exact allowlisted dynamic cases.
  - `RG-048` - CSS fallbacks must remain classified and exact.
  - `RG-049` - legacy style surfaces must stay owned and classified.
  - `RG-050` - anti-drift tests and allowlists must remain executable.
- Non-applicable invariants:
  - Backend-only guardrails are outside this frontend-design-system audit.
- Required regression evidence:
  - targeted npm tests named in each candidate.
  - static scans listed in each candidate.
  - full `npm run test` after `SC-001`.
- Allowed differences:
  - Fallback and inline allowlist counts may decrease.
  - Guard assertions may change from literals to canonical tokens.
