# Audit Report - frontend-design-system

## Scope

- Domain key: `frontend-design-system`
- Audit date: `2026-05-06-0108`
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
  - `_condamad/audits/frontend-design-system/2026-05-05-2053`
  - `_condamad/audits/frontend-design-system/2026-05-06-0016`

## Executive Result

The post-refactor frontend design-system state is green. Targeted design-system guards, visual smoke, the full Vitest suite, lint, and production build pass.

The remaining debt is governed and smaller than the `2026-05-06-0016` baseline: 10 CSS fallback exceptions across 9 CSS files, 9 inline style exceptions across 6 TSX files, broad hardcoded visual or typography signals across 110 files outside the main token source files, and 5 classified legacy selector/token rows. No Critical or High finding was found.

## Findings Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 4 |
| Low | 0 |
| Info | 2 |

## Findings

### F-001 - Frontend design-system governance remains green

- Severity: Info
- Confidence: High
- Category: missing-guard
- Evidence: E-001, E-002, E-003, E-004, E-005, E-006, E-007, E-008
- Expected rule: token namespaces, typography roles, inline styles, CSS fallbacks, and legacy surfaces remain governed by registries and executable tests.
- Actual state: `RG-044` through `RG-050` are active; targeted guards, visual smoke, full Vitest, lint, and build pass.
- Impact: previous frontend design-system refactors are protected by executable checks.
- Recommended action: keep these guards mandatory for every future frontend style story.
- Story candidate: no
- Files to modify: none.

### F-002 - CSS fallback debt remains active but is now a small, exact surface

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Evidence: E-003, E-009, E-012
- Expected rule: `var(--token, literal)` fallbacks should be rare, classified, and removed when the canonical token is guaranteed.
- Actual state: `CSS_FALLBACK_EXCEPTIONS` contains 10 exact entries. The source scan finds 10 lines across 9 CSS files. `--premium-radius-pill` is declared in `premium-theme.css`, but `--premium-text-muted` and `--premium-glass-border-soft` are consumed without canonical declarations and remain blocked by a product/theme decision.
- Impact: fallback literals still preserve alternate visual decisions beside the canonical token set.
- Recommended action: reduce non-decision fallbacks in one bounded batch, then resolve the premium token decision for `NatalChartPage.css` and `NatalInterpretation.css`.
- Story candidate: yes
- Exhaustive files to modify:
  - `frontend/src/App.css`
  - `frontend/src/components/NatalInterpretation.css`
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
- Actual state: 9 inline style attributes remain across 6 TSX files and are covered by exact allowlists.
- Impact: justified dynamic values still keep styling decisions in TSX, so the allowlist must not grow silently.
- Recommended action: keep runtime geometry and explicit style-prop pass-throughs, but remove or formalize the `Badge` color bridge and any width/left bridge that can become a CSS custom property without changing behavior.
- Story candidate: yes
- Exhaustive files to modify:
  - `frontend/src/layouts/TwoColumnLayout.tsx`
  - `frontend/src/layouts/TwoColumnLayout.css`
  - `frontend/src/components/DomainRankingCard.tsx`
  - `frontend/src/components/DomainRankingCard.css`
  - `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
  - `frontend/src/components/prediction/DayTimelineSectionV4.css`
  - `frontend/src/components/prediction/TimelineRail.tsx`
  - `frontend/src/components/prediction/TimelineRail.css`
  - `frontend/src/components/ui/Badge/Badge.tsx`
  - `frontend/src/components/ui/Badge/Badge.css`
  - `frontend/src/components/ui/Skeleton/Skeleton.tsx`
  - `frontend/src/components/ui/Skeleton/Skeleton.css`
  - `frontend/src/tests/inline-style-allowlist.ts`
  - `frontend/src/tests/design-system-allowlist.ts`

### F-004 - Hardcoded visual and typography decisions remain broad

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Evidence: E-011
- Expected rule: repeated color, spacing, radius, shadow, and typography decisions should converge toward semantic tokens, shared utilities, or exact classified exceptions.
- Actual state: the broad source scan finds 110 files with hardcoded visual or typography signals outside `design-tokens.css`, `theme.css`, and `premium-theme.css`.
- Impact: semantic tokens still compete with local literals across many product surfaces.
- Recommended action: continue phased migration by coherent product surface, with before/after counts and registry updates only when a durable semantic token or typography role is introduced.
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
  - `frontend/src/components/ui/Skeleton/Skeleton.test.tsx`
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
  - `frontend/src/styles/backgrounds.css`
  - `frontend/src/styles/glass.css`
  - `frontend/src/styles/utilities.css`
  - `frontend/src/tests/AdminPage.test.tsx`
  - `frontend/src/tests/AdminPromptsPage.test.tsx`
  - `frontend/src/tests/BottomNavPremium.test.tsx`
  - `frontend/src/tests/chat/ChatComponents.test.tsx`
  - `frontend/src/tests/HeroHoroscopeCard.test.tsx`
  - `frontend/src/tests/MiniInsightCard.test.tsx`
  - `frontend/src/tests/ShortcutCard.test.tsx`
  - `frontend/src/tests/visual-smoke.test.tsx`

### F-005 - Legacy selector and compatibility token surfaces still need exit work

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Evidence: E-005, E-012, E-013
- Expected rule: legacy selectors and compatibility token aliases should stay classified and shrink over time.
- Actual state: `legacy-style-surface-registry.md` contains 5 active classified rows. External-active admin prompt legacy selectors still live in `AdminPromptsPage.css`, and compatibility token aliases remain in `theme.css`.
- Impact: No Legacy remains controlled but active; future migrations must not treat the registry as permanent architecture.
- Recommended action: split route-specific admin prompts legacy markup/style migration from compatibility token retirement.
- Story candidate: yes
- Exhaustive files to modify:
  - `frontend/src/pages/admin/AdminPromptsPage.tsx`
  - `frontend/src/pages/admin/AdminPromptsPage.css`
  - `frontend/src/styles/theme.css`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/legacy-style-surface-registry.md`
  - `frontend/src/tests/legacy-style-policy.test.ts`
  - `frontend/src/tests/theme-tokens.test.ts`
  - `frontend/src/tests/design-system-guards.test.ts`

### F-006 - Build output remains oversized

- Severity: Info
- Confidence: High
- Category: observability-gap
- Evidence: E-007
- Expected rule: production build should remain operational; chunk-size warnings should be tracked separately from design-system correctness.
- Actual state: `npm run build` passes, but Vite warns that `assets/index-*.js` is above 500 kB after minification.
- Impact: this is not a design-system regression, but it remains a user-perceived performance risk if it grows.
- Recommended action: track under a separate frontend performance audit/story, not inside this design-system cleanup batch.
- Story candidate: no
- Files to modify: none in this audit.

## Validation Status

- PASS: `npm run test -- css-fallback inline-style legacy-style theme-tokens design-system visual-smoke`
- PASS: `npm run test`
- PASS: `npm run lint`
- PASS: `npm run build`, with non-blocking Vite chunk-size warning.

## Recommended Next Action

Start with `F-002`: remove guaranteed fallbacks outside the premium decision path, then decide whether `--premium-text-muted` and `--premium-glass-border-soft` become canonical premium tokens or are replaced by existing global tokens. After that, handle `F-003` only for inline styles that can move to CSS custom-property bridges without changing runtime geometry.
