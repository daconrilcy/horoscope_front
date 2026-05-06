<!-- Audit CONDAMAD read-only du domaine frontend design-system apres refactors. -->

# Frontend Design-System Audit - 2026-05-06 08:06

## Scope

- Domain target: `frontend/src` design-system governance.
- Archetype: `legacy-surface-audit` with No Legacy / DRY contract.
- Mode: read-only audit after stories from previous frontend design-system audits and CS-067.
- Guardrails consulted: `_condamad/stories/regression-guardrails.md`, especially `RG-044` to `RG-050`.

## Executive Result

The latest refactors closed the specific CS-067 selector and global alias targets:

- `admin-prompts-legacy` and `admin-prompts-modal--legacy-rollback` have zero active hits in `frontend/src`.
- Global `--text-*`, `--glass*`, and `--primary*` aliases are no longer active in `theme.css`, `App.css`, `index.css`, or `legacy-style-surface-registry.md`.
- CSS fallbacks are reduced to two dynamic `--usage-progress` bridges.
- Inline styles are reduced to five exact allowlisted dynamic/style-prop exceptions.

Remaining work is now concentrated in compatibility/migration token namespaces, hardcoded visual values, and the still-visible product concept named `legacy` in the admin prompts UI.

## Findings Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 3 |
| Low | 1 |
| Info | 2 |

## Findings

### F-001 - Design-system guardrails are green

- Severity: Info
- Evidence: `E-001`, `E-002`, `E-003`, `E-004`, `E-005`, `E-006`
- Result: the executable guards for tokens, fallbacks, inline styles, legacy selectors, lint and build pass.
- Action: keep `RG-044` to `RG-050` mandatory for future frontend style stories.

### F-002 - Compatibility and migration token namespaces remain active

- Severity: Medium
- Evidence: `E-007`, `E-008`, `E-009`, `E-010`
- Result: many consumers still use namespaces classified as compatibility or migration-only: `--bg-*`, `--cta-*`, `--badge-*`, `--nav-*`, `--line`, `--success`, `--danger`, `--btn-text`, `--purple_base`, `--background-*`, `--ni-*`, `--result-*`, `--timeline-*`, `--page-*`, `--inner-light`, `--accent-purple*`.
- Impact: canonical tokens compete with local aliases, which keeps No Legacy debt active even though guards prevent unclassified growth.
- Files to modify:
  - `frontend/src/App.css`
  - `frontend/src/index.css`
  - `frontend/src/styles/theme.css`
  - `frontend/src/styles/backgrounds.css`
  - `frontend/src/hooks/useDailyInsights.ts`
  - `frontend/src/utils/predictionI18n.ts`
  - `frontend/src/layouts/AdminLayout.css`
  - `frontend/src/components/AdminGuard.css`
  - `frontend/src/components/AstroDailyEvents.css`
  - `frontend/src/components/BestWindowCard.css`
  - `frontend/src/components/DayClimateHero.css`
  - `frontend/src/components/DomainRankingCard.css`
  - `frontend/src/components/ErrorBoundary/ErrorBoundary.css`
  - `frontend/src/components/HeroHoroscopeCard.css`
  - `frontend/src/components/MiniInsightCard.css`
  - `frontend/src/components/NatalInterpretation.css`
  - `frontend/src/components/ShortcutsSection.tsx`
  - `frontend/src/components/SignUpForm.css`
  - `frontend/src/components/TurningPointCard.css`
  - `frontend/src/components/astro/AstroMoodBackground.css`
  - `frontend/src/components/layout/Header.css`
  - `frontend/src/components/layout/Sidebar.css`
  - `frontend/src/components/prediction/CategoryGrid.css`
  - `frontend/src/components/prediction/DailyAdviceCard.css`
  - `frontend/src/components/prediction/DailyPageHeader.css`
  - `frontend/src/components/prediction/DayAgenda.css`
  - `frontend/src/components/prediction/DayPredictionCard.css`
  - `frontend/src/components/prediction/DayStateBadge.css`
  - `frontend/src/components/prediction/DayTimelineSectionV4.css`
  - `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
  - `frontend/src/components/prediction/PeriodCard.css`
  - `frontend/src/components/prediction/SectionTitle.css`
  - `frontend/src/components/ui/Badge/Badge.tsx`
  - `frontend/src/pages/ConsultationResultPage.css`
  - `frontend/src/pages/DailyHoroscopePage.css`
  - `frontend/src/pages/HelpPage.css`
  - `frontend/src/pages/admin/AdminAiGenerationsPage.css`
  - `frontend/src/pages/admin/AdminContentPage.css`
  - `frontend/src/pages/admin/AdminEntitlementsPage.css`
  - `frontend/src/pages/admin/AdminLogsPage.css`
  - `frontend/src/pages/admin/AdminSettingsPage.css`
  - `frontend/src/pages/admin/AdminUserDetailPage.css`
  - `frontend/src/pages/admin/PersonasAdmin.css`
  - `frontend/src/pages/landing/sections/TestimonialsSection.css`
  - test consumers to update with canonical names: `frontend/src/tests/BottomNavPremium.test.tsx`, `frontend/src/tests/MiniInsightCard.test.tsx`, `frontend/src/tests/ShortcutCard.test.tsx`, `frontend/src/tests/predictionBands.test.ts`, `frontend/src/tests/visual-smoke.test.tsx`

### F-003 - Hardcoded visual values remain broad

- Severity: Medium
- Evidence: `E-011`
- Result: hardcoded color, spacing, radius, shadow and typography values still appear across broad CSS surfaces, including high-count files such as `App.css`, `HelpPage.css`, `AdminPromptsPage.css`, `Settings.css`, `AstrologerProfilePage.css`, `NatalInterpretation.css`, `NatalChartPage.css`, and landing sections.
- Impact: DRY remains partial; design decisions can diverge from semantic tokens by product surface.
- Files to modify: see exhaustive hardcoded-value file inventory in `01-evidence-log.md` under `E-011`.

### F-004 - Admin prompts still exposes a runtime "legacy" product surface

- Severity: Medium
- Evidence: `E-012`, `E-013`, `E-014`
- Result: selector-level legacy debt was removed, but `AdminPromptsPage.tsx`, `adminPromptsLegacy.ts`, `admin.ts` and tests still expose tab names, state names, ARIA labels and copy containing `legacy`.
- Impact: this may be valid product language, but it is still an active legacy domain concept and should be renamed or explicitly accepted by product.
- Files to modify:
  - `frontend/src/pages/admin/AdminPromptsPage.tsx`
  - `frontend/src/i18n/adminPromptsLegacy.ts`
  - `frontend/src/i18n/admin.ts`
  - `frontend/src/tests/AdminPromptsPage.test.tsx`

### F-005 - CSS fallbacks are now exact dynamic exceptions

- Severity: Info
- Evidence: `E-015`, `E-016`
- Result: only two fallbacks remain and both are classified dynamic runtime bridges.
- Action: no cleanup story needed unless `--usage-progress` ownership changes.

### F-006 - Build still reports oversized main JS chunk

- Severity: Low
- Evidence: `E-006`
- Result: build is green but Vite reports a 1,374.80 kB main chunk.
- Action: track separately under frontend performance, not as a design-token cleanup.

## Story Candidates

- `SC-001`: converge compatibility and migration token namespaces.
- `SC-002`: migrate the next hardcoded visual-value clusters by file group.
- `SC-003`: decide and rename or formally classify the admin prompts legacy product surface.

