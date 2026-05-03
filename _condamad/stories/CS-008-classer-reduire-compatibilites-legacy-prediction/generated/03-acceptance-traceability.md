# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Le registre legacy classe chaque surface auditee. | Added `legacy-surface-audit.md` with `EngineOutput`, `TimeBlock`, `engine_output=`, `categories`, `LLMNarrator`. | `pytest -q app/tests/unit/test_schemas_v3.py`; targeted `rg` classification. | PASS |
| AC2 | Les surfaces removables sont supprimees. | Removed `app.prediction.schemas.TimeBlock`; removed `PredictionPersistenceService.save(engine_output=...)`; migrated internal test consumers. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py ...`; targeted scan shows no `schemas.TimeBlock` active path and no `save(engine_output=...)`. | PASS |
| AC3 | Les surfaces publiques gardees ont une preuve externe. | Kept public `categories` unchanged; classified as `external-active`. | Frontend scan shows active `prediction.categories` consumers; `pytest -q app/tests/unit/test_public_projection.py` passed. | PASS |
| AC4 | Aucun narrateur legacy ne revient. | Existing narrator guard remains active; no runtime narrator file added. | `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py` passed; scan classified governance-only hits. | PASS |
| AC5 | La suppression ne modifie pas les contrats non vises. | No public payload change; persistence API narrowed only for internal legacy kwarg. | `pytest -q`, `ruff check app tests`, `python -c "from app.main import app; ..."` all passed. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
