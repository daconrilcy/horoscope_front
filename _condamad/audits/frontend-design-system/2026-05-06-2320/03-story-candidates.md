<!-- Candidates de stories issus de l'audit frontend design-system apres CS-081. -->

# Story Candidates - frontend-design-system

## SC-001 - Migrer le prochain cluster coherent de valeurs visuelles hardcodees frontend

- Candidate ID: SC-001
- Source finding: F-002
- Suggested story title: Migrer le prochain cluster coherent de valeurs visuelles hardcodees frontend
- Suggested archetype: design-system-token-convergence
- Primary domain: frontend-design-system
- Required contracts: `RG-044`, `RG-045`, `RG-046`, `RG-050`, `RG-058`, No Legacy/DRY, no inline style.
- Draft objective: Select one coherent product cluster from the exhaustive file inventory and replace repeated visual/typography literals with existing tokens, semantic local tokens or typography roles.
- Must include: before/after hardcoded literal inventory, exact modified-file list, no widened allowlist, updated guard for the migrated cluster, CSS-only styling changes unless the selected cluster requires TSX class extraction.
- Validation hints: `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`, targeted `rg --pcre2` scans for the selected files, `npm run lint`, `npm run build`.
- Blockers: Choose the next cluster. Recommended first cluster by evidence density: `App.css`, `HelpPage.css`, `Settings.css`, `AstrologerProfilePage.css`, `NatalInterpretation.css`, or landing CSS. Do not implement all 66 files in one story.

### Exhaustive Files To Modify For F-002

These 66 files are the exhaustive current candidates returned by the audit scan. A follow-up story should choose a coherent subset, but the total affected surface is:

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
- `frontend/src/components/prediction/DayAgenda.css`
- `frontend/src/components/prediction/DayPredictionCard.css`
- `frontend/src/components/prediction/DayTimeline.css`
- `frontend/src/components/prediction/DayTimelineSectionV4.css`
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
- `frontend/src/components/prediction/KeyPointCard.css`
- `frontend/src/components/prediction/PeriodCard.css`
- `frontend/src/components/prediction/SectionTitle.css`
- `frontend/src/components/prediction/TimelineRail.css`
- `frontend/src/components/prediction/TurningPointsList.css`
- `frontend/src/components/ShortcutCard.css`
- `frontend/src/components/SignUpForm.css`
- `frontend/src/components/SignUpForm.tsx`
- `frontend/src/components/TurningPointCard.css`
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

## SC-002 - Fermer la garde No Legacy sur le vocabulaire CSS actif

- Candidate ID: SC-002
- Source finding: F-003
- Suggested story title: Fermer la garde No Legacy sur le vocabulaire CSS actif
- Suggested archetype: architecture-guard-hardening
- Primary domain: frontend-design-system
- Required contracts: `RG-049`, `RG-050`, `RG-057`, No Legacy/DRY.
- Draft objective: Remove the stale `legacy` CSS comment in `AdminPromptsPage.css` or replace it with canonical product wording, then extend the guard so active CSS comments cannot keep unclassified legacy/compatibility vocabulary.
- Must include: exact source cleanup, guard update, no selector alias or route change, no new registry exception unless the wording is intentionally retained with owner and exit condition.
- Validation hints: `npm run test -- design-system legacy-style`, targeted `rg -n --glob "*.css" -- "--default_dropshadow|migration-only|compatibility|legacy|alias" frontend/src`, `npm run lint`.
- Blockers: If the wording is product vocabulary rather than stale legacy language, classify it explicitly; otherwise remove it.

### Exhaustive Files To Modify For F-003

- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/tests/design-system-guards.test.ts`
- Optional only if retaining an exception: `frontend/src/styles/legacy-style-surface-registry.md`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - token namespace ownership applies to any new semantic token.
  - `RG-045` - hardcoded values migrated in previous stories must not return.
  - `RG-046` - typography roles remain canonical for repeated type decisions.
  - `RG-047` - static inline styles remain forbidden.
  - `RG-048` - CSS fallbacks remain exact and classified.
  - `RG-049` - legacy style surfaces require owner, target and exit condition.
  - `RG-050` - design-system anti-drift guards must remain executable.
  - `RG-051` through `RG-058` - recent frontend refactors must not regress.
- Required regression evidence:
  - Focused frontend guard run.
  - Targeted No Legacy scans.
  - Before/after inventories for any selected hardcoded cluster.
- Allowed differences: none unless explicitly documented in a story.
