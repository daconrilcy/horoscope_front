<!-- Story candidates issus de l'audit frontend design-system. -->

# Story Candidates

## SC-001

- Candidate ID: SC-001
- Source finding: F-002
- Suggested story title: Converger les namespaces compatibility et migration-only de tokens frontend
- Suggested archetype: namespace-convergence
- Primary domain: frontend-design-system
- Required contracts: `RG-044`, `RG-045`, `RG-048`, `RG-049`, `no-legacy-dry-audit-contract.md`
- Draft objective: retire or reduce active compatibility/migration token namespaces by replacing consumers with canonical `--color-*`, `--surface-*`, `--shadow-*`, `--type-*`, `--space-*` tokens or documented semantic extensions.
- Must include:
  - before/after scan for `var(--bg-*`, `var(--cta-*`, `var(--badge-*`, `var(--nav-*`, `var(--line)`, `var(--success)`, `var(--danger)`, `var(--btn-text)`, `var(--purple_base)`, `var(--background-*`, `var(--ni-*`, `var(--result-*`, `var(--timeline-*`, `var(--page-*`, `var(--inner-light)`, `var(--accent-purple*)`;
  - updates to `frontend/src/styles/token-namespace-registry.md`;
  - updates to tests that assert alias names.
- Validation hints:
  - `npm run test -- theme-tokens design-system legacy-style`
  - `npm run test -- AppBgStyles BottomNavPremium MiniInsightCard ShortcutCard predictionBands visual-smoke`
  - `npm run lint`
- Blockers: decide whether `--badge-*`, `--nav-*`, and product-layer namespaces should be fully retired or kept as semantic extensions.
- Files to modify:
  - `frontend/src/App.css`
  - `frontend/src/index.css`
  - `frontend/src/styles/theme.css`
  - `frontend/src/styles/backgrounds.css`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/hooks/useDailyInsights.ts`
  - `frontend/src/utils/predictionI18n.ts`
  - `frontend/src/layouts/AdminLayout.css`
  - `frontend/src/components/AdminGuard.css`
  - `frontend/src/components/AstroDailyEvents.css`
  - `frontend/src/components/BestWindowCard.css`
  - `frontend/src/components/DayClimateHero.css`
  - `frontend/src/components/DomainRankingCard.css`
  - `frontend/src/components/ErrorBoundary/ErrorBoundary.css`
  - `frontend/src/components/HeroHoroscopeCard.css`
  - `frontend/src/components/MiniInsightCard.css`
  - `frontend/src/components/NatalInterpretation.css`
  - `frontend/src/components/ShortcutsSection.tsx`
  - `frontend/src/components/SignUpForm.css`
  - `frontend/src/components/TurningPointCard.css`
  - `frontend/src/components/astro/AstroMoodBackground.css`
  - `frontend/src/components/layout/Header.css`
  - `frontend/src/components/layout/Sidebar.css`
  - `frontend/src/components/prediction/CategoryGrid.css`
  - `frontend/src/components/prediction/DailyAdviceCard.css`
  - `frontend/src/components/prediction/DailyPageHeader.css`
  - `frontend/src/components/prediction/DayAgenda.css`
  - `frontend/src/components/prediction/DayPredictionCard.css`
  - `frontend/src/components/prediction/DayStateBadge.css`
  - `frontend/src/components/prediction/DayTimelineSectionV4.css`
  - `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
  - `frontend/src/components/prediction/PeriodCard.css`
  - `frontend/src/components/prediction/SectionTitle.css`
  - `frontend/src/components/ui/Badge/Badge.tsx`
  - `frontend/src/pages/ConsultationResultPage.css`
  - `frontend/src/pages/DailyHoroscopePage.css`
  - `frontend/src/pages/HelpPage.css`
  - `frontend/src/pages/admin/AdminAiGenerationsPage.css`
  - `frontend/src/pages/admin/AdminContentPage.css`
  - `frontend/src/pages/admin/AdminEntitlementsPage.css`
  - `frontend/src/pages/admin/AdminLogsPage.css`
  - `frontend/src/pages/admin/AdminSettingsPage.css`
  - `frontend/src/pages/admin/AdminUserDetailPage.css`
  - `frontend/src/pages/admin/PersonasAdmin.css`
  - `frontend/src/pages/landing/sections/TestimonialsSection.css`
  - `frontend/src/tests/BottomNavPremium.test.tsx`
  - `frontend/src/tests/MiniInsightCard.test.tsx`
  - `frontend/src/tests/ShortcutCard.test.tsx`
  - `frontend/src/tests/predictionBands.test.ts`
  - `frontend/src/tests/visual-smoke.test.tsx`

## SC-002

- Candidate ID: SC-002
- Source finding: F-003
- Suggested story title: Migrer les prochains clusters de valeurs visuelles hardcodees frontend
- Suggested archetype: duplicate-rule-removal
- Primary domain: frontend-design-system
- Required contracts: `RG-045`, `RG-046`, `RG-050`, `no-legacy-dry-audit-contract.md`
- Draft objective: reduce hardcoded CSS values by priority clusters while preserving product visuals.
- Must include:
  - `hardcoded-values-before.md` and `hardcoded-values-after.md`;
  - no broad refactor across unrelated product surfaces in one story;
  - token registry update only when a token is durable.
- Validation hints:
  - `npm run test -- design-system visual-smoke`
  - focused page/component tests for each touched cluster
  - `npm run lint`
- Blockers: choose the first cluster. Recommended order: admin prompts/settings, then HelpPage, then natal/profile, then landing.
- Files to modify:
  - exhaustive candidate files are listed in `01-evidence-log.md` under `E-011 Hardcoded-Value File Inventory`.

## SC-003

- Candidate ID: SC-003
- Source finding: F-004
- Suggested story title: Renommer ou formaliser la surface admin prompts legacy
- Suggested archetype: legacy-facade-removal
- Primary domain: frontend-design-system
- Required contracts: `RG-049`, `no-legacy-dry-audit-contract.md`
- Draft objective: resolve the remaining admin prompts `legacy` terminology after selector migration.
- Must include:
  - product decision: rename to archive/history or explicitly keep `legacy`;
  - before/after scan of `AdminPromptsPage.tsx`, `adminPromptsLegacy.ts`, `admin.ts`, and `AdminPromptsPage.test.tsx`;
  - update tests and ARIA labels in the same change.
- Validation hints:
  - `npm run test -- AdminPromptsPage AdminPromptsRouting legacy-style`
  - `npm run lint`
- Blockers: product vocabulary decision is required before implementation.
- Files to modify:
  - `frontend/src/pages/admin/AdminPromptsPage.tsx`
  - `frontend/src/i18n/adminPromptsLegacy.ts`
  - `frontend/src/i18n/admin.ts`
  - `frontend/src/tests/AdminPromptsPage.test.tsx`
