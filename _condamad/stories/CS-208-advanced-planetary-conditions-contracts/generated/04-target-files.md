# Target Files - CS-208

## Files to Inspect

- `backend/app/domain/astrology/advanced_conditions/contracts.py`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/condition/contracts.py`
- `backend/tests/unit/domain/astrology/test_dignity_contracts.py`
- `backend/tests/unit/domain/astrology/test_traditional_condition_normalizer.py`
- `_condamad/stories/regression-guardrails.md`

## Files to Modify

- `backend/app/domain/astrology/planetary_conditions/__init__.py`
- `backend/app/domain/astrology/planetary_conditions/contracts.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
- `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/evidence/validation.md`
- `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/generated/*.md`
- `_condamad/stories/story-status.md`

## Forbidden Production Surfaces

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

## Search Terms

- `AdvancedPlanetaryConditionsResult`
- `SolarProximityCondition`
- `planetary_conditions`
- `Any`
- `dict[str, Any]`
- `calculate_|compute_|resolve_|detect_|score_delta|interpretation_weight|prompt`
