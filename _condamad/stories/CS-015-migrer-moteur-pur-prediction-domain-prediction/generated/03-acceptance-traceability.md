# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `app/domain/prediction` existe comme owner moteur. | `backend/app/domain/prediction` contient les modules moteur purs. | `rg --files app/domain/prediction` depuis `backend`. | PASS |
| AC2 | Les services consomment `app.domain.prediction`. | Imports des services prediction vers `app.domain.prediction`; zero import `app.prediction`. | `rg -n "from app\.prediction" app/services/prediction -g "*.py"` zero-hit. | PASS |
| AC3 | Le domaine n'importe aucune couche interdite. | Guards AST et absence d'imports API/infra/services/settings/LLM runtime. | `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` et scan interdit sous `app/domain/prediction`. | PASS |
| AC4 | Les tests moteur restent passants. | Aucun changement comportemental du moteur; imports tests canoniques. | `pytest -q app/tests/unit/test_engine_orchestrator.py app/tests/unit/test_transit_signal_v3.py` et test astro foundation. | PASS |
| AC5 | Les preuves avant/apres sont persistantes. | Artefacts `domain-prediction-before.md` et `domain-prediction-after.md`. | Presence des deux fichiers et references dans `generated/10-final-evidence.md`. | PASS |
