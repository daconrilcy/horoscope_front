<!-- Candidats stories issus de l'audit frontend design-system apres refactors. -->

# Story Candidates - frontend-design-system

## SC-001

- Candidate ID: SC-001
- Source finding: F-002
- Suggested story title: Migrer les clusters CSS frontend restants de valeurs visuelles et typographiques
- Suggested archetype: design-system-token-convergence
- Primary domain: frontend-design-system
- Required contracts:
  - `_condamad/stories/regression-guardrails.md`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/typography-roles.md`
  - `frontend/src/styles/css-fallback-allowlist.md`
  - `frontend/src/styles/legacy-style-surface-registry.md`
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/design-system-allowlist.ts`
- Draft objective: reduce the remaining hardcoded visual and typography ownership debt by migrating one bounded residual CSS cluster to existing or newly documented semantic tokens and typography roles.
- Must include:
  - choose one coherent subset from the exhaustive residual file list below;
  - classify each selected literal as global token, semantic page/component token, typography role, typed runtime constant, or intentionally local final one-off;
  - keep all static styling in `.css` files and avoid new inline styles;
  - update token namespace and typography registries when adding or changing semantic ownership;
  - add or update exact anti-return guards for the selected cluster;
  - preserve `RG-044` through `RG-060`;
  - do not reopen closed clusters unless the story explicitly changes their owner block and updates their existing guard.
- Validation hints:
  - `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`
  - `npm run test`
  - `npm run lint`
  - `npm run build`
  - targeted before/after scan for the selected literals.
- Blockers: choose the next cluster. Do not attempt all 50 residual files in one story unless the user explicitly accepts a broad migration.

## Exhaustive Residual Files To Modify

- `frontend/src/components/AdminGuard.css`
- `frontend/src/components/astro/AstroMoodBackground.css`
- `frontend/src/components/AstroDailyEvents.css`
- `frontend/src/components/AstroFoundationSection.css`
- `frontend/src/components/BestWindowCard.css`
- `frontend/src/components/DayClimateHero.css`
- `frontend/src/components/DomainRankingCard.css`
- `frontend/src/components/ErrorBoundary/ErrorBoundary.css`
- `frontend/src/components/HeroHoroscopeCard.css`
- `frontend/src/components/layout/Header.css`
- `frontend/src/components/layout/Sidebar.css`
- `frontend/src/components/MiniInsightCard.css`
- `frontend/src/components/NatalInterpretation.css`
- `frontend/src/components/prediction/CategoryGrid.css`
- `frontend/src/components/prediction/DayAgenda.css`
- `frontend/src/components/prediction/DayPredictionCard.css`
- `frontend/src/components/prediction/DayTimeline.css`
- `frontend/src/components/prediction/DayTimelineSectionV4.css`
- `frontend/src/components/prediction/KeyPointCard.css`
- `frontend/src/components/prediction/PeriodCard.css`
- `frontend/src/components/prediction/SectionTitle.css`
- `frontend/src/components/prediction/TimelineRail.css`
- `frontend/src/components/prediction/TurningPointsList.css`
- `frontend/src/components/settings/DeleteAccountModal.css`
- `frontend/src/components/ShortcutCard.css`
- `frontend/src/components/SignUpForm.css`
- `frontend/src/components/TurningPointCard.css`
- `frontend/src/index.css`
- `frontend/src/layouts/AdminLayout.css`
- `frontend/src/layouts/PageLayout.css`
- `frontend/src/layouts/WizardLayout.css`
- `frontend/src/pages/admin/AdminAiGenerationsPage.css`
- `frontend/src/pages/admin/AdminContentPage.css`
- `frontend/src/pages/admin/AdminDashboardPage.css`
- `frontend/src/pages/admin/AdminEntitlementsPage.css`
- `frontend/src/pages/admin/AdminLogsPage.css`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/pages/admin/AdminSamplePayloadsAdmin.css`
- `frontend/src/pages/admin/AdminSettingsPage.css`
- `frontend/src/pages/admin/AdminSupportPage.css`
- `frontend/src/pages/admin/AdminUserDetailPage.css`
- `frontend/src/pages/admin/AdminUsersPage.css`
- `frontend/src/pages/admin/PersonasAdmin.css`
- `frontend/src/pages/AstrologerProfilePage.css`
- `frontend/src/pages/billing/billing-return.css`
- `frontend/src/pages/BirthProfilePage.css`
- `frontend/src/pages/ConsultationResultPage.css`
- `frontend/src/pages/DashboardPage.css`
- `frontend/src/pages/NatalChartPage.css`
- `frontend/src/pages/PrivacyPolicyPage.css`

## Governance Files To Inspect Or Modify

- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/premium-theme.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/styles/legacy-style-surface-registry.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/design-system-allowlist.ts`
