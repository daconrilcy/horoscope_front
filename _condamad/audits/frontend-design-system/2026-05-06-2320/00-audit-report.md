<!-- Rapport d'audit frontend design-system apres les refactors jusqu'a CS-081. -->

# Audit Report - frontend-design-system

## Scope

- Target domain: `frontend-design-system`.
- Comparative context: audits `_condamad/audits/frontend-design-system/2026-05-04-2238` through `_condamad/audits/frontend-design-system/2026-05-06-2139`.
- Refactors now considered implemented: the stories planned in those audits through CS-081.
- Archetype used: `legacy-surface-audit` plus `test-guard-coverage-audit`, adapted to the bounded frontend design-system surface.
- Mode: read-only for application code; audit artifacts only under `_condamad/audits/frontend-design-system/2026-05-06-2320/`.

## Expected Responsibility

The frontend design-system domain owns CSS token namespaces, typography roles, static style governance, page-scoped style boundaries, legacy style surfaces and executable anti-drift guards. It must not keep unclassified aliases, migration-only namespaces, static inline style decisions, CSS fallbacks, cross-page token dependencies or compatibility vocabulary without an explicit owner and exit condition.

## Applicable Guardrails

- `RG-044` - CSS token namespace ownership.
- `RG-045` - hardcoded frontend visual values.
- `RG-046` - frontend typography roles.
- `RG-047` - static inline styles.
- `RG-048` - CSS variable fallbacks.
- `RG-049` - frontend legacy style surfaces.
- `RG-050` - design-system anti-drift guards.
- `RG-051` - page-scoped token isolation.
- `RG-052` - migration-only namespace convergence.
- `RG-053` and `RG-057` - frontend runtime compatibility removal.
- `RG-054` - legacy admin redirects.
- `RG-055` - prediction premium visual literals.
- `RG-056` - shared UI visual literals.
- `RG-058` - chat cluster visual literals.

## Executive Result

The refactors remain stable. Evidence shows:

- focused frontend design-system guard suite passes: 6 files, 134 tests;
- full frontend Vitest suite passes: 115 files, 1252 tests passed, 8 skipped;
- lint passes;
- production build passes;
- no `HelpPage.css` consumption of `--settings-*`;
- no active `/admin/pricing`, `/admin/monitoring` or `/admin/personas` route/redirect/facade source hit;
- CSS fallbacks are limited to two dynamic `--usage-progress` exceptions;
- TSX inline styles are limited to five exact dynamic/style-prop exceptions.

Two follow-up risks remain:

- 66 non-test application files still contain hardcoded visual or typography literals outside `frontend/src/styles/**`;
- one CSS comment in `AdminPromptsPage.css` still contains No Legacy vocabulary while the current guard focuses on selectors and runtime vocabulary.

## Findings Summary

| ID | Severity | Confidence | Category | Story candidate |
|---|---|---|---|---|
| F-001 | Info | High | missing-guard | no |
| F-002 | Medium | High | duplicate-responsibility | yes |
| F-003 | Medium | High | missing-guard | yes |
| F-004 | Low | High | observability-gap | no |

## Key Findings

### F-001 - Frontend design-system guardrails are active

The guard suite, full Vitest, lint and build are executable and green. Recent refactors through CS-081 did not reopen the known page-scoped token, runtime compatibility, admin redirect, inline-style or CSS fallback surfaces.

### F-002 - Hardcoded visual and typography literals remain broad

The broad static scan still finds 66 non-test application files with literal colors, shadows, radii, typography values or related style literals outside `frontend/src/styles/**`. This is not a regression from the migrated clusters because those clusters are guarded, but it remains duplicate responsibility versus token and typography ownership.

### F-003 - CSS No Legacy vocabulary is not fully guarded

`frontend/src/pages/admin/AdminPromptsPage.css:1792` still contains `Route legacy : investigation hors catalogue`. The existing legacy-style guard covers selectors and aliases, but it does not reject CSS comment vocabulary. This leaves a small but real No Legacy guard gap.

### F-004 - Build still emits a chunk-size warning

The production build passes, but Vite reports the main JS chunk at 1,370.37 kB after minification. This is a frontend performance concern, not a design-system correctness blocker.

## Exhaustive Files To Modify

### F-002: Hardcoded Visual And Typography Literals

The following 66 files are the exhaustive candidate files returned by the non-test scan after excluding `frontend/src/tests/**` and `frontend/src/styles/**`. A story should choose a coherent subset and update the relevant guard coverage.

- `frontend/src/App.css`
- `frontend/src/components/AdminGuard.css`
- `frontend/src/components/astro/AstroMoodBackground.css`
- `frontend/src/components/astro/AstroMoodBackground.tsx`
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
- `frontend/src/components/prediction/DailyAdviceCard.css`
- `frontend/src/components/prediction/DayAgenda.css`
- `frontend/src/components/prediction/DayPredictionCard.css`
- `frontend/src/components/prediction/DayTimeline.css`
- `frontend/src/components/prediction/DayTimelineSectionV4.css`
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
- `frontend/src/components/prediction/KeyPointCard.css`
- `frontend/src/components/prediction/PeriodCard.css`
- `frontend/src/components/prediction/SectionTitle.css`
- `frontend/src/components/prediction/TimelineRail.css`
- `frontend/src/components/prediction/TurningPointsList.css`
- `frontend/src/components/ShortcutCard.css`
- `frontend/src/components/SignUpForm.css`
- `frontend/src/components/SignUpForm.tsx`
- `frontend/src/components/TurningPointCard.css`
- `frontend/src/index.css`
- `frontend/src/layouts/AdminLayout.css`
- `frontend/src/layouts/LandingLayout.css`
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
- `frontend/src/pages/ChatPage.css`
- `frontend/src/pages/ConsultationResultPage.css`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/pages/DashboardPage.css`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/landing/LandingPage.css`
- `frontend/src/pages/landing/sections/FaqSection.css`
- `frontend/src/pages/landing/sections/LandingFooter.css`
- `frontend/src/pages/landing/sections/LandingNavbar.css`
- `frontend/src/pages/landing/sections/PricingSection.css`
- `frontend/src/pages/landing/sections/ProblemSection.css`
- `frontend/src/pages/landing/sections/SocialProofSection.css`
- `frontend/src/pages/landing/sections/SolutionSection.css`
- `frontend/src/pages/landing/sections/TestimonialsSection.css`
- `frontend/src/pages/NatalChartPage.css`
- `frontend/src/pages/settings/Settings.css`

### F-003: CSS No Legacy Guard Gap

Required files:

- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/tests/design-system-guards.test.ts`

Optional only if keeping a classified exception:

- `frontend/src/styles/legacy-style-surface-registry.md`

### F-001: Guard Preservation Files

No application change is required. Keep these files in validation scope for any follow-up story:

- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/inline-style-allowlist.ts`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/styles/legacy-style-surface-registry.md`
- `_condamad/stories/regression-guardrails.md`

## Validation

- `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`: PASS.
- `npm run test`: PASS.
- `npm run lint`: PASS.
- `npm run build`: PASS with Vite chunk-size warning.

Python audit validation is recorded after artifact generation and must be run through the project venv per repository policy.

