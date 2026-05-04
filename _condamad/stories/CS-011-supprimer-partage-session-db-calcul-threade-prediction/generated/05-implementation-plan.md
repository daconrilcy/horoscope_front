# Implementation Plan

## Finding

`PredictionComputeRunner.run_with_timeout` definit actuellement `ctx_loader` avec fermeture sur `db`, puis l'injecte dans `EngineOrchestrator` execute dans `ThreadPoolExecutor`.

## Approach

Choix retenu: precharger le contexte prediction avant la soumission au thread avec la session appelante, puis injecter au worker un loader pur qui retourne ce contexte precharge. Le worker ne consomme donc pas `db`, et le timeout conserve le comportement d'erreur controlee.

## Files to modify

- `backend/app/services/prediction/compute_runner.py`
- `backend/app/tests/unit/test_prediction_compute_runner.py`
- preuves CONDAMAD CS-011

## Tests

- Ajouter un test dedie du runner validant que `context_loader.load` s'execute dans le thread appelant, que le worker voit le contexte precharge et que la session n'est pas reutilisee apres timeout.
- Conserver la regression `test_daily_prediction_service.py`.

## No Legacy stance

Aucun wrapper, alias, fallback ou session globale. Le chemin dangereux est remplace par un chargement explicite hors thread.

## Rollback

Revenir au fichier `compute_runner.py` et au test dedie si la strategie de contexte precharge casse l'orchestrateur; ne pas restaurer la capture de `db` sans decision explicite.
