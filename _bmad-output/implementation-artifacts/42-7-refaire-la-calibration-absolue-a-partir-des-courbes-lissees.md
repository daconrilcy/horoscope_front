# Story 42.7: Refaire la calibration absolue à partir des courbes lissées

Status: done

## Story

As a backend maintainer,
I want recalibrer les notes journalières à partir de métriques continues plus riches,
so that les notes cessent de s'écraser autour du neutre quand la dynamique intrajournalière existe réellement.

## Acceptance Criteria

1. La calibration v3 s'appuie au minimum sur:
   - `level_day`
   - `intensity_day`
   - `dominance_day`
   - `stability_day`
2. Une journée intense mais ambivalente n'est plus assimilée à une journée plate.
3. Le backend garde une note publique lisible sur 20.
4. Le moteur permet la comparaison v2/v3 de calibration sur des fixtures identiques.
5. Les tests montrent une meilleure discrimination que la formule v2 sur des cas ciblés.

## Tasks / Subtasks

- [x] Task 1: Définir les nouvelles métriques de calibration (AC: 1)
  - [x] Définir la dérivation depuis `S_smooth(c,t)`
  - [x] Introduire les seuils ou percentiles nécessaires

- [x] Task 2: Réimplémenter la calibration absolue v3 (AC: 2, 3)
  - [x] Brancher la nouvelle logique dans `calibrator.py`
  - [x] Préserver une sortie lisible sur 20

- [x] Task 3: Préparer la comparaison v2/v3 (AC: 4)
  - [x] Exposer un mode comparatif ou des fixtures de comparaison
  - [x] Éviter de casser le chemin v2

- [x] Task 4: Tests (AC: 5)
  - [x] Comparaison sur journées plates, ambiguës et intensives
  - [x] Vérification de la discrimination gagnée

## Dev Notes

- La formule v2 `0.70 mean + 0.20 peak90 + 0.10 close` a bien servi, mais elle fait partie de la dette explicitement visée par Epic 42.
- Le but n'est pas juste de retuner des coefficients; il faut changer de base métrique.
- Cette story est la suite naturelle de 42.6, pas un tuning isolé.

### Project Structure Notes

- Fichiers principaux:
  - `backend/app/prediction/calibrator.py`
  - `backend/app/prediction/aggregator.py`
  - `backend/app/tests/unit/test_calibrator.py`

### References

- [Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]
- [Source: backend/app/prediction/calibrator.py]
- [Source: backend/app/prediction/aggregator.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 42.

### Completion Notes List

- Calibration v3 rebranchée sur les ancres `CalibrationData` au lieu d'une formule purement hardcodée.
- La note absolue combine maintenant calibration, intensité, dominance et stabilité sans casser le neutre à 10.
- La comparaison v2/v3 reste possible sur fixtures identiques via les tests ciblés.

### File List

- `backend/app/prediction/calibrator.py`
- `backend/app/prediction/aggregator.py`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/prediction/schemas.py`
- `backend/app/tests/unit/test_v3_calibration.py`
- `backend/app/tests/unit/test_v3_metrics.py`
- `_bmad-output/implementation-artifacts/42-7-refaire-la-calibration-absolue-a-partir-des-courbes-lissees.md`
