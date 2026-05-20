# CS-198 Planet Sect Validation

## Runtime source

Runtime source found: `AstrologyRuntimeReference.dignity_reference.accidental_rules`
contains typed `in_sect` and `out_of_sect` rules with `planet_code` and
`chart_sect_code`.

Observed in canonical seed/repository evidence:

- `sun`, `jupiter`, `saturn` -> `in_sect` for `day`.
- `moon`, `venus`, `mars` -> `in_sect` for `night`.
- `mercury` -> `in_sect` for runtime sect `all`, interpreted as
  `common` / `variable_by_condition`.
- `uranus` has no explicit rule in current runtime data and is therefore
  projected as `unknown`, not via fallback.

## Before / after

Allowed delta: only `dignities.planets[planet_code].sect_condition` is added.
The chart-level `dignities.sect`, scores and breakdowns stay stable in the
snapshot excerpt.

## Commands run

- `pytest -q backend/tests/unit/domain/astrology/test_dignity_contracts.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/app/tests/unit/test_chart_json_builder.py` - PASS
- `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_result_service.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py` - PASS
- `pytest -q backend/tests/unit/domain/astrology/test_dignity_contracts.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py` - PASS, 58 passed.
- `ruff format .` - PASS, 1473 files left unchanged.
- `ruff check .` - PASS, all checks passed.
- `git diff --check` - PASS.
- `python -c "from app.main import app; print(app.title)"` from `backend/` after venv activation - PASS, `horoscope-backend`.

## Scan results

- `rg -n "SectCalculator" backend/app/services/chart/json_builder.py` - PASS zero hit.
- `rg -n "PlanetSectConditionCalculator|planet_sect_condition_calculator" backend/app/services/chart backend/app/domain/astrology/condition backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters -g "*.py"` - PASS zero hit.
- `rg -n "\b7,\s*8,\s*9,\s*10,\s*11,\s*12\b|\b1,\s*2,\s*3,\s*4,\s*5,\s*6\b" backend/app/domain/astrology/dignities backend/app/services/chart -g "*.py"` - PASS zero hit.
- `rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|COMMON_PLANETS|NEUTRAL_PLANETS|planet.*diurnal|planet.*nocturnal" backend/app/domain/astrology/dignities backend/app/services/chart -g "*.py"` - PASS zero hit.
- `rg -n "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|OpenAI|AIEngineAdapter|chat\.completions|prompt" backend/app/domain/astrology/dignities -g "*.py"` - PASS zero hit.

Allowed hits for legacy-field scan:

- `chart_sect_code` appears in runtime fixture/repository/mapper and in
  `planet_sect_condition_calculator.py` as the runtime condition key. No public
  alias field is introduced.
- `sect_code` appears in triplicity runtime contracts/repository/fixture. No
  public `sect_code` field is introduced by CS-198.

## Generated contract

No generated OpenAPI/client schema models the nested chart JSON shape for
`dignities.planets`; the change is a dynamic payload additive projection.
