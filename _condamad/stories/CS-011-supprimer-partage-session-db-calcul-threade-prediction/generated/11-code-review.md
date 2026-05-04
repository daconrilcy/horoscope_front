# CONDAMAD Code Review

## Review target

- Story: `CS-011-supprimer-partage-session-db-calcul-threade-prediction`
- Source: `_condamad/stories/CS-011-supprimer-partage-session-db-calcul-threade-prediction/00-story.md`
- Status reviewed: `ready-to-review`
- Reviewer date: 2026-05-04

## Inputs reviewed

- Story contract and AC1-AC4.
- Capsule evidence: acceptance traceability, validation plan, No Legacy / DRY guardrails, final evidence.
- Runtime files:
  - `backend/app/services/prediction/compute_runner.py`
  - `backend/app/tests/unit/test_prediction_compute_runner.py`
  - `backend/app/tests/unit/test_daily_prediction_service.py`
  - `backend/app/services/prediction/engine_orchestrator.py`
  - `backend/app/services/prediction/context_loader.py`
- Governance files:
  - `_condamad/stories/regression-guardrails.md`
  - `_condamad/stories/story-status.md`
  - `threaded-db-before.md`
  - `threaded-db-after.md`

## Diff summary

- `PredictionComputeRunner.run_with_timeout` precharge le contexte DB avant la creation du worker.
- Le `ctx_loader` injecte au worker retourne le contexte precharge et ne reference plus `db`.
- Le timeout conserve `DailyPredictionServiceError("timeout", ...)` et utilise `executor.shutdown(wait=False, cancel_futures=True)`.
- Un test unitaire dedie et une garde AST couvrent la non-capture de session.
- Le registre ajoute `RG-031` pour l'invariant durable de CS-011.

Les fichiers non suivis CS-012 et CS-013 sont presents dans le worktree mais hors cible de cette revue.

## Review layers

- Diff integrity: PASS, aucun changement applicatif hors `compute_runner.py` et test dedie CS-011.
- Acceptance audit: PASS, AC1-AC4 ont une preuve executable ou persistante.
- Validation audit: PASS, validations ciblees relancees en venv.
- DRY / No Legacy audit: PASS, aucun wrapper, alias, fallback silencieux ou import DB direct interdit.
- Edge / failure audit: PASS, le timeout rend l'erreur controlee sans attendre la fin du worker.
- Security / data audit: PASS, pas de secret, auth, CORS ou surface API touchee.

## Findings

Aucun finding actionnable.

## Acceptance audit

| AC | Verdict | Evidence |
|---|---|---|
| AC1 | PASS | `compute_runner.py` lignes 67-86 precharge le contexte puis retourne uniquement `loaded_context`; test AST `test_ctx_loader_does_not_capture_caller_db_session`. |
| AC2 | PASS | `DailyPredictionServiceError("timeout", ...)` conserve en timeout; tests runner + daily prediction passent. |
| AC3 | PASS | Docstrings francaises du module, de la classe et de `run_with_timeout` documentent le contexte precharge. |
| AC4 | PASS | `threaded-db-before.md` et `threaded-db-after.md` presents et relus. |

## Validation audit

Commandes executees:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/unit/test_prediction_compute_runner.py app/tests/unit/test_daily_prediction_service.py
ruff check app/services/prediction/compute_runner.py app/tests/unit/test_daily_prediction_service.py app/tests/unit/test_prediction_compute_runner.py
pytest -q app/tests/unit/test_backend_db_test_harness.py app/tests/unit/test_daily_prediction_guardrails.py
python -c "from app.main import app; print(app.title)"
```

Resultats:

- `20 passed in 0.21s`
- `All checks passed!`
- `15 passed in 8.19s`
- Import FastAPI OK: `horoscope-backend`

Scans executes:

```powershell
cd backend
rg -n "non-thread-safe|thread-safe|session worker|contexte precharge" app/services/prediction/compute_runner.py
rg -n "SessionLocal|engine" app/tests/unit/test_prediction_compute_runner.py app/tests/unit/test_daily_prediction_service.py
rg -n "context_loader\.load\(db|expire_all|non-thread-safe" app/services/prediction/compute_runner.py
git diff --check
git ls-files --others --exclude-standard
git status --short
```

Resultats:

- Documentation `contexte precharge` trouvee dans le runner.
- Aucun import `SessionLocal` ni `engine`; hits `engine_*` classes comme faux positifs.
- Aucun hit actif `context_loader.load(db`, `expire_all` ou ancien commentaire `non-thread-safe`.
- `git diff --check` passe; seuls des avertissements CRLF sont emis.

## DRY / No Legacy audit

- Pas de second runner, queue, session globale ou factory implicite.
- Le timeout reste proprietaire dans `PredictionComputeRunner`.
- `RG-011` respecte: aucun nouvel import direct `SessionLocal` / `engine` dans les tests cibles.
- `RG-031` respecte: test dedie + scan de documentation + absence de capture `db`.

## Residual risks

- La suite backend complete n'a pas ete relancee pendant cette revue; elle etait documentee comme conditionnelle dans la capsule. Les tests cibles, guards applicables et import applicatif passent.
- Le choix de prechargement sort volontairement l'I/O DB du worker timeoute, ce qui correspond a l'option autorisee par la story.

## Verdict

CLEAN
