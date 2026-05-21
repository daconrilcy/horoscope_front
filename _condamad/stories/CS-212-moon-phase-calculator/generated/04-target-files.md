# Target Files

## Must Read

- `backend/app/domain/astrology/planetary_conditions/contracts.py`
- `backend/app/domain/astrology/planetary_conditions/__init__.py`
- `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
- `backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py`
- `backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
- Existing calculator tests in `backend/tests/unit/domain/astrology/planetary_conditions/`
- `_condamad/stories/regression-guardrails.md`

## Must Search

- Existing `moon_phase_calculator` or `calculate_moon_phase_condition`
- Forbidden symbols in the new calculator: API/infra/services dependencies, scoring, interpretation, `NatalResult`, transits, progressions, eclipses, ephemerides.
- Public symbols in adjacent roots to prove no integration.

## Likely Modified

- `backend/app/domain/astrology/planetary_conditions/__init__.py`
- `backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py`
- `_condamad/stories/CS-212-moon-phase-calculator/generated/*.md`
- `_condamad/stories/CS-212-moon-phase-calculator/evidence/validation.md`
- `_condamad/stories/story-status.md`

## Forbidden Unless Justified

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
