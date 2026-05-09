<!-- Plan de validation CS-119 pour prouver la suppression et la non-reintroduction. -->

# Validation Plan

## Environment Assumptions

- Frontend root: `frontend/`
- Package scripts: `npm run test`, `npm run lint`
- Python story validation must run from repo root after
  `.\.venv\Scripts\Activate.ps1`.

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Component guards | `npm run test -- component-usage component-architecture design-system visual-smoke` | `frontend` | yes | all targeted suites pass |
| Frontend lint/type graph | `npm run lint` | `frontend` | yes | TypeScript lint configs pass |

## Architecture / Import Guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| B2B/ops/privacy symbols absent | `rg -n "B2BAstrologyPanel|B2BBillingPanel|B2BEditorialPanel|B2BUsagePanel|OpsMonitoringPanel|OpsPersonaPanel|PrivacyPanel" src -g "*.ts" -g "*.tsx" -g "*.css"` | `frontend` | yes | no active hits |
| Daily symbols absent | `rg -n "DailyInsightsSection|MiniInsightCard|ConstellationSVG|HeroHoroscopeCard|TodayHeader" src -g "*.ts" -g "*.tsx" -g "*.css"` | `frontend` | yes | no active hits except allowed non-component CSS comment if classified |
| Prediction symbols absent | `rg -n "DayPredictionCard|getDayPredictionToneClassKey|TurningPointsList" src -g "*.ts" -g "*.tsx" -g "*.css"` | `frontend` | yes | no active hits |
| Deleted import paths absent | `rg -n "components/(B2BAstrologyPanel|B2BBillingPanel|B2BEditorialPanel|B2BUsagePanel|OpsMonitoringPanel|OpsPersonaPanel|PrivacyPanel|DailyInsightsSection|MiniInsightCard|ConstellationSVG|HeroHoroscopeCard|TodayHeader)|components/prediction/(DayPredictionCard|TurningPointsList)" src -g "*.ts" -g "*.tsx"` | `frontend` | yes | no active hits |
| Deleted CSS absent | `rg -n "HeroHoroscopeCard\\.css|MiniInsightCard\\.css|DayPredictionCard\\.css|TurningPointsList\\.css" src -g "*.ts" -g "*.tsx" -g "*.css"` | `frontend` | yes | no active hits |

## Story Validation

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story validate | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-119-supprimer-composants-test-only-sans-ui-runtime/00-story.md` | repo root | yes | validation passes |
| Story validate contracts | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-119-supprimer-composants-test-only-sans-ui-runtime/00-story.md` | repo root | yes | validation passes |
| Story lint | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-119-supprimer-composants-test-only-sans-ui-runtime/00-story.md` | repo root | yes | lint passes |
| Story strict lint | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-119-supprimer-composants-test-only-sans-ui-runtime/00-story.md` | repo root | yes | strict lint passes |

## Diff Review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff stat | `git diff --stat` | repo root | yes | only story-related files changed |
| Whitespace/conflict check | `git diff --check` | repo root | yes | no whitespace/conflict marker errors |
| Worktree status | `git status --short` | repo root | yes | expected dirty files only |
