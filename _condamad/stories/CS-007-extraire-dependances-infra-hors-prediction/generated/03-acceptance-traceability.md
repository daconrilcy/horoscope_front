# Acceptance traceability - CS-007

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Le contexte n'importe plus SQLAlchemy depuis prediction. | `PredictionContextLoader` deplace vers `app.services.prediction.context_loader`; contrats purs `LoadedPredictionContext` et `CalibrationData` exposes par `app.prediction.context`; garde AST ajoutee sans allowlist. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` PASS; scan infra apres zero hit. | PASS |
| AC2 | La persistence prediction reste fonctionnelle. | `PredictionPersistenceService` deplace vers `app.services.prediction.persistence_service`; consumers et tests migres. | `pytest -q app/tests/unit/test_context_loader.py` PASS; `pytest -q app/tests/integration/test_prediction_persistence.py app/tests/integration/test_engine_persistence_e2e.py` PASS. | PASS |
| AC3 | Les consumers utilisent le service canonique. | Imports actifs migres vers `app.services.prediction.context_loader` et `app.services.prediction.persistence_service`. | `rg -n "app\\.prediction\\.context_loader\|app\\.prediction\\.persistence_service" app tests` zero hit. | PASS |
| AC4 | Pas de racine `backend/prediction`. | Aucun dossier racine `backend/prediction` cree. | `python -c "import os; assert not os.path.exists('prediction')"` PASS depuis `backend`. | PASS |
| AC5 | Les preuves avant apres sont persistees. | `infra-dependency-before.md` et `infra-dependency-after.md` ajoutes. | Artefacts presents; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` PASS. | PASS |
