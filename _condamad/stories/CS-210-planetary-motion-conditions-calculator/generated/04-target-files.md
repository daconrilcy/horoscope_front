# Target Files - CS-210

## Must Read

- `backend/app/domain/astrology/planetary_conditions/contracts.py`
- `backend/app/domain/astrology/planetary_conditions/__init__.py`
- `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py`
- `_condamad/stories/regression-guardrails.md`

## Likely Modified

- `backend/app/domain/astrology/planetary_conditions/contracts.py`
- `backend/app/domain/astrology/planetary_conditions/__init__.py`
- `backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py`
- `backend/app/domain/astrology/planetary_conditions/planetary_motion_profiles.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py`
- `_condamad/stories/CS-210-planetary-motion-conditions-calculator/generated/*`
- `_condamad/stories/CS-210-planetary-motion-conditions-calculator/evidence/validation.md`

## Forbidden Unless Explicitly Justified

- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/dignities/**`
- `backend/app/domain/astrology/condition/**`
- `backend/app/domain/astrology/dominance/**`
- `backend/app/domain/astrology/interpretation_adapters/**`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/api/**`
- `backend/app/infra/**`
- `backend/migrations/**`
- `frontend/src/**`
