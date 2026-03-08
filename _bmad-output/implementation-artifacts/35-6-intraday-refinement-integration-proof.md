# Story 35.6 : Intraday refinement integration proof

Status: done

## Story

As a développeur du moteur de prédiction quotidienne,
I want une preuve d'intégration que le raffinement temporel intraday est réellement branché dans le pipeline moteur,
so that les événements `exact` ne soient pas limités à un simple snapping au quart d'heure.

## Acceptance Criteria

### AC1 — Le raffinement n'est pas seulement une primitive isolée

Le moteur doit appeler `TemporalSampler.refine_around(...)` dans le flux réel de traitement des événements.

### AC2 — Les événements `exact` sont affinés

Un événement `exact` détecté sur la grille coarse est recalculé à une granularité plus fine autour du timestamp initial.

### AC3 — La preuve est observable dans la sortie moteur

Le test d'intégration doit vérifier un timestamp final non aligné sur les pas de 15 minutes.

## Tasks / Subtasks

### T1 — Brancher le raffinement dans l'orchestrateur

- [x] Modifier `backend/app/prediction/engine_orchestrator.py`
  - [x] Ajouter `_refine_detected_events(...)`
  - [x] Raffiner les événements `exact` via `TemporalSampler.refine_around(...)`

### T2 — Ajouter la logique de refinement côté détecteur

- [x] Modifier `backend/app/prediction/event_detector.py`
  - [x] Ajouter `refine_exact_event(...)`
  - [x] Rechercher le minimum d'orbe sur les pas raffinés
  - [x] Marquer le metadata avec `refined=True`

### T3 — Ajouter la preuve d'intégration

- [x] Créer `backend/app/tests/integration/test_intraday_refinement_integration.py`
  - [x] Cas de test avec timestamp coarse à `:15`
  - [x] Raffinement observé à `:16`
  - [x] Vérification que l'événement final n'est pas aligné sur un quart d'heure

## Completion Notes List

- Le raffinement minute n'est plus seulement testé en isolation dans `test_temporal_sampler.py`.
- Le pipeline réel affine désormais les événements `exact`.
- La preuve d'intégration est observable dans la sortie moteur elle-même, via un timestamp raffiné non multiple de 15 minutes.
- Le raffinage est implémenté de manière défensive pour ne pas casser les stubs de tests historiques qui ne définissent pas `refine_around()` ou `refine_exact_event()`.

## Validation

- `pytest -q app/tests/integration/test_intraday_refinement_integration.py`
- inclus dans la validation consolidée :
  - `pytest -q app/tests/unit/test_engine_orchestrator.py app/tests/integration/test_prediction_persistence.py app/tests/integration/test_engine_persistence_e2e.py app/tests/integration/test_intraday_refinement_integration.py app/tests/integration/test_db_bootstrap.py app/tests/integration/test_db_bootstrap_partial_upgrade.py app/tests/regression/test_engine_non_regression.py`
- résultat consolidé : `64 passed`

## File List

- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/prediction/event_detector.py`
- `backend/app/tests/integration/test_intraday_refinement_integration.py`

