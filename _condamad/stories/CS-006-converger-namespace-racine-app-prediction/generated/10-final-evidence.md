# Final Evidence - CS-006

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-006-converger-namespace-racine-app-prediction`
- Source story: `_condamad/stories/CS-006-converger-namespace-racine-app-prediction/00-story.md`
- Capsule path: `_condamad/stories/CS-006-converger-namespace-racine-app-prediction`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: recorded before edits.
- Pre-existing dirty files: `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`, and untracked CONDAMAD story folders CS-006 to CS-013.
- AGENTS.md files considered: `AGENTS.md`.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated for this execution. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Covers AC1-AC5. |
| `generated/04-target-files.md` | yes | yes | PASS | Story-specific target map. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Executable commands listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific No Legacy rules. |
| `generated/10-final-evidence.md` | yes | yes | PASS | To be completed after validation. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `prediction-namespace-map.md` covers every file from `prediction-namespace-before.md`, including the 16 templates as individual rows. | `rg --files app/prediction` run after migration; after inventory persisted and compared to the mapping. | PASS | Review CR-001 fixed by replacing the wildcard template row with per-file ownership rows. |
| AC2 | `backend/app/services/prediction/engine_orchestrator.py` is the canonical service owner; active consumers import it. | `pytest -q app/tests/unit/test_engine_orchestrator.py` passed as part of targeted command. | PASS | |
| AC3 | `backend/app/prediction/engine_orchestrator.py` removed; no re-export added in `app.prediction.__init__`. | `rg -n "app\\.prediction\\.engine_orchestrator" app tests` returned zero active hits. `LLMNarrator` scans classified below. | PASS | |
| AC4 | `backend/app/tests/unit/test_daily_prediction_guardrails.py` now checks exact Python inventory and forbidden imports by AST. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` passed. | PASS | |
| AC5 | `prediction-namespace-before.md` and `prediction-namespace-after.md` persisted. | Namespace guard and `rg --files app/prediction` passed. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `_condamad/stories/CS-006-converger-namespace-racine-app-prediction/00-story.md` | modified | Mark implementation tasks complete. | AC1-AC5 |
| `_condamad/stories/CS-006-converger-namespace-racine-app-prediction/generated/*` | added/modified | Capsule execution, traceability and final evidence. | AC1-AC5 |
| `_condamad/stories/CS-006-converger-namespace-racine-app-prediction/prediction-namespace-before.md` | added | Baseline before inventory. | AC1, AC5 |
| `_condamad/stories/CS-006-converger-namespace-racine-app-prediction/prediction-namespace-after.md` | added | Baseline after inventory. | AC5 |
| `_condamad/stories/CS-006-converger-namespace-racine-app-prediction/prediction-namespace-map.md` | added | Owner routing map. | AC1 |
| `_condamad/stories/story-status.md` | modified | Set CS-006 to `ready-to-review`. | AC1-AC5 |
| `backend/app/services/prediction/engine_orchestrator.py` | moved/modified | Canonical owner for prediction orchestration. | AC2, AC3 |
| `backend/app/jobs/__init__.py` | modified | Import canonical orchestrator. | AC2, AC3 |
| `backend/app/jobs/generate_daily_calibration_dataset.py` | modified | Import canonical orchestrator. | AC2, AC3 |
| `backend/app/jobs/qa/generate_qa_cases.py` | modified | Import canonical orchestrator. | AC2, AC3 |
| `backend/app/services/prediction/compute_runner.py` | modified | Import canonical orchestrator. | AC2, AC3 |
| `backend/app/services/prediction/service.py` | modified | Type-check canonical orchestrator. | AC2, AC3 |
| `backend/app/services/natal/astro_context_builder.py` | modified | Import canonical orchestrator. | AC2, AC3 |
| `backend/app/services/user_profile/prediction_baseline_service.py` | modified | Import canonical orchestrator. | AC2, AC3 |
| `backend/app/tests/unit/test_daily_prediction_guardrails.py` | modified | Add namespace growth and forbidden import guards. | AC4 |
| `backend/app/tests/unit/test_engine_orchestrator.py` | modified | Import canonical orchestrator. | AC2 |
| `backend/app/tests/unit/test_calibration_versioning.py` | modified | Import canonical orchestrator. | AC2 |
| `backend/app/tests/unit/test_astro_calculator.py` | modified | Remove root `from app.prediction import` import shape. | AC3 |
| `backend/app/tests/regression/helpers.py` | modified | Import canonical orchestrator. | AC2 |
| `backend/app/tests/integration/test_intraday_refinement_integration.py` | modified | Import canonical orchestrator. | AC2 |

## Files deleted

| File | Purpose | Related AC |
|---|---|---|
| `backend/app/prediction/engine_orchestrator.py` | Removed old owner path after move to `app.services.prediction`. | AC2, AC3 |

## Tests added or updated

| Test file | Change | Related AC |
|---|---|---|
| `backend/app/tests/unit/test_daily_prediction_guardrails.py` | Added AST/file inventory guards. | AC4 |
| `backend/app/tests/unit/test_engine_orchestrator.py` | Updated import to canonical owner. | AC2 |
| `backend/app/tests/unit/test_calibration_versioning.py` | Updated import to canonical owner. | AC2 |
| `backend/app/tests/unit/test_astro_calculator.py` | Removed root package import form. | AC3 |
| `backend/app/tests/regression/helpers.py` | Updated import to canonical owner. | AC2 |
| `backend/app/tests/integration/test_intraday_refinement_integration.py` | Updated import to canonical owner. | AC2 |

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `pytest -q app/tests/unit/test_daily_prediction_guardrails.py app/tests/unit/test_engine_orchestrator.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | `backend` | PASS | 0 | 35 passed. |
| `rg -n "app\\.prediction\\.engine_orchestrator" app tests` | `backend` | PASS | 1 | Zero active hits; `rg` exits 1 on no matches. |
| `rg -n "from app\\.prediction\\.llm_narrator import LLMNarrator|LLMNarrator\\(|LLMNarrator\\.narrate" app tests` | `backend` | PASS | 1 | Zero active hits; `rg` exits 1 on no matches. |
| `rg -n "from app\\.prediction import|app\\.prediction\\.llm_narrator|LLMNarrator" app tests` | `backend` | PASS | 0 | Two classified guard/historical hits, no active legacy runtime hit. |
| `rg --files app/prediction` | `backend` | PASS | 0 | Inventory captured in `prediction-namespace-after.md`. |
| `ruff format --check app tests` | `backend` | FAIL then PASS | 1 then 0 | First run required formatting of touched files; after `ruff format app tests`, 1079 files already formatted. |
| `ruff format app tests` | `backend` | PASS | 0 | 7 touched files reformatted, 1072 unchanged. |
| `ruff check app tests` | `backend` | PASS | 0 | All checks passed. |
| `python -c "from app.main import app; print(app.title)"` | `backend` | PASS | 0 | FastAPI app imports; title `horoscope-backend`. |
| `pytest -q` | `backend` | PASS | 0 | 3578 passed, 12 skipped. |
| `git diff --check` | repo root | PASS | 0 | No whitespace/conflict errors. |
| `git diff --stat` | repo root | PASS | 0 | Diff reviewed; includes expected story files and pre-existing CONDAMAD registry/story changes. |
| `git status --short` | repo root | PASS | 0 | Final status recorded below. |

## Commands skipped or blocked

None.

## Post-review fixes

| Review finding | Fix | Validation evidence | Status |
|---|---|---|---|
| `CR-001` - template mapping used a wildcard row instead of file-by-file ownership. | Replaced `backend/app/prediction/editorial_templates/**` with 16 exact template rows in `prediction-namespace-map.md`. | PowerShell comparison found `template_count=16` and `missing=0`; no wildcard row remains. | PASS |

## DRY / No Legacy evidence

| Pattern | File | Classification | Action | Status |
|---|---|---|---|---|
| `app.prediction.engine_orchestrator` | n/a | active_legacy_removed | Old active imports removed. | PASS |
| `from app.prediction import` | n/a | active_legacy_removed | Root package import in `test_astro_calculator.py` replaced by explicit module import. | PASS |
| `app.prediction.llm_narrator` | `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | test_guard_expected_hit | Guard defines the forbidden module as data for AST validation. | PASS |
| `LLMNarrator` | `backend/app/domain/llm/governance/data/legacy_residual_registry.json` | allowed_historical_reference | Registry text describes a bounded legacy perimeter; not an import or executable runtime path. | PASS |
| `LLMNarrator` | tests/app scan for import/call patterns | active_legacy_removed | Specific import/call scan returned zero hits. | PASS |

## Diff review

Reviewed with `git diff --stat` and `git diff --check`. The active code diff is scoped to moving `EngineOrchestrator`, updating its consumers, and adding the namespace guard. Pre-existing dirty CONDAMAD files/folders are preserved.

## Final worktree status

```text
M _condamad/stories/regression-guardrails.md
M _condamad/stories/story-status.md
M backend/app/jobs/__init__.py
M backend/app/jobs/generate_daily_calibration_dataset.py
M backend/app/jobs/qa/generate_qa_cases.py
D backend/app/prediction/engine_orchestrator.py
M backend/app/services/natal/astro_context_builder.py
M backend/app/services/prediction/compute_runner.py
M backend/app/services/prediction/service.py
M backend/app/services/user_profile/prediction_baseline_service.py
M backend/app/tests/integration/test_intraday_refinement_integration.py
M backend/app/tests/regression/helpers.py
M backend/app/tests/unit/test_astro_calculator.py
M backend/app/tests/unit/test_calibration_versioning.py
M backend/app/tests/unit/test_daily_prediction_guardrails.py
M backend/app/tests/unit/test_engine_orchestrator.py
?? _condamad/stories/CS-006-converger-namespace-racine-app-prediction/
?? _condamad/stories/CS-007-extraire-dependances-infra-hors-prediction/
?? _condamad/stories/CS-008-classer-reduire-compatibilites-legacy-prediction/
?? _condamad/stories/CS-009-separer-projection-publique-enrichissement-llm/
?? _condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/
?? _condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/
?? _condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/
?? _condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/
?? backend/app/services/prediction/engine_orchestrator.py
```

## Remaining risks

The untracked CS-007 to CS-013 folders and pre-existing changes to `_condamad/stories/regression-guardrails.md` were present before implementation and were not authored by this execution.

## Suggested reviewer focus

Review the new canonical owner `app.services.prediction.engine_orchestrator`, the exact namespace allowlist in `test_daily_prediction_guardrails.py`, and whether the chosen first batch boundary is acceptable before later stories move pure engine modules.
