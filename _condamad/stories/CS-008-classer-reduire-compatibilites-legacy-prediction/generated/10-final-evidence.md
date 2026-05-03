# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-008-classer-reduire-compatibilites-legacy-prediction
- Source story: `../00-story.md`
- Capsule path: `_condamad/stories/CS-008-classer-reduire-compatibilites-legacy-prediction`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: pre-existing `_condamad` registry/status changes and untracked CS-008..CS-013 capsules.
- Pre-existing dirty files: `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`, untracked story capsule directories.
- AGENTS.md files considered: root `AGENTS.md`.
- Capsule generated: yes.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status/tasks updated only. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated baseline accepted. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC5 complete. |
| `generated/04-target-files.md` | yes | yes | PASS | Updated with actual owners. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Commands executed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Complete. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `legacy-surface-audit.md` classifies all audited surfaces. | `pytest -q app/tests/unit/test_schemas_v3.py` PASS; classified targeted scans. | PASS | `EngineOutput` and `categories` intentionally kept. |
| AC2 | Removed `schemas.TimeBlock`; removed persistence `engine_output=` keyword; migrated consumers. | Targeted tests PASS; guard `test_prediction_removed_legacy_compatibility_surfaces_stay_removed` PASS. | PASS | Remaining `TimeBlock` hits are canonical `block_generator` or `V3TimeBlock`. |
| AC3 | Public `categories` kept as `external-active`. | `pytest -q app/tests/unit/test_public_projection.py` PASS; frontend scan shows active consumers. | PASS | No public payload removal. |
| AC4 | No `LLMNarrator` file or runtime import added. | `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py` PASS. | PASS | RG-016/RG-017 preserved. |
| AC5 | Non-target contracts unchanged; OpenAPI smoke passes. | `python -c "from app.main import app; ..."` PASS; full `pytest -q` PASS. | PASS | No API route/schema deletion. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/prediction/schemas.py` | modified | Delete `TimeBlock` compatibility dataclass. | AC2 |
| `backend/app/services/prediction/persistence_service.py` | modified | Remove `engine_output=` compatibility kwarg. | AC2 |
| `backend/app/tests/integration/test_v3_baselines.py` | modified | Use `V3TimeBlock`. | AC2 |
| `backend/app/tests/unit/test_calibration_versioning.py` | modified | Use `bundle=`. | AC2 |
| `backend/app/tests/unit/test_persistence_explainability.py` | modified | Use `bundle=`. | AC2 |
| `backend/app/tests/unit/test_daily_prediction_guardrails.py` | modified | Add reintroduction guard. | AC2, AC4 |
| `legacy-surface-audit.md` | added | Baseline classification. | AC1, AC3 |
| `legacy-surface-after.md` | added | Final classification. | AC5 |
| `_condamad/stories/story-status.md` | modified | Mark CS-008 ready-to-review. | AC1-AC5 |

## Files deleted

| File | Reason |
|---|---|
| None | Removed class/kwarg only. |

## Tests added or updated

- Added guard `test_prediction_removed_legacy_compatibility_surfaces_stay_removed`.
- Updated persistence/calibration/baseline tests to canonical `bundle=` / `V3TimeBlock`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `pytest -q app/tests/unit/test_daily_prediction_guardrails.py app/tests/unit/test_persistence_explainability.py app/tests/unit/test_calibration_versioning.py app/tests/integration/test_v3_baselines.py app/tests/unit/test_public_projection.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | `backend/` | PASS | 0 | 37 passed. |
| `pytest -q app/tests/unit/test_schemas_v3.py` | `backend/` | PASS | 0 | 28 passed. |
| `rg -n "EngineOutput|TimeBlock|engine_output=|\bcategories\b|LLMNarrator" app tests` | `backend/` | PASS | 0 | Hits classified; removed surfaces only in guard/canonical contexts. |
| `python -c "from app.main import app; schema = app.openapi(); assert 'paths' in schema; assert '/v1/predictions/daily' in schema['paths']"` | `backend/` | PASS | 0 | OpenAPI generated. |
| `ruff check app tests` | `backend/` | PASS | 0 | All checks passed. |
| `git diff --check` | `backend/` | PASS | 0 | CRLF warnings only, no whitespace errors. |
| `pytest -q` | `backend/` | PASS | 0 | 3580 passed, 12 skipped. |
| `python -m uvicorn app.main:app --host 127.0.0.1 --port 8765` plus `GET /openapi.json` | `backend/` | PASS | 0 | Local server answered 200; job stopped after smoke test. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| None | no | N/A | N/A | N/A |

## DRY / No Legacy evidence

- `schemas.TimeBlock` deleted instead of re-exported or aliased.
- `save(engine_output=...)` deleted instead of silently mapped through `**kwargs`.
- Public `categories` classified `external-active`; no deletion without API decision.
- `LLMNarrator` remains blocked by existing runtime/test guards.

## Diff review

- `git diff --stat` reviewed: only backend prediction files/tests and CS-008 evidence/status files are part of this story.
- Pre-existing `_condamad/stories/regression-guardrails.md` and other untracked story capsules were not reverted.

## Final worktree status

- `M _condamad/stories/regression-guardrails.md` (pre-existing dirty file)
- `M _condamad/stories/story-status.md`
- `M backend/app/prediction/schemas.py`
- `M backend/app/services/prediction/persistence_service.py`
- `M backend/app/tests/integration/test_v3_baselines.py`
- `M backend/app/tests/unit/test_calibration_versioning.py`
- `M backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `M backend/app/tests/unit/test_persistence_explainability.py`
- `?? _condamad/stories/CS-008-classer-reduire-compatibilites-legacy-prediction/`
- `?? _condamad/stories/CS-009-separer-projection-publique-enrichissement-llm/` (pre-existing untracked story capsule)
- `?? _condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/` (pre-existing untracked story capsule)
- `?? _condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/` (pre-existing untracked story capsule)
- `?? _condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/` (pre-existing untracked story capsule)
- `?? _condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/` (pre-existing untracked story capsule)

## Remaining risks

- `EngineOutput` remains an active internal DTO; a dedicated migration story is needed if the project wants to retire it completely.
- Public `categories` remains active until product/API/frontend migration decision.

## Suggested reviewer focus

- Confirm `EngineOutput` classification as active rather than removable in CS-008.
- Review the new guard scope for `save(engine_output=...)`.
- Confirm keeping public `categories` is acceptable given frontend consumers.
