# Validation Evidence

## Commands run

| Command | Working directory | Result | Evidence summary |
|---|---|---|---|
| `npm run test -- AstrologersPage design-system visual-smoke` | `frontend` | PASS | 3 files, 75 tests passed after review fixes. |
| `npm run test -- inline-style css-fallback page-architecture` | `frontend` | PASS | 3 files, 28 tests passed after page-size correction. |
| `npm run test:e2e -- astrologer-profile-ui.spec.ts` | `frontend` | PASS | 1 Playwright test passed; desktop/mobile no horizontal overflow and hero CTA visible. |
| `npm run lint` | `frontend` | PASS | TypeScript lint gates passed. |
| `npm run build` | `frontend` | PASS | Production build completed. |
| `rg -n "AstrologerProfile\|profile-" src/App.css` | `frontend` | PASS | Zero hits. |
| `rg -n "style=" src/pages/AstrologerProfilePage.tsx src/features/astrologers/components/AstrologerProfileSections.tsx` | `frontend` | PASS | Zero hits. |
| `rg -n "overflow-x:\s*hidden" src/pages/AstrologerProfilePage.css` | `frontend` | PASS | Zero hits. |
| `rg -n "profile-main-grid\|specialties-card\|profile-mission-card" src/pages/AstrologerProfilePage.css` | `frontend` | PASS | Required rhythm selectors present. |
| `rg -n "@media \(max-width: 768px\)\|profile-hero\|profile-mobile" src/pages/AstrologerProfilePage.css` | `frontend` | PASS | Mobile/hero selectors present. |
| `rg -n "astrologer-card\|astrologer-grid\|compat\|compatibility\|legacy\|alias\|shim" src/pages/AstrologerProfilePage.css src/features/astrologers/components/AstrologerProfileSections.tsx src/pages/AstrologerProfilePage.tsx` | `frontend` | PASS | Zero active hits. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-129-ameliorer-ui-profil-astrologue/00-story.md` | repo root | PASS | Story validation passed with venv activated. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-129-ameliorer-ui-profil-astrologue/00-story.md` | repo root | PASS | Required contracts present; no missing required contracts. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-129-ameliorer-ui-profil-astrologue/00-story.md` | repo root | PASS | Story lint passed with venv activated. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-129-ameliorer-ui-profil-astrologue/00-story.md` | repo root | PASS | Strict story lint passed with venv activated. |
| `git diff --check` | repo root | PASS | No whitespace errors; Git reported CRLF normalization warnings only. |

## Initial failure and fix evidence

- `npm run test -- inline-style css-fallback page-architecture` initially failed because `AstrologerProfilePage.tsx` exceeded the page-size guard at 715 then 702 lines.
- The route file was reduced below the threshold without changing behavior.
- Review found a positive review-count edge case with no excerpts. The implementation was updated so `reviewCount > 0` is the public-review source of truth and `reviews: []` renders a non-empty collected-reviews state.
- Follow-up review found an excerpt-only edge case where `review_summary.review_count: 0` contradicted returned review excerpts. The page now normalizes the public review count from summary and excerpts, with a dedicated regression test.
- Final requested review loop reran the full CS-129 validation set and found no additional issue to fix.

## Skipped checks

- No required checks skipped.
- Local long-running dev server was not left running. Playwright started the Vite dev server through `frontend/playwright.config.ts`, proving local startup for the profile flow.
