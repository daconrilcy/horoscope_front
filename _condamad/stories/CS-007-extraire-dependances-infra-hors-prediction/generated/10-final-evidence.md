# Final Evidence - CS-007

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-007-extraire-dependances-infra-hors-prediction`
- Source story: `_condamad/stories/CS-007-extraire-dependances-infra-hors-prediction/00-story.md`
- Capsule path: `_condamad/stories/CS-007-extraire-dependances-infra-hors-prediction`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-007-extraire-dependances-infra-hors-prediction/00-story.md`
- Initial `git status --short`: pre-existing dirty files included `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`, and untracked CS-007 through CS-013 story folders.
- Pre-existing dirty files: unrelated story folders CS-008 through CS-013 left untouched.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status/tasks updated only. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated before implementation. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC5 completed. |
| `generated/04-target-files.md` | yes | yes | PASS | Story-specific targets listed. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Executable checks listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Forbidden paths listed. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed with validation evidence. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `PredictionContextLoader` moved to `app.services.prediction.context_loader`; `LoadedPredictionContext` and `CalibrationData` live in pure `app.prediction.context`; `test_prediction_pure_namespace_has_no_db_loader_or_persistence_imports` has no allowlist. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` passed as part of targeted run; infra scan returned zero hits. | PASS | DB loader, SQLAlchemy and repository dependencies removed from `app.prediction`. |
| AC2 | `PredictionPersistenceService` moved to `app.services.prediction.persistence_service`; all persistence tests import canonical service path. | `pytest -q app/tests/integration/test_prediction_persistence.py app/tests/integration/test_engine_persistence_e2e.py` passed, 12 tests. | PASS | Persistence semantics preserved by integration tests. |
| AC3 | Active consumers migrated away from `app.prediction.context_loader` and `app.prediction.persistence_service`. | `rg -n "app\\.prediction\\.context_loader\|app\\.prediction\\.persistence_service" app tests` returned zero hits. | PASS | No facade or re-export kept. |
| AC4 | No `backend/prediction` root directory created. | `python -c "import os; assert not os.path.exists('prediction')"` passed from `backend`. | PASS | |
| AC5 | `infra-dependency-before.md` and `infra-dependency-after.md` persisted. | Artefacts present; guardrail test passed; after scan is zero-hit. | PASS | No allowlist exception remains. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/prediction/context.py` | added | Pure loaded-context contract. | AC1 |
| `backend/app/infra/db/repositories/prediction_schemas.py` | modified | Re-export pure `CalibrationData` for infra compatibility. | AC1 |
| `backend/app/prediction/calibrator.py` | modified | Consume pure `CalibrationData` without importing infra. | AC1 |
| `backend/app/prediction/public_projection.py` | modified | Remove SQLAlchemy `Session` type dependency from prediction. | AC1 |
| `backend/app/services/prediction/context_loader.py` | added/moved | Canonical DB context loader owner. | AC1, AC2 |
| `backend/app/services/prediction/persistence_service.py` | added/moved | Canonical DB persistence owner. | AC2 |
| `backend/app/prediction/context_loader.py` | deleted | Remove legacy active path. | AC1, AC3 |
| `backend/app/prediction/persistence_service.py` | deleted | Remove legacy active path. | AC2, AC3 |
| `backend/app/services/prediction/__init__.py` | modified | Export canonical services. | AC3 |
| Backend consumers/tests importing old modules | modified | Migrate imports to canonical paths. | AC3 |
| `backend/app/tests/unit/test_daily_prediction_guardrails.py` | modified | Inventory update and infra boundary guard. | AC1, AC4 |
| `_condamad/stories/CS-007-extraire-dependances-infra-hors-prediction/**` | added/modified | Capsule, before/after evidence, final traceability. | AC1-AC5 |
| `_condamad/stories/story-status.md` | modified | Mark CS-007 `ready-to-review`. | AC5 |

## Files deleted

| File | Reason |
|---|---|
| `backend/app/prediction/context_loader.py` | Legacy DB loader path removed, not kept as facade. |
| `backend/app/prediction/persistence_service.py` | Legacy persistence path removed, not kept as facade. |

## Tests added or updated

- Updated `backend/app/tests/unit/test_daily_prediction_guardrails.py` with an AST guard for forbidden DB loader/persistence imports under `app.prediction`.
- Updated context, persistence, engine, integration, regression and service tests to import canonical service modules.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `git status --short` | repository root | PASS | 0 | Dirty worktree recorded before edits. |
| `rg -n "sqlalchemy|Session|DailyPredictionRepository|PredictionReferenceRepository|PredictionRulesetRepository|from app\\.infra" backend/app/prediction -g "*.py"` | repository root | PASS | 0 | Baseline captured in `infra-dependency-before.md`. |
| `ruff format app tests` | `backend` | PASS | 0 | 3 files reformatted. |
| `ruff check app tests` | `backend` | FAIL then PASS | 1 then 0 | Initial import ordering issues fixed with Ruff; rerun passed. |
| `ruff check app tests --fix` | `backend` | PASS | 0 | 22 import/order issues fixed. |
| `pytest -q app/tests/unit/test_context_loader.py app/tests/unit/test_daily_prediction_service.py app/tests/unit/test_daily_prediction_guardrails.py` | `backend` | PASS | 0 | 40 tests passed. |
| `pytest -q app/tests/integration/test_prediction_persistence.py app/tests/integration/test_engine_persistence_e2e.py` | `backend` | PASS | 0 | 12 tests passed. |
| `pytest -q app/tests/unit/test_backend_db_test_harness.py` | `backend` | PASS | 0 | 4 tests passed, RG-011 evidence. |
| `rg -n "app\\.prediction\\.context_loader|app\\.prediction\\.persistence_service" app tests` | `backend` | PASS | 1 | Zero hits; old active import paths absent. |
| `rg -n "sqlalchemy|Session|DailyPredictionRepository|PredictionReferenceRepository|PredictionRulesetRepository|from app\\.infra" app/prediction -g "*.py"` | `backend` | PASS | 1 | Zero hits; no allowlist exception remains. |
| `python -c "import os; assert not os.path.exists('prediction')"` | `backend` | PASS | 0 | No root `backend/prediction` directory. |
| `python -c "from app.main import app; print(len(app.routes))"` | `backend` | PASS | 0 | App imported; 220 routes registered. |
| `git diff --check` | repository root | PASS | 0 | No whitespace/conflict errors; Git reported LF-to-CRLF warnings only. |
| `git status --short` | repository root | PASS | 0 | Final worktree status captured below. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| `pytest -q` | no | Timed out after 304 seconds. | A regression outside the targeted prediction/persistence surface could remain undetected. | Targeted unit tests, integration persistence/e2e tests, RG-011 guard, lint, app import and architecture scans passed. |

## DRY / No Legacy evidence

| Pattern | Result | Classification | Action | Status |
|---|---|---|---|---|
| `app.prediction.context_loader` | zero hits under `backend/app` and `backend/tests` active scopes | active_legacy_removed | Deleted old file; consumers migrated. | PASS |
| `app.prediction.persistence_service` | zero hits under `backend/app` and `backend/tests` active scopes | active_legacy_removed | Deleted old file; consumers migrated. | PASS |
| `sqlalchemy` / repository imports under `app/prediction` | zero hits | forbidden_surface_removed | `CalibrationData` moved to pure context; `Session` annotation removed. | PASS |
| compatibility shim / alias / re-export | no old module file remains | active_legacy_removed | No facade created. | PASS |

## Diff review

- `git diff --stat` reviewed: code changes are limited to moving DB loader/persistence ownership, import migration, guard updates, and CONDAMAD evidence.
- `git diff --check` passed with line-ending warnings only.
- Untracked CS-008 through CS-013 story folders were pre-existing and not modified for this story.

## Final worktree status

```text
 M _condamad/stories/regression-guardrails.md
 M _condamad/stories/story-status.md
 M backend/app/api/v1/routers/internal/llm/qa.py
 M backend/app/api/v1/routers/public/predictions.py
 M backend/app/jobs/__init__.py
 M backend/app/jobs/generate_daily_calibration_dataset.py
 M backend/app/jobs/qa/generate_qa_cases.py
 M backend/app/jobs/refresh_user_baselines.py
 M backend/app/ops/llm/bootstrap/__init__.py
 D backend/app/prediction/context_loader.py
 M backend/app/prediction/contribution_calculator.py
 M backend/app/prediction/domain_router.py
 M backend/app/prediction/event_detector.py
 M backend/app/prediction/impulse_signal_builder.py
 M backend/app/prediction/intraday_activation_builder.py
 M backend/app/prediction/natal_sensitivity.py
 D backend/app/prediction/persistence_service.py
 M backend/app/prediction/transit_signal_builder.py
 M backend/app/services/natal/astro_context_builder.py
 M backend/app/services/prediction/__init__.py
 M backend/app/services/prediction/compute_runner.py
 M backend/app/services/prediction/engine_orchestrator.py
 M backend/app/services/prediction/service.py
 M backend/app/services/user_profile/prediction_baseline_service.py
 M backend/app/tests/integration/test_daily_prediction_qa.py
 M backend/app/tests/integration/test_engine_persistence_e2e.py
 M backend/app/tests/integration/test_intraday_refinement_integration.py
 M backend/app/tests/integration/test_prediction_persistence.py
 M backend/app/tests/integration/test_v3_persistence.py
 M backend/app/tests/regression/__init__.py
 M backend/app/tests/regression/helpers.py
 M backend/app/tests/unit/test_calibration_versioning.py
 M backend/app/tests/unit/test_context_loader.py
 M backend/app/tests/unit/test_daily_prediction_guardrails.py
 M backend/app/tests/unit/test_engine_orchestrator.py
 M backend/app/tests/unit/test_impulse_signal_v3.py
 M backend/app/tests/unit/test_intraday_activation_v3.py
 M backend/app/tests/unit/test_persistence_explainability.py
?? _condamad/stories/CS-007-extraire-dependances-infra-hors-prediction/
?? _condamad/stories/CS-008-classer-reduire-compatibilites-legacy-prediction/
?? _condamad/stories/CS-009-separer-projection-publique-enrichissement-llm/
?? _condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/
?? _condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/
?? _condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/
?? _condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/
?? backend/app/prediction/context.py
?? backend/app/services/prediction/context_loader.py
?? backend/app/services/prediction/persistence_service.py
```

## Remaining risks

- Full backend `pytest -q` did not finish within 304 seconds. Targeted story-critical checks passed.
- Full backend `pytest -q` was not rerun after the review fixes. Targeted story-critical checks passed.

## Suggested reviewer focus

- Confirm the canonical ownership of `PredictionContextLoader` and `PredictionPersistenceService` under `app.services.prediction`.
- Confirm the zero-hit infra scan and the pure `CalibrationData` ownership under `app.prediction.context`.
