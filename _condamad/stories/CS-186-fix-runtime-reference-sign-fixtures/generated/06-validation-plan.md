# Validation Plan

## Environment Assumptions

- Python commands run from PowerShell after `.\.venv\Scripts\Activate.ps1`.
- Backend tests run from `backend/`.

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Affected tests | `pytest -q app/tests/unit/test_aspect_orb_overrides.py app/tests/unit/test_aspect_ruleset_schema.py app/tests/unit/test_golden_zodiac_sidereal_ayanamsa.py app/tests/unit/test_natal_metadata.py app/tests/unit/test_natal_pipeline_swisseph.py app/tests/unit/test_natal_tt.py` | `backend/` | yes | all pass |
| Runtime guard | `pytest -q app/tests/unit/test_astrology_runtime_reference_guard.py` | `backend/` | yes | all pass |

## DRY / No Legacy Scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| RG-114 app scan | `rg -n "ELEMENT_BY_SIGN|MODALITY_BY_SIGN|POLARITY_BY_SIGN|SIGN_PROFILE_DATA" app/domain/astrology app/services/natal -g "*.py"` | `backend/` | yes | no matches |
| Fixture seed mapping scan | `rg -n "SIGN_PROFILE_DATA" tests/factories app/tests -g "*.py"` | `backend/` | yes | no matches |

## Quality Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend/` | yes | no formatting errors |
| Lint | `ruff check .` | `backend/` | yes | no lint errors |

## Regression Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend suite | `pytest -q` | `backend/` | yes | all pass or failure classified |

## Diff Review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Whitespace/conflict markers | `git diff --check` | repo root | yes | no errors |
| Diff summary | `git diff --stat` | repo root | yes | only story-scoped changes plus pre-existing user changes |
| Worktree status | `git status --short` | repo root | yes | expected files recorded |
