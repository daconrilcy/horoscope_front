# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Le worker ne capture pas la session appelante. | `compute_runner.py` charge le contexte hors thread et le worker utilise un contexte precharge sans acces a `db`; `test_ctx_loader_does_not_capture_caller_db_session` verrouille l'AST. | `pytest -q app/tests/unit/test_prediction_compute_runner.py`; scan `context_loader.load(db|expire_all|non-thread-safe` sans hit actif. | PASS |
| AC2 | Le timeout reste controle. | `run_with_timeout` conserve `DailyPredictionServiceError("timeout", ...)` et arrete l'attente executor avec `shutdown(wait=False)`. | `pytest -q app/tests/unit/test_daily_prediction_service.py app/tests/unit/test_prediction_compute_runner.py`. | PASS |
| AC3 | La solution documente le comportement DB. | Docstring module/classe/methode dans `compute_runner.py` documente le contexte precharge et l'absence de capture SQLAlchemy. | Scan `rg -n "non-thread-safe|thread-safe|session worker|contexte precharge" app/services/prediction/compute_runner.py`. | PASS |
| AC4 | Les preuves avant apres sont conservees. | Ajout de `threaded-db-before.md` et `threaded-db-after.md`. | Presence des artefacts et references dans `generated/10-final-evidence.md`. | PASS |
