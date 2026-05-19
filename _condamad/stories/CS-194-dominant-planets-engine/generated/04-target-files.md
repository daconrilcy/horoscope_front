<!-- Carte des fichiers cibles pour limiter le delta de CS-194. -->

# Target Files

## Must Read

- `backend/app/domain/astrology/condition/contracts.py`
- `backend/app/domain/astrology/condition/planet_condition_profile_service.py`
- `backend/app/domain/astrology/interpretation/chart_signature.py`
- `backend/app/domain/astrology/interpretation/dominant_aspects.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`

## Must Search

- `rg -n "planet_dominance|PlanetDominance|dominance_factor" backend`
- `rg -n "SIGN_RULERS|PLANET_RULERS|DOMINANCE_FACTORS|DOMINANCE_WEIGHTS" backend/app backend/tests frontend/src`
- `rg -n "Session|select\\(|from app\\.infra|from app\\.services|from app\\.api|from app\\.domain\\.prediction|from app\\.services\\.prediction" backend/app/domain/astrology/dominance -g "*.py"`

## Likely Modified

- `backend/migrations/versions/*.py`
- `backend/app/infra/db/models/dignity_reference.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/services/reference_data/dignity_seed_service.py`
- `docs/db_seeder/astrology/astral_dominance_factor_types.json`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/dominance/**`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/tests/unit/domain/astrology/test_planet_dominance_engine.py`
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_chart_result_service.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `_condamad/stories/regression-guardrails.md`

## Forbidden Unless Justified

- `frontend/**`
- `backend/app/domain/prediction/**`
- `backend/app/services/llm_generation/**`
- `backend/app/domain/astrology/dignities/**`
- `backend/app/domain/astrology/condition/planet_condition_profile_service.py`
