<!-- Rapport principal de l'audit frontend design-system apres refactors du 2026-05-07. -->

# Audit Report - frontend-design-system

## Scope

- Domain target: `frontend-design-system`.
- Audit archetype: adapted `test-guard-coverage-audit` plus No Legacy/DRY and token ownership checks.
- Read-only mode: no application code was modified.
- Output folder: `_condamad/audits/frontend-design-system/2026-05-07-1730/`.
- Previous audited waves considered: `2026-05-04-2238` through `2026-05-07-1021`, plus delivered frontend stories evidenced by `CS-073` through `CS-085` final artifacts.

## Executive Result

The refactors delivered after the previous audits materially improved the frontend design-system state. The dedicated guards for token namespaces, page-scoped namespaces, CSS fallbacks, inline styles, No Legacy vocabulary, runtime compatibility removals, App, Settings, Help, Chat, UI shared components, Prediction premium and Landing all pass.

The remaining actionable debt is no longer the old 70-file list from `2026-05-07-1021`. After removing clusters now protected by exact guards, the current residual list is 50 CSS application files. These files still contain visual or typography literals that are not yet in a closed cluster evidence set.

## Finding Summary

| ID | Severity | Confidence | Category | Story candidate |
|---|---|---|---|---|
| F-001 | Info | High | missing-guard | no |
| F-002 | Medium | High | duplicate-responsibility | yes |
| F-003 | Info | High | legacy-surface | no |
| F-004 | Low | High | observability-gap | no |

## Findings

### F-001 - Frontend design-system guardrails remain active

- Evidence: E-001, E-002, E-003, E-004, E-005, E-006.
- Expected rule: the frontend design-system guard suite must protect token namespaces, typography roles, inline styles, CSS fallbacks, legacy style surfaces, runtime compatibility removals and migrated cluster literals.
- Actual state: targeted design-system tests, full Vitest, lint and build pass. The guard file includes a dedicated `CS-085` landing anti-return check and the delivered story evidence exists.
- Impact: positive invariant; future stories can rely on `RG-044` through `RG-060`.
- Recommended action: keep these guardrails mandatory for every frontend design-system story.

### F-002 - Residual hardcoded visual and typography ownership remains in 50 CSS files

- Evidence: E-003, E-007, E-008.
- Expected rule: repeated visual and typography decisions should converge to global tokens, documented semantic token namespaces, component/page semantic variables, or typography roles.
- Actual state: the raw scan still finds candidate literals in 86 application CSS files outside `frontend/src/styles/**`; after excluding clusters already closed by exact guards and final story evidence, 50 CSS files remain actionably unclosed.
- Impact: Medium maintainability and DRY risk; multiple local files still own similar visual decisions without a final cluster-level migration record.
- Recommended action: migrate the remaining files by bounded clusters and update exact guards.
- Story candidate: SC-001.

### F-003 - Previously active frontend legacy and compatibility surfaces are closed or classified

- Evidence: E-002, E-003, E-004, E-009, E-010.
- Expected rule: removed compatibility behavior, legacy routes, stale style vocabulary, non-classified fallbacks and static inline styles must not return.
- Actual state: design-system guards pass; exact inline-style and CSS fallback allowlists remain limited to known dynamic/custom-property bridges. CSS No Legacy scan hits are either words inside legitimate fallback UI class names or admin prompt graph domain terms already covered by tests.
- Impact: no new No Legacy implementation defect found in the audited frontend design-system scope.
- Recommended action: preserve the current guard coverage and avoid broad allowlists.

### F-004 - Production bundle warning remains visible

- Evidence: E-006.
- Expected rule: frontend build must pass; warnings outside visual ownership should be separated from design-system convergence.
- Actual state: build passes and Vite still reports `assets/index-Dg5Awx35.js` above 500 kB.
- Impact: low performance follow-up risk, not a design-system ownership defect.
- Recommended action: track in a separate `frontend-performance` audit/story if needed.

## Exhaustive Files To Modify For F-002

These are the current actionable CSS files after excluding clusters closed by exact guards and final evidence. A future story should choose coherent subsets; the list is exhaustive for the current residual design-system ownership finding.

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
- `frontend/src/components/prediction/DayAgenda.css`
- `frontend/src/components/prediction/DayPredictionCard.css`
- `frontend/src/components/prediction/DayTimeline.css`
- `frontend/src/components/prediction/DayTimelineSectionV4.css`
- `frontend/src/components/prediction/KeyPointCard.css`
- `frontend/src/components/prediction/PeriodCard.css`
- `frontend/src/components/prediction/SectionTitle.css`
- `frontend/src/components/prediction/TimelineRail.css`
- `frontend/src/components/prediction/TurningPointsList.css`
- `frontend/src/components/settings/DeleteAccountModal.css`
- `frontend/src/components/ShortcutCard.css`
- `frontend/src/components/SignUpForm.css`
- `frontend/src/components/TurningPointCard.css`
- `frontend/src/index.css`
- `frontend/src/layouts/AdminLayout.css`
- `frontend/src/layouts/PageLayout.css`
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
- `frontend/src/pages/ConsultationResultPage.css`
- `frontend/src/pages/DashboardPage.css`
- `frontend/src/pages/NatalChartPage.css`
- `frontend/src/pages/PrivacyPolicyPage.css`

## Governance Files Likely To Modify With Any F-002 Story

- `frontend/src/styles/design-tokens.css` - only if a repeated value belongs in global tokens.
- `frontend/src/styles/theme.css` - only if a shared semantic app/theme token is the canonical owner.
- `frontend/src/styles/premium-theme.css` - only if a premium semantic token is reused or extended.
- `frontend/src/styles/token-namespace-registry.md` - required for every new or changed semantic namespace.
- `frontend/src/styles/typography-roles.md` - required for new or changed typography roles.
- `frontend/src/tests/design-system-guards.test.ts` - required for exact anti-return guards.
- `frontend/src/tests/theme-tokens.test.ts` - required when namespace or token registry behavior changes.
- `frontend/src/tests/css-fallback-policy.test.ts` - preserve exact fallback policy.
- `frontend/src/tests/inline-style-policy.test.ts` - preserve no static inline styles.
- `frontend/src/tests/legacy-style-policy.test.ts` - preserve No Legacy CSS vocabulary policy.
- `frontend/src/tests/visual-smoke.test.tsx` - update only when rendered critical surfaces need coverage.
- `frontend/src/tests/design-system-allowlist.ts` - update only for exact, justified exceptions; no broad folder allowlist.

## Recommended Next Clusters

- Admin CSS cluster: `frontend/src/pages/admin/*.css` plus `frontend/src/layouts/AdminLayout.css`.
- Prediction remainder cluster: `frontend/src/components/prediction/*.css` excluding already-closed premium files.
- Natal/profile cluster: `frontend/src/pages/NatalChartPage.css`, `frontend/src/components/NatalInterpretation.css`, `frontend/src/pages/AstrologerProfilePage.css`.
- Shared shell/components cluster: layout, header/sidebar, cards and remaining shared component CSS.
- Account/billing/public pages cluster: birth profile, consultation result, privacy, billing return, signup and delete account modal.

## Validation

- `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke App FaqSection`: PASS.
- `npm run test`: PASS, 115 files, 1258 passed, 8 skipped.
- `npm run lint`: PASS.
- `npm run build`: PASS with Vite chunk-size warning.
