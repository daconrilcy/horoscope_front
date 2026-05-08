<!-- Plan de validation CS-101. -->

# CS-101 Validation Plan

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Lint/static frontend | `npm run lint` | `frontend/` | yes | TypeScript lint passes |
| Page architecture guard | `npm run test -- page-architecture` | `frontend/` | yes | no stale or missing page-size exceptions |
| Targeted page tests | `npm run test -- AstrologerProfile BirthProfile SubscriptionSettings AdminSamplePayloads` | `frontend/` | yes | touched page tests pass |
| Static guard scan | `rg -n "style=\\{\\{|fetch\\(|axios\\.|\\bany\\b" <touched files>` | repo root | yes | no unclassified new violations |
| Diff review | `git diff --stat` and targeted `git diff -- <files>` | repo root | yes | only CS-101 scoped changes plus pre-existing dirty files |
| Story validate | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story` | repo root after `.\.venv\Scripts\Activate.ps1` | yes | validation passes |
| Story contract explain | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story` | repo root after `.\.venv\Scripts\Activate.ps1` | yes | no missing required contracts |
| Story lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story` | repo root after `.\.venv\Scripts\Activate.ps1` | yes | lint passes |
| Story strict lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story` | repo root after `.\.venv\Scripts\Activate.ps1` | yes | strict lint passes |
