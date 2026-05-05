# Audit Report - frontend-design-system

## Scope

- Domain key: `frontend-design-system`
- Audit date: `2026-05-05-1942`
- Mode: read-only application audit; only audit artifacts were written.
- Archetype used: `legacy-surface-audit` with mandatory DRY, No Legacy, mono-domain ownership, and guard coverage checks.
- Baseline audits reviewed:
  - `_condamad/audits/frontend-design-system/2026-05-04-2238`
  - `_condamad/audits/frontend-design-system/2026-05-05-1411`
  - `_condamad/audits/frontend-design-system/2026-05-05-1501`
  - `_condamad/audits/frontend-design-system/2026-05-05-1748`
  - `_condamad/audits/frontend-design-system/2026-05-05-1831`

## Executive Result

The refactors reduced the governed fallback surface again: the executable fallback allowlist and markdown registry now both expose 68 entries, and the fallback scan touches 14 CSS files. The targeted design-system guard suite, lint, and production build pass.

One new active defect appeared after the refactors: the full frontend Vitest suite fails because `src/tests/visual-smoke.test.tsx` still asserts old hardcoded typography values while `src/App.css` now uses design tokens. This is a guard drift, not evidence that the tokenized CSS should be reverted.

## Findings Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 5 |
| Low | 0 |
| Info | 1 |

## Findings

### F-001 - Frontend design-system governance remains active

- Severity: Info
- Confidence: High
- Category: missing-canonical-owner
- Evidence: E-001, E-002, E-003, E-004, E-005, E-006
- Expected rule: token namespaces, typography roles, inline styles, CSS fallbacks, and legacy style surfaces remain governed by registries and executable tests.
- Actual state: `RG-044` through `RG-050` are active; the registries are present; targeted design-system tests pass; lint and build pass.
- Impact: the previous High governance risk remains controlled.
- Recommended action: keep the guardrails mandatory for future frontend stories.
- Story candidate: no
- Files to modify: none.

### F-002 - Visual smoke guard still expects pre-token typography literals

- Severity: Medium
- Confidence: High
- Category: runtime-contract-drift
- Evidence: E-007, E-008
- Expected rule: regression guards should assert the canonical design-system contract after refactor, not obsolete literal values.
- Actual state: `npm run test` and isolated `npm run test -- visual-smoke` fail because `visual-smoke.test.tsx` expects `font-size: 18px`, `font-size: 12px`, and `font-weight: 500`; `App.css` now uses `var(--font-size-lg)`, `var(--font-size-xs)`, and `var(--font-weight-medium)`.
- Impact: the full test gate is red, and the failing guard can push future work to reintroduce hardcoded literals.
- Recommended action: update the visual smoke test to assert tokenized typography or resolve token values through the design-token source, without reverting `App.css`.
- Story candidate: yes
- Exhaustive files to modify:
  - `frontend/src/tests/visual-smoke.test.tsx`

### F-003 - CSS fallback debt remains active but bounded

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Evidence: E-003, E-004, E-010
- Expected rule: `var(--token, literal)` fallbacks should be rare, classified, and removed when the canonical token is guaranteed.
- Actual state: 68 fallback exceptions are registered, and the scan touches 14 CSS files. This is improved from the previous audit, but literals remain active as compatibility, dynamic, or migration-only values.
- Impact: fallback literals continue to preserve alternate visual decisions beside the canonical token set.
- Recommended action: reduce fallbacks in bounded batches, starting with the files below, and update both `css-fallback-allowlist.md` and `design-system-allowlist.ts`.
- Story candidate: yes
- Exhaustive files to modify:
  - `frontend/src/App.css`
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
  - `frontend/src/pages/landing/sections/TestimonialsSection.css`
  - `frontend/src/pages/NatalChartPage.css`
  - `frontend/src/pages/settings/Settings.css`
  - `frontend/src/styles/css-fallback-allowlist.md`
  - `frontend/src/tests/design-system-allowlist.ts`

### F-004 - Inline style exceptions remain active

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Evidence: E-003, E-004, E-009
- Expected rule: static styles live in CSS files; inline styles are limited to exact dynamic exceptions or component style-prop bridges.
- Actual state: 16 inline style exceptions remain across 10 TSX files. They are allowlisted, but still bypass the project-level no-inline-style rule unless each entry stays genuinely dynamic.
- Impact: static visual decisions can remain hidden in TSX instead of reusable CSS.
- Recommended action: move removable entries to CSS/custom properties; keep only runtime geometry, dynamic colors, or explicit style-prop bridges.
- Story candidate: yes
- Exhaustive files to modify:
  - `frontend/src/layouts/TwoColumnLayout.tsx`
  - `frontend/src/components/DomainRankingCard.tsx`
  - `frontend/src/components/TurningPointCard.tsx`
  - `frontend/src/components/ui/Badge/Badge.tsx`
  - `frontend/src/components/ui/Skeleton/Skeleton.tsx`
  - `frontend/src/components/prediction/CategoryGrid.tsx`
  - `frontend/src/components/prediction/DayPredictionCard.tsx`
  - `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
  - `frontend/src/components/prediction/TimelineRail.tsx`
  - `frontend/src/features/chat/components/AstrologerPickerModal.tsx`
  - `frontend/src/tests/inline-style-allowlist.ts`
  - `frontend/src/tests/design-system-allowlist.ts`

### F-005 - Hardcoded visual and typography decisions remain broad

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Evidence: E-011
- Expected rule: repeated color, spacing, radius, shadow, and typography decisions should converge toward semantic tokens, shared utilities, or exact classified exceptions.
- Actual state: the broad source scan finds 107 application files, excluding test roots and canonical token source files, that still contain hardcoded visual or typography signals.
- Impact: semantic tokens compete with local literals across many product surfaces, increasing future drift cost.
- Recommended action: continue phased migration by product surface and highest-repeat clusters, with before/after counts and guard updates per batch.
- Story candidate: yes
- Exhaustive files to modify:
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
  - `frontend/src/components/icons/DashboardIcons.tsx`
  - `frontend/src/components/layout/Header.css`
  - `frontend/src/components/layout/Sidebar.css`
  - `frontend/src/components/MiniInsightCard.css`
  - `frontend/src/components/NatalInterpretation.css`
  - `frontend/src/components/prediction/CategoryGrid.css`
  - `frontend/src/components/prediction/DailyAdviceCard.css`
  - `frontend/src/components/prediction/DailyPageHeader.css`
  - `frontend/src/components/prediction/DayAgenda.css`
  - `frontend/src/components/prediction/DayPredictionCard.css`
  - `frontend/src/components/prediction/DayPredictionCard.tsx`
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
  - `frontend/src/components/ui/Skeleton/Skeleton.tsx`
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
  - `frontend/src/pages/PrivacyPolicyPage.css`
  - `frontend/src/pages/settings/Settings.css`
  - `frontend/src/pages/support/SupportTicketList.tsx`
  - `frontend/src/styles/backgrounds.css`
  - `frontend/src/styles/glass.css`
  - `frontend/src/styles/utilities.css`

### F-006 - Legacy selector and compatibility token surfaces still need exit work

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Evidence: E-002, E-003, E-012
- Expected rule: legacy selectors and compatibility token aliases should stay classified and shrink over time.
- Actual state: the registry is present and guarded, but active compatibility and migration-only surfaces remain in `App.css`, `AdminPromptsPage.css`, `theme.css`, and the style registries.
- Impact: No Legacy remains a controlled but active debt surface; future migrations must avoid adding unclassified aliases or selectors.
- Recommended action: split a story for legacy selector extinction and compatibility token retirement, keeping the registry exact.
- Story candidate: yes
- Exhaustive files to modify:
  - `frontend/src/App.css`
  - `frontend/src/pages/admin/AdminPromptsPage.css`
  - `frontend/src/styles/theme.css`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/legacy-style-surface-registry.md`
  - `frontend/src/styles/css-fallback-allowlist.md`

## Validation Status

- PASS: `npm run test -- design-system css-fallback inline-style legacy-style theme-tokens`
- PASS: `npm run lint`
- PASS: `npm run build`, with non-blocking Vite chunk-size warning.
- FAIL: `npm run test` because `src/tests/visual-smoke.test.tsx` has 2 failing assertions.
- FAIL: `npm run test -- visual-smoke` reproduces the same 2 failures.

## Recommended Next Action

Fix `F-002` first because it keeps the full frontend suite red and its correction is tightly bounded to one test file. Then continue the already successful fallback-reduction path from `F-003`, followed by inline-style reduction and broad hardcoded-value migration.
