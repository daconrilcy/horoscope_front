# Target Files - CS-216

## Must Read

- `backend/app/domain/astrology/planetary_conditions/contracts.py`
- `backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`
- `backend/app/domain/astrology/planetary_conditions/signal_factory.py`
- `backend/app/domain/astrology/planetary_conditions/__init__.py`
- `backend/app/domain/astrology/dignities/advanced_condition_modifiers.py`
- `backend/app/domain/astrology/dignities/advanced_condition_modifier_profiles.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/interpretation/__init__.py`
- `backend/app/domain/astrology/interpretation/profile_fields.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`
- `backend/tests/unit/domain/astrology/dignities/test_advanced_condition_modifiers.py`
- `backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py`

## Likely Modified

- `backend/app/domain/astrology/interpretation/advanced_conditions/contracts.py`
- `backend/app/domain/astrology/interpretation/advanced_conditions/advanced_condition_profile_catalog.py`
- `backend/app/domain/astrology/interpretation/advanced_conditions/profile_runtime.py`
- `backend/app/domain/astrology/interpretation/advanced_conditions/__init__.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/tests/unit/domain/astrology/interpretation/advanced_conditions/test_profile_runtime.py`
- `backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py`
- `_condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/evidence/validation.md`
- generated capsule evidence files.

## Forbidden Unless Blocker Is Documented

- `backend/app/domain/astrology/dignities/**`
- `backend/app/domain/astrology/planetary_conditions/**`
- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/interpretation_adapters/**`
- `backend/app/services/chart/json_builder.py`
- `backend/app/api/**`
- `backend/app/infra/**`
- `backend/migrations/**`
- `frontend/src/**`

## Required Searches

- `rg -n "interpretation_profiles_by_planet|AdvancedConditionInterpretationProfile|resolve_advanced_condition_profiles" backend/app backend/tests -g "*.py"`
- Forbidden scoring, surface, final-text and recalculation scans from the story validation plan.
