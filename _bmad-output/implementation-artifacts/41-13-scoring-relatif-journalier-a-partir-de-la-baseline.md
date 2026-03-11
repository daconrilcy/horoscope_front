# Story 41.13: Scoring relatif journalier à partir de la baseline

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a prediction engine designer,
I want calculer des métriques relatives utilisateur pour chaque catégorie du daily,
so that le système puisse distinguer une journée neutre absolue d’une journée neutre avec des dominantes personnelles légères mais significatives.

## Acceptance Criteria

1. Le backend calcule, pour chaque catégorie quotidienne, des métriques relatives dérivées de la baseline utilisateur:
   - `relative_z_score` ou équivalent robuste
   - `relative_percentile` ou fallback robuste
   - `relative_rank`

2. Le calcul relatif est stable et sûr sur les cas dégénérés:
   - variance nulle
   - baseline absente
   - échantillon trop faible
   - catégorie absente dans la baseline

3. Le scoring relatif ne modifie pas le scoring absolu existant:
   - `note_20`, `raw_score`, `power`, `volatility` restent inchangés
   - aucune réécriture du ton global ou des fenêtres décisionnelles à ce stade

4. Le service applicatif daily peut obtenir les métriques relatives pour une journée donnée sans dupliquer la logique statistique.

5. Des tests couvrent:
   - calcul nominal
   - fallback sans baseline
   - variance nulle
   - ordering/ranking relatif
   - non-régression du scoring absolu

## Tasks / Subtasks

- [x] Task 1: Introduire les types de scoring relatif (AC: 1, 2)
  - [x] Définir les DTO/types backend nécessaires
  - [x] Ajouter la structure de retour par catégorie
  - [x] Rendre explicites les cas `unavailable`

- [x] Task 2: Implémenter le calcul relatif (AC: 1, 2, 3)
  - [x] Créer un service/calculateur dédié
  - [x] Utiliser la baseline 12 mois comme entrée
  - [x] Gérer les fallbacks sur variance nulle et baseline absente

- [x] Task 3: Intégrer le scoring relatif dans le flux daily backend (AC: 3, 4)
  - [x] Brancher le service applicatif ou une couche dédiée de projection interne
  - [x] Préserver strictement le scoring absolu existant
  - [x] Éviter toute duplication de logique entre service et assembleur

- [x] Task 4: Tester la non-régression et les edge cases (AC: 5)
  - [x] Tests unitaires de calcul
  - [x] Tests d’intégration service daily
  - [x] Vérifier que les sorties absolues restent inchangées

## Dev Notes

- Cette story introduit la lecture relative, pas encore son exposition publique principale.
- La métrique canonique recommandée reste calculée sur `raw_score`, avec fallback percentile lorsque l’écart-type n’est pas exploitable.
- Le résultat relatif doit pouvoir être consommé aussi bien par le debug que par la future projection publique des journées plates.
- Le flux de calcul doit rester déterministe et testable sans dépendre de l’éditorial.

### Project Structure Notes

- Fichiers backend principaux:
  - `backend/app/services/daily_prediction_service.py`
  - `backend/app/services/daily_prediction_types.py`
  - nouveau service de scoring relatif
  - éventuellement `backend/app/prediction/persisted_snapshot.py` si enrichissement typé temporaire

### Technical Requirements

- Le scoring relatif doit être une couche additive.
- Les métriques doivent être disponibles sans casser la compatibilité du contrat public.
- Le ranking relatif doit être stable et explicite en cas d’égalité.
- Les fallbacks doivent éviter toute division instable ou faux signal amplifié.

### Architecture Compliance

- La logique statistique relative ne doit pas être dispersée entre service, routeur et assembleur.
- Le service applicatif consomme une couche dédiée de scoring relatif.
- L’API publique ne doit pas encore dépendre implicitement de détails statistiques bas niveau.

### Library / Framework Requirements

- Réutiliser uniquement la stack backend existante.
- Aucun ajout de dépendance requis.

### File Structure Requirements

- Le calcul relatif vit côté `services` ou `prediction` backend.
- Les types partagés éventuels doivent rester explicites et proches du domaine daily.

### Testing Requirements

- Couvrir:
  - z-score nominal
  - variance nulle
  - baseline absente
  - ranking relatif
  - non-régression du scoring absolu
- Exécuter `ruff check` et `pytest` dans le venv.

### Previous Story Intelligence

- 40.2 a déjà renforcé la discrimination des scores en calibration provisoire; cette story doit enrichir la lecture sans contredire ce travail. [Source: _bmad-output/implementation-artifacts/40-2-discrimination-scores-calibration-provisoire.md]
- 41.8 à 41.11 ont clarifié le découpage service/assembleur/snapshot; le scoring relatif doit s’insérer proprement dans cette architecture. [Source: _bmad-output/implementation-artifacts/41-8-decoupage-service-applicatif-daily-prediction.md]

### Git Intelligence Summary

- Les derniers refactors Epic 41 ont réduit le couplage entre service, API et persistance; ce scoring relatif doit rester une couche bien isolée pour éviter une nouvelle confusion de responsabilités.

### Project Context Reference

- Aucun `project-context.md` détecté dans le repo.
- Les règles actives du repo viennent de `AGENTS.md`, de `epics.md` et de la spec `_bmad-output/planning-artifacts/epic-41-relative-calibration-spec.md`.

### References

- [Source: _bmad-output/planning-artifacts/epic-41-relative-calibration-spec.md]
- [Source: backend/app/services/daily_prediction_service.py]
- [Source: backend/app/services/daily_prediction_types.py]
- [Source: backend/app/prediction/public_projection.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story créée à partir de la spec de calibration relative Epic 41 rédigée le 2026-03-10.

### Completion Notes List

- Scoring relatif branché dans le flux daily via une couche dédiée de service/calcul, sans mutation des champs absolus du snapshot.
- Fallback sur variance nulle rendu exploitable via percentile et ranking, avec tie-break stable en cas d’égalité.
- Lookup de baseline assoupli sur la baseline la plus récente compatible, et les métriques relatives restent internes à 41.13 sans fuite dans la projection publique.

### File List

- `backend/app/prediction/persisted_relative_score.py`
- `backend/app/prediction/relative_scoring_calculator.py`
- `backend/app/services/relative_scoring_service.py`
- `backend/app/services/daily_prediction_service.py`
- `backend/app/infra/db/repositories/user_prediction_baseline_repository.py`
- `backend/app/prediction/persisted_snapshot.py`
- `backend/app/prediction/public_projection.py`
- `backend/app/tests/unit/test_relative_scoring_calculator.py`
- `backend/app/tests/integration/test_relative_scoring_service.py`
- `backend/app/tests/unit/test_daily_prediction_service.py`
- `backend/app/tests/unit/test_public_projection.py`
- `_bmad-output/implementation-artifacts/41-13-scoring-relatif-journalier-a-partir-de-la-baseline.md`
