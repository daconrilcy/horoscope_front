# CS-198 Validation Plan

Toutes les commandes Python doivent etre lancees apres:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Tests cibles

- `pytest -q backend/tests/unit/domain/astrology/test_dignity_contracts.py`
- `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
- `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py`
- `pytest -q backend/app/tests/unit/test_chart_json_builder.py`
- `pytest -q backend/app/tests/unit/test_chart_result_service.py`
- `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py`

## Qualite

- `ruff format .`
- `ruff check .`

## Guards

- `rg -n "SectCalculator" backend/app/services/chart/json_builder.py`
- `rg -n "PlanetSectConditionCalculator|planet_sect_condition_calculator" backend/app/services/chart backend/app/domain/astrology/condition backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters -g "*.py"`
- `rg -n "\b7,\s*8,\s*9,\s*10,\s*11,\s*12\b|\b1,\s*2,\s*3,\s*4,\s*5,\s*6\b" backend/app/domain/astrology/dignities backend/app/services/chart -g "*.py"`
- `rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|COMMON_PLANETS|NEUTRAL_PLANETS|planet.*diurnal|planet.*nocturnal" backend/app/domain/astrology/dignities backend/app/services/chart -g "*.py"`
- `rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code|planet_sect_code|planet_sect_legacy" backend/app backend/tests -g "*.py"`
- `$forbidden = "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|OpenAI|AIEngineAdapter|chat\.completions|prompt"; rg -n $forbidden backend/app/domain/astrology/dignities -g "*.py"`
