# Validation Plan

## Environment assumptions

- Repository root: `C:\dev\horoscope_front`
- Frontend root: `C:\dev\horoscope_front\frontend`
- Package scripts discovered from `frontend/package.json`; use `npm run ...`.
- Python story validation must run after `.\.venv\Scripts\Activate.ps1`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Design-system focused guards | `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` | `frontend` | yes | matching Vitest guard files pass |
| Full frontend tests | `npm run test` | `frontend` | yes | all Vitest tests pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Visual/type literal scan | `rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(|font-size:|font-weight:|line-height:|letter-spacing:|box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," src/layouts/AdminLayout.css src/pages/admin -g "*.css"` | `frontend` | yes | only owner declarations or classified final values remain |
| No fallback CSS literal scan | `rg -n "var\(\s*--[a-zA-Z0-9_-]+\s*," src/layouts/AdminLayout.css src/pages/admin -g "*.css"` | `frontend` | yes | zero hits |
| No Legacy vocabulary scan | `rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only|PASS with limitation|TODO" src/layouts/AdminLayout.css src/pages/admin -g "*.css"` | `frontend` | yes | zero unclassified active style hits |
| Page-scoped namespace scan | `rg -n -- "--settings-|--help-|--chat-|--app-|--landing-" src/layouts/AdminLayout.css src/pages/admin -g "*.css"` | `frontend` | yes | zero hits |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Frontend lint/type static check | `npm run lint` | `frontend` | yes | no TypeScript errors |
| Frontend production build | `npm run build` | `frontend` | yes | build succeeds |
| Story contract validation | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-086-migrer-cluster-admin-valeurs-visuelles-typographiques/00-story.md` | repo root | yes | story validates |
| Story strict lint | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-086-migrer-cluster-admin-valeurs-visuelles-typographiques/00-story.md` | repo root | yes | story lints |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-scoped files changed |
| Whitespace/conflict check | `git diff --check` | repo root | yes | no whitespace errors or conflict markers |
| Worktree status | `git status --short` | repo root | yes | expected story files only plus pre-existing dirty files |

## Commands that may be skipped only with justification

- None of the required commands may be skipped without recording blocker, risk and compensating evidence.
