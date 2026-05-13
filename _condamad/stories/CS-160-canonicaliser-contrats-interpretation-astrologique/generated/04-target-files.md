# Target Files CS-160

## Must Read

- `backend/app/domain/astrology/runtime/house_runtime_data.py`
- `backend/app/domain/astrology/interpretation/house_strength.py`
- `backend/app/domain/astrology/builders/house_runtime_builder.py`
- `backend/app/services/chart/json_builder.py`
- `backend/tests/unit/domain/astrology/test_house_strength.py`
- `backend/tests/unit/domain/astrology/test_house_runtime_builder.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `_condamad/stories/regression-guardrails.md`

## Must Search

- `rg -n "HouseStrengthRuntimeData|strength\\.score|reasons\\.append|reasons\\s*=\\s*\\[" backend/app backend/tests -g "*.py"`
- `rg -n "strength\\.score\\s*[<>]=?" backend/app/domain/prediction -g "*.py"`
- `rg -n "app\\.domain\\.prediction|app\\.services\\.prediction|prediction_categories|house_category_weights|visibility_weight|base_priority|routing_role|DomainRouter|PublicAstroFoundationProjector" backend/app/domain/astrology -g "*.py"`

## Likely Modified

- `backend/app/domain/astrology/interpretation/house_strength_contracts.py`
- `backend/app/domain/astrology/interpretation/house_strength.py`
- `backend/app/domain/astrology/interpretation/__init__.py`
- `backend/app/domain/astrology/runtime/house_runtime_data.py`
- `backend/app/services/chart/json_builder.py`
- `backend/tests/unit/domain/astrology/test_house_strength.py`
- `backend/tests/unit/domain/astrology/test_house_runtime_builder.py`
- `backend/app/tests/unit/test_chart_json_builder.py`

## Forbidden Unless Directly Justified

- `backend/app/domain/prediction/**`
- `backend/migrations/**`
- `frontend/**`
