# Validation Plan

## Environment assumptions

- OS: Windows / PowerShell.
- Python commands run only after `.\.venv\Scripts\Activate.ps1`.
- Backend commands run from `backend/` unless a repo-root script path is required.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Targeted script guard tests | `pytest -q app/tests/unit/test_natal_cross_tool_report_dev_script.py` | `backend/` | yes | all tests pass |
| Existing helper tests | `pytest -q app/tests/unit/test_cross_tool_report.py` | `backend/` | yes | all tests pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Golden import boundary scan | `rg -n "app\.tests\.golden" backend/app scripts -g "*.py"` | repo root | yes | hits limited to tests/golden and dev script |
| Helper duplication scan | `rg -n "cross_tool_report" scripts backend` | repo root | yes | no root duplicate helper |
| Dev command docs scan | `rg -n "natal-cross-tool-report-dev.py|Activate.ps1" docs scripts/ownership-index.md backend/README.md` | repo root | yes | command and venv activation documented |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ruff format check | `ruff format --check .` | `backend/` | yes | no formatting changes required |
| Ruff lint | `ruff check .` | `backend/` | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Full backend tests | `pytest -q` | `backend/` | yes | all tests pass or limitation recorded |
| Story validator | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/classify-natal-cross-tool-dev-report/00-story.md` | repo root | yes | story validates |
| Story lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/classify-natal-cross-tool-dev-report/00-story.md` | repo root | yes | lint passes |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff stat | `git diff --stat` | repo root | yes | only story-related files changed |
| Whitespace check | `git diff --check` | repo root | yes | no whitespace errors |
| Final status | `git status --short` | repo root | yes | expected files only |
