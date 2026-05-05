# Validation Plan - CS-052

## Environment assumptions

- Frontend root: `frontend`
- Package manager/script runner: `npm`
- Python commands require `. .\.venv\Scripts\Activate.ps1`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Fallback/design-system/theme guards | `npm run test -- css-fallback design-system theme-tokens` | `frontend` | yes | all tests pass |
| Frontend lint/typecheck | `npm run lint` | `frontend` | yes | no TypeScript errors |
| Final fallback scan | `rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," src -g "*.css"` | `frontend` | yes | only allowlisted/classified hits |
| Ambiguous premium classification | `rg -n "needs-user-decision\|premium" css-fallbacks-*.md` | story folder | yes | remaining premium blockers documented |

## Story checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story validate | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-052-reduire-cluster-restant-fallbacks-css-natal-chart/00-story.md` | repo root after venv activation | yes | PASS |
| Story lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-052-reduire-cluster-restant-fallbacks-css-natal-chart/00-story.md` | repo root after venv activation | yes | PASS |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff whitespace | `git diff --check` | repo root | yes | no whitespace errors |
| Scope review | `git diff --stat` | repo root | yes | only story-related files plus other requested story changes |
