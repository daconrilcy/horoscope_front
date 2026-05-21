# Target Files

## Must Read

- `backend/app/domain/astrology/advanced_conditions/contracts.py`
- `backend/app/domain/astrology/advanced_conditions/advanced_condition_engine.py`
- `backend/app/domain/astrology/advanced_conditions/traditional_condition_normalizer.py`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/services/chart/json_builder.py`
- `docs/db_seeder/astrology/astral_planet_natures.json`
- `docs/db_seeder/astrology/astral_advanced_condition_types.json`
- `docs/db_seeder/astrology/astral_advanced_condition_weights.json`
- `backend/tests/factories/astrology_runtime_reference_factory.py`
- `backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`
- `backend/app/tests/unit/test_chart_json_builder.py`

## Must Search

- `AstrologyRuntimeReference|planet_natures|nature_for_planet|PlanetSectCondition`
- `BENEFIC_PLANETS|MALEFIC_PLANETS|MIXED_PLANETS|NEUTRAL_PLANETS`
- `SectCalculator|PlanetSectConditionCalculator|AdvancedConditionEngine`
- `planet_code\s+in|if .*planet_code.*mars|if .*planet_code.*saturn|if .*planet_code.*jupiter|if .*planet_code.*venus`

## Likely Modified

- `backend/app/domain/astrology/advanced_conditions/contracts.py`
- `backend/app/domain/astrology/advanced_conditions/sect_nature_mitigation_detector.py`
- `backend/app/domain/astrology/advanced_conditions/advanced_condition_engine.py`
- `backend/app/domain/astrology/advanced_conditions/traditional_condition_normalizer.py`
- `backend/app/domain/astrology/advanced_conditions/__init__.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `docs/db_seeder/astrology/astral_advanced_condition_types.json`
- `docs/db_seeder/astrology/astral_advanced_condition_weights.json`
- tests under `backend/tests/unit/domain/astrology` and `backend/app/tests/unit`
- CS-206 evidence files.

## Forbidden Unless Justified

- `backend/app/api/**`
- `backend/app/domain/prediction/**`
- `migrations/**`
- `backend/app/domain/astrology/dignities/sect_calculator.py`
- `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py`
- `frontend/**`
