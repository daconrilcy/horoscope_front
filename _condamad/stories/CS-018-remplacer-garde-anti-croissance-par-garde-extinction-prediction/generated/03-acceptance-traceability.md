# Acceptance traceability - CS-018

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | La garde echoue si `backend/app/prediction` existe. | `test_prediction_legacy_namespace_has_no_files` verifie l'absence du dossier legacy. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`; `rg --files app/prediction`. | PASS |
| AC2 | La garde echoue si `app.prediction` est importe. | `test_prediction_legacy_import_paths_are_removed` scanne par AST `app` et `tests`. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`; `rg -n "from app\.prediction\|import app\.prediction" app tests -g "*.py"`. | PASS |
| AC3 | L'allowlist CS-012 n'est plus runtime. | La garde ne lit plus `prediction-namespace-allowlist.md`; l'allowlist reste artefact historique. | `rg -n "_PREDICTION_NAMESPACE_ALLOWLIST\|prediction-namespace-allowlist\|allowlist" app/tests/unit/test_daily_prediction_guardrails.py`. | PASS |
| AC4 | Les invariants prediction restent couverts. | La garde conserve les tests d'invariants prediction existants et ajoute l'extinction legacy finale. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py app/tests/unit/test_daily_prediction_service.py`; integration API cible. | PASS |
| AC5 | Les artefacts `_condamad` sont seuls exceptes. | Les scans executables ciblent `app` et `tests`; les references `_condamad` sont classees historiques. | Scans zero-hit sous `backend/app` et `backend/tests`; classification des hits `_condamad` dans l'evidence finale. | PASS |
