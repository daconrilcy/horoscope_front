# Validation Plan

## Environment Assumptions

- OS: Windows / PowerShell.
- Python commands require `.\\.venv\\Scripts\\Activate.ps1`.
- Frontend package manager declared by `frontend/package.json`: `npm`.

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend traditional chain | `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py backend/tests/unit/domain/astrology/test_traditional_condition_normalizer.py backend/tests/unit/domain/astrology/test_sect_nature_mitigation_detector.py backend/tests/unit/domain/astrology/test_advanced_condition_engine.py backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` | repo root | yes | all tests pass |
| Frontend expert panel | `npm --prefix frontend test -- NatalExpertPanel` | repo root | yes | test file passes |

## DRY / No Legacy Scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Doctrine constants | `rg -n $doctrine backend/app frontend -g "*.py" -g "*.ts" -g "*.tsx" -g "*.js" -g "*.jsx"` | repo root | yes | no forbidden non-owner hits |
| Legacy aliases | `rg -n $legacy backend/app backend/tests frontend -g "*.py" -g "*.ts" -g "*.tsx" -g "*.js" -g "*.jsx"` | repo root | yes | all hits classified |
| Calculator leakage | `rg -n $calculators backend/app/services/chart frontend backend/app/infra/db/repositories -g "*.py" -g "*.ts" -g "*.tsx" -g "*.js" -g "*.jsx"` | repo root | yes | no forbidden leakage |
| Frontend derivation | `rg -n $frontendDerivation frontend -g "*.ts" -g "*.tsx" -g "*.js" -g "*.jsx"` | repo root | yes | no forbidden frontend derivation |

## Quality Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend format | `.\\.venv\\Scripts\\Activate.ps1; ruff format .` | repo root | yes | no formatting changes needed or formatter succeeds |
| Backend lint | `.\\.venv\\Scripts\\Activate.ps1; ruff check .` | repo root | yes | no lint errors |
| Frontend type/lint | `npm --prefix frontend run lint` | repo root | yes | TypeScript no-emit checks pass |
| Frontend build | `npm --prefix frontend run build` | repo root | yes | production build succeeds |
| Frontend typecheck script probe | `npm --prefix frontend run typecheck` | repo root | conditional | pass if script exists; otherwise document adaptation |

## Evidence Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Evidence files exist | `Test-Path` for the six required evidence artifacts | repo root | yes | every path returns `True` |
| Final status JSON | `.\\.venv\\Scripts\\Activate.ps1; python -m json.tool "$e/traditional-advanced-final-status.json"` | repo root | yes | JSON parses |
| Story validate | `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story` | repo root | yes | PASS |
| Story lint strict | `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story` | repo root | yes | PASS |

