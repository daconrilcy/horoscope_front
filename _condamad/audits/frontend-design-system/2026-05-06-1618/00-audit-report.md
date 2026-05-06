<!-- Rapport d'audit frontend design-system apres refactors. -->

# Audit Report - frontend-design-system

## Scope

- Target domain: `frontend-design-system`
- Comparative context: previous audits under `_condamad/audits/frontend-design-system/2026-05-04-2238` through `2026-05-06-1031`.
- Archetype used: `legacy-surface-audit` with `test-guard-coverage-audit` evidence, adapted to the bounded frontend design-system and frontend compatibility surface requested by the user.
- Mode: read-only for application code; audit artifacts written under `_condamad/audits/frontend-design-system/2026-05-06-1618/`.

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
- `RG-053` - runtime compatibility removal/classification.
- `RG-054` - legacy admin redirects.
- `RG-055` - prediction premium visual literals.

## Summary

The refactors materially improved the design-system state:

- focused guard suite passes: 12 files, 194 tests;
- lint passes;
- build passes;
- `HelpPage.css` no longer consumes `--settings-*`;
- `--settings-*`, `--profile-*`, and `--astro-*` are registered as semantic extensions instead of migration-only namespaces;
- `--default_dropshadow` is no longer present in the scanned token surfaces;
- legacy admin redirects `/admin/pricing`, `/admin/monitoring`, and `/admin/personas` have zero hits;
- CSS fallbacks are reduced to two dynamic `--usage-progress` exceptions;
- TSX inline styles are reduced to five exact allowlisted runtime/style-prop exceptions.

Remaining audit findings are narrower than the previous audits: broad hardcoded visual/typography literals remain, and a small runtime compatibility surface still needs classification.

## Findings

| ID | Severity | Category | Story candidate |
|---|---|---|---|
| F-001 | Info | missing-guard | no |
| F-002 | Medium | duplicate-responsibility | yes |
| F-003 | Medium | legacy-surface | yes |
| F-004 | Low | observability-gap | no |

## Exhaustive Files To Modify By Finding

### F-002: Hardcoded visual and typography literals

The following 101 files are the exhaustive candidate files returned by the non-test scan after excluding `src/styles/**`. A story must choose a bounded subset rather than modifying all files in one pass.

- `frontend/src/App.css`
- `frontend/src/index.css`
- `frontend/src/components/AdminGuard.css`
- `frontend/src/components/AstroDailyEvents.css`
- `frontend/src/components/AstroFoundationSection.css`
- `frontend/src/components/astro/AstroMoodBackground.tsx`
- `frontend/src/components/astro/AstroMoodBackground.css`
- `frontend/src/layouts/AdminLayout.css`
- `frontend/src/components/BestWindowCard.css`
- `frontend/src/layouts/LandingLayout.css`
- `frontend/src/layouts/AuthLayout.css`
- `frontend/src/components/ConstellationSVG.tsx`
- `frontend/src/pages/AstrologerProfilePage.css`
- `frontend/src/pages/admin/AdminAiGenerationsPage.css`
- `frontend/src/layouts/WizardLayout.css`
- `frontend/src/pages/BirthProfilePage.css`
- `frontend/src/components/DayClimateHero.css`
- `frontend/src/layouts/PageLayout.css`
- `frontend/src/layouts/TwoColumnLayout.tsx`
- `frontend/src/pages/admin/AdminContentPage.css`
- `frontend/src/features/chat/components/ChatComposer.css`
- `frontend/src/pages/billing/billing-return.css`
- `frontend/src/layouts/TwoColumnLayout.css`
- `frontend/src/pages/admin/AdminDashboardPage.css`
- `frontend/src/pages/admin/AdminEntitlementsPage.css`
- `frontend/src/components/DomainRankingCard.css`
- `frontend/src/pages/ConsultationResultPage.css`
- `frontend/src/pages/admin/AdminLogsPage.css`
- `frontend/src/components/HeroHoroscopeCard.css`
- `frontend/src/pages/DashboardPage.css`
- `frontend/src/features/chat/components/ChatPageHeader.css`
- `frontend/src/components/ErrorBoundary/ErrorBoundary.css`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/pages/ChatPage.css`
- `frontend/src/features/chat/components/ChatQuotaBanner.css`
- `frontend/src/features/chat/components/ConversationItem.css`
- `frontend/src/features/chat/components/ChatWindow.css`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/features/chat/components/ConversationList.css`
- `frontend/src/pages/admin/AdminSamplePayloadsAdmin.css`
- `frontend/src/pages/admin/AdminSettingsPage.css`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/components/MiniInsightCard.css`
- `frontend/src/pages/admin/AdminSupportPage.css`
- `frontend/src/components/NatalInterpretation.css`
- `frontend/src/components/icons/DashboardIcons.tsx`
- `frontend/src/components/prediction/CategoryGrid.css`
- `frontend/src/pages/admin/AdminUserDetailPage.css`
- `frontend/src/pages/admin/AdminUsersPage.css`
- `frontend/src/components/layout/Sidebar.css`
- `frontend/src/pages/landing/LandingPage.css`
- `frontend/src/components/layout/Header.css`
- `frontend/src/components/prediction/DailyAdviceCard.css`
- `frontend/src/pages/support/SupportTicketList.tsx`
- `frontend/src/pages/admin/PersonasAdmin.css`
- `frontend/src/pages/landing/sections/FaqSection.css`
- `frontend/src/components/ShortcutCard.css`
- `frontend/src/components/prediction/DailyPageHeader.css`
- `frontend/src/components/SignUpForm.css`
- `frontend/src/pages/landing/sections/LandingFooter.css`
- `frontend/src/pages/landing/sections/LandingNavbar.css`
- `frontend/src/components/SignUpForm.tsx`
- `frontend/src/pages/landing/sections/PricingSection.css`
- `frontend/src/pages/landing/sections/ProblemSection.css`
- `frontend/src/components/TurningPointCard.css`
- `frontend/src/pages/PrivacyPolicyPage.css`
- `frontend/src/components/settings/DeleteAccountModal.css`
- `frontend/src/components/prediction/DayTimeline.css`
- `frontend/src/components/prediction/DayPredictionCard.tsx`
- `frontend/src/pages/landing/sections/SocialProofSection.css`
- `frontend/src/pages/NatalChartPage.css`
- `frontend/src/pages/landing/sections/SolutionSection.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/components/prediction/DayPredictionCard.css`
- `frontend/src/pages/landing/sections/TestimonialsSection.css`
- `frontend/src/components/prediction/DayAgenda.css`
- `frontend/src/components/prediction/DayStateBadge.css`
- `frontend/src/components/prediction/DayTimelineSectionV4.css`
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
- `frontend/src/components/prediction/DecisionWindowsSection.tsx`
- `frontend/src/components/prediction/DayTimelineSection.css`
- `frontend/src/components/ui/Badge/Badge.css`
- `frontend/src/components/prediction/KeyPointCard.css`
- `frontend/src/components/prediction/PeriodCard.css`
- `frontend/src/components/prediction/PeriodCardsRow.css`
- `frontend/src/components/ui/EmptyState/EmptyState.css`
- `frontend/src/components/prediction/SectionTitle.css`
- `frontend/src/components/ui/Button/Button.css`
- `frontend/src/components/ui/Card/Card.css`
- `frontend/src/components/ui/Field/Field.css`
- `frontend/src/components/prediction/TimelineRail.css`
- `frontend/src/components/ui/ErrorState/ErrorState.css`
- `frontend/src/components/prediction/TurningPointsList.css`
- `frontend/src/components/ui/Modal/Modal.css`
- `frontend/src/components/ui/Skeleton/Skeleton.tsx`
- `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.css`
- `frontend/src/components/ui/Skeleton/Skeleton.css`
- `frontend/src/components/ui/Select/Select.css`
- `frontend/src/components/ui/LockedSection/LockedSection.css`
- `frontend/src/components/ui/UserMenu/UserMenu.css`
- `frontend/src/components/ui/UserAvatar/UserAvatar.css`

### F-003: Frontend runtime compatibility paths

These five files are the exhaustive files to modify or classify for the remaining explicit compatibility vocabulary found by E-009:

- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/utils/dailySummaryHelper.ts`
- `frontend/src/i18n/predictions.ts`
- `frontend/src/components/DailyInsightsSection.tsx`
- `frontend/src/components/NatalInterpretation.tsx`

Recommended optional artifact if compatibility remains intentional:

- `frontend/src/styles/frontend-compatibility-registry.md` or another repo-approved frontend docs location.

### F-001: Guard preservation

No application file modification is required. Keep these files in scope for validation only:

- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/styles/legacy-style-surface-registry.md`

### F-004: Bundle warning

No design-system application file is prescribed by this audit. A separate performance story would inspect routing and chunk ownership before naming files.

## Validation

- `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke HelpPage AdminPage ConsultationMigration consultationStore TurningPointsEnriched DailyHoroscopePage`: PASS.
- `npm run lint`: PASS.
- `npm run build`: PASS with Vite chunk-size warning.

## Recommended Next Action

Create one bounded story for `SC-001` first, selecting a coherent file cluster from the 101-file list. Run `SC-002` separately because compatibility semantics need product/contract decisions and should not be mixed with visual token migration.
