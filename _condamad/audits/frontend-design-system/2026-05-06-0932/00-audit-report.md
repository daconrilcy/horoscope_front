<!-- Audit CONDAMAD read-only du domaine frontend design-system apres refactors. -->

# Audit Report - frontend-design-system

## Scope

- Domain target: `frontend/src` design-system governance.
- Archetype: `legacy-surface-audit` plus No Legacy / DRY contract.
- Mode: read-only audit after implementation of the planned stories from audits `2026-05-04-2238` through `2026-05-06-0806`, including `CS-068`, `CS-069`, and `CS-070`.
- Guardrails consulted: `_condamad/stories/regression-guardrails.md`, especially `RG-044` to `RG-050`.

## Expected Responsibility

The frontend design-system layer must keep `frontend/src/styles/design-tokens.css` as the global token source of truth, keep local token namespaces classified, prevent unclassified CSS fallbacks and inline styles, classify or remove legacy style surfaces, and converge repeated visual literals into semantic tokens by bounded product clusters.

## Evidence Summary

- Guard tests are green for token namespaces, design-system drift, CSS fallbacks, inline styles, legacy selectors, admin prompts, and visual smoke (`E-001` to `E-006`).
- Lint and build pass (`E-007`, `E-008`), with the recurring Vite chunk warning still present.
- CSS fallbacks are reduced to exactly two dynamic `--usage-progress` bridges (`E-009`, `E-010`).
- Inline styles are reduced to exactly five allowlisted runtime/style-prop bridges (`E-011`, `E-012`).
- The CS-070 admin prompts runtime vocabulary migration is effective: `adminPromptsLegacy`, `AdminPromptsLegacyStrings`, `promptsLegacy`, `legacyTab`, `admin-prompts-legacy`, and `admin-prompts-modal--legacy-rollback` have zero active hits in the admin prompts runtime/test surface (`E-013`).
- Remaining design-system debt is now concentrated in hardcoded visual values outside token owner files, an unclassified `.astrologer-card-alias` style surface, and legacy wording in consultation i18n labels outside the admin prompts scope (`E-014` to `E-017`).

## Findings Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 3 |
| Low | 1 |
| Info | 3 |

## Key Findings

- `F-001`: Frontend design-system guardrails are green and should remain mandatory.
- `F-002`: CSS fallback debt is controlled; the only remaining fallbacks are dynamic runtime bridges.
- `F-003`: Inline-style debt is controlled; the only remaining styles are exact dynamic/style-prop exceptions.
- `F-004`: Hardcoded visual values remain broad across 106 application files outside the token-owner CSS files.
- `F-005`: `.astrologer-card-alias` remains an active alias-named CSS surface but is not classified in the legacy style registry.
- `F-006`: Consultation i18n still exposes user-visible `(Legacy)` labels outside the admin prompts refactor scope.
- `F-007`: The production build is green but still emits the oversized main chunk warning.

## Exhaustive Files To Modify

### F-004 - Hardcoded Visual / Typography Debt: 106 Files

These files are candidates for bounded hardcoded-value migration. They should not be migrated in one broad story; choose coherent product clusters and capture before/after counts.

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

### F-005 - Alias-Named CSS Surface: 3 Files

- `frontend/src/App.css`
- `frontend/src/features/astrologers/components/AstrologerCard.tsx`
- `frontend/src/styles/legacy-style-surface-registry.md`

### F-006 - Consultation Legacy Labels: 2 Files

- `frontend/src/i18n/consultations.ts`
- Focused tests to update/add with the chosen product decision, likely under `frontend/src/tests/ConsultationMigration.test.tsx` or a new focused consultation i18n test.

### F-007 - Build Chunk Warning: 2 Files

- `frontend/vite.config.ts`
- Route/module entry files selected by a dedicated performance story after bundle analysis.

## Regression Guardrails

- `RG-044`: applies to token namespace ownership and registry synchronization.
- `RG-045`: applies to repeated visual value migration.
- `RG-046`: applies to typography role migration.
- `RG-047`: applies to inline style policy.
- `RG-048`: applies to CSS fallback policy.
- `RG-049`: applies to legacy style surface classification.
- `RG-050`: applies to executable design-system drift guards.

## Recommendations

1. Implement `SC-001` first: classify or rename `.astrologer-card-alias`, and strengthen the legacy-style guard so alias-named selectors are not invisible when they do not contain `legacy`.
2. Implement `SC-002` as a product decision story for consultation i18n labels; do not silently rename user-visible labels without confirmation.
3. Continue hardcoded-value migration through `SC-003`, starting with a bounded surface with high repeat count such as `HelpPage.css`, `AdminPromptsPage.css`, `AstrologerProfilePage.css`, or prediction timeline CSS.
4. Track the Vite chunk warning separately under performance, not as a design-token cleanup.

## Validation Plan

- `npm run test -- AdminPromptsPage AdminPromptsRouting legacy-style design-system theme-tokens css-fallback inline-style visual-smoke`
- `npm run lint`
- `npm run build`
- Audit validation through the CONDAMAD domain auditor scripts from the repository root after activating `.venv`.
