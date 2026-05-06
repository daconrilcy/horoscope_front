# Story Candidates - frontend-design-system

## SC-001

- Candidate ID: SC-001
- Source finding: F-002
- Suggested story title: Reduire les derniers fallbacks CSS et statuer les tokens premium manquants
- Suggested archetype: css-fallback-debt-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-048`, `RG-050`, `frontend/src/styles/css-fallback-allowlist.md`, `frontend/src/tests/design-system-allowlist.ts`
- Draft objective: remove guaranteed CSS fallback literals from the 10-entry surface and resolve whether missing premium tokens become canonical tokens or are replaced by global tokens.
- Must include:
  - Capture before/after fallback counts.
  - Remove simple guaranteed fallbacks first: `--usage-progress` dynamic entries should remain unless the runtime bridge changes.
  - Decide `--premium-text-muted` and `--premium-glass-border-soft` for `NatalChartPage.css` and `NatalInterpretation.css`.
  - Update markdown and executable fallback registries in the same change.
  - Do not introduce new local literal fallbacks.
- Validation hints:
  - `cd frontend && npm run test -- css-fallback design-system theme-tokens`
  - `cd frontend && npm run lint`
  - `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," frontend/src -g "*.css"`
- Blockers: User/product/theme decision required for `--premium-text-muted` and `--premium-glass-border-soft`.
- Exhaustive files to modify:
  - `frontend/src/App.css`
  - `frontend/src/components/NatalInterpretation.css`
  - `frontend/src/components/SignUpForm.css`
  - `frontend/src/features/chat/components/ChatWindow.css`
  - `frontend/src/pages/admin/AdminEntitlementsPage.css`
  - `frontend/src/pages/landing/sections/TestimonialsSection.css`
  - `frontend/src/pages/NatalChartPage.css`
  - `frontend/src/pages/settings/Settings.css`
  - `frontend/src/styles/premium-theme.css`
  - `frontend/src/styles/css-fallback-allowlist.md`
  - `frontend/src/tests/design-system-allowlist.ts`
  - `frontend/src/tests/css-fallback-policy.test.ts`

## SC-002

- Candidate ID: SC-002
- Source finding: F-003
- Suggested story title: Reduire les exceptions de styles inline encore convertibles
- Suggested archetype: inline-style-debt-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-047`, `RG-050`, `frontend/src/tests/inline-style-allowlist.ts`, `frontend/src/tests/design-system-allowlist.ts`
- Draft objective: convert remaining inline style entries that can be represented by CSS custom properties, classes, or component variants without losing runtime behavior.
- Must include:
  - Classify every current inline style as runtime geometry, CSS custom-property bridge, color bridge, or style-prop pass-through.
  - Preserve `Skeleton` style-prop pass-through unless the public component API changes.
  - Prefer classes or typed CSS variable bridges for `Badge` color and timeline geometry when feasible.
  - Update allowlists only after code changes.
- Validation hints:
  - `cd frontend && npm run test -- inline-style design-system`
  - `cd frontend && npm run lint`
  - `rg -n "style=\\{" frontend/src -g "*.tsx"`
- Blockers: `Skeleton` style-prop behavior may be an intentional component API contract.
- Exhaustive files to modify:
  - `frontend/src/layouts/TwoColumnLayout.tsx`
  - `frontend/src/layouts/TwoColumnLayout.css`
  - `frontend/src/components/DomainRankingCard.tsx`
  - `frontend/src/components/DomainRankingCard.css`
  - `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
  - `frontend/src/components/prediction/DayTimelineSectionV4.css`
  - `frontend/src/components/prediction/TimelineRail.tsx`
  - `frontend/src/components/prediction/TimelineRail.css`
  - `frontend/src/components/ui/Badge/Badge.tsx`
  - `frontend/src/components/ui/Badge/Badge.css`
  - `frontend/src/components/ui/Skeleton/Skeleton.tsx`
  - `frontend/src/components/ui/Skeleton/Skeleton.css`
  - `frontend/src/tests/inline-style-allowlist.ts`
  - `frontend/src/tests/design-system-allowlist.ts`
  - `frontend/src/tests/inline-style-policy.test.ts`

## SC-003

- Candidate ID: SC-003
- Source finding: F-004
- Suggested story title: Migrer un cluster coherent de valeurs visuelles hardcodees
- Suggested archetype: hardcoded-design-value-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-044`, `RG-045`, `RG-046`, `RG-050`, `frontend/src/styles/token-namespace-registry.md`, `frontend/src/styles/typography-roles.md`
- Draft objective: reduce one coherent product-surface batch from the 110-file hardcoded visual list without broad refactor.
- Must include:
  - Pick one bounded cluster: admin prompts, natal interpretation/chart, prediction cards, shared UI primitives, or chat shell.
  - Use existing tokens, typography roles, and utility classes before creating new tokens.
  - Record before/after counts for touched files.
  - Update token namespace or typography registries only when a durable semantic token or role is introduced.
- Validation hints:
  - `cd frontend && npm run test -- design-system theme-tokens visual-smoke`
  - `cd frontend && npm run lint`
  - Targeted component/page tests for the chosen surface.
- Blockers: Product/design decision may be needed when near-equivalent literal values should converge to one semantic token.
- Exhaustive files to modify:
  - See the exhaustive `F-004` file list in `00-audit-report.md`.
  - Always include `frontend/src/styles/token-namespace-registry.md` if new token ownership is introduced.
  - Always include `frontend/src/styles/typography-roles.md` if new typography roles or exceptions are introduced.
  - Always include `frontend/src/tests/design-system-allowlist.ts` if guard exceptions change.

## SC-004

- Candidate ID: SC-004
- Source finding: F-005
- Suggested story title: Retirer les selectors legacy admin prompts et aliases compatibility restants
- Suggested archetype: legacy-style-surface-extinction
- Primary domain: frontend-design-system
- Required contracts: `RG-044`, `RG-049`, `RG-050`, `frontend/src/styles/legacy-style-surface-registry.md`, `frontend/src/styles/token-namespace-registry.md`
- Draft objective: retire or narrow classified admin prompt legacy selectors and compatibility token aliases while keeping No Legacy governance exact.
- Must include:
  - Separate admin prompt route markup/style migration from global token alias retirement.
  - Remove `.admin-prompts-legacy*` and `.admin-prompts-modal--legacy-rollback` only when canonical route-specific markup exists.
  - Retire `--text-*`, `--glass*`, and `--primary*` aliases only after consumers use canonical `--color-*` tokens.
  - Update both registries and keep legacy-style tests exact.
- Validation hints:
  - `cd frontend && npm run test -- legacy-style theme-tokens design-system AdminPromptsPage`
  - `cd frontend && npm run lint`
  - `rg -n "legacy|--text-|--glass|--primary" frontend/src/styles frontend/src/App.css frontend/src/pages/admin/AdminPromptsPage.css`
- Blockers: `admin-prompts-legacy` is marked external-active and needs a product/user decision before route-specific migration.
- Exhaustive files to modify:
  - `frontend/src/pages/admin/AdminPromptsPage.tsx`
  - `frontend/src/pages/admin/AdminPromptsPage.css`
  - `frontend/src/styles/theme.css`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/legacy-style-surface-registry.md`
  - `frontend/src/tests/legacy-style-policy.test.ts`
  - `frontend/src/tests/theme-tokens.test.ts`
  - `frontend/src/tests/design-system-guards.test.ts`

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
  - Targeted npm tests named in each candidate.
  - Static scans listed in each candidate.
  - Full `npm run test` after stories touching shared tests or registries.
- Allowed differences:
  - Fallback and inline allowlist counts may decrease.
  - Legacy selector and compatibility alias registries may shrink.
  - Hardcoded-value scan counts may decrease or move to canonical token sources.
