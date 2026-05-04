# Implementation Plan

## Findings

- `backend/app/domain/prediction` did not exist before implementation.
- `backend/app/prediction` contained 55 tracked files and active imports across services, API, infra, jobs and tests.
- CS-015 a CS-017 were not implemented yet, so the only available canonical owner matching the story was `backend/app/domain/prediction`.

## Changes

- Move the legacy package to `backend/app/domain/prediction`.
- Replace active imports from `app.prediction.*` to `app.domain.prediction.*`.
- Convert the former growth allowlist guard into an extinction guard.
- Persist before/after inventory and removal audit.

## Validation

- Targeted unit guard and engine tests.
- Daily prediction API integration tests.
- Negative scans for old imports and old folder.
- `ruff check app tests` and `ruff format --check app tests`.
- Minimal app import startup check.

## Risk

- The implementation removes `app.prediction` for internal code. External, undocumented consumers of that Python package would break, which is intended by the story unless such a consumer is documented.
