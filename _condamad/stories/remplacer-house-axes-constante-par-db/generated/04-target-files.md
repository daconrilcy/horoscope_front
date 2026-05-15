# Target Files

## Must read

- `backend/app/domain/astrology/constants/house_axes.py`
- `backend/app/domain/astrology/builders/house_runtime_builder.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/infra/db/models/interpretation_reference.py`
- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/tests/unit/domain/astrology/test_house_runtime_builder.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`

## Must search

- `rg "resolve_house_axis|HOUSE_AXES|house_axes" backend docs`
- `rg "astral_house_axis|house_axis" backend`
- `rg "app\\.domain\\.prediction|app\\.services\\.prediction" backend/app/domain/astrology -g "*.py"`

## Likely modified

- `backend/app/domain/astrology/builders/house_runtime_builder.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/tests/unit/domain/astrology/test_house_runtime_builder.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`

## Likely deleted

- `backend/app/domain/astrology/constants/house_axes.py`

## Forbidden unless justified

- Migrations existantes.
- Frontend.
- Suites de tests globales.

