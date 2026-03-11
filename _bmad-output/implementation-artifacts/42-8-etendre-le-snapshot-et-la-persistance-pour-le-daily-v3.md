# Story 42.8: Étendre le snapshot et la persistance pour le daily v3

Status: completed

## Story

As a platform engineer,
I want persister les nouvelles métriques du moteur v3 sans casser la lecture existante,
so that le backend puisse comparer, auditer et projeter v2 et v3 pendant la transition.

## Acceptance Criteria

1. Le snapshot quotidien supporte les métriques v3 par thème et les sorties de bloc/fenêtre nécessaires.
2. La persistance reste backward compatible avec les consommateurs actuels.
3. Les migrations et modèles restent versionnés et auditables.
4. Le dépôt de lecture peut relire un snapshot v2 ou v3 sans ambiguïté.
5. `engine_version` et `snapshot_version` sont persistés et utilisés par la politique de réutilisation et de lecture.
6. Les tests de lecture/écriture couvrent la coexistence v2/v3.

## Tasks / Subtasks

- [x] Task 1: Étendre les modèles et schémas de persistance (AC: 1, 3)
  - [x] Définir les champs ou tables additionnels nécessaires
  - [x] Préparer la migration Alembic correspondante

- [x] Task 2: Étendre les objets snapshot et repository (AC: 1, 4)
  - [x] Ajouter `snapshot_version`
  - [x] Ajouter les lectures v3 dans `persisted_snapshot.py`
  - [x] Étendre la reconstruction repository

- [x] Task 3: Adapter le service de persistance (AC: 2, 4, 5)
  - [x] Ajouter `engine_version`
  - [x] Sauvegarder les nouvelles métriques sans casser le chemin v2
  - [x] Garantir une relecture complète cohérente
  - [x] Injecter ces versions dans l'`input_hash` et la reuse policy

- [x] Task 4: Tests (AC: 6)
  - [x] Tester write/read v3
  - [x] Tester coexistence avec runs v2
  - [x] Tester l'absence de collision logique v2/v3

## Dev Notes

- Cette story ne doit pas imposer un basculement produit; elle prépare la coexistence technique.
- La capacité de comparer et d'auditer v2/v3 dépend directement de la qualité de cette persistance.
- Favoriser des champs explicitement nommés plutôt que des blobs opaques si possible.
- Cette story est l'endroit où versionner explicitement le cycle de vie du run pour éviter les collisions logiques pendant la transition.

### Project Structure Notes

- Fichiers principaux:
  - `backend/app/prediction/persisted_snapshot.py`
  - `backend/app/prediction/persistence_service.py`
  - `backend/app/infra/db/models/daily_prediction.py`
  - `backend/app/infra/db/repositories/daily_prediction_repository.py`

### References

- [Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]
- [Source: backend/app/prediction/persisted_snapshot.py]
- [Source: backend/app/prediction/persistence_service.py]
- [Source: backend/app/infra/db/models/daily_prediction.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 42.

### Completion Notes List

- Story prête pour porter la transition technique v2/v3 dans la persistance quotidienne.

### File List

- `_bmad-output/implementation-artifacts/42-8-etendre-le-snapshot-et-la-persistance-pour-le-daily-v3.md`
- `backend/app/infra/db/models/daily_prediction.py`
- `backend/app/infra/db/repositories/daily_prediction_repository.py`
- `backend/app/prediction/persistence_service.py`
- `backend/app/prediction/persisted_snapshot.py`
- `backend/app/tests/integration/test_v3_persistence.py`
