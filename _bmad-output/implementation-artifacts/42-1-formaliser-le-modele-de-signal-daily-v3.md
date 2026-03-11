# Story 42.1: Formaliser le modèle de signal daily v3

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend architect,
I want introduire un contrat de calcul v3 explicite pour le daily,
so that le moteur puisse manipuler des couches de signal continues (`B`, `T`, `A`, `E`) sans casser immédiatement la pile v2.

## Acceptance Criteria

1. Le backend introduit des types/schemas v3 distincts pour:
   - le signal composite par thème et par pas de temps
   - les couches `B(c)`, `T(c,t)`, `A(c,t)`, `E(c,t)`
   - les métriques dérivées journalières et intrajournalières
2. Un feature flag ou sélecteur runtime permet de choisir explicitement entre moteur v2 et moteur v3.
3. Le backend supporte aussi un mode `dual` permettant d'exécuter v2 et v3 sur la même entrée pour comparaison.
4. `engine_version`, `snapshot_version` et `evidence_pack_version` sont définis explicitement comme conventions du cycle de vie v3.
5. `DailyPredictionService` et `EngineOrchestrator` peuvent accueillir le nouveau pipeline sans casser le contrat applicatif actuel.
6. Les contrats internes v3 restent découplés du DTO public actuel.
7. Des tests verrouillent la compatibilité backward quand v3 est désactivé et la comparabilité minimale en mode `dual`.

## Tasks / Subtasks

- [x] Task 1: Définir les types internes du moteur v3 (AC: 1)
  - [x] Ajouter les nouveaux objets de signal dans `schemas.py`
  - [x] Définir les structures de séries temporelles par thème
  - [x] Définir un contrat explicite pour les métriques journalières v3

- [x] Task 2: Introduire le sélecteur runtime v2/v3/dual (AC: 2, 3)
  - [x] Ajouter le mode `dual`
  - [x] Ajouter un feature flag ou sélecteur de moteur dans la config runtime
  - [x] Brancher ce sélecteur dans `daily_prediction_service.py`
  - [x] Propager la sélection jusqu'à `engine_orchestrator.py`

- [x] Task 3: Formaliser les conventions de version (AC: 4)
  - [x] Définir `engine_version`
  - [x] Définir `snapshot_version`
  - [x] Définir `evidence_pack_version`
  - [x] Préparer leur injection dans hash/persistance/lecture future

- [x] Task 4: Préserver la compatibilité de la pile existante (AC: 5, 6)
  - [x] Éviter toute fuite des objets v3 dans le routeur public
  - [x] Conserver le contrat de retour applicatif actuel
  - [x] Prévoir un point d'extension propre pour les stories suivantes

- [x] Task 5: Tester la coexistence v2/v3 (AC: 7)
  - [x] Ajouter des tests de sélection moteur
  - [x] Tester le fallback v2 par défaut
  - [x] Ajouter quelques fixtures canoniques pour le mode `dual`
  - [x] Vérifier l'absence de régression sur le service daily existant

## Dev Notes

- Cette story est le socle de tout l'Epic 42. Elle ne doit pas encore modifier la logique métier des scores, seulement créer l'ossature de calcul v3.
- Le bon objectif est d'introduire une frontière claire entre:
  - sortie brute du moteur v2
  - futures courbes v3
  - projection publique
- Le feature flag doit être pensé pour supporter:
  - exécution v2 seule
  - exécution v3 seule
  - éventuellement comparaison v2/v3 ultérieure
- Cette story doit installer très tôt le mode `dual`; le backtesting complet viendra plus tard, mais la comparabilité ne doit pas attendre 42.17.
- Les conventions `engine_version`, `snapshot_version` et `evidence_pack_version` doivent être posées ici pour éviter des collisions logiques plus tard.

### Project Structure Notes

- Fichiers principaux:
  - `backend/app/prediction/schemas.py`
  - `backend/app/prediction/engine_orchestrator.py`
  - `backend/app/services/daily_prediction_service.py`
  - `backend/app/core/config.py` si un flag runtime centralisé est déjà utilisé

### Technical Requirements

- Ne pas casser les signatures publiques existantes.
- Les nouveaux types v3 doivent être suffisamment expressifs pour porter:
  - signal par thème/step
  - métriques journalières
  - métriques de blocs/régimes
- Le design doit éviter d'obliger un deuxième refactor massif des stories 42.2 à 42.17.

### Architecture Compliance

- La story doit préserver la séparation existante:
  - service applicatif
  - moteur de calcul
  - persistance
  - projection publique
- Le moteur v3 ne doit pas être branché directement au routeur FastAPI.

### Testing Requirements

- Couvrir la sélection v2/v3.
- Vérifier que le moteur v2 reste le chemin nominal par défaut.
- Exécuter `ruff check` et les tests ciblés dans le venv.

### References

- [Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]
- [Source: _bmad-output/planning-artifacts/epics.md#Epic-42]
- [Source: backend/app/services/daily_prediction_service.py]
- [Source: backend/app/prediction/engine_orchestrator.py]
- [Source: backend/app/prediction/schemas.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 42.

### Completion Notes List

- Story terminée : Contrat de calcul v3 formalisé et intégré avec sélecteur de mode.

### File List

- `backend/app/prediction/schemas.py`
- `backend/app/core/config.py`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/services/prediction_compute_runner.py`
- `backend/app/services/daily_prediction_service.py`
- `backend/app/tests/unit/test_engine_orchestrator.py`
