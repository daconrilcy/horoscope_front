# Validation Plan

## Environment assumptions

- OS: Windows / PowerShell.
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Backend commands run from `backend/`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story validate | `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\remove-llm-narrator-legacy-direct-openai\00-story.md` | `backend/` | yes | story valid |
| Story lint | `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\remove-llm-narrator-legacy-direct-openai\00-story.md` | `backend/` | yes | no strict lint errors |
| Deprecation guard | `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | `backend/` | yes | guard passes |
| Migration tests | `pytest -q tests/llm_orchestration/test_narrator_migration.py` | `backend/` | yes | migration tests pass |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Legacy narrator scan | `rg -n "LLMNarrator\|llm_narrator" backend/app backend/tests docs` | repo root | yes | no active runtime facade hits; remaining hits classified |
| Provider direct scan | `rg -n "LLMNarrator\(|from app\.prediction\.llm_narrator import LLMNarrator|chat\.completions\.create|openai\.AsyncOpenAI" app tests` | `backend/` | yes | no forbidden active hits |
| API/docs generated check | `rg -n "LLMNarrator|llm_narrator" frontend/src backend/app/api docs` | repo root | yes | no API/generated references; docs/config hits classified |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ruff check | `ruff check .` | `backend/` | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend targeted regression | `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py tests/llm_orchestration/test_narrator_migration.py` | `backend/` | yes | all selected tests pass |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-related files changed |
| Whitespace/conflict check | `git diff --check` | repo root | yes | no issues |
| Final status | `git status --short` | repo root | yes | expected dirty files only |

## Commands that may be skipped only with justification

- Full `pytest -q` may be skipped only if targeted validation and story-required checks pass and the run is too broad for the current turn.
