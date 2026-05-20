# Target Files

## Must Read

- `backend/app/services/chart/json_builder.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_chart_result_service.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py`
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`
- `_condamad/stories/regression-guardrails.md`

## Must Search

- Forbidden projection engines in `backend/app/services/chart/json_builder.py`.
- Legacy sect aliases in `backend/app backend/tests`.
- Structural block consumers for `astral_points`, `signs_runtime`, `chart_balance`, `house_rulers`.

## Likely Modified

- `backend/app/services/chart/json_builder.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_chart_result_service.py`
- `_condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/*`
- `_condamad/stories/CS-201-natal-public-json-projection-cleanup/generated/*`
- `_condamad/stories/story-status.md`

## Forbidden Unless Directly Justified

- `frontend/**`
- `backend/app/api/**`
- `backend/app/infra/**`
- `backend/app/domain/astrology/**` calculation owners
- `migrations/**`
- `docs/db_seeder/**`
