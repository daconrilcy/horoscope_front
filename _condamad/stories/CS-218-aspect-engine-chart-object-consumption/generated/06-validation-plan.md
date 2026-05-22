# Validation Plan

## Environment Assumptions

- OS: Windows / PowerShell.
- Python commands require `.\.venv\Scripts\Activate.ps1`.
- Backend validation runs from repo root for targeted tests and from
  `backend/` for global quality.

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Selector/projector aspects | `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_aspect_chart_object_inputs.py` | repo root | yes | all pass |
| Natal aspect flow | `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_natal_aspects_include_points.py` | repo root | yes | all pass |
| Architecture guard | `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_chart_object_runtime_architecture.py` | repo root | yes | all pass |
| NatalResult collections | `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_natal_result_chart_objects.py` | repo root | yes | all pass |
| Aspect runtime non-regression | `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py` | repo root | yes | all pass |

## Architecture / DRY / No Legacy Scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| No `object_type` branch in calculators | `rg -n "object_type ==|\.object_type|ChartObjectType" backend/app/domain/astrology/calculators -g "*.py"` | repo root | yes | zero active hits |
| No direct historical collections in aspect engine | `rg -n "planet_positions|astral_points|angles|fixed_stars" backend/app/domain/astrology/calculators -g "*.py"` | repo root | yes | only classified non-aspect-engine hits |
| No specialized aspect builders | `rg -n "PlanetAspectBodyBuilder|AngleAspectBodyBuilder|AstralPointAspectBodyBuilder|FixedStarAspectBodyBuilder" backend/app backend/tests -g "*.py"` | repo root | yes | only test guard constants |
| RG registered | `rg -n "RG-145" _condamad/stories/regression-guardrails.md` | repo root | yes | one registry hit |

## Quality Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `.\.venv\Scripts\Activate.ps1; Push-Location backend; ruff format .; Pop-Location` | repo root | yes | no formatting errors |
| Lint | `.\.venv\Scripts\Activate.ps1; Push-Location backend; ruff check .; Pop-Location` | repo root | yes | no lint errors |
| Full backend suite | `.\.venv\Scripts\Activate.ps1; Push-Location backend; pytest -q; Pop-Location` | repo root | yes | all pass |
| Diff whitespace | `git diff --check` | repo root | yes | no whitespace errors |

## Story Contract Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story validate | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md` | repo root | yes | PASS |
| Story validate explain | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md` | repo root | yes | no missing contracts |
| Story lint | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md` | repo root | yes | PASS |
| Story lint strict | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-218-aspect-engine-chart-object-consumption/00-story.md` | repo root | yes | PASS |
