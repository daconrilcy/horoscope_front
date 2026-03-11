# Story 42.12: Étendre la baseline utilisateur en baseline day, slot et saison

Status: ready-for-dev

## Story

As a platform engineer,
I want enrichir la baseline utilisateur pour tenir compte du jour, de l'heure et de la saison,
so that la calibration personnelle compare des choses comparables et puisse servir le scoring v3.

## Acceptance Criteria

1. La persistance supporte au minimum:
   - `baseline_day`
   - `baseline_slot`
   - `baseline_month` ou `baseline_season`
2. Les nouvelles baselines sont versionnées par utilisateur, thème, fenêtre et versions métier.
3. La story couvre prioritairement le modèle, la migration, le repository et une génération minimale déterministe.
4. La résolution runtime avancée des bonnes baselines selon le contexte est traitée explicitement par la story suivante.
5. Un budget de performance explicite borne le coût de génération de baseline enrichie.
6. Les tests couvrent lecture, écriture et génération minimale déterministe.

## Tasks / Subtasks

- [ ] Task 1: Étendre le modèle de baseline (AC: 1, 2)
  - [ ] Définir les nouveaux niveaux de baseline
  - [ ] Adapter modèle, migration et repository

- [ ] Task 2: Introduire une génération minimale déterministe des nouvelles baselines (AC: 3, 5)
  - [ ] Ajouter la production par slot et saison/mois
  - [ ] Conserver le caractère déterministe
  - [ ] Définir un SLO de génération

- [ ] Task 3: Préparer la lecture pour la story suivante (AC: 4)
  - [ ] Exposer les primitives repository utiles
  - [ ] Éviter de mélanger ici repository, génération et résolution produit avancée

- [ ] Task 4: Tests (AC: 6)
  - [ ] Tester write/read sur les trois niveaux
  - [ ] Tester génération minimale déterministe et versionnement

## Dev Notes

- La baseline journalière seule est jugée trop grossière pour le moteur v3.
- Cette story étend le travail des stories 41.12 et 41.15, mais avec une ambition plus fine et un modèle préparé pour les créneaux.
- Prévoir une modélisation qui reste lisible et requêtable.
- Cette story est volontairement resserrée: modèle + persistance + génération minimale. La résolution runtime avancée part en 42.13 pour éviter d'en faire un goulet d'étranglement.

### Project Structure Notes

- Fichiers principaux:
  - `backend/app/services/user_prediction_baseline_service.py`
  - `backend/app/infra/db/repositories/user_prediction_baseline_repository.py`
  - `backend/app/infra/db/models/user_prediction_baseline.py`

### References

- [Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]
- [Source: backend/app/services/user_prediction_baseline_service.py]
- [Source: backend/app/infra/db/repositories/user_prediction_baseline_repository.py]
- [Source: backend/app/infra/db/models/user_prediction_baseline.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 42.

### Completion Notes List

- Story prête pour enrichir la baseline utilisateur au-delà du simple niveau journalier.

### File List

- `_bmad-output/implementation-artifacts/42-12-etendre-la-baseline-utilisateur-en-baseline-day-slot-et-saison.md`
