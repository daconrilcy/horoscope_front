# Target Files

## Must read

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/runtime/**`
- `backend/app/services/natal/calculation_service.py`
- `backend/app/services/reference_data_service.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/infra/db/house_system_reference.py`
- Existing tests under `backend/app/tests/unit` and `backend/tests/unit/domain/astrology`

## Required searches

- `rg -n "ReferenceDataService\.get_active_reference_data|reference_data: dict" backend/app/domain/astrology backend/app/services/natal`
- `rg -n "PLANET_KEYWORDS|SIGN_RULERS|DEFAULT_ORB|ASPECT_WEIGHTS|HOUSE_MEANINGS" backend/app/domain/astrology backend/app/services/natal`
- `rg -n "UNKNOWN_SIGN|EXACT_ORB_DEG|TIGHT_RATIO|MODERATE_RATIO" backend/app/domain/astrology backend/app/services/natal`
- `rg -n "SwissEph.*simplified|simplified.*SwissEph|calculation_engine.*simplified" backend/app/domain/astrology backend/app/services/natal`
- `rg -n "domain\.prediction|app\.domain\.prediction|app\.services\.prediction|AIEngineAdapter|OpenAI|chat\.completions|llm" backend/app/domain/astrology`

## Modified files

- Runtime contracts: `backend/app/domain/astrology/runtime/runtime_reference.py`, `backend/app/domain/astrology/runtime/__init__.py`
- Domain calculation: `backend/app/domain/astrology/natal_calculation.py`, `backend/app/domain/astrology/builders/aspect_runtime_builder.py`, `backend/app/domain/astrology/interpretation/aspect_strength.py`
- Infra/service: `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`, `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`, `backend/app/infra/db/repositories/__init__.py`, `backend/app/services/natal/calculation_service.py`, `backend/app/services/reference_data_service.py`
- Tests/factories: `backend/tests/factories/astrology_runtime_reference_factory.py`, new guard/contract tests, and migrated natal/aspect tests.

## Forbidden or high-risk files

- `frontend/**` unchanged.
- `backend/pyproject.toml` unchanged.
- No new dependency or requirements file.
