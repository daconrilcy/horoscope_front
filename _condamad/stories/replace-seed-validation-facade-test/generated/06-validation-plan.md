# Validation Plan

## Environment assumptions

- OS: Windows / PowerShell.
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Backend working directory for Python quality commands: `backend/`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Seed validation behavior | `pytest -q app/tests/unit/test_seed_validation.py` | `backend/` | yes | invalid required persona contract raises, current contracts pass |
| No-op guard | `pytest -q app/tests/unit/test_backend_noop_tests.py` | `backend/` | yes | guard passes over backend tests |
| Pricing assertion conversion | `pytest -q app/tests/unit/test_pricing_experiment_service.py` | `backend/` | yes | pricing tests pass |

## Architecture / negative scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| No-op scan | `rg -n "assert True\|pass$" backend/app/tests backend/tests -g test_*.py` | repo root | yes | no direct no-op test body or executable `assert True`; remaining hits classified |
| Removed facade symbol | `rg -n "seed_validation_required_persona_empty_allowed\|assert True" backend/app/tests backend/tests -g test_*.py` | repo root | yes | old facade absent; only guard text self-references `assert True` |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend/` | yes | no unrelated files reformatted |
| Lint | `ruff check .` | `backend/` | yes | no lint errors |
| Pytest collection | `pytest --collect-only -q --ignore=.tmp-pytest` | `backend/` | yes | collection succeeds |
| Full regression | `pytest -q` | `backend/` | yes | suite passes |
| App import/start smoke | `python -c "from app.main import app; print(app.title)"` | `backend/` | yes | FastAPI app imports |

## Story validation

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story validation | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/replace-seed-validation-facade-test/00-story.md` | repo root | yes | PASS |
| Story lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/replace-seed-validation-facade-test/00-story.md` | repo root | yes | PASS |
| Capsule validation | `python -B .agents/skills/condamad-dev-story/scripts/condamad_validate.py _condamad/stories/replace-seed-validation-facade-test --final` | repo root | yes | PASS after evidence completion |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story files changed |
| Whitespace check | `git diff --check` | repo root | yes | no whitespace errors |
| Worktree status | `git status --short` | repo root | yes | expected files only |
