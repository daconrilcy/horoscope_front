<!-- Rapport d'audit frontend design-system apres les refactors des audits listes jusqu'au 2026-05-06-2320. -->

# Audit Report - frontend-design-system

## Scope

- Target domain: `frontend-design-system`.
- Comparative context: audits `_condamad/audits/frontend-design-system/2026-05-04-2238` through `_condamad/audits/frontend-design-system/2026-05-06-2320`.
- Refactors considered implemented: all stories planned in the audits named by the user, including the follow-ups from `2026-05-06-2320`.
- Archetype used: `legacy-surface-audit` plus `test-guard-coverage-audit`, adapted to the bounded frontend design-system surface.
- Mode: read-only for application code; audit artifacts only under `_condamad/audits/frontend-design-system/2026-05-07-0017/`.

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
- `RG-059` - App cluster visual literals.
- `RG-060` - No Legacy vocabulary in active CSS comments.

## Executive Result

The refactors are stable. Evidence shows:

- focused frontend design-system guard suite passes: 6 files, 136 tests;
- full frontend Vitest suite passes: 115 files, 1254 tests passed, 8 skipped;
- lint passes;
- production build passes;
- no `HelpPage.css` consumption of `--settings-*`;
- no active `/admin/pricing`, `/admin/monitoring` or `/admin/personas` route/redirect/facade source hit;
- no active CSS comment containing No Legacy vocabulary;
- no active runtime compatibility vocabulary hit for the CS-080 surfaces;
- CSS fallbacks are limited to two dynamic `--usage-progress` exceptions;
- TSX inline styles are limited to five exact dynamic/style-prop exceptions.

The remaining design-system implementation risk is concentrated in broad hardcoded visual or typography literals across 68 non-test application files outside `frontend/src/styles/**`. This is not a regression from the migrated clusters because the targeted guardrails are green, but it remains duplicate responsibility versus token and typography ownership.

## Findings Summary

| ID | Severity | Confidence | Category | Story candidate |
|---|---|---|---|---|
| F-001 | Info | High | missing-guard | no |
| F-002 | Medium | High | duplicate-responsibility | yes |
| F-003 | Info | High | legacy-surface | no |
| F-004 | Low | High | observability-gap | no |

## Key Findings

### F-001 - Frontend design-system guardrails are active

The guard suite, full Vitest, lint and build are executable and green after the listed refactors. Inline-style and CSS fallback exceptions remain exact, classified and tested.

### F-002 - Hardcoded visual and typography literals remain broad

The broad static scan still finds 68 non-test application files with literal colors, shadows, radii, typography values or related style literals outside `frontend/src/styles/**`. The scan is intentionally broad: implementation stories must inspect the selected cluster and distinguish legitimate semantic-token owner declarations from values that should move to global tokens, page-scoped semantic tokens, component-scoped semantic tokens or typography roles.

### F-003 - Previously active legacy/compatibility surfaces are closed

The known surfaces from the prior audit are closed by evidence: no CSS comment No Legacy vocabulary hit, no HelpPage-to-Settings token dependency, no removed admin legacy route source hit, no removed runtime compatibility vocabulary hit, no active `--default_dropshadow`, and no active `migration-only` namespace row.

### F-004 - Build still emits a chunk-size warning

The production build passes, but Vite reports `assets/index-BK31TCkH.js` at 1,370.37 kB after minification. This is a frontend performance concern, not a design-system correctness blocker.

## Exhaustive Files To Modify

### F-002: Hardcoded Visual And Typography Literals

The following 68 files are the exhaustive candidate files returned by the current non-test scan after excluding `frontend/src/tests/**` and `frontend/src/styles/**`. A story should choose a coherent subset and update the relevant exact guard coverage.

- `frontend/src/App.css`
- `frontend/src/components/AdminGuard.css`
- `frontend/src/components/AstroDailyEvents.css`
- `frontend/src/components/AstroFoundationSection.css`
- `frontend/src/components/BestWindowCard.css`
- `frontend/src/components/DayClimateHero.css`
- `frontend/src/components/DomainRankingCard.css`
- `frontend/src/components/ErrorBoundary/ErrorBoundary.css`
- `frontend/src/components/HeroHoroscopeCard.css`
- `frontend/src/components/MiniInsightCard.css`
- `frontend/src/components/NatalInterpretation.css`
- `frontend/src/components/ShortcutCard.css`
- `frontend/src/components/SignUpForm.css`
- `frontend/src/components/SignUpForm.tsx`
- `frontend/src/components/TurningPointCard.css`
- `frontend/src/components/astro/AstroMoodBackground.css`
- `frontend/src/components/astro/AstroMoodBackground.tsx`
- `frontend/src/components/layout/Header.css`
- `frontend/src/components/layout/Sidebar.css`
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
- `frontend/src/features/chat/components/ChatWindow.css`
- `frontend/src/features/chat/components/ConversationItem.css`
- `frontend/src/index.css`
- `frontend/src/layouts/AdminLayout.css`
- `frontend/src/layouts/LandingLayout.css`
- `frontend/src/layouts/WizardLayout.css`
- `frontend/src/pages/AstrologerProfilePage.css`
- `frontend/src/pages/BirthProfilePage.css`
- `frontend/src/pages/ChatPage.css`
- `frontend/src/pages/ConsultationResultPage.css`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/pages/DashboardPage.css`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/NatalChartPage.css`
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
- `frontend/src/pages/billing/billing-return.css`
- `frontend/src/pages/landing/LandingPage.css`
- `frontend/src/pages/landing/sections/FaqSection.css`
- `frontend/src/pages/landing/sections/LandingFooter.css`
- `frontend/src/pages/landing/sections/LandingNavbar.css`
- `frontend/src/pages/landing/sections/PricingSection.css`
- `frontend/src/pages/landing/sections/ProblemSection.css`
- `frontend/src/pages/landing/sections/SocialProofSection.css`
- `frontend/src/pages/landing/sections/SolutionSection.css`
- `frontend/src/pages/landing/sections/TestimonialsSection.css`
- `frontend/src/pages/settings/Settings.css`

### F-001: Guard Preservation Files

No application change is required. Keep these files in validation scope for any follow-up frontend design-system story:

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

### F-003: Closed Legacy Surface Files

No application change is required. Keep these closed surfaces guarded:

- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/app/routes.tsx`
- `frontend/src/pages/AdminPage.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`

## No Legacy / DRY Assessment

- DRY: partially failed by F-002 because local literals still duplicate visual and typographic ownership that should converge toward tokens or semantic roles.
- No Legacy: passes for the audited CS-074 through CS-083 surfaces. Remaining `fallback` vocabulary hits in runtime code are domain/product fallbacks, Suspense fallbacks, avatar fallbacks or registry/test policy text, not unclassified legacy compatibility surfaces.
- Dependency direction: no cross-page token dependency was found for `HelpPage.css` consuming `--settings-*`.
- Mono-domain ownership: the design-system governance files remain the canonical owners for token namespaces, CSS fallbacks, inline styles and legacy style surfaces.

## Recommended Order

1. Create one story from `SC-001` for the next hardcoded-value cluster.
2. Prioritize high-density user-facing surfaces: `frontend/src/pages/HelpPage.css`, `frontend/src/pages/settings/Settings.css`, `frontend/src/pages/AstrologerProfilePage.css`, `frontend/src/pages/landing/LandingPage.css`, and `frontend/src/components/NatalInterpretation.css`.
3. Treat `frontend/src/App.css` separately because it now owns `--app-*` semantic tokens; the story should decide which literals stay as app-scoped semantic token definitions and which should be promoted to global tokens or more granular page/component namespaces.
4. Track F-004 in a separate frontend performance audit/story if bundle size is now a product concern.

## Validation Status

- `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`: PASS.
- `npm run test`: PASS.
- `npm run lint`: PASS.
- `npm run build`: PASS with Vite chunk-size warning.
- Python audit validation: recorded after artifact generation, run through the project venv per repository policy.
