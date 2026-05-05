# Story Candidates - frontend-design-system

## SC-001 - Aligner le registre markdown et l'allowlist executable des fallbacks CSS

- Candidate ID: SC-001
- Source finding: F-002
- Suggested story title: Rendre `css-fallback-allowlist.md` exact et verifie contre l'allowlist executable
- Suggested archetype: design-system-contract-parity
- Primary domain: frontend-design-system
- Required contracts: `RG-048`, `RG-050`, CSS fallback allowlist, design-system guard suite
- Draft objective: Eliminate the drift between the documented fallback registry and `CSS_FALLBACK_EXCEPTIONS` so there is one exact source of truth with statuses, reasons, and exit conditions for every remaining fallback.
- Must include: complete 165-entry parity or a generated single-source contract, a guard that fails when markdown and executable entries differ, and no unclassified fallback growth.
- Validation hints: `npm run test -- css-fallback design-system`; targeted scan `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," frontend/src -g "*.css"`; `npm run lint`.
- Blockers: Choose whether markdown generates TypeScript allowlist, TypeScript generates markdown, or a shared data file generates both.
- Files to modify:
  - `frontend/src/styles/css-fallback-allowlist.md`
  - `frontend/src/tests/design-system-allowlist.ts`
  - `frontend/src/tests/css-fallback-policy.test.ts`
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/design-system-policy.ts`

## SC-002 - Supprimer le prochain lot de styles inline statiques

- Candidate ID: SC-002
- Source finding: F-003
- Suggested story title: Convertir les styles inline statiques restants vers CSS
- Suggested archetype: inline-style-debt-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-047`, inline-style allowlist, CSS-only style rule
- Draft objective: Reduce the 30 remaining inline style attributes by extracting static styling into CSS files while preserving dynamic custom properties, runtime geometry, and explicit style-prop bridges.
- Must include: classification of each touched inline style as static or dynamic, CSS extraction for static entries, allowlist reduction, no new `style` attributes, and component/page tests for touched surfaces.
- Validation hints: `npm run test -- inline-style design-system`; `rg -n "style=\\{" frontend/src -g "*.tsx"`; `npm run lint`.
- Blockers: None identified.
- Files to modify:
  - `frontend/src/layouts/TwoColumnLayout.tsx`
  - `frontend/src/components/DomainRankingCard.tsx`
  - `frontend/src/components/NatalInterpretation.tsx`
  - `frontend/src/components/TurningPointCard.tsx`
  - `frontend/src/components/prediction/CategoryGrid.tsx`
  - `frontend/src/components/prediction/DayPredictionCard.tsx`
  - `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
  - `frontend/src/components/prediction/PeriodCard.tsx`
  - `frontend/src/components/prediction/TimelineRail.tsx`
  - `frontend/src/components/ui/Badge/Badge.tsx`
  - `frontend/src/components/ui/Form/Form.tsx`
  - `frontend/src/components/ui/Skeleton/Skeleton.tsx`
  - `frontend/src/features/chat/components/AstrologerPickerModal.tsx`
  - `frontend/src/features/chat/components/ChatLayout.tsx`
  - `frontend/src/pages/AstrologerProfilePage.tsx`
  - `frontend/src/pages/NotFoundPage.tsx`
  - `frontend/src/pages/settings/AccountSettings.tsx`
  - related CSS files for the touched components/pages

## SC-003 - Reduire les fallbacks CSS allowlistes

- Candidate ID: SC-003
- Source finding: F-004
- Suggested story title: Reduire les fallbacks `var(--token, value)` dans les surfaces partagees
- Suggested archetype: css-fallback-debt-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-048`, CSS fallback allowlist, token namespace registry
- Draft objective: Replace compatibility or migration-only fallback literals with required canonical tokens or documented token imports, starting with shared UI and layout CSS before page-level surfaces.
- Must include: before/after fallback count, updated exact fallback contract, no unclassified fallback, and targeted UI/page tests for changed surfaces.
- Validation hints: `npm run test -- css-fallback design-system Button Badge EmptyState ErrorState LockedSection Modal Select UpgradeCTA`; targeted `rg` fallback count; `npm run lint`.
- Blockers: Some fallbacks may require deciding whether isolated component tests must import global token CSS or whether the component owns a semantic extension token.
- Files to modify:
  - `frontend/src/App.css`
  - `frontend/src/layouts/WizardLayout.css`
  - `frontend/src/layouts/PageLayout.css`
  - `frontend/src/layouts/TwoColumnLayout.css`
  - `frontend/src/features/chat/components/ChatQuotaBanner.css`
  - `frontend/src/features/chat/components/ChatWindow.css`
  - `frontend/src/styles/utilities.css`
  - `frontend/src/components/NatalInterpretation.css`
  - `frontend/src/components/SignUpForm.css`
  - `frontend/src/styles/glass.css`
  - `frontend/src/components/ui/ErrorState/ErrorState.css`
  - `frontend/src/components/ui/Badge/Badge.css`
  - `frontend/src/components/prediction/DayPredictionCard.css`
  - `frontend/src/components/layout/Sidebar.css`
  - `frontend/src/pages/BirthProfilePage.css`
  - `frontend/src/components/ui/EmptyState/EmptyState.css`
  - `frontend/src/components/layout/Header.css`
  - `frontend/src/components/prediction/CategoryGrid.css`
  - `frontend/src/components/prediction/PeriodCard.css`
  - `frontend/src/components/prediction/KeyPointCard.css`
  - `frontend/src/pages/settings/Settings.css`
  - `frontend/src/pages/admin/AdminEntitlementsPage.css`
  - `frontend/src/pages/NatalChartPage.css`
  - `frontend/src/components/ui/Select/Select.css`
  - `frontend/src/pages/HelpPage.css`
  - `frontend/src/pages/admin/AdminPromptsPage.css`
  - `frontend/src/components/ui/Modal/Modal.css`
  - `frontend/src/components/ui/LockedSection/LockedSection.css`
  - `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.css`
  - `frontend/src/pages/landing/sections/TestimonialsSection.css`

## SC-004 - Reduire les valeurs visuelles et typographiques hardcodees restantes

- Candidate ID: SC-004
- Source finding: F-005
- Suggested story title: Poursuivre la migration des valeurs visuelles hardcodees par clusters
- Suggested archetype: hardcoded-design-value-reduction
- Primary domain: frontend-design-system
- Required contracts: `RG-044`, `RG-045`, `RG-046`, `RG-050`, token namespace registry, typography roles
- Draft objective: Continue the design-token migration by reducing repeated color, spacing, radius, shadow, and typography literals in the highest-impact CSS clusters that are not yet covered by migrated batches.
- Must include: before/after static counts, explicit migrated file list, no expansion of unclassified token namespaces, and registry updates only when a permanent semantic token is introduced.
- Validation hints: `npm run test -- design-system theme-tokens`; targeted `rg` counts for migrated files; `npm run lint`; visual smoke for touched page-level surfaces.
- Blockers: Product/design decision may be needed when near-equivalent literal values should converge to one semantic token.
- Files to modify: see the exhaustive `F-005 - Hardcoded Visual / Typography Files Outside Token Sources` list in `00-audit-report.md`.
