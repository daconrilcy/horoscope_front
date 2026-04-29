# Validation Plan

## Environment assumptions

- Working OS: Windows / PowerShell.
- Python commands must run after `.\\.venv\\Scripts\\Activate.ps1`.
- Backend working directory for pytest/ruff: `backend/`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Runtime collection | `pytest --collect-only -q --ignore=.tmp-pytest` | `backend/` | yes | Collection succeeds and includes all retained test files. |
| Collection guard | `pytest -q app/tests/unit/test_backend_pytest_collection.py` | `backend/` | yes | Guard tests pass. |

## Unit tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| New pytest collection guard | `pytest -q app/tests/unit/test_backend_pytest_collection.py` | `backend/` | yes | All tests pass. |

## Integration tests

Not directly applicable. The story changes pytest discovery rather than application integration behavior.

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Configured roots exist | `pytest -q app/tests/unit/test_backend_pytest_collection.py` | `backend/` | yes | No nonexistent `testpaths`. |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Forbidden missing test root | `rg -n "app/ai_engine/tests" backend/pyproject.toml` | repo root | yes | No hit if the directory remains absent. |
| Opt-in evidence | `rg -n "opt-in\|exception" ../_condamad/stories` | `backend/` | yes | Only story/evidence references; no hidden opt-in suite. |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend/` | yes | Formatting completes without error. |
| Lint | `ruff check .` | `backend/` | yes | No lint errors. |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Full backend tests | `pytest -q` | `backend/` | yes | All tests pass. |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | Only story-scoped files changed. |
| Whitespace/conflict check | `git diff --check` | repo root | yes | No whitespace or conflict marker errors. |
| Final status | `git status --short` | repo root | yes | Expected files only. |

## Commands that may be skipped only with justification

- Full `pytest -q` may be skipped only for an environment/runtime blocker after targeted guard and collect-only evidence are available.
- Story lint scripts may be skipped if unavailable, with exact command and file-not-found evidence.
