# Sect Contract Validation

## Commands run

| Command | Working directory | Result | Summary |
|---|---|---|---|
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_dignity_contracts.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` | repo root | PASS | 33 passed |
| `.\.venv\Scripts\Activate.ps1; ruff check . --fix; ruff format .; ruff check .` | repo root | PASS | 1 import ordering issue fixed, format unchanged after fix, all checks passed |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` | repo root | PASS | 2748 passed, 1 skipped, 1177 deselected |
| `rg -n "SectCalculator" backend/app/services/chart/json_builder.py` | repo root | PASS | zero hits |
| `rg -n "\b7,\s*8,\s*9,\s*10,\s*11,\s*12\b|\b1,\s*2,\s*3,\s*4,\s*5,\s*6\b" backend/app/domain/astrology/dignities backend/app/services/chart -g "*.py"` | repo root | PASS | zero hits |
| `rg -n "PlanetSectCondition|planet_sect_condition" backend/app backend/tests -g "*.py"` | repo root | PASS | zero hits |
| `rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code" backend/app backend/tests -g "*.py"` | repo root | PASS_WITH_CLASSIFIED_HITS | runtime reference internals only; no public compatibility alias added |
| `$forbidden = "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|OpenAI|AIEngineAdapter|chat\.completions|prompt"; rg -n $forbidden backend/app/domain/astrology/dignities -g "*.py"` | repo root | PASS | zero hits |
| `git diff --check` | repo root | PASS | no whitespace errors; Git emitted line-ending warnings only |

## Classified alias scan hits

| Pattern | File | Classification | Action | Status |
|---|---|---|---|---|
| `sect_code` | `backend/app/domain/astrology/runtime/runtime_reference.py` | runtime reference field for triplicity rulers | kept | allowed runtime internal |
| `sect_code` | `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` | DB reference projection | kept | allowed runtime internal |
| `sect_code` | `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` | DB-to-runtime mapper | kept | allowed runtime internal |
| `sect_code` | `backend/app/domain/astrology/dignities/essential_dignity_calculator.py` | existing triplicity reference usage | kept | allowed runtime internal |
| `sect_code` / `chart_sect_code` | `backend/tests/factories/astrology_runtime_reference_factory.py` | test reference data | kept | allowed fixture reference |
| `chart_sect_code` | `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py` | existing runtime condition key for hayz-style rules | kept | allowed runtime internal, not a public alias |

## Generated contract check

No generated frontend client or typed OpenAPI schema for `dignities.sect` was changed in this story. The backend chart JSON remains dynamically projected by `build_chart_json()`. The allowed public delta is documented by `sect-contract-before.json` and `sect-contract-after.json`.

## Review fixes

- Added symmetric missing-`below_horizon` rule coverage.
- Added strict `ChartSectResult` validation and projection fail-closed checks so `dignities.sect` cannot silently degrade to `null` when dignity results exist.
