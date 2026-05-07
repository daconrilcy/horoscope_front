# Validation Plan

## Environment Assumptions

- Repository root: `C:\dev\horoscope_front`
- Frontend root: `frontend`
- Package manager observed: npm scripts in `frontend/package.json`
- Python commands must run only after `.\.venv\Scripts\Activate.ps1`

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Design-system focused guards | `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` | `frontend` | yes | matching Vitest suites pass |
| Full frontend tests | `npm run test` | `frontend` | yes | all Vitest tests pass |

## Unit Tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Settings anti-return guard | `npm run test -- design-system` | `frontend` | yes | Settings guard fails if migrated literals return |

## Integration Tests

- No API, route, store or runtime integration is modified.

## Architecture / Import Guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Page-scoped namespace ownership | `rg -n -- "--settings-" src --glob "*.css"` | `frontend` | yes | only `Settings.css` consumes `--settings-*`, plus allowed registry/test references outside CSS if reviewed separately |
| CSS fallback policy | `rg -n "var\(\s*--[a-zA-Z0-9_-]+\s*," src/pages/settings/Settings.css` | `frontend` | yes | only `--usage-progress` remains and is allowlisted |

## DRY / No Legacy Scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Visual literal scan | `rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/pages/settings/Settings.css` | `frontend` | yes | remaining hits are only owners documented in after evidence |
| Typography literal scan | `rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/pages/settings/Settings.css` | `frontend` | yes | repeatable typography uses `--type-*`, `--font-*`, `--line-height-*`, or documented `--settings-*` |
| Shape/elevation/fallback scan | `rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," src/pages/settings/Settings.css` | `frontend` | yes | repeatable shape/elevation uses tokens or documented `--settings-*` |
| No Legacy vocabulary scan | `rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" src/pages/settings/Settings.css` | `frontend` | yes | zero hits |

## Quality Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Frontend lint/type check | `npm run lint` | `frontend` | yes | TypeScript lint configs pass |
| Frontend build | `npm run build` | `frontend` | yes | production build completes |
| Story validation | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-084-migrer-cluster-settings-valeurs-visuelles-typographiques/00-story.md` | repo root | yes | story contract validates |
| Story lint | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-084-migrer-cluster-settings-valeurs-visuelles-typographiques/00-story.md` | repo root | yes | story lint passes |

## Regression Checks

- Applicable guardrails: `RG-044` to `RG-060`.
- Required combined evidence: `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`, `npm run test`, `npm run lint`, `npm run build`, targeted scans.

## Diff Review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-scoped files changed |
| Whitespace/conflict check | `git diff --check` | repo root | yes | no conflict markers or whitespace errors |
| Worktree status | `git status --short` | repo root | yes | expected files only |

## Commands That May Be Skipped Only With Justification

- None for this story. If an environment blocker appears, record `BLOCKED`; do not mark an AC as `PASS_WITH_LIMITATIONS`.
