# Validation Plan

## Environment assumptions

- OS: Windows / PowerShell.
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Backend working directory for Python checks: `backend/`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Targeted architecture guard | `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_backend_test_helper_imports.py` | repo root | yes | all tests pass |

## Unit tests

Covered by the targeted architecture guard above; no application behavior unit test is affected.

## Integration tests

Not applicable: the story changes only a static architecture guard.

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Cross-test import negative scan | `.\.venv\Scripts\Activate.ps1; cd backend; rg -n "from app\.tests\.(integration\|unit\|regression)\.test_\|from tests\.(integration\|unit\|regression)\.test_" app/tests tests -g "test_*.py"` | repo root | yes | no hits, exit 1 accepted as zero-hit |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Duplicate guard owner search | `rg -n "test_backend_test_helper_imports|FORBIDDEN_PREFIXES|from app\.tests\.(integration\|unit\|regression)\.test_" backend _condamad -g "*.py" -g "*.md"` | repo root | yes | no duplicate active guard implementation |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .` | repo root | yes | formatting succeeds |
| Lint | `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` | repo root | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Full backend suite | `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` | repo root | yes | suite passes |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-related files changed |
| Whitespace/conflict check | `git diff --check` | repo root | yes | no errors |
| Worktree status | `git status --short` | repo root | yes | expected files only, aside from pre-existing inaccessible temp warnings if present |

## Commands that may be skipped only with justification

No required command is planned to be skipped.
