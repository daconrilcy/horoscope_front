# Validation Plan

## Environment assumptions

- Commands Python are run in PowerShell after `.\.venv\Scripts\Activate.ps1`.
- Working directory for Python checks: `backend`.
- No new dependency is required.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Orchestrator regression | `pytest -q app/tests/unit/test_engine_orchestrator.py` | `backend` | yes | all tests pass |
| Namespace guard | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` | `backend` | yes | all tests pass |
| LLM narrator guard | `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | `backend` | yes | all tests pass |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Old orchestrator import scan | `rg -n "app\\.prediction\\.engine_orchestrator" app tests` | `backend` | yes | zero active hits |
| LLMNarrator scan | `rg -n "from app\\.prediction\\.llm_narrator import LLMNarrator|LLMNarrator\\(|LLMNarrator\\.narrate" app tests` | `backend` | yes | zero active hits |
| Namespace inventory | `rg --files app/prediction` | `backend` | yes | matches approved after inventory |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ruff check | `ruff check app tests` | `backend` | yes | no lint errors |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Whitespace/conflict check | `git diff --check` | repo root | yes | no errors |
| Diff summary | `git diff --stat` | repo root | yes | only story-scoped files changed |
| Final status | `git status --short` | repo root | yes | expected files only |
