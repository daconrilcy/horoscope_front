# Acceptance Traceability - CS-006

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | La cartographie couvre chaque fichier actuel. | `prediction-namespace-map.md` liste chaque fichier Python/template du baseline initial et son owner cible. | `rg --files app/prediction` + revue de la cartographie. | PASS |
| AC2 | Le premier lot migre utilise les owners canoniques. | `engine_orchestrator.py` est deplace vers `app.services.prediction`; les consommateurs importent `app.services.prediction.engine_orchestrator`. | `pytest -q app/tests/unit/test_engine_orchestrator.py`. | PASS |
| AC3 | Aucun re-export legacy ne remplace la migration. | Aucun `app.prediction.engine_orchestrator` actif, aucun re-export depuis `app.prediction.__init__`. | Scans `rg` des anciens imports et `LLMNarrator`. | PASS |
| AC4 | Une garde bloque la croissance du namespace. | `test_daily_prediction_guardrails.py` contient une allowlist exacte des fichiers `app/prediction`. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. | PASS |
| AC5 | Les preuves avant apres sont persistees. | `prediction-namespace-before.md` et `prediction-namespace-after.md` sont presents. | Existence des artefacts + garde AST. | PASS |
