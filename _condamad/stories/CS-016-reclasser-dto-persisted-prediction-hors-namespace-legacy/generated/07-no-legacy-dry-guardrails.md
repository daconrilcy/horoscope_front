# No Legacy / DRY Guardrails

## Canonical owner

`backend/app/domain/prediction` is the only active owner for persisted prediction DTOs used across domain, services, API tests and DB repositories.

## Forbidden imports

- `from app.prediction.persisted_snapshot`
- `from app.prediction.persisted_relative_score`
- `from app.prediction.persisted_baseline`
- `from app.prediction.context import CalibrationData`
- Any import of `app.prediction.persisted_*` or `app.prediction.context` from `backend/app/infra/db/repositories`.

## Forbidden implementation patterns

- Recreate `backend/app/prediction`.
- Add a re-export module under `app.prediction`.
- Duplicate DTO dataclasses under `app.infra`.
- Add fallback imports from legacy to canonical.
- Keep tests importing legacy paths as nominal behavior.

## Required evidence

- Persistent classification in `persisted-dto-classification.md`.
- Negative scans for legacy imports.
- Guard test in `backend/app/tests/unit/test_daily_prediction_guardrails.py`.
- Persistence and API regression tests.
