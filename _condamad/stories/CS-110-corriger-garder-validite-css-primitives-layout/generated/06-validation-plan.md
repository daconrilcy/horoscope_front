<!-- Plan de validation CS-110. -->

# Validation Plan CS-110

## Environment assumptions

- Frontend package manager: `npm` because `frontend/package-lock.json` is present.
- Python story tooling: run only after `.\.venv\Scripts\Activate.ps1`.

## Commands

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| CSS invalid pattern scan | `rg -n "padding: var\\(--layout-page-padding\\)\\);" frontend/src/layouts` | repo root | yes | zero hits |
| Design-system guard | `npm run test -- design-system` | `frontend/` | yes | all tests pass |
| Layout architecture guard | `npm run test -- page-architecture layout` | `frontend/` | yes | all tests pass |
| Frontend lint | `npm run lint` | `frontend/` | yes | exit 0 |
| Story validate | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-110-corriger-garder-validite-css-primitives-layout/00-story.md` | repo root | yes | PASS |
| Story strict lint | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-110-corriger-garder-validite-css-primitives-layout/00-story.md` | repo root | yes | PASS |
