# Validation Plan - CS-054

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Design/theme guards | `npm run test -- design-system theme-tokens` | `frontend` | yes | all tests pass |
| Frontend lint/typecheck | `npm run lint` | `frontend` | yes | no TypeScript errors |
| Targeted cluster scan | `rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|font-size:|font-weight:|box-shadow:|border-radius:" src/components/prediction/DayPredictionCard.css` | `frontend` | yes | all hits classified |
| Final decision scan | `rg -n "TODO|TBD|unclassified" hardcoded-values-after.md` | story folder | yes | zero hits |
| Story validate | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-054-migrer-prochain-cluster-valeurs-visuelles-hardcodees/00-story.md` | repo root after venv activation | yes | PASS |
| Story lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-054-migrer-prochain-cluster-valeurs-visuelles-hardcodees/00-story.md` | repo root after venv activation | yes | PASS |
| Diff whitespace | `git diff --check` | repo root | yes | no whitespace errors |
