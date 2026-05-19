# Target Files

## Must inspect

- `backend/app/domain/astrology/condition/contracts.py`
- `backend/app/domain/astrology/condition/planet_condition_profile_service.py`
- `backend/app/domain/astrology/condition/planet_condition_signal_builder.py`
- `backend/app/domain/astrology/dominance/planet_dominance_engine.py`
- `backend/app/domain/astrology/dominance/contracts.py`
- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/infra/db/models/dignity_reference.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `_condamad/stories/regression-guardrails.md`

## Likely modified

- `backend/migrations/versions/20260519_0134_create_advanced_condition_references.py`
- `backend/app/infra/db/models/dignity_reference.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/services/reference_data/dignity_seed_service.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/dominance/planet_dominance_engine.py`
- `backend/app/services/chart/json_builder.py`
- `docs/db_seeder/astrology/astral_advanced_condition_*.json`
- Targeted backend tests under `backend/tests/unit/domain/astrology` and
  `backend/app/tests/unit`.

## Forbidden unless justified

- `frontend/**`
- `backend/app/services/llm_generation/**`
- `backend/app/domain/prediction/**`
- `backend/app/domain/astrology/calculators/**`
- Position astronomy or SwissEph adapters.
