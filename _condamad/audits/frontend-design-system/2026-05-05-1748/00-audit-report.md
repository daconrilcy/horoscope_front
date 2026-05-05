# Audit Report - frontend-design-system

## Scope

- Domain target: `frontend/src` design-system and style consumption layer.
- Baseline audits: `_condamad/audits/frontend-design-system/2026-05-04-2238/`, `_condamad/audits/frontend-design-system/2026-05-05-1411/`, and `_condamad/audits/frontend-design-system/2026-05-05-1501/`.
- Audit archetype: custom frontend design-system audit using CONDAMAD DRY, No Legacy, missing canonical owner, duplicate responsibility, runtime contract drift, missing guard, and test-guard coverage dimensions.
- Read-only mode: application code was not modified.
- Output folder: `_condamad/audits/frontend-design-system/2026-05-05-1748/`.

## Expected Responsibility

The frontend design-system layer should keep visual decisions in governed CSS tokens, utilities, registries, and static guards. Page and component CSS may keep migration debt only when it is explicitly classified, guarded, and attached to an exit condition. Static inline styles remain forbidden by project rule unless they are exact dynamic exceptions. Documentation registries and executable allowlists must describe the same source of truth.

## Evidence Summary

- Regression guardrails `RG-044` through `RG-050` remain active for frontend design-system surfaces (E-001).
- Canonical registries and guard tests remain present in `frontend/src/styles` and `frontend/src/tests` (E-002, E-003).
- Targeted design-system tests pass: 5 files and 108 tests passed (E-004).
- `npm run lint`, `npm run build`, and full `npm run test` pass (E-005, E-006, E-007).
- Current static counts: 30 TSX `style` attributes, 165 CSS fallback usages, 1671 color-like hits, 1570 typography declaration hits, and 2653 spacing/radius/shadow declaration hits (E-008 through E-012).
- The CSS fallback markdown registry claims to be exact but lists only 7 rows, while the executable `CSS_FALLBACK_EXCEPTIONS` allowlist owns the complete 165-entry contract (E-013, E-014).

## Findings Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 4 |
| Low | 0 |
| Info | 1 |

## Key Findings

- `F-001`: Token ownership and anti-drift governance remain active and validated.
- `F-002`: CSS fallback governance has drifted between the markdown registry and executable allowlist.
- `F-003`: Static inline-style debt is reduced but still preserved in allowlisted TSX surfaces.
- `F-004`: CSS fallback debt is reduced but remains broad across shared UI, layouts, pages, and compatibility CSS.
- `F-005`: Hardcoded visual and typography decisions remain broad outside token sources.

## Exhaustive Files To Modify

### F-002 - Fallback Registry / Allowlist Contract

- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/design-system-policy.ts`

### F-003 - Remaining TSX Inline Style Files

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

### F-004 - Remaining CSS Fallback Files

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

### F-005 - Hardcoded Visual / Typography Files Outside Token Sources

- `frontend/src/index.css`
- `frontend/src/App.css`
- `frontend/src/layouts/AuthLayout.css`
- `frontend/src/layouts/AdminLayout.css`
- `frontend/src/layouts/PageLayout.css`
- `frontend/src/layouts/WizardLayout.css`
- `frontend/src/components/AdminGuard.css`
- `frontend/src/styles/backgrounds.css`
- `frontend/src/styles/glass.css`
- `frontend/src/styles/utilities.css`
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
- `frontend/src/components/TurningPointCard.css`
- `frontend/src/components/astro/AstroMoodBackground.css`
- `frontend/src/components/astro/AstroMoodBackground.tsx`
- `frontend/src/components/layout/Header.css`
- `frontend/src/components/layout/Sidebar.css`
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
- `frontend/src/components/ui/Badge/Badge.css`
- `frontend/src/components/ui/Button/Button.css`
- `frontend/src/components/ui/Card/Card.css`
- `frontend/src/components/ui/EmptyState/EmptyState.css`
- `frontend/src/components/ui/ErrorState/ErrorState.css`
- `frontend/src/components/ui/Field/Field.css`
- `frontend/src/components/ui/Form/Form.tsx`
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
- `frontend/src/layouts/LandingLayout.css`
- `frontend/src/pages/AstrologerProfilePage.css`
- `frontend/src/pages/AstrologerProfilePage.tsx`
- `frontend/src/pages/BirthProfilePage.css`
- `frontend/src/pages/ChatPage.css`
- `frontend/src/pages/ConsultationResultPage.css`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/pages/DashboardPage.css`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/NatalChartPage.css`
- `frontend/src/pages/PrivacyPolicyPage.css`
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
- `frontend/src/pages/settings/AccountSettings.tsx`
- `frontend/src/pages/settings/Settings.css`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`.
- Applicable invariants:
  - `RG-044` - token namespace ownership for frontend CSS variables.
  - `RG-045` - migrated hardcoded values must not return in the covered batch.
  - `RG-046` - semantic typography roles are canonical for migrated surfaces.
  - `RG-047` - static inline styles are forbidden unless exactly allowlisted.
  - `RG-048` - unclassified CSS variable fallbacks are forbidden.
  - `RG-049` - legacy CSS selectors and aliases must remain classified.
  - `RG-050` - anti-drift design-system guards must remain executable.
- Required regression evidence: E-001 through E-007 cover the active frontend guardrails and executable validation.
- Allowed differences: no application code differences were introduced by this audit.

## Recommendations

1. First fix the fallback governance drift by making `css-fallback-allowlist.md` and `CSS_FALLBACK_EXCEPTIONS` a single exact contract, then add a guard that proves parity.
2. Reduce the remaining 30 inline styles by extracting static entries from `AccountSettings.tsx`, `AstrologerProfilePage.tsx`, `NotFoundPage.tsx`, `Form.tsx`, `PeriodCard.tsx`, and `Skeleton.tsx`; keep only documented dynamic bridges.
3. Reduce the 165 CSS fallbacks by shared UI/layout files first, then page-level CSS.
4. Continue hardcoded visual and typography cleanup by cluster, using before/after counts and avoiding unclassified token namespace growth.

## Validation Plan

- Audit validation must run with repository Python policy: `.\.venv\Scripts\Activate.ps1` first, then the CONDAMAD validator/linter.
- Frontend validation commands already executed in this audit: targeted guard tests, lint, build, and full Vitest suite.
