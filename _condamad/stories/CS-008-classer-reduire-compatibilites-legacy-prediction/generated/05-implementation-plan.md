# Implementation Plan

## Initial findings

- Canonical orchestrator/persistence owners are under `backend/app/services/prediction`.
- `categories` is active in frontend types/pages/mappers and must remain `external-active`.
- `app.prediction.schemas.TimeBlock` had only a fixture-style consumer; canonical owners are `V3TimeBlock` and `block_generator.TimeBlock`.
- `PredictionPersistenceService.save(engine_output=...)` was only an internal compatibility keyword; production service already passes `bundle=`.
- `LLMNarrator` remains physically removed and guarded by RG-016/RG-017.

## Proposed changes

- Persist `legacy-surface-audit.md` and `legacy-surface-after.md`.
- Delete `schemas.TimeBlock`.
- Require `bundle` in `PredictionPersistenceService.save` and remove `**legacy_kwargs` handling.
- Migrate internal tests from `engine_output=` to `bundle=`.
- Add a guard in `test_daily_prediction_guardrails.py` blocking `schemas.TimeBlock` and `save(engine_output=...)`.
- Leave `EngineOutput` and public `categories` in place with explicit classification.

## Tests to add or update

- Update `app/tests/integration/test_v3_baselines.py`.
- Update `app/tests/unit/test_calibration_versioning.py`.
- Update `app/tests/unit/test_persistence_explainability.py`.
- Add `test_prediction_removed_legacy_compatibility_surfaces_stay_removed`.

## Risk assessment

- `EngineOutput` remains as a classified active internal surface; migrating it fully would be a separate V2 DTO convergence story.
- Public `categories` remains due frontend consumers and should not be removed without API/product decision.

## Rollback strategy

- Revert only story-scoped code and capsule changes.
