# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | L'inventaire avant/apres du namespace est persiste. | Ajout de `prediction-namespace-before.md` et `prediction-namespace-after.md`. | Artefacts presents; tests de garde PASS. | PASS |
| AC2 | Aucun fichier ne reste sous `backend/app/prediction`. | Deplacement des fichiers suivis vers `backend/app/domain/prediction`; suppression du package legacy. | `rg --files app/prediction` depuis `backend/` retourne aucun fichier car chemin absent. | PASS |
| AC3 | Aucun import actif `app.prediction` ne reste. | Remplacement des consommateurs internes vers `app.domain.prediction.*`. | Scans zero-hit des imports legacy sous `app tests` et `backend/tests`; test de garde PASS. | PASS |
| AC4 | Les owners canoniques sont audites. | `removal-audit.md` classe les surfaces et decisions de migration. | Revue de `removal-audit.md`; tests API et moteur PASS. | PASS |
| AC5 | La garde d'extinction bloque la reintroduction. | `test_daily_prediction_guardrails.py` verifie absence du dossier, importabilite negative et imports AST interdits. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py app/tests/unit/test_engine_orchestrator.py` PASS. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
