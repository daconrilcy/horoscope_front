# CS-130 - Final evidence

Status: ready-to-review

## Summary

Implemented a canonical non-admin central width at layout level and removed competing page-level width caps from non-admin pages. Admin width ownership is unchanged.
Review-fix pass removed one missed active cap on `/astrologers` and deleted stale Dashboard CSS selectors that were no longer consumed by the route.

## Files changed

- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/backgrounds.css`
- `frontend/src/styles/app/layout.css`
- `frontend/src/styles/app/cards.css`
- `frontend/src/layouts/PageLayout.css`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/pages/ChatPage.css`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/pages/DashboardPage.css` (deleted)
- `frontend/src/pages/NatalChartPage.css`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/billing/billing-return.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/pages/AstrologerProfilePage.css`
- `frontend/src/pages/ConsultationResultPage.css`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/AppBgStyles.test.ts`
- `frontend/e2e/layout-width-cs130.spec.ts`
- `_condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/layout-width-before.md`
- `_condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/layout-width-after.md`
- `_condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/generated/*.md`
- `_condamad/stories/story-status.md`

## Validation

| Command | Result |
|---|---|
| `npm run test -- design-system page-architecture layout` | PASS, 62 tests |
| `npm run test -- AppShell visual-smoke` | PASS, 22 tests |
| `npm run test -- AstrologersPage AstrologerProfilePage DailyHoroscopePage NatalChartPage SubscriptionGuidePage ConsultationResultPage` | PASS for discovered suites, 120 tests |
| `npm run test -- design-system AppBgStyles DashboardPage AstrologersPage visual-smoke page-architecture layout` | PASS, 166 tests |
| `npm run test -- BillingSuccessPage BillingCancelPage design-system AppBgStyles DashboardPage AstrologersPage visual-smoke page-architecture layout` | PASS, 177 tests |
| `npx playwright test e2e/layout-width-cs130.spec.ts` | PASS, 1 test |
| `npm run lint` | PASS |
| `npm run test` | PASS, 113 files, 1209 tests passed, 8 skipped (user rerun evidence at 16:58:39) |
| `npm run test -- router` | PASS, 11 tests |
| `npm run test -- AdminPromptsPage.releaseCatalog.integration` | PASS, 1 test |
| `npm run test -- --maxWorkers=1` | BLOCKED/TIMEOUT after 4 minutes in this environment |
| `npm run test:e2e` | FAIL, unrelated existing E2E assertions: dashboard AC4/AC5 selectors `.mini-cards-grid` / `.hero-card__constellation-svg` absent from current `/dashboard`, and admin prompts CTA selector timed out. CS-130 targeted E2E passed. |
| `rg -n -g "*.css" -- "max-width:\s*(900px|1100px|1200px|none\s*!important)|--layout-max-width|app-bg-container:has|overflow-x:\s*hidden" src/pages src/layouts src/styles` | PASS with classified residual hits: landing/public section and media query breakpoints |
| `rg -n "DashboardPage\.css|dashboard-container|dashboard-title|dashboard-welcome|dashboard-header|dashboard-container__bg" src -g "*.tsx" -g "*.ts" -g "*.css"` | PASS, only admin dashboard names remain |
| `rg -n -g "*.css" -g "*.tsx" -- "layout-admin-max-width|app-bg-container--admin|admin-container" src/layouts src/styles src/pages/admin` | PASS, admin owner unchanged |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/00-story.md` | PASS |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/00-story.md` | PASS |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/00-story.md` | PASS |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/00-story.md` | PASS |
| `npm run dev -- --host 127.0.0.1` | PASS, Vite started at `http://127.0.0.1:5174/` because `5173` was already in use |
| static guard `rg -n "fetch\(|axios\." ...` | PASS for modified files; broader page scan only matched `refetch` substrings, not direct HTTP |
| static guard `rg -n "\bany\b" ...` | PASS, no hits in modified frontend files |
| static guard `rg -n "style=\{\{" ...` | PASS, no hits in modified frontend files |
| static guard `rg -n "fetch\(|axios\.|style=\{\{|\bany\b" <modified files>` | PASS, zero hits |

## Guardrails

- `RG-047`: no inline style added.
- `RG-048`: no `var(--token, value)` fallback added.
- `RG-059` / `RG-078`: App CSS modularity preserved; `styles/app/cards.css` is now included in the CS-130 guard scan.
- `RG-064` / `RG-068`: page and layout architecture guards pass.
- `RG-080`: profile keeps no inline style and no `overflow-x: hidden`.
- `RG-081`: new executable guard protects non-admin central width ownership across active App CSS modules and page CSS surfaces.

## Skipped

- None for CS-130 targeted checks.

## Remaining risk

Landing/public section widths remain separate and classified out of scope. The global E2E suite has pre-existing/current-DOM failures outside CS-130; the targeted CS-130 browser check passes.
