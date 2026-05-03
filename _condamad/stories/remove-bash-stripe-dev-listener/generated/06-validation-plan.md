# Validation Plan

## Environment assumptions

- OS target: Windows / PowerShell.
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Backend tests run from `backend/`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Targeted guards | `pytest -q app/tests/unit/test_scripts_ownership.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/unit/test_start_dev_stack_script.py` | `backend/` | yes | all tests pass |
| Story validate | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/remove-bash-stripe-dev-listener/00-story.md` | repo root | yes | story validates |
| Story lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/remove-bash-stripe-dev-listener/00-story.md` | repo root | yes | story lint passes |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Active forbidden surface | `rg -n "stripe-listen-webhook\\.sh|Git Bash|WSL|#!/usr/bin/env bash" scripts docs backend/app/tests` | repo root | yes | no active hits |
| Script inventory | `rg --files scripts` | repo root | yes | no Bash listener; ownership rows align |
| Deleted file absence | `rg --files scripts \| rg "stripe-listen-webhook\\.sh"` | repo root | yes | no hit |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format check | `ruff format --check app/tests/unit/test_scripts_ownership.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/unit/test_start_dev_stack_script.py` | `backend/` | yes | no formatting changes needed |
| Lint check | `ruff check app/tests/unit/test_scripts_ownership.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/unit/test_start_dev_stack_script.py` | `backend/` | yes | no lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Project quality gate | `./scripts/quality-gate.ps1` | repo root | conditional | pass if feasible in environment |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff stat | `git diff --stat` | repo root | yes | only story-scoped files changed |
| Diff whitespace | `git diff --check` | repo root | yes | no whitespace/conflict errors |
| Final status | `git status --short` | repo root | yes | expected files only |

## Commands that may be skipped only with justification

- Full `pytest -q` if targeted guards plus story-specific scans are sufficient and full suite cost is outside this focused cleanup.
- `./scripts/quality-gate.ps1` if frontend dependencies or environment services are unavailable.
