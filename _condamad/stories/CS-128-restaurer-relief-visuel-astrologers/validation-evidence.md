# Validation Evidence

<!-- Journal des validations executees pour CS-128. -->

## Frontend commands

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `npm run test -- AstrologersPage design-system visual-smoke` | `frontend/` | PASS | 0 | 3 files, 68 tests passed; includes route states, design guard and rendered DOM smoke for `/astrologers`. |
| `npm run test -- theme-tokens css-fallback inline-style legacy-style` | `frontend/` | PASS | 0 | 4 files, 108 tests passed. |
| `npm run lint` | `frontend/` | PASS | 0 | TypeScript lint configs passed. |
| `npm run build` | `frontend/` | PASS | 0 | Production build completed. |

## Scans

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `rg -n "person-card\|people-page\|astrologer" src/App.css` | `frontend/` | PASS | 1 | Zero hits; `App.css` remains import-only for this surface. |
| `rg -n "style=" src/pages/AstrologersPage.tsx src/features/astrologers/components/AstrologerCard.tsx src/features/astrologers/components/AstrologerGrid.tsx` | `frontend/` | PASS | 1 | Zero hits; no inline style introduced. |
| `rg -n "\.astrologer-(card\|grid\|card-avatar\|card-specialties)" src/styles/app src/features/astrologers src/pages/AstrologersPage.tsx` | `frontend/` | PASS | 1 | Zero hits for exact forbidden selectors. |
| `rg --files src/styles/app` | `frontend/` | PASS | 0 | Only `typography.css`, `tokens.css`, `states.css`, `skeletons.css`, `notices.css`, `media.css`, `layout.css`, `forms.css`, `cards.css`, `buttons.css`, `base.css`. |
| `git diff --check` | repo root | PASS | 0 | No whitespace/conflict-marker errors; only line-ending warnings reported by Git for existing checkout behavior. |

## Story validation commands

All Python commands were run from repo root after activating `.venv`.

| Command | Result | Exit status | Evidence summary |
|---|---|---:|---|
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md` | PASS | 0 | CONDAMAD story validation passed. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md` | PASS | 0 | Required contracts satisfied. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md` | PASS | 0 | Story lint passed. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md` | PASS | 0 | Strict story lint passed. |

## Review findings resolved

| Finding | Resolution |
|---|---|
| Missing after/final validation evidence | Added this file, `astrologers-visual-after.md`, and completed `generated/10-final-evidence.md`. |
| Broad legacy scan matches `default-astrologer-grid` | Classified as out-of-scope false positive and added exact forbidden selector zero-hit scan. |
| `visual-smoke` only checked static CSS | Added rendered DOM smoke for `/astrologers` with mocked hooks, `MemoryRouter` and `QueryClientProvider`. |
| User screenshot shows insufficient relief | Added compact visual tokens in `tokens.css`, applied them in `cards.css`, updated CSS guards and kept raw visual values out of active card declarations. |
| Runtime CSS still transparent after token refactor | Moved compact tokens that depend on `--astro-*` to `.person-card`, added compact avatar background/border tokens, and restored icon positioning against the card instead of the topline. |
| Micro-adjustments requested after final capture | Icon depth set above avatar, soft gradient ring added, icon/photo spacing increased, Etienne divider contrast raised, and style text forced to anthracite token. |
| Top menu transparent during vertical scroll | Header glass layer strengthened with token-backed background, blur/saturation and pseudo-element veil; static guard added in `design-system-guards.test.ts`. |

## Skipped or limited

| Check | Reason | Risk | Compensating evidence |
|---|---|---|---|
| Real backend authenticated screenshot | Backend login was not required for CSS validation; controlled Playwright route mocks auth/settings/astrologers while rendering the real app and CSS. | Header/auth shell can differ from a real session if backend state differs. | Controlled screenshot `generated/visual-after-icon-fix.png`, CSS/DOM tests and production build passed. |
