# Target Files

## Read before implementation

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/replace-seed-validation-facade-test/00-story.md`
- `backend/app/tests/unit/test_seed_validation.py`
- `backend/app/ops/llm/bootstrap/use_cases_seed.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- Existing backend architecture guards under `backend/app/tests/unit/test_backend_*.py`

## Searches run

```powershell
rg -n "SeedValidationError|seed validation|required persona|persona" backend/app backend/scripts backend/tests
rg -n "assert True|pass$" backend/app/tests backend/tests -g test_*.py
rg -n "seed_30_5|PROMPTS_TO_SEED|seed validation|SeedValidationError|validate_seed|validate.*PROMPTS" backend/app/tests backend/tests backend/app backend/scripts -g *.py
rg -n "seed_validation_required_persona_empty_allowed|assert True" backend/app/tests backend/tests -g test_*.py
```

## Modified files

- `backend/app/ops/llm/bootstrap/use_cases_seed.py`
- `backend/app/tests/unit/test_seed_validation.py`
- `backend/app/tests/unit/test_backend_noop_tests.py`
- `backend/app/tests/unit/test_pricing_experiment_service.py`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/replace-seed-validation-facade-test/**`

## Forbidden or intentionally untouched

- `frontend/`
- `backend/alembic/`
- `requirements.txt`
- API routes and OpenAPI contract files
