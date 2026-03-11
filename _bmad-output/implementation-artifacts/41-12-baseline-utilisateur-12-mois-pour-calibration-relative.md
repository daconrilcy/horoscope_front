# Story 41.12: Baseline utilisateur 12 mois pour calibration relative

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend maintainer de la daily prediction,
I want persister une baseline utilisateur simulée sur 12 mois par catégorie,
so that le système puisse comparer une journée donnée à l’historique personnel de l’utilisateur sans recalculer cette distribution à chaque requête.

## Acceptance Criteria

1. Une nouvelle couche de persistance stocke une baseline utilisateur 12 mois par catégorie avec au minimum:
   - `mean_raw_score`
   - `std_raw_score`
   - `mean_note_20`
   - `std_note_20`
   - percentiles utiles (`p10`, `p50`, `p90`)
   - `sample_size_days`
   - fenêtre temporelle de calcul
   - couple `reference_version` / `ruleset_version`
   - `house_system_effective`

2. Le modèle de données supporte un recalcul déterministe et versionné:
   - baseline distincte par utilisateur, catégorie et fenêtre
   - invalidation naturelle en cas de changement de versions ou de house system
   - unicité empêchant les doublons silencieux

3. La génération de baseline repose sur le moteur daily existant et reste découplée de l’API publique:
   - pas d’appel HTTP interne
   - pas de dépendance au routeur
   - usage d’un service/backend job dédié

4. Les cas dégénérés sont explicitement gérés:
   - historique vide ou incomplet
   - variance nulle
   - catégorie absente

5. Des tests couvrent:
   - la migration / le modèle DB
   - la persistance / lecture repository
   - le versionnement et l’unicité
   - la déterminisme de génération sur un utilisateur donné

## Tasks / Subtasks

- [x] Task 1: Introduire le modèle de baseline utilisateur (AC: 1, 2)
  - [x] Créer la migration Alembic correspondante
  - [x] Ajouter le modèle SQLAlchemy
  - [x] Définir les contraintes d’unicité et les index utiles

- [x] Task 2: Créer la couche repository/read-write de baseline (AC: 1, 2, 4)
  - [x] Ajouter un repository dédié
  - [x] Supporter l’upsert / replace versionné
  - [x] Exposer une lecture simple par utilisateur + version active

- [x] Task 3: Définir le service de génération de baseline (AC: 3, 4)
  - [x] Introduire un service `UserPredictionBaselineService` ou équivalent
  - [x] Réutiliser le moteur daily existant sans coupler la couche API
  - [x] Gérer explicitement les cas variance nulle / échantillon incomplet

- [x] Task 4: Couvrir la couche par des tests ciblés (AC: 5)
  - [x] Tests de migration / modèle
  - [x] Tests repository
  - [x] Tests de génération déterministe
  - [x] Tests des cas limites de variance et historique incomplet

## Dev Notes

- Cette story pose le socle de la calibration relative utilisateur sans modifier encore le contrat public daily.
- La baseline doit être pensée comme une donnée métier versionnée, pas comme un cache opaque.
- Le calcul principal recommandé repose sur `raw_score`, les statistiques sur `note_20` restant utiles pour exposition/debug.
- Le service de génération doit rester compatible avec le couple `reference_version` / `ruleset_version` actif et avec l’éventuel `house_system_effective`.
- Cette story ne doit pas encore produire de micro-tendances visibles dans l’API publique.

### Project Structure Notes

- Fichiers backend principaux:
  - `backend/app/infra/db/models/` (nouveau modèle baseline)
  - `backend/app/infra/db/repositories/` (nouveau repository baseline)
  - `backend/app/services/` (nouveau service baseline)
  - `backend/alembic/versions/` (nouvelle migration)
  - `backend/app/services/daily_prediction_service.py` (lecture ultérieure, pas forcément modifié dans cette story)

### Technical Requirements

- La baseline doit être calculable et relisible indépendamment de l’API.
- Les statistiques doivent être déterministes pour un même utilisateur et une même fenêtre de simulation.
- Les champs stockés doivent suffire aux futures stories de scoring relatif sans imposer une nouvelle migration immédiate.
- Prévoir explicitement la possibilité de recalculer la baseline lors d’un changement de version métier.

### Architecture Compliance

- La baseline utilisateur est une couche de donnée intermédiaire entre moteur de calcul et projection publique.
- Le routeur FastAPI ne doit pas intervenir dans sa génération.
- Le service applicatif daily ne doit pas porter le détail de calcul statistique de la baseline.

### Library / Framework Requirements

- Réutiliser SQLAlchemy, Alembic, FastAPI et Pytest existants uniquement.
- Aucun ajout de dépendance externe requis pour les statistiques de base.

### File Structure Requirements

- Le modèle et le repository baseline doivent vivre côté `infra/db`.
- Le calcul et l’orchestration baseline doivent vivre côté `services`, pas côté routeur ni frontend.

### Testing Requirements

- Couvrir:
  - migration
  - repository
  - génération de baseline
  - cas variance nulle / sample incomplet
- Exécuter `ruff check` et `pytest` dans le venv.

### Previous Story Intelligence

- 37.2 et 37.3 ont déjà introduit des jobs et statistiques de calibration côté catégories; cette story doit réutiliser cet état de l’art sans le dupliquer. [Source: _bmad-output/implementation-artifacts/37-2-job-generation-rawday-calibration.md]
- 41.11 a clarifié la frontière persistance/API avec un snapshot typé; cette story doit suivre cette même logique de séparation claire des représentations de lecture et de calcul. [Source: _bmad-output/implementation-artifacts/41-11-snapshot-persisted-et-nettoyage-frontiere-api-persistance.md]

### Git Intelligence Summary

- Les refactors récents Epic 41 ont montré que la lisibilité des frontières service/persistance est critique; la baseline doit être introduite comme une couche dédiée explicite, pas comme un enrichissement opportuniste du run daily.

### Project Context Reference

- Aucun `project-context.md` détecté dans le repo.
- Les règles actives du repo viennent de `AGENTS.md`, de `epics.md` et de la spec `_bmad-output/planning-artifacts/epic-41-relative-calibration-spec.md`.

### References

- [Source: _bmad-output/planning-artifacts/epic-41-relative-calibration-spec.md]
- [Source: _bmad-output/planning-artifacts/epics.md#Epic-41]
- [Source: backend/app/services/daily_prediction_service.py]
- [Source: backend/app/tests/integration/test_daily_prediction_qa.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story créée à partir de la spec de calibration relative Epic 41 rédigée le 2026-03-10.

### Completion Notes List

- Baseline versionnée persistée avec bornes de fenêtre explicites (`window_start_date`, `window_end_date`) et unicité par utilisateur/catégorie/fenêtre/versions/house system.
- Génération rendue déterministe via une date de fin explicite et garde-fous sur historique incomplet, catégorie absente et variance nulle.
- Tests d’intégration étendus sur migration, upsert, versionnement, déterminisme et historique incomplet.

### File List

- `backend/app/infra/db/models/user_prediction_baseline.py`
- `backend/app/infra/db/repositories/user_prediction_baseline_repository.py`
- `backend/app/prediction/persisted_baseline.py`
- `backend/app/services/user_prediction_baseline_service.py`
- `backend/app/tests/integration/test_user_prediction_baseline.py`
- `backend/migrations/versions/20260310_0043_add_user_prediction_baselines.py`
- `_bmad-output/implementation-artifacts/41-12-baseline-utilisateur-12-mois-pour-calibration-relative.md`
