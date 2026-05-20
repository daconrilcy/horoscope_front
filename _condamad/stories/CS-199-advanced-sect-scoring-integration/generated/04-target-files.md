# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-199-advanced-sect-scoring-integration/00-story.md`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
- `backend/app/domain/astrology/advanced_conditions/advanced_condition_engine.py`
- `backend/app/domain/astrology/advanced_conditions/hayz_calculator.py`
- `backend/app/domain/astrology/condition/planet_condition_profile_service.py`
- `backend/app/domain/astrology/dominance/planet_dominance_engine.py`
- `backend/app/domain/astrology/interpretation_adapters/interpretation_adapter_engine.py`
- `backend/app/services/chart/json_builder.py`
- Relevant unit tests under `backend/tests/unit/domain/astrology/` and `backend/app/tests/unit/`.

## Required searches before editing

```powershell
rg -n "hayz|out_of_sect|PlanetSectCondition|sect_condition" backend/app/domain/astrology backend/tests -g "*.py"
rg -n "SectCalculator|PlanetSectConditionCalculator|planet_sect_condition_calculator" backend/app/domain/astrology/condition backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters backend/app/services/chart -g "*.py"
rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|SECT_PLANETS|DAY_SECT_PLANETS|NIGHT_SECT_PLANETS|ABOVE_HORIZON_HOUSES|BELOW_HORIZON_HOUSES" backend/app -g "*.py"
```

## Modified files

- `backend/app/domain/astrology/advanced_conditions/hayz_calculator.py`
- `backend/tests/unit/domain/astrology/advanced_condition_test_helpers.py`
- `backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`
- `backend/tests/unit/domain/astrology/test_hayz_calculator.py`
- `backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py`
- `backend/tests/unit/domain/astrology/test_planet_dominance_engine.py`
- `backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py`
- `_condamad/stories/CS-199-advanced-sect-scoring-integration/evidence/*`
- `_condamad/stories/CS-199-advanced-sect-scoring-integration/generated/*`

## Forbidden or high-risk files

- `frontend/**`
- `backend/app/api/**`
- `backend/app/infra/**`
- `backend/app/domain/prediction/**`
- `backend/app/infra/db/**`
- `migrations/**`
- `docs/db_seeder/**`
