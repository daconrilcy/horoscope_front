# Validation Plan

## Environment assumptions

- Run Python commands from `backend/` after `.\.venv\Scripts\Activate.ps1`.
- Do not create `requirements.txt`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Canonical narration unit tests | `pytest -q tests/unit/prediction/test_llm_narrator.py` | `backend/` | yes | all tests pass |
| Prediction warning policy | `pytest -q -W error::DeprecationWarning tests/unit/prediction` | `backend/` | yes | all tests pass without deprecation warnings |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Forbidden class usage scan | `rg -n "from app\.prediction\.llm_narrator import LLMNarrator|LLMNarrator\(|LLMNarrator\.narrate" tests app/tests -g "test_*.py"` | `backend/` | yes | no unclassified nominal class usage |
| Backend guard tests | `pytest -q app/tests/unit/test_backend_noop_tests.py` | `backend/` | yes | RG-014 stays green |

## Lint / static checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend/` | yes | formatting succeeds |
| Lint | `ruff check .` | `backend/` | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Relevant LLM orchestration coverage | `pytest -q tests/llm_orchestration/test_narrator_migration.py` | `backend/` | yes | all tests pass |
| Governance registry coverage | `pytest -q tests/integration/test_llm_governance_registry.py` | `backend/` | yes | all tests pass |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-related files changed |
| Whitespace/conflict check | `git diff --check` | repo root | yes | no whitespace or conflict marker errors |
| Worktree status | `git status --short` | repo root | yes | expected files only |

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
