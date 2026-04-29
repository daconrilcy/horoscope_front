# Validation Plan

## Environment assumptions

- Python commands run only after `.\.venv\Scripts\Activate.ps1`.
- Backend commands run from `backend/`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Topology guard | `pytest -q app/tests/unit/test_backend_test_topology.py` | `backend/` | yes | all tests pass |
| Collection guard | `pytest -q app/tests/unit/test_backend_pytest_collection.py` | `backend/` | yes | all tests pass |
| Moved LLM test | `pytest -q tests/llm_orchestration/test_qualified_context.py` | `backend/` | yes | all tests pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Runtime collection | `pytest --collect-only -q --ignore=.tmp-pytest` | `backend/` | yes | collection succeeds |
| Static inventory | `rg --files . -g test_*.py -g *_test.py -g !.tmp-pytest/**` | `backend/` | yes | all files belong to approved roots |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Embedded test path scan | `rg "app/domain/llm/prompting/tests/test_qualified_context|app\\.domain\\.llm\\.prompting\\.tests" backend _condamad -g *.py -g *.md` | repo root | yes | no active backend import or test path remains |
| Legacy keyword classification | `rg "legacy|compat|shim|fallback|deprecated|alias" _condamad/stories/converge-backend-test-topology backend/app/tests/unit/test_backend_test_topology.py backend/app/tests/unit/test_backend_pytest_collection.py backend/tests/llm_orchestration/test_qualified_context.py -g *.md -g *.py` | repo root | yes | hits classified |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend/` | yes | no formatting errors |
| Lint | `ruff check .` | `backend/` | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Full backend suite | `pytest -q` | `backend/` | yes | all tests pass |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff stat | `git diff --stat` | repo root | yes | only story-related files changed |
| Whitespace/conflicts | `git diff --check` | repo root | yes | no issues |
| Final status | `git status --short` | repo root | yes | expected files only |
