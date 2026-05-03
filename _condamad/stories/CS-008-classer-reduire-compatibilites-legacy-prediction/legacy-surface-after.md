# Legacy Surface After — CS-008

Post-implementation comparison.

| Item | Final state | Evidence | Decision |
|---|---|---|---|
| `EngineOutput` | Preserved as classified `canonical-active` for current V2 editorial/persistence surface. | Full backend suite passes; remaining hits are active production/tests, not a removable facade in this story. | `keep` |
| `app.prediction.schemas.TimeBlock` | Removed. | `backend/app/prediction/schemas.py` no longer defines `class TimeBlock`; `backend/app/tests/integration/test_v3_baselines.py` now uses `V3TimeBlock`; `test_prediction_removed_legacy_compatibility_surfaces_stay_removed` guards the deletion. | `delete` |
| `PredictionPersistenceService.save(engine_output=...)` | Removed. | `backend/app/services/prediction/persistence_service.py` now requires `bundle`; calibration/explainability tests migrated to `bundle=`; guard scans AST calls to `save(engine_output=...)`. | `replace-consumer` |
| `categories` public field | Preserved as `external-active`. | Frontend uses `prediction.categories` in types, pages, dashboard hooks and mappers; backend public projection tests still validate the field. | `keep` |
| `LLMNarrator` | Remains removed. | `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py` passed; targeted scan keeps only historical/governance references. | `delete` |

Allowed differences: deletion of `schemas.TimeBlock` and removal of the `save(engine_output=...)` compatibility keyword. Public `categories` is intentionally unchanged.
