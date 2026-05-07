<!-- Rapport principal du nouvel audit frontend design-system apres refactors. -->

# Audit Report - frontend-design-system

## Scope

- Domain target: `frontend-design-system`.
- Audit archetype: adapted `test-guard-coverage-audit` plus No Legacy/DRY and token ownership checks.
- Read-only mode: no application code was modified.
- Output folder: `_condamad/audits/frontend-design-system/2026-05-07-1021/`.

## Executive Result

The refactors implemented from the previous audits left the guard suite in a green state. Token namespace classification, typography roles, inline-style policy, CSS fallback policy, legacy style classification, visual smoke checks and the full Vitest suite pass.

The remaining actionable design-system debt is still hardcoded visual and typography ownership. The current scan identifies 70 CSS application files outside `frontend/src/styles/**` that still contain candidate literals. These files must not be migrated in one broad story; they should be handled by bounded clusters with before/after scans and exact guards.

## Finding Summary

| ID | Severity | Confidence | Category | Story candidate |
|---|---|---|---|---|
| F-001 | Info | High | missing-guard | no |
| F-002 | Medium | High | duplicate-responsibility | yes |
| F-003 | Info | High | legacy-surface | no |
| F-004 | Low | High | observability-gap | no |

## Findings

### F-001 - Frontend design-system guardrails are active

- Evidence: E-002, E-005, E-006, E-009, E-010, E-011, E-012.
- Expected rule: the frontend design-system guard suite must protect token namespaces, type roles, inline styles, CSS fallbacks, legacy style surfaces and No Legacy vocabulary.
- Actual state: all targeted guards pass, lint passes, inline style hits and CSS fallback hits remain exact allowlisted exceptions.
- Impact: positive invariant; future stories can rely on `RG-044` through `RG-060`.
- Recommended action: keep these guardrails mandatory.

### F-002 - Hardcoded visual and typography literals remain broad

- Evidence: E-004, E-005, E-013.
- Expected rule: repeated visual and typography decisions should converge to global tokens, documented semantic token namespaces, component/page semantic variables, or typography roles.
- Actual state: 70 CSS application files outside `frontend/src/styles/**` still match hardcoded visual/typography literal patterns.
- Impact: Medium maintainability risk and DRY risk; multiple local files can continue to own similar visual decisions.
- Recommended action: migrate the next bounded cluster and update exact guards.
- Story candidate: SC-001.

### F-003 - Previously active legacy and compatibility surfaces are closed or classified

- Evidence: E-005, E-009, E-010, E-011, E-012.
- Expected rule: no removed design-system compatibility surface should return as alias, shim, fallback, stale comment, page-token leak or static inline style.
- Actual state: guards pass; remaining inline styles and CSS fallbacks are exact dynamic exceptions.
- Impact: no new implementation risk found.
- Recommended action: preserve the current guard coverage.

### F-004 - Production bundle warning remains visible

- Evidence: E-007.
- Expected rule: build must pass; warnings outside the audited domain should be separated.
- Actual state: build passes and Vite reports `assets/index-tzuNTTVF.js` above 500 kB.
- Impact: low performance follow-up risk, not a design-system ownership defect.
- Recommended action: track in a separate frontend performance audit/story if needed.

## Exhaustive Files To Modify For F-002

These are the current CSS application files that still require classification or migration for hardcoded visual/typography literals. A future story should choose a coherent subset, not all files at once.

- `frontend/src/App.css`
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
- `frontend/src/components/prediction/DailyAdviceCard.css`
- `frontend/src/components/prediction/DailyPageHeader.css`
- `frontend/src/components/prediction/DayAgenda.css`
- `frontend/src/components/prediction/DayPredictionCard.css`
- `frontend/src/components/prediction/DayStateBadge.css`
- `frontend/src/components/prediction/DayTimeline.css`
- `frontend/src/components/prediction/DayTimelineSectionV4.css`
- `frontend/src/components/prediction/KeyPointCard.css`
- `frontend/src/components/prediction/PeriodCard.css`
- `frontend/src/components/prediction/SectionTitle.css`
- `frontend/src/components/prediction/TimelineRail.css`
- `frontend/src/components/prediction/TurningPointsList.css`
- `frontend/src/components/ShortcutCard.css`
- `frontend/src/components/SignUpForm.css`
- `frontend/src/components/TurningPointCard.css`
- `frontend/src/components/ui/Button/Button.css`
- `frontend/src/components/ui/Skeleton/Skeleton.css`
- `frontend/src/features/chat/components/ChatQuotaBanner.css`
- `frontend/src/features/chat/components/ConversationItem.css`
- `frontend/src/features/chat/components/ConversationList.css`
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

## Recommended Next Clusters

- Admin CSS cluster: `frontend/src/pages/admin/*.css`.
- Landing CSS cluster: `frontend/src/pages/landing/**/*.css` and `frontend/src/layouts/LandingLayout.css`.
- Natal/profile cluster: `frontend/src/pages/NatalChartPage.css`, `frontend/src/components/NatalInterpretation.css`, `frontend/src/pages/AstrologerProfilePage.css`.
- Remaining prediction cluster: `frontend/src/components/prediction/*.css` and `frontend/src/pages/DailyHoroscopePage.css`.

## Validation

- `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`: PASS.
- `npm run test`: PASS.
- `npm run lint`: PASS.
- `npm run build`: PASS with existing Vite chunk-size warning.
