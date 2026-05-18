# Validation Plan

## Environment assumptions

- Repository root: `c:\dev\horoscope_front`
- Backend commands run from `backend/`
- All Python commands require `.\.venv\Scripts\Activate.ps1`

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Seed integrity | `pytest -q app/tests/unit/test_astral_point_seed_integrity.py` | `backend/` | yes | all pass |
| Runtime repository | `pytest -q app/tests/unit/test_astral_point_repository.py app/tests/unit/test_astrology_runtime_reference_repository.py` | `backend/` | yes | all pass |
| Resolver and natal points | `pytest -q tests/unit/domain/astrology/test_astral_point_calculation_resolver.py tests/unit/domain/astrology/test_natal_result_contains_configured_points.py tests/unit/domain/astrology/test_natal_aspects_include_points.py` | `backend/` | yes | all pass |
| Boundaries and service regression | `pytest -q app/tests/unit/test_astrology_runtime_reference_guard.py app/tests/unit/test_astrology_prediction_boundary.py app/tests/unit/test_natal_calculation_service.py` | `backend/` | yes | all pass |
| Existing seed/docs coverage | `pytest -q app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_backend_docs_ownership.py` | `backend/` | yes | all pass |
| API propagation and real point aspect output | `pytest -q app/tests/integration/test_natal_calculate_api.py::test_calculate_natal_passes_include_points_in_aspects tests/unit/domain/astrology/test_natal_aspects_include_points.py` | `backend/` | yes | all pass |
| Consolidated targeted story suite | `pytest -q app/tests/unit/test_astral_point_seed_integrity.py app/tests/unit/test_astral_point_repository.py app/tests/unit/test_astrology_runtime_reference_repository.py app/tests/unit/test_prediction_reference_repository.py tests/unit/domain/astrology/test_astral_point_calculation_resolver.py tests/unit/domain/astrology/test_natal_result_contains_configured_points.py tests/unit/domain/astrology/test_natal_aspects_include_points.py app/tests/unit/test_astrology_runtime_reference_guard.py app/tests/unit/test_astrology_prediction_boundary.py app/tests/unit/test_natal_calculation_service.py app/tests/integration/test_natal_calculate_api.py::test_calculate_natal_passes_include_points_in_aspects` | `backend/` | yes | all pass |
| Runtime evidence generation | inline Python script after `.\.venv\Scripts\Activate.ps1; Set-Location backend` | repo root then `backend/` | yes | after artifacts generated from repository/service execution |

## DRY / No Legacy Scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Flat point fields | `rg -n "true_node|mean_node|\blilith\b" app/domain/astrology app/services/natal -g "*.py"` | `backend/` | yes | zero active hit |
| Local point catalogs | `rg -n "ASTRAL_POINTS\s*=|POINT_VARIANTS\s*=|NODE_VARIANTS\s*=|LILITH_VARIANTS\s*=" app/domain/astrology app/services/natal -g "*.py"` | `backend/` | yes | zero active hit |
| Runtime dict contracts | `rg -n "dict\[str, Any\]|list\[dict" app/domain/astrology/runtime app/infra/db/repositories/astrology_runtime_reference_repository.py app/infra/db/repositories/astrology_runtime_reference_mapper.py -g "*.py"` | `backend/` | yes | only classified non-point legacy hits |
| Editorial contamination | `rg -n "AstralPointInterpretationKeywordModel|AstralPointInterpretationProfileModel|keyword_set|micro_note" app/domain/astrology/natal_calculation.py app/domain/astrology/calculators -g "*.py"` | `backend/` | yes | zero hit |

## Quality Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format changed Python files | `ruff format <changed python files>` | `backend/` | yes | formatted |
| Lint backend | `ruff check .` | `backend/` | yes | no errors |
| Story validate/lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py ...` and `condamad_story_lint.py --strict ...` | repo root | yes | PASS |

## Diff Review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | story files only |
| Whitespace check | `git diff --check` | repo root | yes | no errors |
| Worktree status | `git status --short` | repo root | yes | expected story files only plus pre-existing unrelated doc |
