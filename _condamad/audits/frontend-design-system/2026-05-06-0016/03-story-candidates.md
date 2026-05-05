# Story Candidates - frontend-design-system

## SC-001

- Candidate ID: SC-001
- Source finding: F-002
- Suggested story title: Reduire les fallbacks CSS restants apres refactor
- Suggested archetype: css-fallback-debt-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-048`, `RG-050`, `frontend/src/styles/css-fallback-allowlist.md`, `frontend/src/tests/design-system-allowlist.ts`
- Draft objective: remove a bounded batch from the 24 classified CSS fallback exceptions while keeping markdown and executable registries exact.
- Must include:
  - Capture before/after fallback counts.
  - Start with `PeriodCard.css`, `NatalInterpretation.css`, `KeyPointCard.css`, and `NatalChartPage.css`.
  - Replace only fallbacks whose canonical token is guaranteed in app and test setup.
  - Update `frontend/src/styles/css-fallback-allowlist.md` and `frontend/src/tests/design-system-allowlist.ts` in the same change.
- Validation hints:
  - `npm run test -- css-fallback design-system theme-tokens`
  - `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," src -g "*.css"`
  - targeted component/page tests for touched surfaces
- Blockers: `NatalChartPage.css` still has `needs-user-decision` premium aliases absent from `premium-theme.css`; decide whether to declare canonical premium tokens or replace with existing global tokens.

## SC-002

- Candidate ID: SC-002
- Source finding: F-003
- Suggested story title: Reduire les styles inline dynamiques convertibles
- Suggested archetype: inline-style-debt-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-047`, `RG-050`, `frontend/src/tests/inline-style-allowlist.ts`, `frontend/src/tests/design-system-allowlist.ts`
- Draft objective: convert remaining inline style entries that can be represented by CSS custom properties or classes without losing runtime behavior.
- Must include:
  - Classify each remaining inline style as runtime geometry, CSS custom-property bridge, color bridge, or style-prop pass-through.
  - Move removable visual declarations out of TSX and into the appropriate CSS files.
  - Update allowlists only after code changes.
  - Preserve `Skeleton` style-prop behavior unless a component API decision explicitly changes it.
- Validation hints:
  - `npm run test -- inline-style design-system`
  - `rg -n "style=\\{" src -g "*.tsx"`
  - component tests for touched surfaces
- Blockers: `Skeleton` style-prop pass-through and progress geometry may be intentional public component contracts.

## SC-003

- Candidate ID: SC-003
- Source finding: F-004
- Suggested story title: Migrer un cluster coherent de valeurs visuelles hardcodees
- Suggested archetype: hardcoded-design-value-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-044`, `RG-045`, `RG-046`, `RG-050`, `frontend/src/styles/token-namespace-registry.md`, `frontend/src/styles/typography-roles.md`
- Draft objective: reduce one coherent product-surface batch from the 116-file hardcoded visual list without broad refactor.
- Must include:
  - Choose one bounded cluster, preferably prediction cards, natal interpretation, chat shell, or admin prompt surfaces.
  - Use existing tokens, typography roles, and utility classes before creating new tokens.
  - Record before/after counts for the selected files.
  - Update token namespace or typography registries only when a durable semantic token or role is introduced.
- Validation hints:
  - `npm run test -- design-system theme-tokens visual-smoke`
  - `npm run lint`
  - targeted visual/component tests for the chosen surface
- Blockers: design/product decision may be needed when near-equivalent literal values should converge to one semantic token.

## SC-004

- Candidate ID: SC-004
- Source finding: F-005
- Suggested story title: Retirer les selectors legacy et aliases compatibility restants
- Suggested archetype: legacy-style-surface-extinction
- Primary domain: frontend-design-system
- Required contracts: `RG-044`, `RG-049`, `RG-050`, `frontend/src/styles/legacy-style-surface-registry.md`, `frontend/src/styles/token-namespace-registry.md`
- Draft objective: retire or narrow classified legacy selectors and compatibility token aliases while keeping No Legacy governance exact.
- Must include:
  - Classify each remaining legacy selector family as remove-now, migrate, or needs-user-decision.
  - Move chat shell styles from `App.css` to canonical chat component CSS where possible.
  - Retire token aliases only after consumers use canonical `--color-*` tokens.
  - Update both registries and keep legacy-style tests exact.
- Validation hints:
  - `npm run test -- legacy-style theme-tokens design-system`
  - `rg -n "legacy|--text-|--glass|--primary" src/styles src/App.css src/pages/admin/AdminPromptsPage.css`
- Blockers: `admin-prompts-legacy` is marked external-active and needs a product/user decision before route-specific migration.

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
  - full `npm run test` after stories touching shared tests or registries.
- Allowed differences:
  - fallback and inline allowlist counts may decrease.
  - legacy selector and compatibility alias registries may shrink.
  - hardcoded-value scan counts may decrease or move to canonical token sources.
