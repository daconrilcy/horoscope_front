# Audit Report - frontend-design-system

## Scope

- Domain key: `frontend-design-system`
- Audit date: `2026-05-05-2053`
- Skill: `condamad-domain-auditor`
- Mode: read-only application audit; only audit artifacts were written.
- Archetype used: `legacy-surface-audit` with mandatory DRY, No Legacy, mono-domain ownership, dependency direction, and guard coverage checks.
- Baseline audits reviewed:
  - `_condamad/audits/frontend-design-system/2026-05-04-2238`
  - `_condamad/audits/frontend-design-system/2026-05-05-1411`
  - `_condamad/audits/frontend-design-system/2026-05-05-1501`
  - `_condamad/audits/frontend-design-system/2026-05-05-1748`
  - `_condamad/audits/frontend-design-system/2026-05-05-1831`
  - `_condamad/audits/frontend-design-system/2026-05-05-1942`

## Executive Result

The CS-047 to CS-051 refactors closed the previously red `visual-smoke` contract and the full frontend gate is now green: targeted design-system guards, `npm run test`, `npm run lint`, and `npm run build` all pass. The build still emits the known Vite chunk-size warning for the main bundle.

The remaining design-system debt is controlled by exact registries and tests, but it is still active: 54 CSS fallback exceptions, 15 inline style exceptions, broad hardcoded visual signals in 106 application files, and classified legacy selector / compatibility token surfaces remain. No new Critical or High risk was found.

## Findings Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 4 |
| Low | 0 |
| Info | 2 |

## Findings

### F-001 - Frontend design-system governance is green after refactor

- Severity: Info
- Confidence: High
- Category: missing-canonical-owner
- Evidence: E-001, E-002, E-003, E-004, E-005, E-006, E-007, E-008
- Expected rule: token namespaces, typography roles, inline styles, CSS fallbacks, and legacy surfaces remain governed by registries and executable tests.
- Actual state: `RG-044` through `RG-050` are active; targeted guards, full Vitest suite, lint, and build pass.
- Impact: the previous runtime guard drift is closed and governance remains executable.
- Recommended action: keep the guards mandatory for future frontend stories.
- Story candidate: no
- Files to modify: none.

### F-002 - CSS fallback debt remains active and concentrated

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Evidence: E-003, E-009
- Expected rule: `var(--token, literal)` fallbacks should be rare, classified, and removed when the canonical token is guaranteed.
- Actual state: `CSS_FALLBACK_EXCEPTIONS` contains 54 exact entries; the scan finds fallback usage in 10 CSS files. `NatalChartPage.css` is now the dominant remaining cluster.
- Impact: fallback literals still preserve alternate visual decisions beside the canonical token set.
- Recommended action: reduce fallbacks in bounded batches, starting with `NatalChartPage.css`, and update both fallback registries in the same change.
- Story candidate: yes
- Exhaustive files to modify:
  - `frontend/src/App.css`
  - `frontend/src/components/NatalInterpretation.css`
  - `frontend/src/components/prediction/KeyPointCard.css`
  - `frontend/src/components/prediction/PeriodCard.css`
  - `frontend/src/components/SignUpForm.css`
  - `frontend/src/features/chat/components/ChatWindow.css`
  - `frontend/src/pages/admin/AdminEntitlementsPage.css`
  - `frontend/src/pages/landing/sections/TestimonialsSection.css`
  - `frontend/src/pages/NatalChartPage.css`
  - `frontend/src/pages/settings/Settings.css`
  - `frontend/src/styles/css-fallback-allowlist.md`
  - `frontend/src/tests/design-system-allowlist.ts`

### F-003 - Inline style exceptions remain dynamic but still bypass CSS ownership

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Evidence: E-004, E-010
- Expected rule: static styles live in CSS files; inline styles are limited to exact dynamic exceptions or component style-prop bridges.
- Actual state: 15 inline style attributes remain across 9 TSX files and are covered by exact allowlists.
- Impact: even justified dynamic values keep styling decisions in TSX, so future static additions can hide behind the same pattern if the allowlist grows.
- Recommended action: convert removable color/background/position bridges to CSS custom properties or component classes where practical; keep only runtime geometry and explicit style-prop pass-throughs.
- Story candidate: yes
- Exhaustive files to modify:
  - `frontend/src/layouts/TwoColumnLayout.tsx`
  - `frontend/src/components/DomainRankingCard.tsx`
  - `frontend/src/components/prediction/CategoryGrid.tsx`
  - `frontend/src/components/prediction/DayPredictionCard.tsx`
  - `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
  - `frontend/src/components/prediction/TimelineRail.tsx`
  - `frontend/src/components/TurningPointCard.tsx`
  - `frontend/src/components/ui/Badge/Badge.tsx`
  - `frontend/src/components/ui/Skeleton/Skeleton.tsx`
  - `frontend/src/tests/inline-style-allowlist.ts`
  - `frontend/src/tests/design-system-allowlist.ts`

### F-004 - Hardcoded visual and typography decisions remain broad

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Evidence: E-011
- Expected rule: repeated color, spacing, radius, shadow, and typography decisions should converge toward semantic tokens, shared utilities, or exact classified exceptions.
- Actual state: the broad source scan finds 106 application files, excluding test roots and canonical token source files, with hardcoded visual or typography signals.
- Impact: semantic tokens still compete with local literals across many product surfaces.
- Recommended action: continue phased migration by coherent product surface, with before/after counts and registry updates only when a durable semantic token is introduced.
- Story candidate: yes
- Exhaustive files to modify:
  - `frontend/src/App.css`
  - `frontend/src/index.css`
  - `frontend/src/components/AdminGuard.css`
  - `frontend/src/components/AstroDailyEvents.css`
  - `frontend/src/components/AstroFoundationSection.css`
  - `frontend/src/components/astro/AstroMoodBackground.css`
  - `frontend/src/components/astro/AstroMoodBackground.tsx`
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
  - `frontend/src/styles/backgrounds.css`
  - `frontend/src/styles/glass.css`
  - `frontend/src/styles/premium-theme.css`
  - `frontend/src/styles/utilities.css`

### F-005 - Legacy selector and compatibility token surfaces still need exit work

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Evidence: E-012
- Expected rule: legacy selectors and compatibility token aliases should stay classified and shrink over time.
- Actual state: the registry remains exact and guarded, but active migration-only selector families still live in `App.css` and `AdminPromptsPage.css`; compatibility token aliases remain in `theme.css`.
- Impact: No Legacy remains controlled but active; future migrations must not treat the registry as permanent architecture.
- Recommended action: split a story for chat shell / admin prompts legacy selector extinction and compatibility token retirement.
- Story candidate: yes
- Exhaustive files to modify:
  - `frontend/src/App.css`
  - `frontend/src/pages/admin/AdminPromptsPage.css`
  - `frontend/src/styles/theme.css`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/legacy-style-surface-registry.md`

### F-006 - Build output remains oversized

- Severity: Info
- Confidence: High
- Category: missing-guard
- Evidence: E-007
- Expected rule: production build should remain operational; chunk-size warnings should be tracked separately from design-system correctness.
- Actual state: `npm run build` passes, but Vite warns that `assets/index-*.js` is above 500 kB after minification.
- Impact: this is not a design-system regression, but it remains a user-perceived performance risk if it grows.
- Recommended action: track under a separate frontend performance audit/story, not inside the design-system cleanup batch.
- Story candidate: no
- Files to modify: none in this audit.

## Validation Status

- PASS: `npm run test -- design-system css-fallback inline-style legacy-style theme-tokens`
- PASS: `npm run test -- visual-smoke`
- PASS: `npm run test`
- PASS: `npm run lint`
- PASS: `npm run build`, with non-blocking Vite chunk-size warning.

## Recommended Next Action

Start with `F-002` on `NatalChartPage.css`, because it is the largest concentrated fallback cluster and will also reduce the compatibility-token pressure captured in `F-005`. Then handle inline style exceptions only where a CSS custom-property bridge can reduce TSX styling without losing runtime behavior.
