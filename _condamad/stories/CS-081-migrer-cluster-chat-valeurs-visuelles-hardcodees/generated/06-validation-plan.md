# Validation Plan

## Environment assumptions

- OS: Windows / PowerShell.
- Frontend package manager observed: `npm` with `package-lock.json`.
- Python commands must run only after `.\.venv\Scripts\Activate.ps1`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Guard CS-081 | `npm run test -- design-system` | `frontend/` | yes | design-system guard suite passes |
| Frontend guarded subset | `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` | `frontend/` | yes | targeted suites pass |

## Unit tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Visual smoke coverage | `npm run test -- visual-smoke` | `frontend/` | yes | smoke tests pass |

## Integration tests

Not applicable: no API, route, hook or runtime integration change.

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Token namespace registry | `npm run test -- theme-tokens design-system` | `frontend/` | yes | registry and namespace guards pass |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Color literals | `rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/pages/ChatPage.css src/features/chat/components -g "*.css" -g "*.tsx"` | `frontend/` | yes | hits only in documented `--chat-*` owner |
| Typography declarations | `rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/pages/ChatPage.css src/features/chat/components -g "*.css" -g "*.tsx"` | `frontend/` | yes | declarations use tokens or `--chat-*` roles |
| Radius/elevation/fallback scan | `rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," src/pages/ChatPage.css src/features/chat/components -g "*.css" -g "*.tsx"` | `frontend/` | yes | no literal fallback; radius/elevation tokenized |
| Forbidden vocabulary | `rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" src/pages/ChatPage.css src/features/chat/components` | `frontend/` | yes | only classified avatar fallback naming and shimmer names |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| TypeScript lint | `npm run lint` | `frontend/` | yes | no TypeScript errors |
| Production build | `npm run build` | `frontend/` | yes | build succeeds |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story validate | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-081-migrer-cluster-chat-valeurs-visuelles-hardcodees/00-story.md` | repo root | yes | story validates |
| Story lint | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-081-migrer-cluster-chat-valeurs-visuelles-hardcodees/00-story.md` | repo root | yes | story lint passes |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-scoped files changed plus pre-existing unrelated dirty files preserved |
| Diff check | `git diff --check` | repo root | yes | no whitespace or conflict marker issues |
| Worktree status | `git status --short` | repo root | yes | expected dirty files recorded |
