# Final Evidence

## Story status

- Validation outcome: PASS_WITH_LIMITATIONS
- Ready for review: yes
- Story key: `CS-011-supprimer-partage-session-db-calcul-threade-prediction`
- Source story: `_condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/00-story.md`
- Capsule path: `_condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Initial `git status --short`: pre-existing `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`, CS-011/CS-012/CS-013 untracked capsules.
- AGENTS.md files considered: `AGENTS.md`.
- Capsule generated: completed missing `generated/` files in existing capsule.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Created for CS-011. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC4 mapped. |
| `generated/04-target-files.md` | yes | yes | PASS | Target files scoped. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Commands listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | RG-011/RG-031 mapped. |
| `generated/10-final-evidence.md` | yes | yes | PASS | To be completed after validation. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `compute_runner.py` precharge le contexte avant `executor.submit`; `ctx_loader` retourne uniquement le contexte precharge. | `pytest -q app/tests/unit/test_prediction_compute_runner.py` PASS; garde AST `test_ctx_loader_does_not_capture_caller_db_session`; scan `context_loader.load(db|expire_all|non-thread-safe` sans hit. | PASS | Aucun worker ne reference `db`. |
| AC2 | Timeout conserve `DailyPredictionServiceError("timeout", ...)`; executor `shutdown(wait=False)`. | `pytest -q app/tests/unit/test_daily_prediction_service.py app/tests/unit/test_prediction_compute_runner.py` PASS. | PASS | Suite complete timeout, voir limitations. |
| AC3 | Docstrings francaises module/classe/methode de `compute_runner.py` decrivent le contexte precharge et l'isolation session. | `rg -n "non-thread-safe|thread-safe|session worker|contexte precharge" app/services/prediction/compute_runner.py` trouve la documentation corrigee. | PASS | Ancien commentaire non-thread-safe absent. |
| AC4 | `threaded-db-before.md` et `threaded-db-after.md` ajoutes. | Artefacts presents et controles par diff/status. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/services/prediction/compute_runner.py` | modified | Precharger le contexte hors thread et documenter l'isolation DB. | AC1, AC2, AC3 |
| `backend/app/tests/unit/test_prediction_compute_runner.py` | added | Tests runtime timeout + garde AST anti capture `db`. | AC1, AC2, AC3 |
| `_condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/00-story.md` | restored/modified | Restaurer la story source et cocher les taches. | AC4 |
| `_condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/threaded-db-before.md` | added | Baseline du risque initial. | AC4 |
| `_condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/threaded-db-after.md` | added | Preuve apres correction. | AC4 |
| `_condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/generated/*` | added/modified | Capsule, traceabilite et evidence. | AC1-AC4 |
| `_condamad/stories/story-status.md` | modified | Passer CS-011 en `ready-to-review`. | AC4 |

## Files deleted

| File | Reason | Related AC |
|---|---|---|
| None | No deletion expected. | |

## Tests added or updated

| File | Tests | Purpose |
|---|---|---|
| `backend/app/tests/unit/test_prediction_compute_runner.py` | `test_run_preloads_prediction_context_before_worker_thread`; `test_ctx_loader_does_not_capture_caller_db_session`; `test_timeout_returns_controlled_error_without_reusing_caller_session` | Prouver runtime + garde anti-retour. |

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `pytest -q app/tests/unit/test_prediction_compute_runner.py app/tests/unit/test_daily_prediction_service.py` | `backend/` | PASS | 0 | 20 passed. |
| `ruff check app/services/prediction/compute_runner.py app/tests/unit/test_daily_prediction_service.py app/tests/unit/test_prediction_compute_runner.py` | `backend/` | PASS | 0 | All checks passed. |
| `ruff format --check app/services/prediction/compute_runner.py app/tests/unit/test_prediction_compute_runner.py` | `backend/` | PASS | 0 | 2 files already formatted; ruff cache warning non bloquant `Acces refuse`. |
| `rg -n "non-thread-safe\|thread-safe\|session worker\|contexte precharge" app/services/prediction/compute_runner.py` | `backend/` | PASS | 0 | Hit sur la doc `contexte precharge`; aucun ancien commentaire non-thread-safe. |
| `rg -n "SessionLocal\|engine" app/tests/unit/test_prediction_compute_runner.py app/tests/unit/test_daily_prediction_service.py` | `backend/` | PASS | 0 | Hits classes comme faux positifs `engine_input` / `engine_mode`; aucun import `SessionLocal` ou `engine`. |
| `rg -n "context_loader\.load\(db\|expire_all\|non-thread-safe" app/services/prediction/compute_runner.py` | `backend/` | PASS | 1 | Zero hit, donc aucun ancien chemin actif. |
| `pytest -q app/tests/unit/test_backend_db_test_harness.py app/tests/unit/test_daily_prediction_guardrails.py` | `backend/` | PASS | 0 | 15 passed; couvre RG-011 et garde-fous prediction. |
| `python -c "from app.main import app; print(app.title)"` | `backend/` | PASS | 0 | Import FastAPI OK, titre `horoscope-backend`. |
| `pytest -q` | `backend/` | BLOCKED | 124 | Timeout apres 304s dans l'environnement. |
| `git diff --check` | repo root | PASS | 0 | Pas d'erreur whitespace; warnings CRLF existants. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| Full backend `pytest -q` completion | conditional | Lance mais depasse 5 minutes. | Une regression hors tests cibles pourrait rester non detectee. | Tests cibles, guards RG-011/RG-031 et import FastAPI passent. |

## DRY / No Legacy evidence

- Aucun wrapper, alias, fallback ou session globale ajoute.
- `ctx_loader` ne reference plus `db`; garde AST dediee.
- Scan `context_loader.load(db|expire_all|non-thread-safe` sans hit dans `compute_runner.py`.
- Scan `SessionLocal|engine` dans les tests: uniquement faux positifs `engine_input` / `engine_mode`, aucun import DB direct.

## Diff review

- Diff revu via `git diff --stat`, `git diff --check`, `git status --short`.
- Les changements applicatifs sont limites a `compute_runner.py` et au nouveau test runner.
- Les capsules CS-012/CS-013 et les modifications preexistantes du registre etaient deja presentes et non modifiees pour cette story.

## Final worktree status

```text
 M _condamad/stories/regression-guardrails.md
 M _condamad/stories/story-status.md
 M backend/app/services/prediction/compute_runner.py
?? _condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/
?? _condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/
?? _condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/
?? backend/app/tests/unit/test_prediction_compute_runner.py
```

## Remaining risks

- La suite backend complete n'a pas termine avant timeout 304s; validation cible et guards pertinents passent.

## Suggested reviewer focus

- Verifier que le prechargement du contexte hors thread est acceptable pour le perimetre timeout.
- Relire le choix `executor.shutdown(wait=False, cancel_futures=True)` sur timeout.
- Confirmer la classification des hits `SessionLocal|engine` comme faux positifs.
