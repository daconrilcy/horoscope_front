<!-- Cartographie des fichiers cible CS-215. -->

# Target Files

## Inspected Before Editing

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
- `backend/app/domain/astrology/dignities/__init__.py`
- `backend/app/domain/astrology/planetary_conditions/contracts.py`
- `backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`
- `backend/app/domain/astrology/natal_calculation.py`
- Tests existants de `backend/tests/unit/domain/astrology`.

## Modified Or Added

- `backend/app/domain/astrology/dignities/advanced_condition_modifiers.py`
- `backend/app/domain/astrology/dignities/advanced_condition_modifier_profiles.py`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
- `backend/app/domain/astrology/dignities/__init__.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/tests/unit/domain/astrology/dignities/test_advanced_condition_modifiers.py`
- `backend/tests/unit/domain/astrology/dignities/test_accidental_dignity_conditions_integration.py`

## Forbidden Unless Blocker

- `backend/app/domain/astrology/planetary_conditions/**`
- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/interpretation_adapters/**`
- `backend/app/services/chart/json_builder.py`
- `backend/app/api/**`
- `backend/app/infra/**`
- `backend/migrations/**`
- `frontend/src/**`

No forbidden production surface was modified.
