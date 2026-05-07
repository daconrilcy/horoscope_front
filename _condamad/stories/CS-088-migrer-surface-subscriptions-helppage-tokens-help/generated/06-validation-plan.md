# Validation Plan

## Environment assumptions

- Repository root: `C:\dev\horoscope_front`
- Frontend root: `frontend`
- Frontend package manager in repository: npm scripts in `package.json`
- Python commands must run only after `.\.venv\Scripts\Activate.ps1`

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Guards Help subscriptions | `npm run test -- design-system css-fallback inline-style legacy-style visual-smoke HelpPage` | `frontend` | yes | all targeted tests pass |
| Frontend lint/typecheck | `npm run lint` | `frontend` | yes | no errors |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Visual literals scan | `rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/pages/HelpPage.css` | `frontend` | yes | hits classified in after artifact |
| Typography scan | `rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/pages/HelpPage.css` | `frontend` | yes | subscriptions hits use tokens or owner vars |
| Shape/elevation/fallback scan | `rg -n "box-shadow:|border-radius:|linear-gradient|radial-gradient|var\(\s*--[a-zA-Z0-9_-]+\s*," src/pages/HelpPage.css` | `frontend` | yes | no unclassified fallback; subscriptions values routed |
| Forbidden namespace scan | `rg -n -- "--settings-|--app-|--chat-|--landing-|--admin-" src/pages/HelpPage.css` | `frontend` | yes | no hits |
| No Legacy vocabulary scan | `rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" src/pages/HelpPage.css` | `frontend` | yes | no active CSS hits |

## Story validation

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story validate | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-088-migrer-surface-subscriptions-helppage-tokens-help/00-story.md` | repo root | yes | story validates |
| Story lint strict | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-088-migrer-surface-subscriptions-helppage-tokens-help/00-story.md` | repo root | yes | no lint errors |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff stat | `git diff --stat` | repo root | yes | only story files changed |
| Whitespace check | `git diff --check` | repo root | yes | no conflict markers or whitespace errors |
| Final status | `git status --short` | repo root | yes | expected story changes only |
