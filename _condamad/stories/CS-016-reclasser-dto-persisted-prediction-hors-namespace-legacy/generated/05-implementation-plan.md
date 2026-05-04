# Implementation Plan

## Repository findings

- `backend/app/prediction` is already absent in the current worktree.
- Persisted DTOs already live under `backend/app/domain/prediction`.
- Repositories DB import `PersistedPredictionSnapshot`, `PersistedUserBaseline` and `CalibrationData` from `app.domain.prediction`.
- Existing guardrails block the legacy package globally, but RG-036 needs an explicit repository-level persisted DTO guard.

## Changes

- Persist DTO ownership decisions in `persisted-dto-classification.md`.
- Capture observed before/after inventories.
- Add `test_prediction_repositories_do_not_import_legacy_persisted_dtos`.
- Complete CONDAMAD traceability and final evidence.
- Move CS-016 status to `ready-to-review` after validation.

## Tests and checks

- `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`
- `pytest -q app/tests/integration/test_v3_persistence.py app/tests/integration/test_relative_scoring_service.py`
- `pytest -q app/tests/integration/test_daily_prediction_api.py`
- Legacy import scans required by the story.
- `ruff check app/infra/db/repositories app/tests`

## Rollback

Revert only the CS-016 guard/test and CONDAMAD evidence files. No runtime schema or API changes are expected.
