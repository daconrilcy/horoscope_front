<!-- Guardrails No Legacy / DRY generes pour CS-217. -->

# No Legacy / DRY Guardrails

## Canonical Owners

- Contract owner: `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- Projection owner: `backend/app/domain/astrology/builders/chart_object_runtime_builder.py`
- Natal wiring owner: `backend/app/domain/astrology/natal_calculation.py`

## Forbidden

- `calculability`
- shim, alias, fallback, compatibility wrapper, duplicate active contract
- Pydantic/FastAPI/SQLAlchemy/API/infra/services imports in the new runtime and builder modules
- `object_type` decision branches in business calculators outside projection builders
- public JSON/API/frontend/db/migration changes

## Required Evidence

- Targeted runtime, natal, and architecture tests pass.
- Negative scans for forbidden dependencies and `calculability`.
- Public leak scan returns zero hits outside allowed runtime/domain/tests.
- Adjacent diff review confirms out-of-scope surfaces are untouched.
