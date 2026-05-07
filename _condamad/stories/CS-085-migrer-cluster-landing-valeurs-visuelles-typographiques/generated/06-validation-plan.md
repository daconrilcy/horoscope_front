# Validation Plan - CS-085

## Environment assumptions

- Frontend package manager: npm, based on `frontend/package-lock.json` and `frontend/package.json`.
- Python story validation commands must run after `.\.venv\Scripts\Activate.ps1`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Landing design-system guards | `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke App FaqSection` | `frontend/` | yes | all selected Vitest files pass |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Visual literals inventory | `rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/layouts/LandingLayout.css src/pages/landing --glob "*.css"` | `frontend/` | yes | remaining hits classified in after artifact |
| Typography literals inventory | `rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/layouts/LandingLayout.css src/pages/landing --glob "*.css"` | `frontend/` | yes | remaining hits classified in after artifact |
| Elevation/radius/fallback inventory | `rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," src/layouts/LandingLayout.css src/pages/landing --glob "*.css"` | `frontend/` | yes | migrated values absent or classified |
| No Legacy vocabulary | `rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" src/layouts/LandingLayout.css src/pages/landing --glob "*.css"` | `frontend/` | yes | zero active hits |
| Page-scoped namespace isolation | `rg -n --glob "*.css" -- "--settings-|--help-|--chat-|--app-" src/layouts/LandingLayout.css src/pages/landing` | `frontend/` | yes | zero hits |
| No unresolved limitation marker evidence | scan generated evidence for unresolved limitation markers used by CONDAMAD closure reports | repo root | yes | zero unresolved active hits |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Frontend tests | `npm run test` | `frontend/` | yes | all Vitest tests pass |
| Frontend lint/type static check | `npm run lint` | `frontend/` | yes | TypeScript checks pass |
| Frontend production build | `npm run build` | `frontend/` | yes | build succeeds |

## Story validation

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story validate | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-085-migrer-cluster-landing-valeurs-visuelles-typographiques/00-story.md` | repo root | yes | validation passes |
| Story lint strict | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-085-migrer-cluster-landing-valeurs-visuelles-typographiques/00-story.md` | repo root | yes | lint passes |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff whitespace | `git diff --check` | repo root | yes | no whitespace/conflict-marker errors |
| Diff summary | `git diff --stat` | repo root | yes | only expected story/frontend files changed |
| Worktree status | `git status --short` | repo root | yes | expected files only |
