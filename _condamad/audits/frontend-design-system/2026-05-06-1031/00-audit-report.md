<!-- Rapport d'audit du domaine frontend design-system apres refactors CS-071 a CS-073. -->

# Audit Report - frontend-design-system

## Scope

- Target domain: `frontend-design-system`
- Archetype: `legacy-surface-audit` with `test-guard-coverage-audit`, `dependency-direction-audit` and `duplicate-rule-removal` dimensions.
- Mode: read-only for application code; audit artifacts written under `_condamad/audits/frontend-design-system/2026-05-06-1031/`.
- Context: follow-up after audits `2026-05-04-2238`, `2026-05-05-1411`, `2026-05-05-1501`, `2026-05-05-1748`, `2026-05-05-1831`, `2026-05-05-1942`, `2026-05-05-2053`, `2026-05-06-0016`, `2026-05-06-0108`, `2026-05-06-0705`, `2026-05-06-0806`, `2026-05-06-0932`.

## Applicable Guardrails

- `RG-044`: frontend CSS token namespaces.
- `RG-045`: frontend hardcoded visual values.
- `RG-046`: frontend typography roles.
- `RG-047`: frontend inline styles.
- `RG-048`: frontend CSS fallbacks.
- `RG-049`: frontend legacy style surfaces.
- `RG-050`: frontend design-system anti-drift suite.

## Summary

CS-071, CS-072 and CS-073 closed the latest targeted debts from the prior audit:

- `.astrologer-card-alias` and other alias/legacy CSS selectors are zero-hit.
- `frontend/src/i18n/consultations.ts` no longer contains `legacy|Legacy`.
- CSS fallbacks remain limited to the two classified `--usage-progress` runtime bridges.
- Inline styles remain limited to the five classified dynamic exceptions.
- The frontend guard suite, lint and build pass.

The remaining actionable debt is now more structural:

- 101 non-test files still contain hardcoded visual or typography literals.
- `HelpPage.css` consumes `--settings-*` variables owned by `Settings.css`.
- `--settings-*`, `--profile-*`, `--astro-*` remain migration-only, and the stale `--default_dropshadow` row remains in the token registry even though runtime usage is zero.
- Frontend compatibility paths remain active for consultations, prediction payloads and admin redirects without one shared classification registry.

## Findings

See `02-finding-register.md` for full finding details.

| ID | Severity | Category | Story candidate |
|---|---|---|---|
| F-001 | Info | missing-guard | no |
| F-002 | Info | legacy-surface | no |
| F-003 | Medium | duplicate-responsibility | yes |
| F-004 | Medium | dependency-direction-violation | yes |
| F-005 | Medium | legacy-surface | yes |
| F-006 | Medium | legacy-surface | yes |
| F-007 | Medium | legacy-surface | yes |
| F-008 | Low | observability-gap | no |

## Exhaustive Files To Modify By Finding

### F-004: HelpPage depends on Settings tokens

- `frontend/src/pages/HelpPage.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/tests/design-system-guards.test.ts`
- Optional shared helper if the guard is centralized: `frontend/src/tests/design-system-policy.ts`

### F-005: Migration-only token namespace convergence

- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/App.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/pages/AstrologerProfilePage.css`
- `frontend/src/tests/design-system-guards.test.ts`
- Optional if token expectations change: `frontend/src/tests/theme-tokens.test.ts`

### F-006: Frontend runtime compatibility registry

- `frontend/src/types/consultation.ts`
- `frontend/src/pages/ConsultationWizardPage.tsx`
- `frontend/src/pages/ConsultationResultPage.tsx`
- `frontend/src/features/consultations/components/ConsultationTypeStep.tsx`
- `frontend/src/features/consultations/components/ConsultationFormStep.tsx`
- `frontend/src/utils/bestWindowCardMapper.ts`
- `frontend/src/utils/domainRankingCardMapper.ts`
- `frontend/src/utils/dayClimateHeroMapper.ts`
- `frontend/src/utils/predictionI18n.ts`
- `frontend/src/utils/turningPointCardMapper.ts`
- `frontend/src/components/prediction/DayTimeline.tsx`
- `frontend/src/components/prediction/TurningPointsList.tsx`
- `frontend/src/tests/ConsultationMigration.test.tsx`
- `frontend/src/tests/consultationStore.test.ts`
- Add one registry file, recommended path pending repo convention: `frontend/src/styles/frontend-compatibility-registry.md` or an equivalent docs location.

### F-007: Admin legacy redirects

- `frontend/src/app/routes.tsx`
- `frontend/src/tests/AdminPage.test.tsx`
- The compatibility registry created for F-006, if route redirects are retained.

### F-003: Hardcoded visual and typography values

The following 101 files are the exhaustive candidate files returned by the non-test scan after excluding `src/styles/**`. A story must choose a bounded subset rather than modifying all files in one pass.

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

## Validation

- `npm run test -- legacy-style ConsultationMigration consultationStore design-system theme-tokens css-fallback inline-style visual-smoke HelpPage`: PASS.
- `npm run lint`: PASS.
- `npm run build`: PASS with chunk-size warning.

## Recommended Next Action

Create the next story from `SC-001`, because it has the smallest blast radius and fixes an actual dependency-direction problem in `HelpPage.css`. Then handle `SC-002` to clean the registry and active migration-only token namespaces.
