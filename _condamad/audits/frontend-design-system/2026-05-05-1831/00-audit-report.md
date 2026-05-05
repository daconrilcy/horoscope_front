# Audit Report - frontend-design-system

## Metadata

- Domain: `frontend-design-system`
- Audit folder: `_condamad/audits/frontend-design-system/2026-05-05-1831`
- Skill: `condamad-domain-auditor`
- Date: `2026-05-05`
- Mode: read-only audit after refactors from audits `2026-05-04-2238`, `2026-05-05-1411`, `2026-05-05-1501`, and `2026-05-05-1748`
- Archetype: `legacy-surface-audit` with No Legacy / DRY and test-guard coverage dimensions

## Scope

The audited domain is the frontend design-system surface under `frontend/src`: CSS tokens, token registries, fallback and inline-style policies, design-system guard tests, and residual visual/typography declarations in React/CSS files.

Out of scope: backend code, product behavior, visual redesign decisions, dependency upgrades, and code edits.

## Executive Result

No Critical or High findings were found.

The previous Medium drift between `frontend/src/styles/css-fallback-allowlist.md` and `frontend/src/tests/design-system-allowlist.ts` is remediated: the markdown registry now lists the same fallback surface exercised by the guard tests, and the targeted design-system suite passes.

Three active Medium findings remain:

- `F-002`: 117 CSS fallback usages remain in 19 CSS files.
- `F-003`: 16 inline `style=` attributes remain in 10 TSX files.
- `F-004`: broad hardcoded visual and typography declarations remain across 109 CSS/TSX files.

`F-001` is an Info observation: the ownership and guardrail architecture introduced by the prior stories is active and validated.

## Evidence Summary

- `E-001` confirms skill contracts and guardrails were read.
- `E-002` confirms prior findings were used as baseline.
- `E-003` confirms frontend guardrail files exist.
- `E-004` confirms targeted design-system tests pass: 5 files, 108 tests.
- `E-005` confirms frontend lint passes.
- `E-006` confirms the full frontend suite passes: 113 files, 1234 tests, 8 skipped.
- `E-007` confirms production build passes, with a Vite chunk-size warning.
- `E-008` confirms the current inline-style surface: 16 hits across 10 files.
- `E-009` confirms the current CSS fallback surface: 117 hits across 19 files.
- `E-010` confirms the current broad hardcoded visual/typography surface: 109 files.

## Findings

See `02-finding-register.md` for the canonical finding table and details.

## Exhaustive Files To Modify

The following lists are exhaustive for the measured active modification surfaces in this audit. If a future story narrows scope, it should copy only the relevant subset and explain the cut.

### F-002 - CSS Fallback Debt: 19 Files

- `frontend/src/App.css`
- `frontend/src/components/layout/Header.css`
- `frontend/src/components/layout/Sidebar.css`
- `frontend/src/components/NatalInterpretation.css`
- `frontend/src/components/prediction/CategoryGrid.css`
- `frontend/src/components/prediction/DayPredictionCard.css`
- `frontend/src/components/prediction/KeyPointCard.css`
- `frontend/src/components/prediction/PeriodCard.css`
- `frontend/src/components/SignUpForm.css`
- `frontend/src/features/chat/components/ChatWindow.css`
- `frontend/src/pages/admin/AdminEntitlementsPage.css`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/pages/BirthProfilePage.css`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/landing/sections/TestimonialsSection.css`
- `frontend/src/pages/NatalChartPage.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/styles/glass.css`
- `frontend/src/styles/utilities.css`

Supporting files to update with each fallback batch:

- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`

### F-003 - Inline Style Debt: 10 Files

- `frontend/src/components/DomainRankingCard.tsx`
- `frontend/src/components/prediction/CategoryGrid.tsx`
- `frontend/src/components/prediction/DayPredictionCard.tsx`
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
- `frontend/src/components/prediction/TimelineRail.tsx`
- `frontend/src/components/TurningPointCard.tsx`
- `frontend/src/components/ui/Badge/Badge.tsx`
- `frontend/src/components/ui/Skeleton/Skeleton.tsx`
- `frontend/src/features/chat/components/AstrologerPickerModal.tsx`
- `frontend/src/layouts/TwoColumnLayout.tsx`

Supporting files to update with each inline-style batch:

- `frontend/src/tests/inline-style-allowlist.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`

### F-004 - Hardcoded Visual And Typography Debt: 109 Files

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
- `frontend/src/components/prediction/DailyPageHeader.css`
- `frontend/src/components/prediction/DayAgenda.css`
- `frontend/src/components/prediction/DayPredictionCard.css`
- `frontend/src/components/prediction/DayStateBadge.css`
- `frontend/src/components/prediction/DayTimeline.css`
- `frontend/src/components/prediction/DayTimelineSection.css`
- `frontend/src/components/prediction/DayTimelineSectionV4.css`
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
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
- `frontend/src/components/TurningPointCard.tsx`
- `frontend/src/components/ui/Badge/Badge.css`
- `frontend/src/components/ui/Button/Button.css`
- `frontend/src/components/ui/Card/Card.css`
- `frontend/src/components/ui/EmptyState/EmptyState.css`
- `frontend/src/components/ui/ErrorState/ErrorState.css`
- `frontend/src/components/ui/Field/Field.css`
- `frontend/src/components/ui/Form/Form.css`
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
- `frontend/src/layouts/WizardLayout.css`
- `frontend/src/pages/admin/AdminAiGenerationsPage.css`
- `frontend/src/pages/admin/AdminContentPage.css`
- `frontend/src/pages/admin/AdminDashboardPage.css`
- `frontend/src/pages/admin/AdminEntitlementsPage.css`
- `frontend/src/pages/admin/AdminLogsPage.css`
- `frontend/src/pages/admin/AdminPromptsLogicGraph.tsx`
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
- `frontend/src/pages/NotFoundPage.css`
- `frontend/src/pages/PrivacyPolicyPage.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/styles/backgrounds.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/glass.css`
- `frontend/src/styles/premium-theme.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/utilities.css`
- `frontend/src/tests/AdminPage.test.tsx`
- `frontend/src/tests/AdminPromptsPage.test.tsx`
- `frontend/src/tests/BottomNavPremium.test.tsx`
- `frontend/src/tests/MiniInsightCard.test.tsx`
- `frontend/src/tests/ShortcutCard.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`

Supporting files to update with each hardcoded-value batch:

- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/styles/legacy-style-surface-registry.md`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`

## Recommended Sequencing

1. Reduce CSS fallback debt first because it is concentrated in 19 files and already has exact parity guards.
2. Remove or reclassify inline style exceptions, starting with component-owned dynamic style props that can become CSS custom properties.
3. Continue hardcoded visual/typography migration by bounded clusters, not repo-wide rewrites.

## Validation Status

- `npm run lint`: PASS.
- `npm run test -- design-system css-fallback inline-style legacy-style theme-tokens`: PASS, 5 test files, 108 tests.
- `npm run test`: PASS, 113 test files, 1234 tests, 8 skipped.
- `npm run build`: PASS; Vite reports a non-blocking chunk-size warning for `index-*.js`.

