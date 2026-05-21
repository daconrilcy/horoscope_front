# Validation Plan

## Environment assumptions

- OS dev: Windows / PowerShell.
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Backend dependencies are managed by `backend/pyproject.toml`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Targeted contracts tests | `$t = "backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py"; pytest -q $t` | repo root | yes | all tests pass |
| Package file exists | `Test-Path backend/app/domain/astrology/planetary_conditions/contracts.py` | repo root | yes | `True` |

## Unit tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Full backend tests | `pytest -q` | repo root | yes | all tests pass |

## Integration tests

Not applicable: CS-208 does not modify API, DB, services, frontend or public JSON.

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Forbidden application imports | `rg -n "from app\\.api|from app\\.infra|from app\\.infrastructure|from app\\.services" backend/app/domain/astrology/planetary_conditions -g "*.py"` | repo root | yes | zero hits |
| Forbidden frameworks | `rg -n "sqlalchemy|fastapi|pydantic" backend/app/domain/astrology/planetary_conditions -g "*.py"` | repo root | yes | zero hits |
| Forbidden calculation names | `rg -n "calculate_|compute_|resolve_|detect_|score_delta|interpretation_weight" backend/app/domain/astrology/planetary_conditions -g "*.py"` | repo root | yes | zero hits |
| Forbidden prompt/LLM names | `rg -n "prompt|OpenAI|AIEngineAdapter" backend/app/domain/astrology/planetary_conditions -g "*.py"` | repo root | yes | zero hits |
| Free annotation scan | `rg -n "\\bAny\\b|dict\\[str, Any\\]" backend/app/domain/astrology/planetary_conditions -g "*.py"` | repo root | yes | zero hits |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Adjacent surface diff | `git diff -- backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dignities backend/app/domain/astrology/condition backend/app/domain/astrology/dominance backend/app/domain/astrology/natal_calculation.py backend/app/services/chart/json_builder.py backend/app/api backend/app/infra backend/migrations frontend/src` | repo root | yes | empty diff |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | repo root | yes | no formatting errors |
| Lint | `ruff check .` | repo root | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story validation | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md` | repo root | yes | validation passes |
| Story strict lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md` | repo root | yes | lint passes |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff check | `git diff --check` | repo root | yes | no whitespace/conflict errors |
| Diff stat | `git diff --stat` | repo root | yes | only story-scoped files |
| Worktree status | `git status --short` | repo root | yes | expected files only |

## Commands that may be skipped only with justification

No required command is planned to be skipped.
