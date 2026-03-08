# Story 35.5 : E2E engine -> persistence contract

Status: done

## Story

As a développeur du moteur de prédiction quotidienne,
I want une preuve end-to-end que la sortie réelle de `EngineOrchestrator.run(...)` est directement compatible avec `PredictionPersistenceService.save(...)`,
so that le contrat runtime moteur -> persistance soit validé sans mapping manuel intermédiaire.

## Acceptance Criteria

### AC1 — Sortie réelle de l'orchestrateur consommée telle quelle

Le test doit exécuter un vrai `EngineOrchestrator.run(...)` et transmettre le `EngineOutput` obtenu directement à `PredictionPersistenceService.save(...)`.

### AC2 — `category_scores` au format riche

La sortie du moteur doit contenir pour chaque catégorie un payload riche avec au minimum :
- `note_20`
- `raw_score`
- `normalized_score`
- `power`
- `volatility`

### AC3 — Persistance complète du run

Le run, les `daily_prediction_category_scores`, les `turning_points` et les `time_blocks` sont persistés sans adaptation ad hoc.

### AC4 — Idempotence par hash conservée

Un second appel avec le même `EngineOutput` réutilise le run existant (`was_reused=True`).

## Tasks / Subtasks

### T1 — Aligner le contrat runtime orchestrateur -> persistance

- [x] Modifier `backend/app/prediction/engine_orchestrator.py`
  - [x] Faire sortir `category_scores` au format riche compatible persistance
  - [x] Conserver le payload éditorial dérivé et les notes par pas

### T2 — Ajouter la preuve d'intégration E2E

- [x] Créer `backend/app/tests/integration/test_engine_persistence_e2e.py`
  - [x] Run réel orchestrateur sur fixture régression
  - [x] Appel direct à `PredictionPersistenceService.save(...)`
  - [x] Vérification des scores, pivots, blocs et réutilisation hash

### T3 — Réaligner la suite de tests sur le contrat enrichi

- [x] Modifier `backend/app/tests/unit/test_engine_orchestrator.py`
- [x] Modifier `backend/app/tests/regression/helpers.py`
- [x] Modifier `backend/app/tests/regression/test_engine_non_regression.py`

## Completion Notes List

- Le mismatch historique entre `EngineOrchestrator` (scores scalaires) et `PredictionPersistenceService` (scores riches) est supprimé.
- Le moteur émet désormais `category_scores` au format runtime cible.
- Le test E2E `test_engine_persistence_e2e.py` valide explicitement l'absence de mapping manuel entre les deux couches.
- L'idempotence par `input_hash` reste garantie après alignement du contrat.

## Validation

- `pytest -q app/tests/integration/test_engine_persistence_e2e.py`
- inclus dans la validation consolidée :
  - `pytest -q app/tests/unit/test_engine_orchestrator.py app/tests/integration/test_prediction_persistence.py app/tests/integration/test_engine_persistence_e2e.py app/tests/integration/test_intraday_refinement_integration.py app/tests/integration/test_db_bootstrap.py app/tests/integration/test_db_bootstrap_partial_upgrade.py app/tests/regression/test_engine_non_regression.py`
- résultat consolidé : `64 passed`

## File List

- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/tests/integration/test_engine_persistence_e2e.py`
- `backend/app/tests/unit/test_engine_orchestrator.py`
- `backend/app/tests/regression/helpers.py`
- `backend/app/tests/regression/test_engine_non_regression.py`

