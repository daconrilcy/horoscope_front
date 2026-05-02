# Validation Plan

## Environment Assumptions

- OS target: Windows / PowerShell.
- Python commands run only after `.\.venv\Scripts\Activate.ps1`.
- Backend working directory for pytest/ruff: `backend`.

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Targeted script guard | `pytest -q app/tests/unit/test_start_dev_stack_script.py` | `backend` | yes | all tests pass |
| RG-015 ownership guard | `pytest -q app/tests/unit/test_backend_quality_test_ownership.py` | `backend` | yes | all tests pass |
| RG-023 scripts ownership guard | `pytest -q app/tests/unit/test_scripts_ownership.py` | `backend` | yes | all tests pass |
| PowerShell help parse | `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start-dev-stack.ps1 -Help` | repo root | yes | command prints script help/parameters without requiring Stripe |

## Architecture / Import Guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Stripe branch scan | `rg -n "Get-Command stripe|stripe-listen-webhook.ps1|WithStripe|SkipStripe" scripts/start-dev-stack.ps1 docs` | repo root | yes | `WithStripe` documented; no `SkipStripe`; Stripe references are conditional |

## DRY / No Legacy Scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| No fallback or alias in script | `rg -n "fallback|compat|alias|SkipStripe" scripts/start-dev-stack.ps1` | repo root | yes | no hits |

## Quality Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ruff format check | `ruff format --check app/tests/unit/test_start_dev_stack_script.py app/tests/unit/test_backend_quality_test_ownership.py` | `backend` | yes | no formatting changes needed |
| Ruff lint check | `ruff check app/tests/unit/test_start_dev_stack_script.py app/tests/unit/test_backend_quality_test_ownership.py` | `backend` | yes | no lint errors |

## Regression Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story validation | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/harden-local-dev-stack-script/00-story.md` | repo root | yes | command passes |
| Story lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/harden-local-dev-stack-script/00-story.md` | repo root | yes | command passes |

## Diff Review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-related files changed |
| Whitespace/conflict check | `git diff --check` | repo root | yes | no whitespace or conflict marker errors |
| Final status | `git status --short` | repo root | yes | expected files only |

## Commands That May Be Skipped Only With Justification

- Full backend `pytest -q` may be skipped only if targeted and ownership guards pass and the full suite is too costly for this ops-script story.
- Full `ruff check .` may be skipped only if targeted Ruff checks pass and broad repository lint has known unrelated scope risk.
