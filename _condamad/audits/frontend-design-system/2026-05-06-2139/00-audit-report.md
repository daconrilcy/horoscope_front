<!-- Rapport d'audit frontend design-system apres les refactors CS-074 a CS-080. -->

# Audit Report - frontend-design-system

## Scope

- Target domain: `frontend-design-system`.
- Comparative context: audits `_condamad/audits/frontend-design-system/2026-05-04-2238` through `_condamad/audits/frontend-design-system/2026-05-06-1618`.
- Refactors now considered implemented: CS-074, CS-075, CS-076, CS-077, CS-078, CS-079 and CS-080.
- Archetype used: `legacy-surface-audit` plus `test-guard-coverage-audit`, adapted to the bounded frontend design-system surface.
- Mode: read-only for application code; audit artifacts only under `_condamad/audits/frontend-design-system/2026-05-06-2139/`.

## Expected Responsibility

The frontend design-system domain owns CSS token namespaces, typography roles, static style governance, page-scoped style boundaries, legacy style surfaces and executable anti-drift guards. It must not keep unclassified aliases, migration-only namespaces, static inline style decisions, CSS fallbacks, cross-page token dependencies or runtime compatibility shims without an explicit owner and exit condition.

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

## Executive Result

The refactors closed the previously active compatibility and cross-page token findings. Current evidence shows:

- focused frontend guard suite passes: 11 files, 192 tests;
- lint passes;
- production build passes;
- no `HelpPage.css` consumption of `--settings-*`;
- no active `/admin/pricing`, `/admin/monitoring` or `/admin/personas` route/redirect/facade hit;
- no runtime source hit for the CS-080 compatibility vocabulary;
- no `--default_dropshadow` active hit;
- no active `migration-only` namespace row in `token-namespace-registry.md`;
- CSS fallbacks are limited to two dynamic `--usage-progress` exceptions;
- TSX inline styles are limited to five allowlisted dynamic/style-prop exceptions.

The remaining design-system risk is now concentrated in broad hardcoded visual/typography literals across 98 non-test application files. This is not a regression from CS-078/CS-079 because the migrated clusters are guarded, but it remains duplicate ownership versus the token and typography registries.

## Findings Summary

| ID | Severity | Confidence | Category | Story candidate |
|---|---|---|---|---|
| F-001 | Info | High | missing-guard | no |
| F-002 | Medium | High | duplicate-responsibility | yes |
| F-003 | Info | High | legacy-surface | no |
| F-004 | Low | High | observability-gap | no |

## Key Findings

### F-001 - Frontend design-system guardrails are active

The guard suite, lint and build are executable and green. The active guardrails now cover token namespace classification, page-scoped token isolation, converged migration-only namespaces, CSS fallback allowlists, inline-style allowlists, removed runtime compatibility vocabulary and removed admin legacy redirects.

### F-002 - Hardcoded visual and typography literals remain broad

The broad static scan still finds 98 non-test application files with literal colors, shadows, radii, typography values, gradients or pixel values outside `frontend/src/styles/**`. These local declarations continue to compete with canonical token and typography ownership. This should continue as bounded cluster migrations, not a single large refactor.

### F-003 - Previously active legacy/compatibility surfaces are closed

The CS-074 through CS-080 surfaces are closed by evidence: no HelpPage-to-Settings token dependency, no removed admin legacy redirect path, no removed runtime compatibility vocabulary, no active `--default_dropshadow`, and no active `migration-only` namespace row.

### F-004 - Build still emits a chunk-size warning

The production build passes, but Vite reports the main JS chunk at 1,370.37 kB after minification. This is a frontend performance concern, not a design-system correctness blocker.

## Exhaustive Files To Modify

### F-002: Hardcoded Visual And Typography Literals

The following 98 files are the exhaustive candidate files returned by the non-test scan after excluding `frontend/src/tests/**` and `frontend/src/styles/**`. A story should choose a coherent subset and update the relevant guard coverage.

- `frontend/src/App.css`
- `frontend/src/components/AdminGuard.css`
- `frontend/src/components/astro/AstroMoodBackground.css`
- `frontend/src/components/astro/AstroMoodBackground.tsx`
- `frontend/src/components/AstroDailyEvents.css`
- `frontend/src/components/AstroFoundationSection.css`
- `frontend/src/components/BestWindowCard.css`
- `frontend/src/components/ConstellationSVG.tsx`
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
- `frontend/src/components/prediction/DailyPageHeader.css`
- `frontend/src/components/prediction/DayAgenda.css`
- `frontend/src/components/prediction/DayPredictionCard.css`
- `frontend/src/components/prediction/DayStateBadge.css`
- `frontend/src/components/prediction/DayTimeline.css`
- `frontend/src/components/prediction/DayTimelineSection.css`
- `frontend/src/components/prediction/DayTimelineSectionV4.css`
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
- `frontend/src/components/prediction/DecisionWindowsSection.tsx`
- `frontend/src/components/prediction/KeyPointCard.css`
- `frontend/src/components/prediction/PeriodCard.css`
- `frontend/src/components/prediction/PeriodCardsRow.css`
- `frontend/src/components/prediction/SectionTitle.css`
- `frontend/src/components/prediction/TimelineRail.css`
- `frontend/src/components/prediction/TurningPointsList.css`
- `frontend/src/components/settings/DeleteAccountModal.css`
- `frontend/src/components/ShortcutCard.css`
- `frontend/src/components/SignUpForm.css`
- `frontend/src/components/SignUpForm.tsx`
- `frontend/src/components/TurningPointCard.css`
- `frontend/src/components/ui/Badge/Badge.css`
- `frontend/src/components/ui/Button/Button.css`
- `frontend/src/components/ui/Card/Card.css`
- `frontend/src/components/ui/EmptyState/EmptyState.css`
- `frontend/src/components/ui/ErrorState/ErrorState.css`
- `frontend/src/components/ui/Field/Field.css`
- `frontend/src/components/ui/LockedSection/LockedSection.css`
- `frontend/src/components/ui/Modal/Modal.css`
- `frontend/src/components/ui/Select/Select.css`
- `frontend/src/components/ui/Skeleton/Skeleton.css`
- `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.css`
- `frontend/src/components/ui/UserAvatar/UserAvatar.css`
- `frontend/src/components/ui/UserMenu/UserMenu.css`
- `frontend/src/features/chat/components/ChatComposer.css`
- `frontend/src/features/chat/components/ChatPageHeader.css`
- `frontend/src/features/chat/components/ChatQuotaBanner.css`
- `frontend/src/features/chat/components/ChatWindow.css`
- `frontend/src/features/chat/components/ConversationItem.css`
- `frontend/src/features/chat/components/ConversationList.css`
- `frontend/src/index.css`
- `frontend/src/layouts/AdminLayout.css`
- `frontend/src/layouts/AuthLayout.css`
- `frontend/src/layouts/LandingLayout.css`
- `frontend/src/layouts/PageLayout.css`
- `frontend/src/layouts/TwoColumnLayout.css`
- `frontend/src/layouts/TwoColumnLayout.tsx`
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
- `frontend/src/pages/PrivacyPolicyPage.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/pages/support/SupportTicketList.tsx`

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

### F-003: Closed Compatibility Surfaces

No application change is required by this audit. Keep these files in regression validation scope only:

- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/app/router.tsx`
- `frontend/src/pages/AdminPage.tsx`
- `frontend/src/tests/AdminPage.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`

### F-004: Performance Follow-Up

No exhaustive file list is prescribed by this design-system audit. A separate frontend performance audit should inspect router boundaries, lazy-loading candidates and Vite chunk ownership before naming files.

## No Legacy / DRY Assessment

- DRY: still partially failed by F-002 because local literals duplicate visual decisions that should converge toward tokens or semantic roles.
- No Legacy: passes for the audited CS-074 through CS-080 surfaces. Remaining legacy vocabulary hits are confined to registry/test policy text, not runtime code.
- Mono-domain ownership: passes for page-scoped token consumption; owner-only use is enforced by `design-system-guards.test.ts`.
- Dependency direction: passes for `HelpPage.css` versus `Settings.css`; no cross-page `--settings-*` use remains.

## Recommended Order

1. Create one story from SC-001 for the next hardcoded-value cluster. Prioritize product surfaces with high visual churn, not already-guarded CS-078/CS-079 migrated literals.
2. Keep CS-074 through CS-080 guard commands mandatory for every frontend design-system story.
3. Track F-004 in a separate frontend performance audit/story if bundle size is now a product concern.

## Validation Status

- `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke ConsultationMigration consultationStore TurningPointsEnriched DailyHoroscopePage AdminPage`: PASS.
- `npm run lint`: PASS.
- `npm run build`: PASS with Vite chunk-size warning.
