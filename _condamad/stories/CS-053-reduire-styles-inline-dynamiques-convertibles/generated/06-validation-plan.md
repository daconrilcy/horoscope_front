# Validation Plan - CS-053

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Inline/design guards | `npm run test -- inline-style design-system` | `frontend` | yes | all tests pass |
| Frontend lint/typecheck | `npm run lint` | `frontend` | yes | no TypeScript errors |
| Final inline scan | `rg -n "style=\{" src -g "*.tsx"` | `frontend` | yes | 14 classified hits |
| Story validate | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-053-reduire-styles-inline-dynamiques-convertibles/00-story.md` | repo root after venv activation | yes | PASS |
| Story lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-053-reduire-styles-inline-dynamiques-convertibles/00-story.md` | repo root after venv activation | yes | PASS |
| Diff whitespace | `git diff --check` | repo root | yes | no whitespace errors |
