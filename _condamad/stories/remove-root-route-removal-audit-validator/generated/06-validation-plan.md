# Validation Plan

## Environment assumptions

- Python commands run only after `.\.venv\Scripts\Activate.ps1`.
- Backend validation commands run from `backend/` unless the command references a repo-root script.
- No frontend validation is required because no frontend file is in scope.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Root script reintroduction guard | `pytest -q app/tests/unit/test_scripts_ownership.py` | `backend/` after venv activation | yes | test passes |
| RG-015 ownership guard | `pytest -q app/tests/unit/test_backend_quality_test_ownership.py` | `backend/` after venv activation | yes | registry covers the new scripts test |
| Story validation | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/remove-root-route-removal-audit-validator/00-story.md` | repo root after venv activation | yes | story validates |
| Story strict lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/remove-root-route-removal-audit-validator/00-story.md` | repo root after venv activation | yes | no strict lint errors |

## Architecture / negative scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| After-scan artifact | `rg -n "validate_route_removal_audit.py\|validate_route_removal_audit" . -g '!artifacts/**' -g '!.codex-artifacts/**'` | repo root | yes | only current evidence, historical audit, and guard references remain |
| Active consumer absence | `rg -n "validate_route_removal_audit.py" scripts backend frontend docs` | repo root | yes | no active command or consumer hit |
| Historical story cleanup | `rg -n "validate_route_removal_audit.py" _condamad/stories/remove-historical-facade-routes` | repo root | yes | no root command citation remains |

## Lint / static checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Python lint | `ruff check .` | `backend/` after venv activation | yes | no lint errors |

## Full regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend regression suite | `pytest -q` | `backend/` after venv activation | yes | all backend tests pass |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff stat | `git diff --stat` | repo root | yes | only story-related files changed |
| Whitespace check | `git diff --check` | repo root | yes | no whitespace/conflict marker issues |
| Final status | `git status --short` | repo root | yes | only expected story changes plus pre-existing unrelated dirty files |

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
