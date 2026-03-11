# Story 42.13: Refaire le scoring relatif v3 autour d'absolu, slot, confiance et rareté

Status: done

## Story

As a prediction engine designer,
I want calculer un scoring relatif plus fin que le simple z-score journalier,
so that le produit puisse comparer un jour, un créneau et une intensité de manière cohérente avec le moteur v3.

## Acceptance Criteria

1. Le backend expose au minimum:
   - `z_abs`
   - `z_slot`
   - `pct_abs`
   - `pct_rel`
   - une notion de rareté
2. Le fallback variance nulle reste robuste.
3. Le scoring relatif devient compatible avec les blocs et fenêtres v3.
4. Le scoring absolu demeure la vérité produit principale.
5. Les tests couvrent absence de baseline, variance nulle et cas nominal.

## Tasks / Subtasks

- [x] Task 1: Définir le contrat de scoring relatif v3 (AC: 1, 4)
  - [x] Ajouter les nouveaux champs de score relatif
  - [x] Définir les conventions de lecture produit

- [x] Task 2: Réimplémenter le calculateur relatif (AC: 1, 2, 3)
  - [x] Adapter `relative_scoring_calculator.py`
  - [x] Utiliser les nouveaux niveaux de baseline

- [x] Task 3: Adapter le service relatif (AC: 3, 4)
  - [x] Résoudre les bonnes baselines selon thème et contexte
  - [x] Préserver le primat de l'absolu

- [x] Task 4: Tests (AC: 5)
  - [x] Cas nominal
  - [x] Variance nulle
  - [x] Baseline absente

## Dev Notes

- Cette story est la traduction relative des stories 42.6 et 42.12.
- Le relatif doit aider, pas prendre le contrôle du produit.
- La rareté mérite une sortie explicite; elle sera utile autant côté QA que côté evidence pack.

### Project Structure Notes

- Fichiers principaux:
  - `backend/app/services/relative_scoring_service.py`
  - `backend/app/prediction/relative_scoring_calculator.py`
  - `backend/app/prediction/persisted_relative_score.py`

### References

- [Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]
- [Source: backend/app/services/relative_scoring_service.py]
- [Source: backend/app/prediction/relative_scoring_calculator.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 42.

### Completion Notes List

- Le scoring relatif expose `z_abs`, `z_slot`, `pct_abs`, `pct_rel` et une rareté explicite autour du baseline v3.
- Code review fix: `RelativeScoringCalculator` accepte à nouveau les baselines legacy journalières en entrée, sans casser le contrat granulaire.
- Code review fix: `PersistedRelativeScore` reste compatible avec les appels positionnels historiques tout en exposant les champs v3.
- Les tests couvrent nominal, variance nulle, baseline absente et ranking stable.

### File List

- `backend/app/prediction/persisted_relative_score.py`
- `backend/app/prediction/relative_scoring_calculator.py`
- `backend/app/tests/unit/test_relative_scoring_calculator.py`
- `backend/app/tests/unit/test_v3_relative_scoring.py`
- `_bmad-output/implementation-artifacts/42-13-refaire-le-scoring-relatif-v3-autour-d-absolu-slot-confiance-et-rarete.md`
