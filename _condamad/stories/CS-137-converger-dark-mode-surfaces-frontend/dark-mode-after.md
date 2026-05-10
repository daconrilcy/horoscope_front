# CS-137 dark mode after

Implementation date: 2026-05-10

## Changed owners

- `frontend/src/styles/app/tokens.css`: dark overrides for app activity, summary panel and astrologer catalog/card tokens.
- `frontend/src/styles/app/tokens.css`: dark overrides for premium page layout tokens scoped on `.dark #root` so `/consultations` consumes them at runtime.
- `frontend/src/layouts/LandingLayout.css`: dark landing layout variables for public surfaces, navbar, language selector and hero cards.
- `frontend/src/pages/PrivacyPolicyPage.css`: explicit privacy page link colors.
- `frontend/src/components/ui/UserAvatar/UserAvatar.css`: stronger avatar dark contrast.
- `frontend/src/components/ShortcutCard.css`: dark dashboard activity card, title and subtitle surfaces.
- `frontend/src/pages/AstrologerProfilePage.css`: dark astrologer profile page variables and surface overrides.
- `frontend/src/pages/HelpPage.css`: dark help/subscription variables.
- `frontend/src/pages/settings/Settings.css`: dark settings variables for cards, accents, text, feedback and progress surfaces.
- `frontend/src/pages/NatalChartPage.css`: dark natal background, CTA, data cards, aspect cards and pills.
- `frontend/src/features/natal-chart/NatalInterpretation.css`: dark interpretation controls, notices, modal and evidence pills.
- `frontend/src/pages/ChatPage.css`: dark chat shell/card/control variables.
- `frontend/src/pages/ConsultationResultPage.css`: dark result page background, cards and back link.
- `frontend/src/styles/app/cards.css`: explicit dashboard title, intro and section heading colors for dark visibility.
- `frontend/src/tests/design-system-guards.test.ts`: CS-137 guard for owners, default blue links, `App.css` isolation, `/consultations` premium tokens and astrologer profile ownership.
- `frontend/e2e/dark-mode-cs137.spec.ts`: runtime guard for the visible `/dashboard` page, `/consultations` and `/astrologers/:id` in `html.dark`.

## Verification

Commands run from `frontend`:

```powershell
npm run test -- theme-tokens design-system visual-smoke
```

Result:

- Test files: 3 passed
- Tests: 151 passed

Targeted runtime dark audit:

```powershell
npm run test:e2e -- dark-mode-cs137.spec.ts
```

Result:

- Test files: 1 passed
- Tests: 3 passed
- Covered routes: `/dashboard`, `/consultations`, `/astrologers/:id`
- `/dashboard` checks: page title, welcome text, horoscope summary text, horoscope CTA background/color, zodiac pill, activity cards and click navigation to `/dashboard/horoscope`

Full frontend suite:

```powershell
npm run test
```

Result:

- Test files: 114 passed
- Tests: 1216 passed, 8 skipped

Additional targeted rerun after full-suite transient dashboard/router failures:

```powershell
npm run test -- DashboardPage router
```

Result:

- Test files: 3 passed
- Tests: 25 passed

Scans run from `frontend`:

```powershell
rg -n "#0000ee|rgb\(0, 0, 238\)|color:\s*blue" src -g "*.css" -g "*.scss"
rg -n "dark|html\.dark" src/App.css
rg -n "style=" src -g "*.tsx" -g "*.jsx"
```

Results:

- Default blue link scan: no result.
- `App.css` dark correction scan: no result.
- `style=` scan: only existing dynamic exceptions remain:
  - `src/components/DomainRankingCard.tsx`
  - `src/components/prediction/DayTimelineSectionV4.tsx`
  - `src/components/ui/Skeleton/Skeleton.tsx`

## Remaining risk

- The targeted Playwright audit covers the two routes missed by the initial implementation, but a full regenerated route-by-route audit over all original screenshots was not added in this pass.
- Admin audit entries still redirect to `/dashboard` with the current test fixture and are treated as duplicated dashboard evidence until an admin-role fixture is available.
