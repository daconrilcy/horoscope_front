# Validation Plan

## Environment Assumptions

- OS: Windows / PowerShell.
- All Python commands require `.\.venv\Scripts\Activate.ps1`.
- Backend dependencies are managed by `backend/pyproject.toml`.

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Payload contracts | `pytest -q backend/tests/unit/domain/astrology/test_chart_object_motion_visibility_payloads.py` | repo root | yes | all pass |
| Runtime builder | `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_builder.py` | repo root | yes | all pass |
| Natal chart objects | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py` | repo root | yes | all pass |
| Architecture guard | `pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` | repo root | yes | all pass |
| Historical conditions | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py` | repo root | yes | all pass |
| Advanced conditions runtime | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py` | repo root | yes | all pass |
| Motion calculator unchanged | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py` | repo root | yes | all pass |
| Visibility calculator unchanged | `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py` | repo root | yes | all pass |

## Quality Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend` | yes | no formatting errors |
| Lint | `ruff check .` | `backend` | yes | no lint errors |
| Backend regression | `pytest -q` | `backend` | yes | all pass |

## DRY / No Legacy Scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Condition terms inventory | `rg -n "combust|cazimi|under_beams|under beams|retrograde|stationary" backend/app/domain/astrology -g "*.py"` | repo root | yes | no unclassified new calculator in builder/runtime |
| Object type branch guard | `rg -n "if .*object_type|\.object_type ==" backend/app/domain/astrology -g "*.py"` | repo root | yes | no forbidden consumer branch |
| Magic thresholds | `rg -n "\b8\.5\b|\b17\b|\b0\.2833\b|\b0\.01\b" backend/app/domain/astrology -g "*.py"` | repo root | yes | no local builder/runtime threshold |
| Calculator calls from mapper | `rg -n "calculate_solar_proximity|calculate_planetary_motion|calculate_solar_phase|calculate_planet_visibility" backend/app/domain/astrology/builders backend/app/domain/astrology/runtime -g "*.py"` | repo root | yes | zero hits |
| Guard registry | `rg -n "RG-146" _condamad/stories/regression-guardrails.md` | repo root | yes | row exists |

## Story Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story validate | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-219-chart-object-motion-visibility-payloads/00-story.md` | repo root | yes | pass |
| Story contract explain | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-219-chart-object-motion-visibility-payloads/00-story.md` | repo root | yes | pass |
| Story lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-219-chart-object-motion-visibility-payloads/00-story.md` | repo root | yes | pass |
| Story strict lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-219-chart-object-motion-visibility-payloads/00-story.md` | repo root | yes | pass |

## Diff Review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Whitespace/conflict check | `git diff --check` | repo root | yes | no errors |
| Diff summary | `git diff --stat` | repo root | yes | scoped story files |
| Worktree status | `git status --short` | repo root | yes | expected dirty files only |
