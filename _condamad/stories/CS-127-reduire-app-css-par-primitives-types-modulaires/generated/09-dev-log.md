# Dev Log

## Preflight

- Initial `git status --short`: existing dirty files included `_condamad/stories/regression-guardrails.md` and `_condamad/stories/story-status.md`; story capsule and `frontend/src/styles/app/` were untracked during implementation.
- Current branch: `main`.
- Existing dirty files were preserved and not reverted.

## Search evidence

- `rg --files src/styles/app` lists the 11 typed modules required by CS-127.
- `rg -n "OLD|legacy|alias|compat|compatibility|shim|migration-only" src/App.css src/styles/app` returned no hits.
- `rg -n -- "--app-.*-(font-size|border-radius|background|color)-[0-9]+" src/App.css src/styles/app` returned no hits.
- Primitive scan confirmed TSX/CSS usage for `notice`, `select-card`, `form-control`, `state-centered`, `stack`, and `cluster`.

## Implementation notes

- `frontend/src/App.css` now contains only the French file comment and typed imports.
- App CSS was split into `frontend/src/styles/app/{tokens,base,typography,layout,buttons,cards,forms,notices,states,media,skeletons}.css`.
- Low-risk TSX consumers now compose primitives without inline styles.
- Design-system helpers now expose `APP_CSS_MODULE_FILES` and `readAppCssSurface()` so guards cover the complete modular App CSS surface.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `npm run test -- BottomNavPremium design-system theme-tokens visual-smoke` | PASS | 168 tests |
| `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` | PASS | 153 tests |
| `npm run lint` | PASS | TypeScript lint configs |
| `npm run build` | PASS | Vite production build; CSS warning fixed and rerun clean |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-127-reduire-app-css-par-primitives-types-modulaires/00-story.md` | PASS | venv activated |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-127-reduire-app-css-par-primitives-types-modulaires/00-story.md` | PASS | venv activated |

## Issues encountered

- Review agents found stale App CSS surface reads, a stale BottomNav test, missing final evidence, and insufficient single-use token proof. These were fixed by shared App CSS helpers, updated tests, regenerated artifacts, and final evidence updates.
- A CSS property corruption in `media.css` was detected by Vite build warnings and corrected before final validation.

## Decisions made

- Single-use `--app-*` variables are retained only when documented in `app-css-variable-usage.md`, with the design-system guard enforcing the retained-decision row.
- `buttons.css` remains a typed App CSS module because button ownership belongs to the App CSS surface for this story.

## Final `git status --short`

- Captured after final validation in `generated/10-final-evidence.md`.
