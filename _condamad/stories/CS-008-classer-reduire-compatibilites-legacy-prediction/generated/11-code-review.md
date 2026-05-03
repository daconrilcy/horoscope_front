# CONDAMAD Code Review

## Review target

- Story: `CS-008-classer-reduire-compatibilites-legacy-prediction`
- Source: `_condamad/stories/CS-008-classer-reduire-compatibilites-legacy-prediction/00-story.md`
- Review date: 2026-05-04
- Review pass: second review after CR-001 fix
- Verdict: `CLEAN`

## Inputs reviewed

- Story contract and AC1-AC5.
- `legacy-surface-audit.md` and `legacy-surface-after.md`.
- `generated/03-acceptance-traceability.md`.
- `generated/10-final-evidence.md`.
- Current git diff for CS-008 application, test, and governance files.
- `_condamad/stories/regression-guardrails.md`, especially RG-016, RG-017, RG-028.
- `_condamad/stories/story-status.md` row for CS-008.

## Diff summary

- Removed `app.prediction.schemas.TimeBlock`.
- Removed `PredictionPersistenceService.save(engine_output=...)` compatibility handling.
- Migrated touched tests to `V3TimeBlock` and `bundle=`.
- Added an AST guard for removed prediction compatibility surfaces.
- Added CS-008 persistent classification artifacts.
- Fixed formatting drift reported by the first review pass.

## Findings

No actionable findings remain.

Resolved finding:

- CR-001 Medium: `ruff format --check app tests` previously failed on `backend/app/prediction/schemas.py` and `backend/app/tests/unit/test_persistence_explainability.py`; fixed with `ruff format` and revalidated in this second review.

## Acceptance audit

| AC | Review result | Notes |
|---|---|---|
| AC1 | PASS | `legacy-surface-audit.md` classifies `EngineOutput`, `TimeBlock`, `engine_output=`, `categories`, and `LLMNarrator`. |
| AC2 | PASS | Removable surfaces are deleted/migrated. Targeted scans and `test_prediction_removed_legacy_compatibility_surfaces_stay_removed` confirm no `app.prediction.schemas.TimeBlock` and no `save(engine_output=...)`. |
| AC3 | PASS | `categories` is preserved and classified `external-active`; active public/frontend consumers are documented. |
| AC4 | PASS | Existing LLM narrator guard remains in place; targeted reviewer test passed. |
| AC5 | PASS | Targeted tests, full backend suite, OpenAPI smoke, lint, and format checks passed. |

## Validation audit

Reviewer commands run from `C:\dev\horoscope_front` with `.\.venv\Scripts\Activate.ps1` before Python tooling:

| Command | Result |
|---|---|
| `cd backend; ruff format --check app tests` | PASS, 1080 files already formatted |
| `cd backend; ruff check app tests` | PASS |
| `cd backend; pytest -q app/tests/unit/test_daily_prediction_guardrails.py app/tests/unit/test_persistence_explainability.py app/tests/unit/test_calibration_versioning.py app/tests/integration/test_v3_baselines.py app/tests/unit/test_public_projection.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | PASS, 37 passed |
| `cd backend; pytest -q app/tests/unit/test_schemas_v3.py` | PASS, 28 passed |
| `cd backend; python -c "from app.main import app; schema = app.openapi(); assert 'paths' in schema; assert '/v1/predictions/daily' in schema['paths']; print('openapi ok')"` | PASS |
| `cd backend; rg -n "EngineOutput\|TimeBlock\|engine_output=\|\bcategories\b\|LLMNarrator" app tests` | PASS with classified expected hits |
| `cd backend; rg -n "from app\.prediction import\|app\.prediction\.llm_narrator\|LLMNarrator" app tests` | PASS with governance-only expected hits |
| `cd backend; rg -n "from app\.prediction\.schemas import .*TimeBlock\|class TimeBlock\|save\(.*engine_output\|engine_output=" app tests` | PASS with expected non-save/non-removed-surface hits only |
| `cd backend; pytest -q` | PASS, 3580 passed, 12 skipped |
| `python -m uvicorn app.main:app --host 127.0.0.1 --port 8765` plus `GET /openapi.json` | PASS, backend smoke ok |
| `git diff --check` | PASS, CRLF warnings only |

## DRY / No Legacy audit

- No compatibility alias or re-export was added for `TimeBlock`.
- `save(engine_output=...)` was removed rather than mapped through a fallback.
- Remaining `EngineOutput` and `categories` hits are classified as active kept surfaces.
- Remaining `TimeBlock` hits are canonical `app.prediction.block_generator.TimeBlock`, `V3TimeBlock`, persisted DB time block models, or guard text.
- Remaining `engine_output=` hits are public projection/API context parameters, not `PredictionPersistenceService.save(engine_output=...)`.
- RG-016, RG-017, and RG-028 are cited and have deterministic evidence.

## Residual risks

- `EngineOutput` remains active by classification; retiring it requires a dedicated migration story.
- Public `categories` remains active until a product/API/frontend contract decision.

## Verdict

`CLEAN`

The second review found no remaining actionable issue. CS-008 is synchronized as `done` in `_condamad/stories/story-status.md`.
